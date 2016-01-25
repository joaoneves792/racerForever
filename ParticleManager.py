from OpenGL.GL import *


class Particles:

    POINTS = None
    PLUS_100_POINTS = None
    MINUS_100_POINTS = None
    HOLY_SHIT = None 
    MAYHEM = None
    ANNIHILATION = None
    SMOKE = 0
    MAX_EMMITTERS = 20 
    POOLED_PARTICLES = 120
    MAX_EMMITTERS3D = 6
    POOLED_PARTICLES3D = 120
    WIDTH = 64
    HEIGHT = 64


class Particle:
    def __init__(self, x=0, y=0, life=0, angle=0, speed_x=0, speed_y=0, size=0, shape=None, deflate=True, w=Particles.WIDTH, h=Particles.HEIGHT):
        self.set_properties(x, y, life, angle, speed_x, speed_y, size, shape, deflate)
        self.w = w
        self.h = h

    def set_properties(self, x, y, life, angle, speed_x, speed_y, size, shape, deflate):
        self.x = x
        self.y = y
        self.life = life
        self.original_life = life
        self.angle = angle
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.size = size
        self.original_size = size
        self.shape = shape
        self.alpha = 1
        self.deflate = deflate

    def update(self, time_delta):
        self.life -= time_delta
        if self.life > 0:
            age_ratio = float(self.life) / float(self.original_life)
            if self.deflate:
                self.size = self.original_size * age_ratio if age_ratio > 0.5 else self.size
            else:
                self.size = self.original_size / age_ratio if age_ratio > 0.5 else self.size
            self.alpha = age_ratio

            self.x += self.speed_x * time_delta
            self.y += self.speed_y * time_delta

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glScalef(self.size/self.w, self.size/self.h, 1)
        self.shape.draw()
        glPopMatrix()
       

class Particle3D:
    def __init__(self):
        self.z = 0
        self.speed_z = 0
        self.accel_x = 0
        self.accel_y = 0
        self.accel_z = 0
        self.texture = 0
        self.set_properties(0,0,0, 0, 0, 0, 0,0,0,0,0,0, 0, False)

    def set_properties(self, x, y, z, life, angle, speed_x, speed_y, speed_z, accel_x, accel_y, accel_z, size, texture, deflate):
        self.z = z
        self.speed_z = speed_z
        self.accel_x = accel_x
        self.accel_y = accel_y
        self.accel_z = accel_z
        self.texture = texture
        self.x = x
        self.y = y
        self.life = life
        self.original_life = life
        self.angle = angle
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.size = size
        self.original_size = size
        self.alpha = 1
        self.deflate = deflate

    def update(self, time_delta):
        if self.z <= 0:
            self.life = 0
            return
        self.life -= time_delta
        if self.life < 0:
            return
        age_ratio = float(self.life) / float(self.original_life)
        if self.deflate:
            self.size = self.original_size * age_ratio if age_ratio > 0.5 else self.size
        else:
            self.size = self.original_size / age_ratio if age_ratio > 0.5 else self.size
        self.alpha = age_ratio

        self.speed_x += self.accel_x*time_delta
        self.speed_y += self.accel_y*time_delta
        self.speed_z += self.accel_z*time_delta
        self.x += self.speed_x*time_delta
        self.y += self.speed_y*time_delta
        self.z += self.speed_z*time_delta

    def draw(self):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glMaterialfv(GL_FRONT, GL_AMBIENT, (1, 1, 1, self.alpha))
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (1, 1, 1, self.alpha))
        glMaterialfv(GL_FRONT, GL_SPECULAR, (1, 1, 1, self.alpha))
        glMaterialfv(GL_FRONT, GL_EMISSION, (0.5, 0.5, 0.5, self.alpha))
        glMaterialfv(GL_FRONT, GL_SHININESS, 0.0)

        glPushMatrix()
        glTranslatef(self.y, self.z, self.x)

        glBegin(GL_TRIANGLES)
        glNormal3f(0,1, 0)
        glTexCoord2f(0, 0)
        glVertex3f(0, 0, 0)
        glNormal3f(0, 1, 0)
        glTexCoord2f(1, 0)
        glVertex3f(self.size, 0, 0) 
        glNormal3f(0, 1, 0)
        glTexCoord2f(0, 1)
        glVertex3f(0, 0, self.size)

        glNormal3f(0, 1, 0)
        glTexCoord2f(1, 0)
        glVertex3f(self.size, 0, 0)    
        glNormal3f(0, 1, 0)
        glTexCoord2f(0, 1)
        glVertex3f(0, 0, self.size)    
        glNormal3f(0, 1, 0)
        glTexCoord2f(1, 1)
        glVertex3f(self.size, 0, self.size)    
        glEnd()
        
        glPopMatrix()
        glDisable(GL_TEXTURE_2D)


class ParticlePool:
    def __init__(self, pool_size):
        self.pool_size = pool_size
        self.pool = [Particle() for i in range(pool_size)]
        self.ready_particle_count = pool_size

    def request_particle(self):
        if self.ready_particle_count == 0:
            print("Available particles limit EXCEEDED!!!")
            return None
        particle = self.pool[self.ready_particle_count-1]
        self.ready_particle_count -= 1
        return particle

    def return_particle(self, returning_particle):
        moved_particle = self.pool[self.ready_particle_count]
        position_to_move_into = self.pool.index(returning_particle)
        self.pool[self.ready_particle_count] = returning_particle
        self.pool[position_to_move_into] = moved_particle
        self.ready_particle_count += 1


class ParticlePool3D(ParticlePool):
    def __init__(self, pool_size):
        self.pool_size = pool_size
        self.pool = [ Particle3D() for i in range(pool_size) ]
        self.ready_particle_count = pool_size


class ParticleEmitter:
    def __init__(self, x, y, speed_x, speed_y, size, shape, num_of_particles, rate):
        global __particlePool__
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.size = size
        self.shape = shape
        self.pool = __particlePool__
        self.particles = []
        self.particle_count = num_of_particles
        self.rate = rate
        self.done = False

    # Must be outside of constructor so that particles are only reserved after emitter is aproved
    def init_particles(self):
        self.particles = [self.pool.request_particle() for i in range(self.particle_count)]
        self.set_particles()

    # abstract
    def set_particles(self):
        pass

    def update(self, time_delta):
        live_particles_count = 0
        new_emissions = self.rate*time_delta
        newly_emitted = 0
        for particle in self.particles:
            if 0 < particle.life < particle.original_life:
                live_particles_count += 1
                particle.update(time_delta)
            elif particle.life > 0 and newly_emitted < new_emissions:
                live_particles_count += 1
                particle.update(time_delta)
                newly_emitted += 1

        if live_particles_count == 0:
            for particle in self.particles:
                self.pool.return_particle(particle)
            self.done = True

    def is_done(self):
        return self.done

    def draw(self):
        if self.done:
            return
        for particle in self.particles:
            if particle.life > 0:
                particle.draw()


class ParticleEmitter3D():
    def __init__(self, x, y, z, speed_x, speed_y, speed_z, accel_x, accel_y, accel_z, size, texture, num_of_particles, rate):
        global __particlePool3D__
        self.x = x
        self.y = y
        self.z = z
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.speed_z = speed_z
        self.accel_x = accel_x
        self.accel_y = accel_y
        self.accel_z = accel_z
        self.size = size
        self.texture = texture
        self.pool = __particlePool3D__
        self.particles = []
        self.particle_count = num_of_particles
        self.rate = rate
        self.done = False
    # Must be outside of constructor so that particles are only reserved after emitter is aproved

    def init_particles(self):
        self.particles = [self.pool.request_particle() for i in range(self.particle_count)]
        self.set_particles()

    # abstract
    def set_particles(self):
        pass

    def update(self, time_delta):
        live_particles_count = 0
        new_emissions = self.rate*time_delta
        newly_emitted = 0
        for particle in self.particles:
            if 0 < particle.life < particle.original_life:
                live_particles_count += 1
                particle.update(time_delta)
            elif particle.life > 0 and newly_emitted < new_emissions:
                live_particles_count += 1
                particle.update(time_delta)
                newly_emitted += 1

        if live_particles_count == 0:
            for particle in self.particles:
                self.pool.return_particle(particle)
            self.done = True

    def is_done(self):
        return self.done

    def draw(self):
        if self.done:
            return
        self.particles.sort(key=(lambda p: p.z)) 
        for particle in self.particles:
            if particle.life > 0:
                particle.draw()


__particlePool__ = ParticlePool(Particles.POOLED_PARTICLES)
__particlePool3D__ = ParticlePool3D(Particles.POOLED_PARTICLES3D)
__particleEmitters__ = []
__particleEmitters3D__ = []


def add_new_emitter(new_emitter):
    global __particleEmitters__
    if len(__particleEmitters__) < Particles.MAX_EMMITTERS:
        __particleEmitters__.append(new_emitter)
        new_emitter.init_particles()
    else:
        print("Too many emitters!!")


def add_new_3d_emitter(new_emitter):
    global __particleEmitters3D__
    if len(__particleEmitters3D__) < Particles.MAX_EMMITTERS3D:
        __particleEmitters3D__.append(new_emitter)
        new_emitter.init_particles()
    else:
        print("Too many 3D emitters!!!")


def update(time_delta):
    global __particleEmitters__
    global __particleEmitters3D__
    for pe in __particleEmitters__[:]:
        pe.update(time_delta)
        if pe.is_done():
            __particleEmitters__.remove(pe)
    for pe3d in __particleEmitters3D__[:]:
        pe3d.update(time_delta)
        if pe3d.is_done():
            __particleEmitters3D__.remove(pe3d)


def draw():
    global __particleEmitters__
    for pe in __particleEmitters__:
        pe.draw()


def draw_3d():
    global __particleEmitters3D__
    for pe in __particleEmitters3D__:
        pe.draw()
