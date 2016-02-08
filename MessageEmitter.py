import ParticleManager
from singletons import Window


class MessageEmitter(ParticleManager.ParticleEmitter):
    def __init__(self, x, y, shape):
        super(MessageEmitter, self).__init__(x, y, 0, 0, 100, shape, 1, 1)

    def set_particles(self):
        for particle in self.particles:
            particle.set_properties(self.x, self.y, 0, 2000, 0, self.speed_x, self.speed_y,  self.size, self.shape, True)


class HolyShit(MessageEmitter):
    def __init__(self, shape):
        super(HolyShit, self).__init__(Window.WIDTH/2, Window.HEIGHT/2, shape)


class Mayhem(MessageEmitter):
    def __init__(self, shape):
        super(Mayhem, self).__init__(Window.WIDTH/2, Window.HEIGHT/2-50, shape)


class Annihilation(MessageEmitter):
    def __init__(self, shape):
        super(Annihilation, self).__init__(Window.WIDTH/2, Window.HEIGHT/2-100, shape)
