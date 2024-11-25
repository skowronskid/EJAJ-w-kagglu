import pygame
import utils.static as game_static
import utils.state as game_state
import copy


class AbstractGame:
    def __init__(self, controller, training=False) -> None:
        self.__innerState = game_state.GameState()
        self.controller = controller
        self.done = False
        self.ticks = 0

        # Initialize Pygame
        if not training:
            pygame.init()
            self.graphics = pygame.display.set_mode((game_static.GAME_WIDTH, game_static.GAME_HEIGHT))
            pygame.display.set_caption("Advanced AI Game")
            self.clock = pygame.time.Clock()

    def get_current_state(self) -> game_state.GameState:
        return copy.deepcopy(self.__innerState)

    def update_frame(self, action_enum=None) -> None:
        if not action_enum:
            action_enum = self.controller.get_action(self.get_current_state())
        self.__innerState.update(action_enum)
        if self.__innerState.current_observation == game_state.GameObservation.enemy_attacked:
            self.done = True
        
    def draw_frame(self) -> None:
        self.graphics.fill(game_static.BACKGROUND)
        # Draw goal
        pygame.draw.rect(
            self.graphics,
            game_static.GOAL_COLOR,
            self.get_pygame_rect(self.__innerState.goal_entity),
        )
        # Draw player
        pygame.draw.rect(
            self.graphics,
            game_static.PLAYER_COLOR,
            self.get_pygame_rect(self.__innerState.player_entity.entity),
        )
        # Draw enemies
        for enemy in self.__innerState.enemy_collection:
            pygame.draw.rect(
                self.graphics,
                game_static.ENEMY_COLOR,
                self.get_pygame_rect(enemy.entity),
            )
        pygame.display.update()

    def delay(self) -> None:
        self.ticks += 1
        print(self.ticks)
        self.clock.tick(game_static.FPS)

    @staticmethod
    def get_pygame_rect(rect: game_static.Entity) -> pygame.Rect:
        return pygame.Rect(rect.x, rect.y, rect.width, rect.height)
    
    def reset(self):
        self.__innerState = game_state.GameState()
        self.done = False
        



def main():
    print("1. Try the game by controlling with keyboard")
    print("2. Use positional model")
    print("3. Use visual model")

    choice = input("Enter your choice: ")
    if choice.strip() == "1":
        from utils.KeyboardController import KeyboardController
        my_game = AbstractGame(KeyboardController())
    elif choice.strip() == "2":
        from utils.PositionalController import PositionalController
        NUMBER_OF_STATES = (
            game_static.ENEMY_COUNT * 6 # each enemy has 6 features: x,y position and velocity, as well as height and width
            + game_static.ENEMY_COUNT # distance from the player to the enemy
            + 8 # player has 8 features: x,y position and velocity, height and width, friction, acceleration factor
            + 4 # goal has 4 features: x,y position, height and width
            + 1 # distance to goal
            
        )
        NUMBER_OF_ACTIONS = 9
        controller = PositionalController(
            model_name="gaming",
            lr = 1,
            discount=1,
            number_of_actions=NUMBER_OF_ACTIONS,
            number_of_states=NUMBER_OF_STATES
        )
        controller.load_model("PC2___-58.75max_-126.58avg_-172.29min__1732547617.model")
        my_game = AbstractGame(controller)
        # load best the model
        
        
        # positional_controller = PositionalController()

        # if input("See how this model performs (y/n)? ").lower().startswith("y"):
        #     my_game = AbstractGame(positional_controller)
        # else:
        #     exit()
    
    elif choice.strip() == "3":
        from utils.VisualController import VisualController
        # visual_controller = VisualController()
        # load best the model


    # Main game loop
    game_loop = True
    while game_loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_loop = False

        my_game.draw_frame()
        my_game.update_frame()
        if my_game.done:
            print('Game Over')
            my_game.reset()
        # else:
        #     print(my_game.done)
        my_game.delay()


    pygame.quit()


if __name__ == "__main__":
    main()
