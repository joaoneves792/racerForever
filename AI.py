import math
import random

from OpenGLContext import GL
from Car import Car
from singletons import RoadPositions, Sounds, Speed, SkidMarks
from utils import car_circle_collision


class AI(Car):  # AI - Non Player Vehicle
    def __init__(self, model, x, speed):
        super(AI, self).__init__(model, RoadPositions.BEYOND_HORIZON, x, speed)
        self.angular_speed = 0
        # self.rotating = False
        # self.rotation_side = True #True = Left False=Right
        self.original_lane = self.vertical_position
        self.switching_to_left_lane = False
        self.switching_to_right_lane = False
        self.crashed = False
        self.rotation_lateral_speed_increase = 0
        self.capsized = False
        self.capsized_angle = 0

    def check_overtake_need(self, cars):
        if self.skidding or (self.switching_to_left_lane or self.switching_to_right_lane):
            return
        for car in cars:
            if car == self:
                continue
            if (car.ahead(self) and car.slower(self)) or (self.horizontal_position > RoadPositions.COLLISION_HORIZON and car_circle_collision(self, car)):
                if not self.change_lane(cars):
                    self.match_speed_of(car)

    def change_lane(self, cars):
        self.original_lane = self.vertical_position
        if self.vertical_position == RoadPositions.LEFT_LANE and self.is_lane_free(cars, RoadPositions.MIDDLE_LANE):
            self.switching_to_right_lane = True
        elif self.vertical_position == RoadPositions.RIGHT_LANE and self.is_lane_free(cars, RoadPositions.MIDDLE_LANE):
            self.switching_to_left_lane = True
        elif self.vertical_position == RoadPositions.MIDDLE_LANE:
            if random.randrange(2) == 0 and self.is_lane_free(cars, RoadPositions.LEFT_LANE):
                self.switching_to_left_lane = True
            elif self.is_lane_free(cars, RoadPositions.RIGHT_LANE):
                self.switching_to_right_lane = True
        if not (self.switching_to_left_lane or self.switching_to_right_lane):
            return False
        return True

    def is_lane_free(self, cars, lane):
        box_x = self.horizontal_position
        box_y = lane
        box_w = self.width_offset + 100  # give it some clearance
        box_h = self.height_offset
        for car in cars:
            if car == self:
                continue
            if self.check_collision_box(box_x, box_y, box_w, box_h, car):
                return False
        return True

    def swerve(self):
        self.change_lane([])  # passing an empty list of other cars: doesnt check if lanes are free

    def match_speed_of(self, other_car):
        if self.speed < 0:  # ignore if we are an ambulance
            return
        if other_car.speed > 0:
            if (other_car.horizontal_position - self.horizontal_position) < self.width+50:
                Sounds.HORN.stop()
                Sounds.HORN.play()
                self.speed = other_car.speed
        else:
            self.speed = 0
            Sounds.BRAKE.stop()
            Sounds.BRAKE.play()
            self.skidding = True
            self.skid_marks_x = self.horizontal_position - 50

    def apply_collision_forces(self, other_speed, other_lateral_speed, impact_vector):
        self.speed += (other_speed - self.speed)
        self.lateral_speed += (other_lateral_speed - self.lateral_speed)
        if impact_vector[1] > 0:
            self.angular_speed += 0.6 * Speed.ONE_DEGREE_MIL * (impact_vector[1] / (self.vehicle.radius * 2))
        else:
            self.angular_speed -= 0.6 * Speed.ONE_DEGREE_MIL * (impact_vector[1] / (self.vehicle.radius * 2))
        self.skidding = True
        # self.crashed = True

    def draw_car(self):
        GL.GLM.pushMatrix()
        if self.capsized:
            GL.GLM.translate(0, 20 * abs(math.sin(0.5 * self.capsized_angle * Speed.DEGREES_TO_RADIANS)), 0)
            GL.GLM.rotate(self.capsized_angle, 1, 0, 0)
        GL.GLM.rotate(self.rotation, 0, 1, 0)
        if abs(self.horizontal_position) > RoadPositions.LOD_DISTANCE:
            self.vehicle.lod.drawGL3()
        else:
            self.vehicle.model.drawGL3()
        self.draw_wheels()
        GL.GLM.popMatrix()

    def update_car(self, time_delta):
        player_speed = Speed.PLAYER_SPEED

        if self.crashed:
            self.speed = self.speed - (0.05 * Speed.ONE_KMH * time_delta) if self.speed > 0 else 0
            lateral_speed_delta = (0.02 * Speed.ONE_KMH * time_delta)
            if self.lateral_speed > 0:
                self.lateral_speed = self.lateral_speed - lateral_speed_delta if self.lateral_speed - lateral_speed_delta > 0 else 0
            else:
                self.lateral_speed = self.lateral_speed + lateral_speed_delta if self.lateral_speed + lateral_speed_delta < 0 else 0

            angular_speed_delta = (0.003 * Speed.ONE_DEGREE_MIL * time_delta)
            if self.angular_speed > 0:
                self.angular_speed = self.angular_speed - angular_speed_delta if self.angular_speed - angular_speed_delta > 0 else 0
            else:
                self.angular_speed = self.angular_speed + angular_speed_delta if self.angular_speed + angular_speed_delta < 0 else 0

            if self.angular_speed > 0.5 * Speed.ONE_DEGREE_MIL:
                self.angular_speed = 0.5 * Speed.ONE_DEGREE_MIL
            elif self.angular_speed < -0.5 * Speed.ONE_DEGREE_MIL:
                self.angular_speed = -0.5 * Speed.ONE_DEGREE_MIL

            if (self.rotation >= 90 or self.rotation <= -90) and self.speed >= Speed.NORMAL_SPEED*3/4 and not self.capsized:
                self.capsized = True
                Sounds.ROLLOVER.play()

            if self.capsized:
                self.angular_speed = 0
                self.speed = self.speed - (0.1 * Speed.ONE_KMH * time_delta) if self.speed - (0.1 * Speed.ONE_KMH * time_delta) > 0 else 0
                if self.rotation < 0 and self.speed > 0:
                    self.capsized_angle -= 0.8 * Speed.ONE_DEGREE_MIL * time_delta
                elif self.rotation > 0 and self.speed > 0:
                    self.capsized_angle += 0.8 * Speed.ONE_DEGREE_MIL * time_delta

                if self.speed == 0:
                    if 45 > self.capsized_angle % 360 > -45:
                        self.capsized_angle = 0
                    elif self.capsized_angle % 360 < 125 and self.capsized_angle > 0:
                        self.capsized_angle = 90
                    elif self.capsized_angle % 360 > -125 and self.capsized_angle < 0:
                        self.capsized_angle = -90
                    else:
                        self.capsized_angle = 180

        if self.speed > 0:
            self.rotation += time_delta*self.angular_speed

        lateral_speed = Speed.PLAYER_LATERAL_SPEED  # *(float(self.speed)/float(Speed.MAX_SPEED))
        if self.switching_to_left_lane:
            if self.original_lane == RoadPositions.RIGHT_LANE:
                if self.vertical_position >= RoadPositions.MIDDLE_LANE:
                    self.switching_to_left_lane = False
                    self.vertical_position = RoadPositions.MIDDLE_LANE
                else:
                    self.lateral_speed = lateral_speed
            else:
                if self.vertical_position >= RoadPositions.LEFT_LANE:
                    self.switching_to_left_lane = False
                    self.vertical_position = RoadPositions.LEFT_LANE
                else:
                    self.lateral_speed = lateral_speed
        elif self.switching_to_right_lane:
            if self.original_lane == RoadPositions.LEFT_LANE:
                if self.vertical_position <= RoadPositions.MIDDLE_LANE:
                    self.switching_to_right_lane = False
                    self.vertical_position = RoadPositions.MIDDLE_LANE
                else:
                    self.lateral_speed = -lateral_speed
            else:
                if self.vertical_position <= RoadPositions.RIGHT_LANE:
                    self.switching_to_right_lane = False
                    self.vertical_position = RoadPositions.RIGHT_LANE
                else:
                    self.lateral_speed = -lateral_speed
        elif not self.crashed:
            self.lateral_speed = 0

        # if self.crashed:
        #    rotation_lateral_speed_increase_delta = math.sin(self.rotation)*0.01*Speed.ONE_KMH*time_delta
        #
        #    if self.rotation > 0 and self.lateral_speed - (self.rotation_lateral_speed_increase + rotation_lateral_speed_increase_delta) > -1*Speed.ONE_KMH:
        #        self.rotation_lateral_speed_increase += rotation_lateral_speed_increase_delta
        #        self.lateral_speed -= self.rotation_lateral_speed_increase
        #    if self.rotation < 0 and self.lateral_speed + self.rotation_lateral_speed_increase + rotation_lateral_speed_increase_delta < 1*Speed.ONE_KMH:
        #        self.rotation_lateral_speed_increase += rotation_lateral_speed_increase_delta
        #        self.lateral_speed += self.rotation_lateral_speed_increase

        horizontal_position_delta = time_delta*(self.speed-player_speed)
        vertical_position_delta = time_delta*self.lateral_speed

        # Corrections so as to not get stuck!
        for car in self.crashed_into:
            impact_vector = []
            if car_circle_collision(self, car, impact_vector, horizontal_position_delta, vertical_position_delta):
                if impact_vector[2] > 0:
                    horizontal_position_delta -= (impact_vector[0]*impact_vector[2])
                    vertical_position_delta -= (impact_vector[1]*impact_vector[2])
                    car.horizontal_position += impact_vector[0]*impact_vector[2]
                    car.vertical_position += impact_vector[1]*impact_vector[2]

        self.vertical_position += vertical_position_delta
        self.horizontal_position += horizontal_position_delta

        if self.vertical_position > RoadPositions.UPPER_LIMIT:
            self.vertical_position = RoadPositions.UPPER_LIMIT
        if self.vertical_position < RoadPositions.LOWER_LIMIT:
            self.vertical_position = RoadPositions.LOWER_LIMIT

        if self.skidding:
            if self.skid_mark is None and self.lateral_speed > 0:
                self.skid_mark = SkidMarks.SKID_LEFT
            elif self.skid_mark is None and self.lateral_speed < 0:
                self.skid_mark = SkidMarks.SKID_RIGHT
            elif self.skid_mark is None and self.lateral_speed == 0:
                self.skid_mark = SkidMarks.SKID_STRAIGHT
            if self.skid_marks_y == 0:
                self.skid_marks_y = self.vertical_position
            if self.skid_marks_x == 0:
                self.skid_marks_x = self.horizontal_position
            else:
                self.skid_marks_x -= time_delta * Speed.PLAYER_SPEED
