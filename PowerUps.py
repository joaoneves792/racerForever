from OpenGL.GL import glTranslate
from OpenGL.raw.GL.VERSION.GL_1_0 import glPushMatrix, glPopMatrix

from constants import PowerUps, Speed, RoadPositions


class PowerUp:
    def __init__(self, game, player=None):
        self.player = player
        self.game = game
        self.icon = PowerUps.EMPTY
        self.x = 0
        self.y = 0

    def drop(self, x, y):
        self.game.dropped_items.append(self)
        self.x = x
        self.y = y

    def execute(self):
        if self.player is None:
            return
        self.player.powerUpTimeOut = PowerUps.TIME_OUT
        self.applyPowerUp()

    # abstract
    def applyPowerUp(self):
        pass

    def picked_up_by(self, player):
        self.game.dropped_items.remove(self)
        self.player = player
        player.addPowerUp(self)

    def update(self, time_delta):
        self.x += time_delta*(-Speed.MAX_SPEED)
        if self.x < RoadPositions.BEHIND_REAR_HORIZON:
            self.game.dropped_items.remove(self)

    def draw(self):
        glPushMatrix()
        glTranslate(self.y, 0, self.x)
        PowerUps.CRATE.draw()
        glPopMatrix()


class Call911(PowerUp):
    def __init__(self, game, player=None):
        super(Call911, self).__init__(game, player)
        self.icon = PowerUps.CALL_911

    def applyPowerUp(self):
        self.game.generate_emergency_vehicle(self.player.vertical_position)


class Hydraulics(PowerUp):
    def __init__(self, game, player=None):
        super(Hydraulics, self).__init__(game, player)
        self.icon = PowerUps.HYDRAULICS

    def applyPowerUp(self):
        self.player.hydraulics = True


class Shield(PowerUp):
    def __init__(self, game, player=None):
        super(Shield, self).__init__(game, player)
        self.icon = PowerUps.SHIELD

    def applyPowerUp(self):
        self.player.shield = True


class Shrink(PowerUp):
    def __init__(self, game, player=None):
        super(Shrink, self).__init__(game, player)
        self.icon = PowerUps.SHRINK

    def applyPowerUp(self):
        self.player.shrunk = True
        self.player.height /= 2
        self.player.height_offset /= 2
        self.player.radius /= 2


class Phaser(PowerUp):
    def __init__(self, game, player=None):
        super(Phaser, self).__init__(game, player)
        self.icon = PowerUps.PHASER

    def applyPowerUp(self):
        self.player.fire_phaser = True
