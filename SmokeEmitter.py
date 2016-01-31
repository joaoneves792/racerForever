import random

import ParticleManager
from singletons import Speed


class SmokeEmitter(ParticleManager.ParticleEmitter3D):
    def __init__(self, x, y, z, speed_z):
        super(SmokeEmitter, self).__init__(x, y, z, 0.01, 0.3, speed_z, 0, 0, 0.0005, 25, ParticleManager.Particles.SMOKE, 20, 0.1)

    def set_particles(self):
        for particle in self.particles:
            particle.set_properties(self.x, self.y, self.z, 1000, 0, self.speed_x + random.randrange(-5, 5) * Speed.ONE_KMH, self.speed_y + random.randrange(-5, 5) * Speed.ONE_KMH, self.speed_z, self.accel_x, self.accel_y, self.accel_z, ParticleManager.Particles.SMOKE, True)