import random

from AI import AI
from singletons import RoadPositions
from PowerUps import Call911, Hydraulics, Shield, Shrink, Phaser


class Truck(AI):
    def __init__(self, model, y, speed, game):
            super(Truck, self).__init__(model, y, speed)
            self.game = game
            self.looted = False

    def update(self, time_delta):
        if self.horizontal_position < RoadPositions.FORWARD_LIMIT and random.randrange(1000) == 1:
            self.dropPowerUp()
        if self.crashed and not self.looted:
            self.dropPowerUp()
            self.dropPowerUp()
            self.looted = True
        super(Truck, self).update(time_delta)

    def dropPowerUp(self):
        rand = random.randrange(5)
        if rand == 0:
            Call911(self.game).drop(self.horizontal_position, self.vertical_position)
        elif rand == 1:
            Hydraulics(self.game).drop(self.horizontal_position, self.vertical_position)
        elif rand == 2:
            Shrink(self.game).drop(self.horizontal_position, self.vertical_position)
        elif rand == 3:
            Phaser(self.game).drop(self.horizontal_position, self.vertical_position)
        else:
            Shield(self.game).drop(self.horizontal_position, self.vertical_position)
