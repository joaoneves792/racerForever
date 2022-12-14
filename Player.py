from OpenGLContext import GL
import ParticleManager
from Car import Car
from singletons import HUD, Speed, RoadPositions, PowerUps
from PointsEmitter import Plus100Points, Minus100Points
from utils import car_circle_collision
from ms3d import MATRIX, LIGHTS
from threading import Lock


class Player(Car):
    def __init__(self, model, z, x, speed, player_id):
        super(Player, self).__init__(model, z, x, speed)
        self.player_id = player_id
        self.input_lock = Lock()
        self.draw_rotation = False
        self.apply_throttle = 0
        self.apply_brakes = 0
        self.apply_left = 0
        self.apply_right = 0
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
            ParticleManager.add_new_emitter(Minus100Points(HUD.POINTS100_X[self.player_id], HUD.POINTS100_SPEED_DIRECTION[self.player_id] * Speed.PLAYER_SPEED - 10 * Speed.ONE_KMH))
        self.score += 0.01 * time_delta
        old_score_hundreds = self.score_hundreds
        self.score_hundreds = int(self.score / 100)
        for i in range(self.score_hundreds-old_score_hundreds):
            ParticleManager.add_new_emitter(Plus100Points(HUD.POINTS100_X[self.player_id], HUD.POINTS100_SPEED_DIRECTION[self.player_id] * Speed.PLAYER_SPEED - 10 * Speed.ONE_KMH))

        # Adjust postition to user input
        with self.input_lock:
            # Reset the speeds
            self.lateral_speed = 0
            Speed.PLAYER_SPEED = Speed.BASE_PLAYER_SPEED

            # Turn left
            if not self.shrunk:
                self.lateral_speed += Speed.PLAYER_LATERAL_SPEED*self.apply_left
            else:
                self.lateral_speed += Speed.PLAYER_LATERAL_SPEED_SHRUNK*self.apply_left

            # Turn right
            if not self.shrunk:
                self.lateral_speed -= Speed.PLAYER_LATERAL_SPEED*self.apply_right
            else:
                self.lateral_speed -= Speed.PLAYER_LATERAL_SPEED_SHRUNK*self.apply_right

            # Throttle
            Speed.PLAYER_SPEED += Speed.PLAYER_ACCELERATE_SPEED*self.apply_throttle
            if self.apply_throttle > 0.05:
                self.throttling = True
            else:
                self.throttling = False

            # Brakes
            Speed.PLAYER_SPEED -= Speed.PLAYER_BRAKE_SPEED*self.apply_brakes
            if self.apply_brakes > 0.05:
                self.braking = True
            else:
                self.braking = False

        if self.speed < Speed.PLAYER_SPEED and not self.braking:
            if self.throttling:
                speed_increase = Speed.ONE_KMH * time_delta
                self.speed = (self.speed + speed_increase) if (self.speed + speed_increase) < (
                    Speed.PLAYER_SPEED + Speed.PLAYER_ACCELERATE_SPEED) else Speed.PLAYER_ACCELERATE_SPEED
            else:
                speed_increase = Speed.ONE_KMH * 0.03 * time_delta
                self.speed = (self.speed + speed_increase) if (self.speed + speed_increase) < Speed.PLAYER_SPEED else Speed.PLAYER_SPEED

        horizontal_position_delta = time_delta*(self.speed - Speed.PLAYER_SPEED)
        vertical_position_delta = time_delta*self.lateral_speed

        # Corrections so as to not get stuck!
        for car in self.crashed_into:
            impact_vector = []
            if car_circle_collision(self, car, impact_vector, horizontal_position_delta, vertical_position_delta):
                if impact_vector[2] > 0:
                    horizontal_position_delta -= (impact_vector[0]*impact_vector[2])
                    car.horizontal_position += impact_vector[0]*impact_vector[2]
                    car.vertical_position += impact_vector[1]*impact_vector[2]

        # self.horizontal_position += horizontal_position_delta
        self.vertical_position += vertical_position_delta

        if self.horizontal_position > RoadPositions.FORWARD_LIMIT:
            self.horizontal_position = RoadPositions.FORWARD_LIMIT
        if self.horizontal_position < RoadPositions.REAR_LIMIT:
            self.horizontal_position = RoadPositions.REAR_LIMIT
        if self.vertical_position > RoadPositions.UPPER_LIMIT-self.height_offset:
            self.vertical_position = RoadPositions.UPPER_LIMIT - self.height_offset
        if self.vertical_position < RoadPositions.LOWER_LIMIT+self.height_offset:
            self.vertical_position = RoadPositions.LOWER_LIMIT + self.height_offset

        GL.Lights.setPosition(LIGHTS.LIGHT_9, self.vertical_position, 15, self.horizontal_position + 50)

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
        self.update_camera()

    def update_camera(self):
        # Update the camera
        GL.GLM.selectMatrix(MATRIX.VIEW)
        GL.GLM.loadIdentity()
        GL.GLM.translate(0, 0, -150)
        GL.GLM.rotate(180, 0, 1, 0)
        GL.GLM.rotate(-self.camera_y_rot, 1, 0, 0)
        GL.GLM.rotate(self.camera_x_rot, 0, 1, 0)
        GL.GLM.translate(-self.vertical_position, -30, -self.horizontal_position)
        GL.GLM.selectMatrix(MATRIX.MODEL)

    def draw_car(self):

        GL.GLM.pushMatrix()
        if self.fire_phaser:
            GL.Lights.disableLighting()
            GL.GLM.pushMatrix()
            GL.GLM.translate(-12.5, 5, 2500)
            GL.GLM.rotate(-90, 1, 0, 0)
            PowerUps.PHASER_RECTANGLE.changeMaterialTransparency("1", 1-self.phaser_alpha)
            PowerUps.PHASER_RECTANGLE.drawGL3()
            GL.GLM.popMatrix()
            GL.Lights.enableLighting()
        if self.hydraulics:
            GL.GLM.pushMatrix()
            GL.GLM.translate(0, 10, 0)
        if self.shrunk:
            GL.GLM.pushMatrix()
            GL.GLM.scale(0.5, 1, 1)
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

    def draw_shadow_pass(self):
        GL.GLM.pushMatrix()
        GL.GLM.translate(self.vertical_position, 0, self.horizontal_position)
        self.vehicle.model.drawGL3()
        GL.GLM.popMatrix()

    def update_mouse(self, movement, ratio):
        self.camera_x_rot += ratio*movement[0]
        self.camera_y_rot += ratio*movement[1]
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
