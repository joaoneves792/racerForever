import math

from OpenGL.GL import *
import ms3d
from OpenGLContext import GL
from constants import RoadPositions, Speed


class Road:
    def __init__(self, z=0):
        self.road = ms3d.ms3d("./Road/road6.ms3d")
        self.road.prepare(GL.Shader)
        self.road_lod = ms3d.ms3d("./Road/road_lod.ms3d")
        self.road_lod.prepare(GL.Shader)
        self.sky = ms3d.ms3d("./Road/sky.ms3d")
        self.sky.prepare(GL.Shader)
        self.length = 600  # calculated by measuring it in milkshape (see comment at beginning of file!)
        self.num_of_tiles = 24  # Needs to be a pair number!!
        self.maximum_rear_pos = ((-(self.num_of_tiles//2))-1)*self.length
        self.maximum_front_pos = ((self.num_of_tiles//2)-1)*self.length
        self.tile_delta = 0
        self.z = []
        self.num_of_lights = 4
        self.tiles_to_lights_ratio = self.num_of_tiles//self.num_of_lights
        self.lights_offset = self.length/2
        self.lights_cutoff = 70
        for i in range(-self.num_of_tiles//2, self.num_of_tiles//2):
            self.z.append(z+i*self.length)
        self.lights = False
        self.sun = True
        self.switch_lights_off = False
        self.switch_lights_on = False
        self.sunrise = False
        self.sunset = False
        self.time = 30000
        # self.time = 43000
        self.sun_angle = math.pi/2

        self.setup_lights()

    def setup_lights(self):
        self.lamp_ambient = (0.5, 0.5, 0.2, 0.5)
        self.lamp_diffuse = (1, 1, 0.799, 0.5)
        self.lamp_specular = (0.1, 0.1, 0.1, 0.1)
        lamp_direction = (0, -1, 0)

        #glEnable(GL_LIGHTING)

        #glLightModelfv(GL_LIGHT_MODEL_COLOR_CONTROL, GL_SINGLE_COLOR)

        #for light in range(GL_LIGHT1, GL_LIGHT4+1):
        #    glLightfv(light, GL_AMBIENT, self.lamp_ambient)
        #    glLightfv(light, GL_DIFFUSE, self.lamp_diffuse)
        #    glLightfv(light, GL_SPECULAR, self.lamp_specular)
        #    glLightfv(light, GL_SPOT_CUTOFF, self.lights_cutoff)
        #    glLightfv(light, GL_SPOT_DIRECTION, lamp_direction)

        #glLightfv(GL_LIGHT0, GL_POSITION, (0, 200, 0, 1))

        #glLightfv(GL_LIGHT6, GL_AMBIENT, (1, 1, 1, 1))
        #glLightfv(GL_LIGHT6, GL_DIFFUSE, self.lamp_diffuse)
        #glLightfv(GL_LIGHT6, GL_SPECULAR, self.lamp_specular)
        #glLightfv(GL_LIGHT6, GL_SPOT_CUTOFF, 17)
        #glLightfv(GL_LIGHT6, GL_SPOT_DIRECTION, (0, -0.27, 1))

        #glEnable(GL_LIGHT0)

    def draw(self):

        if self.sunrise:
            # glEnable(GL_LIGHT0)
            self.sunrise = False
            self.sun = True

        if self.sunset:
            # glDisable(GL_LIGHT0)
            self.sunset = False
            self.sun = False

        if self.switch_lights_on:
            # glEnable(GL_LIGHT1)
            #glEnable(GL_LIGHT2)
            #glEnable(GL_LIGHT3)
            #glEnable(GL_LIGHT4)
            #glEnable(GL_LIGHT6)
            self.switch_lights_on = False
            self.lights = True

        if self.switch_lights_off:
            #glDisable(GL_LIGHT1)
            #glDisable(GL_LIGHT2)
            #glDisable(GL_LIGHT3)
            #glDisable(GL_LIGHT4)
            #glDisable(GL_LIGHT6)
            self.switch_lights_off = False
            self.lights = False

        intensity = 2*math.sin(self.sun_angle)
        if self.lights:
            if 42500 < self.time < 55000:
                compensate_sun = 1-intensity
                ambient = (compensate_sun if compensate_sun > self.lamp_ambient[0] else self.lamp_ambient[0],
                           compensate_sun if compensate_sun > self.lamp_ambient[1] else self.lamp_ambient[1],
                           compensate_sun if compensate_sun > self.lamp_ambient[2] else self.lamp_ambient[2])
            #    for light in range(GL_LIGHT1, GL_LIGHT4+1):
            #        glLightfv(light, GL_AMBIENT, ambient)

            half = self.num_of_tiles//2
            delta = self.tile_delta
            nlights = self.num_of_lights
            for light in range(GL_LIGHT1, GL_LIGHT4+1):
                l = (light - GL_LIGHT1)

                # Magic...
                tile_index = (l+half+((delta//nlights)+(1 if l < (delta % nlights) else 0))*nlights) % self.num_of_tiles

            #    glLightfv(light, GL_POSITION, (RoadPositions.LEFT_LANE, 100, self.z[tile_index] + self.lights_offset, 1))

        if self.sun:
            sin = math.sin(self.sun_angle)
            color = (8*sin, 4*sin, 2*sin, intensity)
            #glLightfv(GL_LIGHT0, GL_AMBIENT, (intensity, intensity, intensity, intensity))
            #glLightfv(GL_LIGHT0, GL_DIFFUSE, color)
            #glLightfv(GL_LIGHT0, GL_SPECULAR, color)
            #glLightfv(GL_LIGHT0, GL_POSITION, (0, 100*self.sun_height, self.length*self.sun_pos, 1))

        for z in self.z:
            GL.GLM.pushMatrix()
            GL.GLM.translate(0, 0, z)
            if abs(z) > (self.num_of_lights*self.length):
                self.road_lod.drawGL3()
            else:
                self.road.drawGL3()
            GL.GLM.popMatrix()

        # glPushMatrix()
        # glScalef(10, 10, 10)
        self.sky.drawGL3()
        # glPopMatrix()

    def advance(self, time_delta):
        for i in range(self.num_of_tiles):
            if self.z[i] <= self.maximum_rear_pos:
                self.z[i] = self.maximum_front_pos - (self.maximum_rear_pos-self.z[i])  # Dont forget the correction factor because of big time_deltas
                self.tile_delta = (self.tile_delta + 1) % self.num_of_tiles
            self.z[i] -= time_delta * Speed.MAX_SPEED

        if self.lights:
            time_delta *= 2
        else:
            time_delta /= 4

        self.time += time_delta

        if self.sun_angle >= 2*math.pi:
            self.sun_angle = 0
        self.sun_angle += 0.000104719*time_delta

        self.sun_height = math.sin(self.sun_angle)
        self.sun_pos = math.cos(self.sun_angle)

        if self.time >= 60000:
            self.time = 0

        if not self.sun:
            if 15000 < self.time < 55000 and self.sun_angle >= 0:
                self.sunrise = True
        else:
            if self.time > 55000 and self.sun_angle >= math.pi:
                self.sunset = True

        if not self.lights:
            if self.time > 42500 and self.time:
                self.switch_lights_on = True
        else:
            if 20000 < self.time < 42500:
                self.switch_lights_off = True
