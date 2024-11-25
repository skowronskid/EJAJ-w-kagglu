import utils.state as game_state
import utils.static as game_static
from utils.ModifiedTensorBoard import ModifiedTensorBoard
import pygame



from collections import deque
import time
from tqdm import tqdm
import random


import numpy as np
import tensorflow as tf
import keras
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam




REPLAY_MEMORY_SIZE = 8_000  # How many last steps to keep for model training
MIN_REPLAY_MEMORY_SIZE = 1_000  
MINIBATCH_SIZE = 16  # How many steps (samples) to use for training
UPDATE_TARGET_EVERY = 5  # Terminal states (end of episodes)



class PositionalController:
    def __init__(self, model_name,lr,discount,number_of_states,number_of_actions) -> None:
        self.lr = lr
        self.discount = discount
        self.number_of_states = number_of_states
        self.number_of_actions = number_of_actions
        
        self.model = self.create_model() # main model

        self.target_model = self.create_model() # target model
        self.target_model.set_weights(self.model.get_weights())
        self.target_update_counter = 0 #when to update target network with main network's weights

        self.replay_memory = deque(maxlen=REPLAY_MEMORY_SIZE) # array with last n steps for minibatch training

        self.tensorboard = ModifiedTensorBoard(log_dir="logs/{}-{}".format(model_name, int(time.time()))) #logging

        
    def create_model(self):
        model = Sequential([
            Dense(128, input_shape=(self.number_of_states,), activation='relu'),
            Dense(128, activation='relu'),
            Dense(128, activation='relu'),
            Dense(self.number_of_actions, activation='linear'),
        ])        
        model.compile(loss='mse', optimizer=Adam(learning_rate=self.lr))
        return model
    
    
    def load_model(self, name):
        self.model = keras.saving.load_model('trained_controllers/' + name)
        self.target_model = keras.saving.load_model('trained_controllers/' + name)


    def get_features(self, state):
        player_info = [
            state.player_entity.entity.height/game_static.MAX_ENTITY_SIZE,
            state.player_entity.entity.width/game_static.MAX_ENTITY_SIZE,
            state.player_entity.friction,
            state.player_entity.acc_factor,
             
            state.player_entity.entity.x/game_static.GAME_WIDTH,  
            state.player_entity.entity.y/game_static.GAME_HEIGHT,
            state.player_entity.velocity.x,
            state.player_entity.velocity.y
        ]
        goal_info = [
            state.goal_entity.x/game_static.GAME_WIDTH,
            state.goal_entity.y/game_static.GAME_HEIGHT,
            # state.goal_entity.height/game_static.MAX_ENTITY_SIZE,
            # state.goal_entity.width/game_static.MAX_ENTITY_SIZE,
            # distance to goal
            (
                np.sqrt(
                    (state.player_entity.entity.x - state.goal_entity.x)**2 
                    + (state.player_entity.entity.y - state.goal_entity.y)**2
                ) / game_static.GAME_DIAGONAL
            ),
            state.player_entity.entity.x - state.goal_entity.x/game_static.GAME_WIDTH, #distance in x
            state.player_entity.entity.y - state.goal_entity.y/game_static.GAME_WIDTH #distance in y
            
        ]
        enemy_info = [
            [
                enemy_entity.entity.x/game_static.GAME_WIDTH,
                enemy_entity.entity.y/game_static.GAME_HEIGHT,
                # enemy_entity.entity.height/game_static.MAX_ENTITY_SIZE,
                # enemy_entity.entity.width/game_static.MAX_ENTITY_SIZE,
                enemy_entity.velocity.x,
                enemy_entity.velocity.y,
                # distance from the player to the enemy
                np.sqrt(
                        (state.player_entity.entity.x - enemy_entity.entity.x)**2 
                        + (state.player_entity.entity.y - enemy_entity.entity.y)**2
                ) / game_static.GAME_DIAGONAL,
                state.player_entity.entity.x - state.enemy_entity.entity.x/game_static.GAME_WIDTH, #distance in x
                state.player_entity.entity.y - state.enemy_entity.entity.y/game_static.GAME_WIDTH #distance in y
            ]
            for enemy_entity in state.enemy_collection
        ]
        return player_info, goal_info, enemy_info
    
    
    def get_action(self, state):
        player_info, goal_info, enemy_info = self.get_features(state)
        state_tensor = tf.convert_to_tensor([float(f) for feature_list in [player_info, goal_info, *enemy_info] for f in feature_list])
        
        # deciding which action to take
        action = self.model.predict(np.array(state_tensor).reshape(-1, self.number_of_states),verbose=0)[0]
        return game_state.GameActions(np.argmax(action))


    def update_replay_memory(self, transition):
        # transition = (observation space, action, reward, new observation space, done)
        self.replay_memory.append(transition)

    # Trains main network every step during episode
    def train(self, terminal_state, step):
        if len(self.replay_memory) < MIN_REPLAY_MEMORY_SIZE: # starting after certain number of steps
            return

        minibatch = random.sample(self.replay_memory, MINIBATCH_SIZE)

        current_states = tf.convert_to_tensor([transition[0] for transition in minibatch]) # get current states from minibatch
        current_qs_list = self.model.predict(current_states,verbose=0) # query the model for Q values

        new_states = np.array([transition[3] for transition in minibatch]) # get future states from minibatch
        future_qs_list = self.target_model.predict(new_states, verbose=0) # use target model to predict future states

        X = []
        y = []

        # Now we need to enumerate our batches
        for index, (current_state, action, reward, new_state, done) in enumerate(minibatch):

            
            if not done: # if the game hasn't ended, get new q from future states
                max_future_q = np.max(future_qs_list[index])
                new_q = reward + self.discount * max_future_q
            else:
                new_q = reward # otherwise set it to 0

            # Update Q value for given state
            current_qs = current_qs_list[index]
            current_qs[action] = new_q

            # And append to our training data
            X.append(current_state)
            y.append(current_qs)
        
        print(X)
        print(y)

        # fit the main model using the batch
        self.model.fit(
            np.array(X), np.array(y),
            batch_size=MINIBATCH_SIZE, verbose=0, shuffle=False,
            callbacks=[self.tensorboard] if terminal_state else None) # log only on terminal state

        # don't update weights of target model every episode
        if terminal_state:
            self.target_update_counter += 1

        # after a set number of episodes update the target model
        if self.target_update_counter > UPDATE_TARGET_EVERY:
            self.target_model.set_weights(self.model.get_weights())
            self.target_update_counter = 0



