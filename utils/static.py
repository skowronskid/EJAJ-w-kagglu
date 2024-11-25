from numpy import sqrt
GAME_WIDTH = 400
GAME_HEIGHT = 300
GAME_DIAGONAL = sqrt(GAME_WIDTH**2 + GAME_HEIGHT**2)
PLAYER_SIZE = 20

GAME_FRICTION = 0.15
GAME_ACC_FACTOR = 1.5

GOAL_SIZE = 10

ENEMY_SIZE = 25
ENEMY_COUNT = 1
ENEMY_SPEED = 4

BACKGROUND = (3, 24, 77)
ENEMY_COLOR = (168, 7, 7)
PLAYER_COLOR = (77, 148, 93)
GOAL_COLOR = (250, 188, 17)

FPS = 10

GAME_SEED = 20


MAX_ENTITY_SIZE = max(PLAYER_SIZE, GOAL_SIZE, ENEMY_SIZE)


class Entity:
    def __init__(self, x,y, width, height) -> None:
        self.x = x 
        self.y = y 
        self.width = width
        self.height = height


class Vector:
    def __init__(self, x=0, y=0) -> None:
        self.x = x
        self.y = y


def check_collision(a: Entity, b: Entity) -> bool:
    if b.x > a.x + a.width or a.x > b.x + b.width:
        return False
    if b.y > a.y + a.height or a.y > b.y + b.height:
        return False
    return True



def move(rect: Entity, v: Vector, boundary: Entity) -> None:
    rect.x += v.x
    rect.y += v.y

    def clamp(rv: int, bv: int, rs: int, bs: int, vv: float) -> tuple[int, float]:
        if rv <= bv or rv + rs >= bv + bs:
            vv = -vv
            rv = bv + 1 if rv <= bv else bv + bs - rs - 1
        return (rv, vv)

    rect.x, v.x = clamp(rect.x, boundary.x, rect.width, boundary.width, v.x)
    rect.y, v.y = clamp(rect.y, boundary.y, rect.height, boundary.height, v.y)

    return rect, v


class Enemy:
    def __init__(self, rect: Entity, vel: Vector) -> None:
        self.entity = rect
        self.velocity = vel

    def __str__(self):
        return f"(Entity: {self.entity}, Velocity: {self.velocity})"

    def move(self, boundary: Entity) -> None:
        self.entity, self.velocity = move(self.entity, self.velocity, boundary)


class Player:
    def __init__(self, rect: Entity, vel: Vector, fr: float, af) -> None:
        self.entity = rect
        self.velocity = vel
        self.friction = fr
        self.acc_factor = af

    def __str__(self):
        return f"(Entity: {self.entity}, Velocity: {self.velocity}, Friction: {self.friction})"

    def move(self, acc: Vector, boundary: Entity) -> None:
        def handle_axis(current_velocity: float, acceleration: float, friction: float, acceleration_factor: float) -> float:
            return current_velocity + (acceleration * acceleration_factor) - (current_velocity * friction)

        self.velocity.x = handle_axis(
            self.velocity.x, acc.x, self.friction, self.acc_factor
        )
        self.velocity.y = handle_axis(
            self.velocity.y, acc.y, self.friction, self.acc_factor
        )
        self.entity, self.velocity = move(self.entity, self.velocity, boundary)
