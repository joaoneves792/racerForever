import math

from ms3d import ms3d, LIGHTS
from OpenGLContext import GL
from singletons import RoadPositions, Speed, LightPositions


class Road:
    def __init__(self, z=0):
        self.road = ms3d("./Road/road7.ms3d")
        self.road.prepare(GL.Shader)
        self.road_night = ms3d("./Road/road7_night.ms3d")
        self.road_night.prepare(GL.Shader)
        self.road_lod = ms3d("./Road/road_lod.ms3d")
        self.road_lod.prepare(GL.Shader)
        self.road_shadows = ms3d("./Road/road_shadows.ms3d")
        self.road_shadows.prepare(GL.Shader)
        self.sky = ms3d("./Road/sky.ms3d")
        self.sky.prepare(GL.Shader)
        self.skyRotation = 0
        self.length = 600  # calculated by measuring it in milkshape (see comment at beginning of file!)
        self.num_of_tiles = 32  # Needs to be a pair number!!
        self.maximum_rear_pos = ((-(self.num_of_tiles//2))-1)*self.length
        self.maximum_front_pos = ((self.num_of_tiles//2)-1)*self.length
        self.tile_delta = 0
        self.z = []
        self.num_of_lights = 8
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
        # self.sun_angle = math.radians(61)
        # self.sun_angle = 3*math.pi/4
        self.sun_angle = math.pi/2

        self.setup_lights()

    def setup_lights(self):

        for light in range(LIGHTS.LIGHT_1, LIGHTS.LIGHT_1+self.num_of_lights):
            GL.Lights.setColor(light, 255, 255, 204, 90)
            GL.Lights.setCone(light, 0, -1, 0, self.lights_cutoff)

        GL.Lights.setColor(LIGHTS.LIGHT_9, 255, 255, 204, 300)
        GL.Lights.setCone(LIGHTS.LIGHT_9, 0, -0.1, 1, 17)

        GL.Lights.setPosition(LIGHTS.LIGHT_0, RoadPositions.MIDDLE_LANE, 1500, 0)
        GL.Lights.setColor(LIGHTS.LIGHT_0, 255, 255, 204, -50)
        GL.Lights.setCone(LIGHTS.LIGHT_0, 0, -1, 0, -180)

        GL.Lights.enable(LIGHTS.LIGHT_0)

    def draw(self):

        if self.sunrise:
            GL.Lights.enable(LIGHTS.LIGHT_0)
            self.sunrise = False
            self.sun = True

        if self.sunset:
            GL.Lights.disable(LIGHTS.LIGHT_0)
            self.sunset = False
            self.sun = False

        if self.switch_lights_on:
            for light in range(LIGHTS.LIGHT_1, LIGHTS.LIGHT_1+self.num_of_lights):
                GL.Lights.enable(light)
            GL.Lights.enable(LIGHTS.LIGHT_9)
            self.switch_lights_on = False
            self.lights = True
            LightPositions.LAMPS = True

        if self.switch_lights_off:
            for light in range(LIGHTS.LIGHT_1, LIGHTS.LIGHT_1+self.num_of_lights):
                GL.Lights.disable(light)
            GL.Lights.disable(LIGHTS.LIGHT_9)
            self.switch_lights_off = False
            self.lights = False
            LightPositions.LAMPS = False

        intensity = 0
        if self.lights:
            half = self.num_of_tiles//2
            delta = self.tile_delta
            nlights = self.num_of_lights
            for light in range(LIGHTS.LIGHT_1, LIGHTS.LIGHT_1+self.num_of_lights):
                l = (light - 1)

                # Magic...
                tile_index = (l+half+((delta//nlights)+(1 if l < (delta % nlights) else 0))*nlights) % self.num_of_tiles
                GL.Lights.setPosition(light, LightPositions.LAMP_X, LightPositions.LAMP_Y, self.z[tile_index]+self.lights_offset)

        if self.sun:
            sin = math.sin(self.sun_angle)
            color = (min(6*sin*255, 255), min(2*sin*255, 255), min(1*sin*255, 255), intensity)
            GL.Lights.setColor(LIGHTS.LIGHT_0, color[0], color[1], color[2], -0.005)
            LightPositions.SUN_Y = 100*self.sun_height
            LightPositions.SUN_Z = self.length*self.sun_pos
            GL.Lights.setPosition(LIGHTS.LIGHT_0, LightPositions.SUN_X, LightPositions.SUN_Y, LightPositions.SUN_Z)

        for z in self.z:
            GL.GLM.pushMatrix()
            GL.GLM.translate(0, 0, z)
            if abs(z) > (self.num_of_lights*2*self.length):
                self.road_lod.drawGL3()
            else:
                if self.lights:
                    self.road_night.drawGL3()
                else:
                    self.road.drawGL3()
            GL.GLM.popMatrix()

        GL.GLM.pushMatrix()
        GL.GLM.scale(12, 12, 12)
        GL.GLM.rotate(self.skyRotation, 0, 1, 0)
        self.sky.drawGL3()
        GL.GLM.popMatrix()

    def draw_shadow_pass(self):
        for z in self.z:
            GL.GLM.pushMatrix()
            GL.GLM.translate(0, 0, z)
            self.road_shadows.drawGL3()
            GL.GLM.popMatrix()

    def advance(self, time_delta):
        for i in range(self.num_of_tiles):
            if self.z[i] <= self.maximum_rear_pos:
                self.z[i] = self.maximum_front_pos - (self.maximum_rear_pos-self.z[i])  # Dont forget the correction factor because of big time_deltas
                self.tile_delta = (self.tile_delta + 1) % self.num_of_tiles
            self.z[i] -= time_delta * Speed.PLAYER_SPEED

        self.skyRotation += 0.0005*time_delta
        if self.skyRotation >= 360:
            self.skyRotation = 0

        if self.lights:
            time_delta *= 2
        else:
            time_delta /= 4

        if self.sun_angle >= 2*math.pi:
            self.sun_angle = 0
        self.sun_angle += 0.000104719*time_delta

        self.sun_height = math.sin(self.sun_angle)
        self.sun_pos = math.cos(self.sun_angle)

        if self.lights and (math.radians(90) >= self.sun_angle >= math.radians(60)):
            self.switch_lights_off = True

        if not self.lights and self.sun_angle >= math.radians(140):
            self.switch_lights_on = True

        if self.sun and self.sun_angle >= math.radians(180+10):
                self.sunset = True

        if not self.sun and (math.radians(90) >= self.sun_angle >= math.radians(-10)):
                self.sunrise = True
