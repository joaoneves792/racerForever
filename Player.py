from OpenGL.GL import glTranslate, glRotate
from OpenGL.raw.GL.VERSION.GL_1_0 import glLightfv, glMatrixMode, glLoadIdentity, glRotatef, glPushMatrix, glTranslatef, \
    glPopMatrix, glScalef
from OpenGL.raw.GL.VERSION.GL_1_1 import GL_LIGHT6, GL_POSITION, GL_PROJECTION, GL_MODELVIEW

from OpenGLContext import GL
import ParticleManager
from Car import Car
from constants import HUD, Speed, RoadPositions, PowerUps, Window
from PointsEmitter import Plus100Points, Minus100Points
from utils import car_circle_collision, draw_3d_rectangle


class Player(Car):
    def __init__(self, model, z, x, speed, player_id):
        super(Player, self).__init__(model, z, x, speed)
        self.player_id = player_id
        self.draw_rotation = False
        self.left = False
        self.right = False
        self.apply_throttle = False
        self.apply_brakes = False
        self.apply_left = False
        self.apply_right = False
        self.release_throttle = False
        self.release_brakes = False
        self.release_left = False
        self.release_right = False
        self.braking = False
        self.throttling = False
        self.crash_handler = None
        self.score = 0
        self.score_hundreds = 0

        self.camera_x_rot = 0
        self.camera_y_rot = 0

        self.inventory = []
        self.powerUpTimeOut = 0
        self.hydraulics = False
        self.shield = False
        self.shrunk = False
        self.fire_phaser = False
        self.phaser_alpha = 0
        self.phaser_gaining_intensity = True

    def apply_collision_forces(self, other_speed, other_lateral_speed, impact_vector):
        self.speed += (other_speed - self.speed)
        self.lateral_speed += (other_lateral_speed - self.lateral_speed)
        self.skidding = True

    def update_car(self, time_delta):
        for i in range(self.score_hundreds - int(self.score / 100)):
            ParticleManager.add_new_emitter(Minus100Points(HUD.POINTS100_X[self.player_id], HUD.POINTS100_SPEED_DIRECTION[self.player_id] * Speed.MAX_SPEED - 10 * Speed.ONE_KMH))
        self.score += 0.01 * time_delta
        old_score_hundreds = self.score_hundreds
        self.score_hundreds = int(self.score / 100)
        for i in range(self.score_hundreds-old_score_hundreds):
            ParticleManager.add_new_emitter(Plus100Points(HUD.POINTS100_X[self.player_id], HUD.POINTS100_SPEED_DIRECTION[self.player_id] * Speed.MAX_SPEED - 10 * Speed.ONE_KMH))

        # Adjust postition to user input
        if self.apply_left:
            self.lateral_speed += Speed.PLAYER_LATERAL_SPEED if not self.shrunk else Speed.PLAYER_LATERAL_SPEED_SHRUNK
            self.apply_left = False
            self.left = True
        if self.apply_right:
            self.lateral_speed -= Speed.PLAYER_LATERAL_SPEED if not self.shrunk else Speed.PLAYER_LATERAL_SPEED_SHRUNK
            self.apply_right = False
            self.right = True
        if self.release_left:
            # self.lateral_speed -= Speed.PLAYER_LATERAL_SPEED if not self.shrunk else Speed.PLAYER_LATERAL_SPEED_SHRUNK
            self.lateral_speed = 0
            self.release_left = False
            self.left = False
        if self.release_right:
            # self.lateral_speed += Speed.PLAYER_LATERAL_SPEED if not self.shrunk else Speed.PLAYER_LATERAL_SPEED_SHRUNK
            self.lateral_speed = 0
            self.release_right = False
            self.right = False

        if self.apply_throttle:
            self.speed += Speed.PLAYER_ACCELERATE_SPEED
            self.apply_throttle = False
            self.throttling = True

        if self.apply_brakes:
            self.speed -= Speed.PLAYER_BRAKE_SPEED
            self.apply_brakes = False
            self.braking = True

        if self.release_throttle:
            self.speed -= Speed.PLAYER_ACCELERATE_SPEED
            self.release_throttle = False
            self.throttling = False

        if self.release_brakes:
            self.speed += Speed.PLAYER_BRAKE_SPEED
            self.release_brakes = False
            self.braking = False

        if self.speed < Speed.MAX_SPEED and not self.braking:
            if self.throttling:
                speed_increase = Speed.ONE_KMH * time_delta
                self.speed = (self.speed + speed_increase) if (self.speed + speed_increase) < (
                    Speed.MAX_SPEED + Speed.PLAYER_ACCELERATE_SPEED) else Speed.PLAYER_ACCELERATE_SPEED
            else:
                speed_increase = Speed.ONE_KMH * 0.03 * time_delta
                self.speed = (self.speed + speed_increase) if (self.speed + speed_increase) < Speed.MAX_SPEED else Speed.MAX_SPEED

        horizontal_position_delta = time_delta*(self.speed - Speed.MAX_SPEED)
        vertical_position_delta = time_delta*self.lateral_speed

        # Corrections so as to not get stuck!
        for car in self.crashed_into:
            impact_vector = []
            if car_circle_collision(self, car, impact_vector, horizontal_position_delta, vertical_position_delta):
                if impact_vector[2] > 0:
                    horizontal_position_delta -= (impact_vector[0]*impact_vector[2])
                    car.horizontal_position += impact_vector[0]*impact_vector[2]
                    car.vertical_position += impact_vector[1]*impact_vector[2]

        self.horizontal_position += horizontal_position_delta
        self.vertical_position += vertical_position_delta

        if self.horizontal_position > RoadPositions.FORWARD_LIMIT:
            self.horizontal_position = RoadPositions.FORWARD_LIMIT
        if self.horizontal_position < RoadPositions.REAR_LIMIT:
            self.horizontal_position = RoadPositions.REAR_LIMIT
        if self.vertical_position > RoadPositions.UPPER_LIMIT-self.height_offset:
            self.vertical_position = RoadPositions.UPPER_LIMIT - self.height_offset
        if self.vertical_position < RoadPositions.LOWER_LIMIT+self.height_offset:
            self.vertical_position = RoadPositions.LOWER_LIMIT + self.height_offset

        glLightfv(GL_LIGHT6, GL_POSITION, (self.vertical_position, 15, self.horizontal_position+100, 1))

        if self.fire_phaser:
            if self.phaser_gaining_intensity:
                self.phaser_alpha += time_delta*0.005
                if self.phaser_alpha >= 1:
                    self.phaser_alpha = 1
                    self.phaser_gaining_intensity = False
            else:
                self.phaser_alpha -= time_delta*0.005
                if self.phaser_alpha <= 0:
                    self.phaser_alpha = 0
                    self.phaser_gaining_intensity = True
                    self.fire_phaser = False

        if self.powerUpTimeOut > 0:
            self.powerUpTimeOut -= time_delta
        if self.powerUpTimeOut <= 0:
            self.disablePowerUps()
            self.powerUpTimeOut = 0

    def draw_car(self):

        #glMatrixMode(GL_PROJECTION)
        #glLoadIdentity()
        #gluPerspective(25, Window.WIDTH/Window.HEIGHT, 1, 20400)
        # giuLookAt(self.vertical_position, 30, self.horizontal_position-150, RoadPositions.MIDDLE_LANE,30,RoadPositions.BEYOND_HORIZON, 0,1,0)
        #glTranslate(0, 0, -150)
        #glRotate(180, 0, 1, 0)
        #glRotatef(-self.camera_y_rot, 1, 0, 0)
        #glRotatef(self.camera_x_rot, 0, 1, 0)
        #glTranslate(-self.vertical_position, -30, -self.horizontal_position)
        #glMatrixMode(GL_MODELVIEW)

        GL.GLM.pushMatrix()
        if self.fire_phaser:
            w = (RoadPositions.COLLISION_HORIZON + abs(RoadPositions.REAR_LIMIT))
            GL.GLM.pushMatrix()
            GL.GLM.translate(0, 1, w/2)
            draw_3d_rectangle(w, self.height, PowerUps.PHASER_FIRE, self.phaser_alpha)
            GL.GLM.popMatrix()
        if self.hydraulics:
            GL.GLM.pushMatrix()
            GL.GLM.translate(0, 10, 0)
        if self.shrunk:
            GL.GLM.pushMatrix()
            # glScalef(0.5, 1, 1)
        self.vehicle.model.drawGL3()
        if self.hydraulics:
            GL.GLM.popMatrix()
        self.draw_wheels()
        if self.shrunk:
            GL.GLM.popMatrix()
        if self.shield:
            PowerUps.ENERGY_SHIELD.drawGL3()
        GL.GLM.popMatrix()
        # self.draw_power_up_timer(cr)

    def update_mouse(self, movement):
        self.camera_x_rot += 0.3*movement[0]
        self.camera_y_rot += 0.3*movement[1]
        if self.camera_y_rot < 0:
            self.camera_y_rot = 0
        if self.camera_y_rot > 180:
            self.camera_y_rot = 180

    def addPowerUp(self, powerup):
        if len(self.inventory) < PowerUps.INVENTORY_SIZE:
            self.inventory.append(powerup)

    def usePowerUp(self, num):
        if(num <= len(self.inventory) and self.powerUpTimeOut == 0):
            self.inventory.pop(num-1).execute()

    def disablePowerUps(self):
        self.hydraulics = False
        self.shield = False
        self.shrunk = False
        self.height = self.vehicle.height
        self.height_offset = self.height/2
        self.radius = self.vehicle.radius
