import pygame


class Window:
    # WIDTH = 1920
    # HEIGHT = 1080
    # FULLSCREEN = True

    WIDTH = 1024
    HEIGHT = 512

    # WIDTH = 1440
    # HEIGHT = 900
    FULLSCREEN = False

    VERSION = "v0.1"


class HUD:
    PLAYER2_DELTA_X = 400
    SCORE_HUD_POS_X = (0, PLAYER2_DELTA_X)
    SCORE_HUD_POS_Y = (Window.HEIGHT, 0)
    SCORE_POS_X = (30, 30+PLAYER2_DELTA_X)
    SCORE_POS_Y = (45, 45)
    TIME_OUT_POS_X = (50, 50+PLAYER2_DELTA_X)
    TIME_OUT_POS_Y = (70, 70)
    INVENTORY_X = (0, PLAYER2_DELTA_X)
    POINTS100_X = (-200, 200+PLAYER2_DELTA_X)
    POINTS100_SPEED_DIRECTION = (1, -1)
    POINTS_HUD = None
    INVENTORY_HUD = None


class KeyboardKeys:
    KEY_ESC = pygame.K_ESCAPE
    KEY_LEFT = (pygame.K_a, pygame.K_LEFT)
    KEY_RIGHT = (pygame.K_d, pygame.K_RIGHT)
    KEY_UP = (pygame.K_w, pygame.K_UP)
    KEY_DOWN = (pygame.K_s, pygame.K_DOWN)

    KEY_Y = pygame.K_y

    KEY_ONE = (pygame.K_1, pygame.K_KP1)
    KEY_FIVE = (pygame.K_5, pygame.K_KP5)
    KEY_TO_NUM = (KEY_ONE[0] - 1, KEY_ONE[1] - 1)


class RoadPositions:
    WIDTH = 400
    LEFT_LANE = 280
    MIDDLE_LANE = 200
    RIGHT_LANE = 120
    UPPER_LIMIT = 320
    LOWER_LIMIT = 80

    FORWARD_LIMIT = 8000
    REAR_LIMIT = -200
    COLLISION_HORIZON = 4100
    BEYOND_HORIZON = 4400
    BEHIND_REAR_HORIZON = -2400

    LOD_DISTANCE = 2000


class Speed:
    ONE_METER = 20
    KMH_TO_MS = 0.2777
    MS_TO_GLMIL = 0.02
    KMH_TO_GLMIL = KMH_TO_MS*MS_TO_GLMIL
    ONE_KMH = KMH_TO_GLMIL
    MAX_KMH = 120
    MAX_SPEED = MAX_KMH*ONE_KMH
    BASE_CRASH_SPEED_DECREASE = (10*ONE_KMH)
    RAD_TO_DEGREE = 57.2958
    MAX_WOBBLE_ROTATION = 0.52359*RAD_TO_DEGREE
    ONE_RADMIL = 0.001*RAD_TO_DEGREE
    ONE_DEGREE_MIL = 1
    DEGREES_TO_RADIANS = 0.017453
    PLAYER_ACCELERATE_SPEED = 30*ONE_KMH
    PLAYER_BRAKE_SPEED = 30*ONE_KMH
    PLAYER_LATERAL_SPEED = 30*ONE_KMH
    PLAYER_LATERAL_SPEED_SHRUNK = 15*ONE_KMH


class Steering:
    CENTERED = 0
    TURN_LEFT = -1
    TURN_RIGHT = 1


class SkidMarks:
    SKID_LEFT = None
    SKID_RIGHT = None
    SKID_STRAIGHT = None


class Sounds:
    ACCEL = None
    BRAKE = None
    CRASH = None
    ROLLOVER = None
    SIREN = None
    HORN = None
    HOLY = None
    MAYHEM = None
    ANNIHILATION = None


class PowerUps:
    TIME_OUT = 10000  # in miliseconds
    INVENTORY_SIZE = 5
    SIZE = 50
    EMPTY = None
    CRATE = None
    SHIELD = None
    ENERGY_SHIELD = None
    HYDRAULICS = None
    CALL_911 = None
    SHRINK = None
    PHASER_FIRE = None
    PHASER = None
