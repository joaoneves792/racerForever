import random

import ParticleManager
from singletons import Speed


class SmokeEmitter(ParticleManager.ParticleEmitter3D):
    def __init__(self, x, y, z, speed_z):
        super(SmokeEmitter, self).__init__(x, 0, z, 0.01, 0.15, speed_z-Speed.PLAYER_SPEED, 0, 0, 0, 25, ParticleManager.Particles.SMOKE, 20, 0.01)

    def set_particles(self):
        for particle in self.particles:
            particle.set_properties(self.x, self.y, self.z, 2500, 0, self.speed_x + random.randrange(-5, 5) * Speed.ONE_KMH, self.speed_y + random.randrange(-5, 5) * Speed.ONE_KMH, self.speed_z, self.accel_x, self.accel_y, self.accel_z, ParticleManager.Particles.SMOKE, False)