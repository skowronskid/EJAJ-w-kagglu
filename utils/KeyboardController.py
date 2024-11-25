import utils.state as game_state
import pygame

KEYS_PRESSED_DEBUG = False


class KeyboardController:
    def __init__(self) -> None:
        pass

    def get_action(self, state: game_state.GameState) -> game_state.GameActions:
        keys = pygame.key.get_pressed()
        
        if KEYS_PRESSED_DEBUG:
            print(keys[pygame.K_UP], keys[pygame.K_RIGHT], keys[pygame.K_DOWN], keys[pygame.K_LEFT])
        
        # if more than 2 keys are pressed - no action
        if sum(keys) > 2: # wrong input
            return game_state.GameActions.no_action
        if sum(keys) == 1:  # cardinal directions
            if keys[pygame.K_UP]:
                return game_state.GameActions.Up
            elif keys[pygame.K_DOWN]:
                return game_state.GameActions.Down
            elif keys[pygame.K_LEFT]:
                return game_state.GameActions.Left
            elif keys[pygame.K_RIGHT]:
                return game_state.GameActions.Right
        # diagonals
        if keys[pygame.K_UP] and keys[pygame.K_RIGHT]:
            return game_state.GameActions.Up_Right
        if keys[pygame.K_DOWN] and keys[pygame.K_RIGHT]:
            return game_state.GameActions.Down_Right
        if keys[pygame.K_DOWN] and keys[pygame.K_LEFT]:
            return game_state.GameActions.Down_Left
        if keys[pygame.K_UP] and keys[pygame.K_LEFT]:
            return game_state.GameActions.Up_Left
        return game_state.GameActions.no_action # all other cases