import utils.static as static
from enum import Enum
import random
import math
import numpy as np

DEBUG = False

class GameActions(Enum):
    no_action = 0
    Up = 1
    Up_Right = 2
    Right = 3
    Down_Right = 4
    Down = 5
    Down_Left = 6
    Left = 7
    Up_Left = 8

class GameObservation(Enum):
    nothing = 0
    enemy_attacked = -1
    reached_goal = 1


class GameState:
    def __init__(self) -> None:
        # random.seed(static.GAME_SEED)
        self.boundary = static.Entity(
            0, 0, static.GAME_WIDTH, static.GAME_HEIGHT
        )
        self.player_entity = static.Player(
            static.Entity(
                np.random.randint(0, static.GAME_WIDTH - static.PLAYER_SIZE),
                np.random.randint(0, static.GAME_HEIGHT - static.PLAYER_SIZE),
                static.PLAYER_SIZE, static.PLAYER_SIZE
            ),
            static.Vector(),
            static.GAME_FRICTION,
            static.GAME_ACC_FACTOR,
        )
        self.goal_entity = static.Entity(
            0, 0, static.GOAL_SIZE, static.GOAL_SIZE
        )
        self.enemy_collection = []
        self.reset_goal()
        self._initialize_enemies()

    def reset_goal(self) -> None:
        self.goal_entity.x = random.randint(0, static.GAME_WIDTH - static.GOAL_SIZE)
        self.goal_entity.y = random.randint(0, static.GAME_HEIGHT - static.GOAL_SIZE)

    def update(self, action: GameActions) -> GameObservation:
        input_vector = self._get_input_vector(action)
        self.current_observation = GameObservation.nothing

        self.player_entity.move(input_vector, self.boundary)
        if static.check_collision(self.player_entity.entity, self.goal_entity):
            self.current_observation = GameObservation.reached_goal
            self.reset_goal()

        for enemy in self.enemy_collection:
            enemy.move(self.boundary)
            if static.check_collision(enemy.entity, self.player_entity.entity):
                self.current_observation = GameObservation.enemy_attacked

        if DEBUG:
            print(self.current_observation)
        return self.current_observation

    def _initialize_enemies(self):
        enemy_size = static.ENEMY_SIZE
        x_limit = static.GAME_WIDTH - enemy_size
        y_limit = static.GAME_HEIGHT - enemy_size
        spawn_margin = static.PLAYER_SIZE * 2

        for _ in range(static.ENEMY_COUNT):
            phi = random.uniform(0, math.pi * 2)
            velocity = static.Vector(
                math.cos(phi) * static.ENEMY_SPEED,
                math.sin(phi) * static.ENEMY_SPEED,
            )
            enemy = static.Enemy(
                static.Entity(
                    random.randint(spawn_margin, x_limit),
                    random.randint(spawn_margin, y_limit),
                    enemy_size,
                    enemy_size,
                ),
                velocity,
            )
            self.enemy_collection.append(enemy)

    @staticmethod
    def _get_input_vector(action: GameActions) -> static.Vector:
        if action == GameActions.Up:
            return static.Vector(0, -1)
        if action == GameActions.Up_Right:
            return static.Vector(1, -1)
        if action == GameActions.Right:
            return static.Vector(1, 0)
        if action == GameActions.Down_Right:
            return static.Vector(1, 1)
        if action == GameActions.Down:
            return static.Vector(0, 1)
        if action == GameActions.Down_Left:
            return static.Vector(-1, 1)
        if action == GameActions.Left:
            return static.Vector(-1, 0)
        if action == GameActions.Up_Left:
            return static.Vector(-1, -1)
        return static.Vector(0, 0)