import random

import ParticleManager
from constants import Speed


class PointsEmitter(ParticleManager.ParticleEmitter):
    def __init__(self, x, y, speed_x, speed_y, size=100, shape=ParticleManager.Particles.POINTS, rate=0.1, num_of_particles=3):
        super(PointsEmitter, self).__init__(x, y, speed_x, speed_y, size, shape, num_of_particles, 0.1)

    def set_particles(self):
        for particle in self.particles:
            particle.set_properties(self.x, self.y, 700, 0, self.speed_x + random.randrange(-5, 5) * Speed.ONE_KMH, self.speed_y + random.randrange(-5, 5) * Speed.ONE_KMH, self.size, self.shape, True)


class Minus10Points(PointsEmitter):
    def __init__(self, x, y, speed_x, speed_y, size=100, shape=ParticleManager.Particles.POINTS, num_of_particles=6):
        super(Minus10Points, self).__init__(x, y, speed_x, speed_y, size, shape, 0.01, num_of_particles)

    def set_particles(self):
        for particle in self.particles:
            particle.set_properties(self.x, self.y, 1200, 0, self.speed_x + random.randrange(-5, 5) * Speed.ONE_KMH, self.speed_y + random.randrange(-5, 5) * Speed.ONE_KMH, self.size, self.shape, True)


class Plus100Points(PointsEmitter):
    def __init__(self, x, speed):
        super(Plus100Points, self).__init__(x, 130, speed, 0.1, 200, ParticleManager.Particles.PLUS_100_POINTS, 1, 1)


class Minus100Points(PointsEmitter):
    def __init__(self, x, speed):
        super(Minus100Points, self).__init__(x, 130, speed,  0.1, 400, ParticleManager.Particles.MINUS_100_POINTS, 1, 1)
