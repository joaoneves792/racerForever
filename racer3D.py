#import pygame2
#pygame_sdl2.import_as_pygame()
import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

import ms3d

import random
import math

#1 MS3D Unit = 1 meter = 20 OpenGL units

class Window:
    #WIDTH = 1920
    #HEIGHT = 1080
    #FULLSCREEN = True
    WIDTH = 1024
    HEIGHT = 512
    FULLSCREEN = False

    VERSION = "v0.1"

class KeyboardKeys:
    KEY_ESC = pygame.K_ESCAPE
    KEY_LEFT  = (pygame.K_LEFT, pygame.K_a)
    KEY_RIGHT = (pygame.K_RIGHT, pygame.K_d)
    KEY_UP = (pygame.K_UP, pygame.K_w)
    KEY_DOWN = (pygame.K_DOWN, pygame.K_s)

    #TODO
    KEY_ONE = (49, 65457)
    KEY_FIVE = (54, 65461)
    KEY_TO_NUM = (KEY_ONE[0] - 1, KEY_ONE[1] - 1)

class RoadPositions:
    WIDTH = 400
    LEFT_LANE = 280 
    MIDDLE_LANE = 200
    RIGHT_LANE = 120 
    UPPER_LIMIT = 320
    LOWER_LIMIT = 80
   
    FORWARD_LIMIT = 200
    REAR_LIMIT = -200
    COLLISION_HORIZON = 300
    BEYOND_HORIZON = 500 
    BEHIND_REAR_HORIZON = -400

class Speed:
    ONE_METER = 20
    KMH_TO_MS = 0.2777
    MS_TO_GLMIL = 0.02
    KMH_TO_GLMIL = KMH_TO_MS*MS_TO_GLMIL
    ONE_KMH = KMH_TO_GLMIL
    MAX_KMH = 120
    MAX_SPEED = MAX_KMH*ONE_KMH
    BASE_CRASH_SPEED_DECREASE = (10*ONE_KMH) 
    RAD_TO_DEGREE = 57.2958
    MAX_WOBBLE_ROTATION = 0.52359*RAD_TO_DEGREE
    ONE_RADMIL = 0.001*RAD_TO_DEGREE
    ONE_DEGREE_MIL = 1
    DEGREES_TO_RADIANS = 0.017453
    PLAYER_ACCELERATE_SPEED = 30*ONE_KMH
    PLAYER_BRAKE_SPEED = 30*ONE_KMH
    PLAYER_LATERAL_SPEED = 30*ONE_KMH
    PLAYER_LATERAL_SPEED_SHRUNK = 15*ONE_KMH

class Steering:
    CENTERED = 0
    TURN_LEFT = -1
    TURN_RIGHT = 1
   

class SkidMarks:
    SKID_LEFT = None
    SKID_RIGHT = None

def box_collision(box1_x, box1_y, box1_w, box1_h, box2_x, box2_y, box2_w, box2_h):
    box1_x = box1_x - box1_w
    box1_y = box1_y + box1_h
    box1_w = box1_w*2
    box1_h = box1_h*2
    box2_x = box2_x - box2_w
    box2_y = box2_y + box2_h
    box2_w = box2_w*2
    box2_h = box2_h*2
    return ((box1_x < box2_x + box2_w)
            and (box1_x + box1_w > box2_x)
            and (box1_y < box2_y + box2_h)
            and (box1_y + box1_h > box2_y))

def circle_collision(circle1_pos, circle1_radius, circle2_pos, circle2_radius, impact_vector):
    dx = circle2_pos[0] - circle1_pos[0]
    dy = circle2_pos[1] - circle1_pos[1]
    radius = circle1_radius + circle2_radius
    pyth = ((dx*dx) + (dy*dy))
    collision = (pyth < (radius*radius))
    #WARNING: Dont Try to improve this code without reading the comments in car_circle_collision and understanding the consequences!!!
    if collision:
        impact_vector.append(dx)
        impact_vector.append(dy)
        impact_vector.append((radius - math.sqrt(pyth))/radius)
    return collision

#angle is in degrees
def rotate_2d_vector(vector, angle):
    cs = math.cos(math.pi*angle/180)
    sn = math.sin(math.pi*angle/180)
    x = vector[0]
    y = vector[1]
    return [x*cs-y*sn, x*sn+y*cs]

def car_circle_collision(car1, car2, impact_vector=[], car1_x_offset=0, car1_y_offset=0):
    car1_rear_circle = ( car1.rear_circle[0]+car1.horizontal_position+car1_x_offset, car1.rear_circle[1] + car1.vertical_position+car1_y_offset)
    car1_front_circle = ( car1.front_circle[0]+car1.horizontal_position+car1_x_offset, car1.front_circle[1] + car1.vertical_position+car1_y_offset)
    car2_rear_circle = ( car2.rear_circle[0]+car2.horizontal_position, car2.rear_circle[1] + car2.vertical_position)
    car2_front_circle =  ( car2.front_circle[0]+car2.horizontal_position, car2.vehicle.front_circle[1] + car2.vertical_position)
    #Apparently the "or" goes on even if one of the operands is already known to be True! That messes up the impact vector
    #WARNING: Dont Try to improve this code without reading the previous line and understanding the consequences!!!
    if circle_collision(car1_rear_circle, car1.vehicle.radius, car2_rear_circle, car2.vehicle.radius, impact_vector):
        return True
    if circle_collision(car1_rear_circle, car1.vehicle.radius, car2_front_circle, car2.vehicle.radius, impact_vector):
        return True
    if circle_collision(car1_front_circle, car1.vehicle.radius, car2_rear_circle, car2.vehicle.radius, impact_vector):
        return True
    if circle_collision(car1_front_circle, car1.vehicle.radius, car2_front_circle, car2.vehicle.radius, impact_vector):
        return True
    return False
            
class VehicleModel:
    def __init__(self, model, wheel, wheel_count):
        self.model = model
        self.wheel = wheel
        self.wheel_positions = []
        self.wheel_count = wheel_count
        self.height = 0
        self.height_offset = 0
        self.width = 0
        self.calculate_dimensions()
        self.rear_circle = []
        self.front_circle = []
        self.radius = self.height_offset+5
        self.calculate_collision_circles()

    def calculate_dimensions(self):
        rear_right = self.model.getJointPosition("col0")
        front_left = self.model.getJointPosition("col1")
        self.height = abs(rear_right[0])+abs(front_left[0])
        self.width = abs(rear_right[2])+abs(front_left[2])
        self.height_offset = self.height/2
        self.width_offset = self.width/2

    def calculate_collision_circles(self):
        self.rear_circle.append(-self.width_offset+self.radius) 
        self.rear_circle.append(0)
        self.front_circle.append(+self.width_offset - self.radius)
        self.front_circle.append(0)


class Car:
    class Wheel:
        FRONT_RIGHT = 0
        FRONT_LEFT  = 1
        REAR_LEFT   = 2
        REAR_RIGHT  = 3
        def __init__(self, wheel_id, model, position):
            self.wheel_id = wheel_id
            self.model = model
            self.position = position
            self.steering = Steering.CENTERED
            self.rotateAngle = 0

        def update(self):
            #Not realistic at all but who cares!!
            if self.rotateAngle >= 360:
                self.rotateAngle = 0;
            self.rotateAngle += 15


        def draw(self):
            glPushMatrix()
            glTranslatef(self.position[0], self.position[1], self.position[2])
            if self.wheel_id == self.FRONT_LEFT or self.wheel_id == self.REAR_LEFT:
                glRotatef(180, 0, 1, 0)
            if self.wheel_id == self.FRONT_LEFT or self.wheel_id == self.FRONT_RIGHT:
                if self.steering == Steering.TURN_LEFT:
                    glRotatef(25, 0, 1, 0)
                elif self.steering == Steering.TURN_RIGHT:
                    glRotatef(-25, 0, 1, 0)
            glRotatef(self.rotateAngle, 1, 0, 0)
            self.model.draw()
            glPopMatrix()

    def __init__(self, vehicle, z, x, speed):
        self.vehicle = vehicle
        self.vertical_position = x
        self.horizontal_position = z
        self.height =  self.vehicle.height #TODO #cairo.ImageSurface.get_height(model)
        self.width = self.vehicle.width #TODO cairo.ImageSurface.get_width(model)
        self.height_offset = self.vehicle.height_offset
        self.width_offset = self.vehicle.width_offset
        self.speed = speed
        self.lateral_speed = 0
        self.rear_circle = self.vehicle.rear_circle[:]
        self.front_circle = self.vehicle.front_circle[:]
        self.rotation = 0
        self.wheels = []
        self.crashed_into = []
        self.skiding = False
        self.skid_marks_x = 0
        self.skid_marks_y = 0
        self.skid_mark = None

        for i in range(vehicle.wheel_count):
            self.wheels.append(self.Wheel(i, vehicle.wheel, vehicle.wheel_positions[i]))


    def update(self,time_delta):
        self.front_circle = rotate_2d_vector(self.front_circle, self.rotation)
        self.rear_circle = rotate_2d_vector(self.rear_circle, self.rotation)
        self.update_car(time_delta) 
        for wheel in self.wheels:
            wheel.update()

    def draw(self):
        if self.skid_mark != None:
            glPushMatrix()
            glDisable(GL_LIGHTING)
            glTranslatef(self.skid_marks_y, 0, self.skid_marks_x)
            self.skid_mark.draw()
            glEnable(GL_LIGHTING)
            glPopMatrix()
        glPushMatrix()
        glTranslatef(self.vertical_position, 0, self.horizontal_position)
        self.draw_car()
        glPopMatrix()

    def draw_wheels(self):
        for wheel in self.wheels:
            wheel.draw()


    def check_collision_box(self, box_x, box_y, box_w, box_h, car):
        box2_x = car.horizontal_position
        box2_y = car.vertical_position
        box2_w = car.width_offset
        box2_h = car.height_offset
        return box_collision(box_x, box_y, box_w, box_h, box2_x, box2_y, box2_w, box2_h)
        
    def ahead(self, other):
        box_x = other.horizontal_position + 5*Speed.ONE_METER
        box_y = other.vertical_position
        box_h = other.height_offset
        box_w = other.width_offset + 5*Speed.ONE_METER #Distance to check for vehicles ahead
        return self.check_collision_box(box_x, box_y, box_w, box_h, self)

    def slower(self, other):
        return (self.speed < other.speed)

    def steer(self, side):
        self.wheels[self.Wheel.FRONT_LEFT].steering = side;
        self.wheels[self.Wheel.FRONT_RIGHT].steering = side;

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

        self.inventory = []
        self.powerUpTimeOut = 0
        self.hydraulics = False
        self.shield = False
        self.shrunk = False
        self.fire_phaser = False
        self.phaser_alpha = 0
        self.phaser_gaining_intensity = True


    def applyCollisionForces(self, other, other_speed, other_lateral_speed, impact_vector):
        self.speed += (other_speed - self.speed)
        self.lateral_speed += (other_lateral_speed - self.lateral_speed)
        self.skiding = True
    
    def update_car(self, time_delta):
        #for i in range(self.score_hundreds - int(self.score / 100)):
        #    ParticleManager.add_new_emmitter(Minus100Points(HUD.POINTS100_X[self.player_id], HUD.POINTS100_SPEED_DIRECTION[self.player_id]*Speed.MAX_SPEED))
        self.score += 0.01 * time_delta
        old_score_hundreds = self.score_hundreds
        self.score_hundreds = int(self.score / 100)
        #for i in range(self.score_hundreds-old_score_hundreds):
        #    ParticleManager.add_new_emmitter(Plus100Points(HUD.POINTS100_X[self.player_id], HUD.POINTS100_SPEED_DIRECTION[self.player_id]*Speed.MAX_SPEED))
        
        #Adjust postition to user input
        if self.apply_left:
            self.lateral_speed += Speed.PLAYER_LATERAL_SPEED if not self.shrunk else Speed.PLAYER_LATERAL_SPEED_SHRUNK
            self.apply_left = False
            self.left = True
        if self.apply_right:
            self.lateral_speed -= Speed.PLAYER_LATERAL_SPEED if not self.shrunk else Speed.PLAYER_LATERAL_SPEED_SHRUNK
            self.apply_right = False
            self.right = True
        if self.release_left:
            #self.lateral_speed -= Speed.PLAYER_LATERAL_SPEED if not self.shrunk else Speed.PLAYER_LATERAL_SPEED_SHRUNK
            self.lateral_speed = 0
            self.release_left = False
            self.left = False
        if self.release_right:
            #self.lateral_speed += Speed.PLAYER_LATERAL_SPEED if not self.shrunk else Speed.PLAYER_LATERAL_SPEED_SHRUNK
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
                speed_increase = Speed.ONE_KMH*time_delta
                self.speed = (self.speed + speed_increase) if (self.speed + speed_increase) < (Speed.MAX_SPEED+Speed.PLAYER_ACCELERATE_SPEED) else Speed.PLAYER_ACCELERATE_SPEED
            else:
                speed_increase = Speed.ONE_KMH*0.03*time_delta
                self.speed = (self.speed + speed_increase) if (self.speed + speed_increase) < Speed.MAX_SPEED else Speed.MAX_SPEED


        horizontal_position_delta = time_delta*(self.speed-Speed.MAX_SPEED)
        vertical_position_delta = time_delta*(self.lateral_speed)
        
        #Corrections so as to not get stuck!
        for car in self.crashed_into:
            impactvector = []
            if car_circle_collision(self, car, impactvector, horizontal_position_delta, vertical_position_delta):
                if impactvector[2] > 0:
                    horizontal_position_delta -= (impactvector[0]*impactvector[2])
                    car.horizontal_position += impactvector[0]*impactvector[2]
                    car.vertical_position += impactvector[1]*impactvector[2]

        self.horizontal_position += horizontal_position_delta 
        self.vertical_position += vertical_position_delta


        if self.horizontal_position > RoadPositions.FORWARD_LIMIT:
            self.horizontal_position = RoadPositions.FORWARD_LIMIT
        if self.horizontal_position < RoadPositions.REAR_LIMIT:
            self.horizontal_position = RoadPositions.REAR_LIMIT
        if self.vertical_position > RoadPositions.UPPER_LIMIT-self.height_offset:
            self.vertical_position = RoadPositions.UPPER_LIMIT-self.height_offset
        if self.vertical_position < RoadPositions.LOWER_LIMIT+self.height_offset:
            self.vertical_position = RoadPositions.LOWER_LIMIT+self.height_offset

        #if self.fire_phaser:
        #    if self.phaser_gaining_intensity:
        #        self.phaser_alpha += time_delta*0.005
        #        if self.phaser_alpha >= 1:
        #            self.phaser_alpha = 1
        #            self.phaser_gaining_intensity = False
        #    else:
        #        self.phaser_alpha -= time_delta*0.005
        #        if self.phaser_alpha <= 0:
        #            self.phaser_alpha = 0
        #            self.phaser_gaining_intensity = True
        #            self.fire_phaser = False

        #if(self.powerUpTimeOut > 0):
        #    self.powerUpTimeOut -= time_delta
        #if self.powerUpTimeOut <= 0:
        #    self.disablePowerUps()
        #    self.powerUpTimeOut = 0

    def draw_car(self):
        glPushMatrix()
        #if self.fire_phaser:
        #    cr.save()
        #    cr.translate(10, self.height_offset - 8)
        #    cr.set_source_surface(PowerUps.PHASER_FIRE, 0, 0)
        #    cr.paint_with_alpha(self.phaser_alpha)
        #    cr.restore()
        #if self.draw_rotation:
        #    x = self.width/2.0
        #    y = self.height/2.0
        #    cr.translate(x, y)
        #    cr.rotate(self.rotation);
        #    cr.translate(-x,-y) 
        #if self.hydraulics:
        #    cr.scale(1.2, 1.2)
        #if self.shrunk:
        #    cr.scale(1, 0.5)
        self.vehicle.model.draw()
        self.draw_wheels()
        #if self.shield:
        #    cr.save()
        #    cr.translate(self.width/2 - PowerUps.ENERGY_SHIELD_WIDTH/2, self.height_offset - PowerUps.ENERGY_SHIELD_HEIGHT/2)
        #    cr.set_source_surface(PowerUps.ENERGY_SHIELD, 0, 0)
        #    cr.paint()
        #    cr.restore()
        glPopMatrix()

        #if self.crash_handler != None:
        #    self.crash_handler.draw(cr)
       
        #self.draw_score(cr)
        #self.draw_power_up_timer(cr)
        #self.draw_inventory(cr)

class NPV(Car): #NPV - Non Player Vehicle
    def __init__(self, model, x, speed):
        super(NPV, self).__init__(model, RoadPositions.BEYOND_HORIZON, x, speed)
        self.angular_speed = 0
        #self.rotating = False
        #self.rotation_side = True #True = Left False=Right
        self.original_lane = self.vertical_position
        self.switching_to_left_lane = False
        self.switching_to_right_lane = False
        self.crashed = False
        self.rotation_lateral_speed_increase = 0
        self.capsized = False
        self.capsized_angle = 0

    def check_overtake_need(self, cars):
        if self.skiding or (self.switching_to_left_lane or self.switching_to_right_lane):
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
        box_x = self.horizontal_position;
        box_y = lane;  
        box_w = self.width_offset + 100 #give it some clearance
        box_h = self.height_offset
        for car in cars:
            if car == self:
                continue
            if self.check_collision_box(box_x, box_y, box_w, box_h, car):
                return False
        return True

    def swerve(self):
        self.change_lane([]) #passing an empty list of other cars: doesnt check if lanes are free

    def match_speed_of(self, other_car):
        if self.speed < 0: #ignore if we are an ambulance
            return
        if other_car.speed > 0:
            if (other_car.horizontal_position - self.horizontal_position) < self.width+50:
                self.speed = other_car.speed
        else:
            self.speed = 0
            self.skiding = True
            self.skid_marks_x = self.horizontal_position - 50

    def applyCollisionForces(self, other, other_speed, other_lateral_speed, impact_vector):
        self.speed += (other_speed - self.speed)
        self.lateral_speed += (other_lateral_speed - self.lateral_speed)
        if impact_vector[1] > 0:
            self.angular_speed += 0.6*Speed.ONE_DEGREE_MIL*(impact_vector[1]/(self.vehicle.radius*2))
        else:
            self.angular_speed -= 0.6*Speed.ONE_DEGREE_MIL*(impact_vector[1]/(self.vehicle.radius*2))
        self.skiding = True
        self.crashed = True

    def draw_car(self):
        glPushMatrix()
        if self.capsized:
            glTranslate(0, 20*abs(math.sin(0.5*self.capsized_angle*Speed.DEGREES_TO_RADIANS)), 0)
            glRotatef(self.capsized_angle, 1, 0, 0)
        glRotatef(self.rotation, 0, 1, 0)
        self.vehicle.model.draw()
        self.draw_wheels()
        
        glPopMatrix()
        
    def update_car(self, time_delta):
        player_speed = Speed.MAX_SPEED
        
        if self.crashed:
            self.speed = self.speed - (0.05*Speed.ONE_KMH*time_delta) if self.speed > 0 else 0
            lateral_speed_delta = (0.02*Speed.ONE_KMH*time_delta) 
            if self.lateral_speed > 0:
                self.lateral_speed = self.lateral_speed - lateral_speed_delta if self.lateral_speed - lateral_speed_delta > 0 else 0
            else:
                self.lateral_speed = self.lateral_speed + lateral_speed_delta if self.lateral_speed + lateral_speed_delta < 0 else 0

            angular_speed_delta = (0.003*Speed.ONE_DEGREE_MIL*time_delta) 
            if self.angular_speed > 0:
                self.angular_speed = self.angular_speed - angular_speed_delta if self.angular_speed - angular_speed_delta > 0 else 0
            else:
                self.angular_speed = self.angular_speed + angular_speed_delta if self.angular_speed + angular_speed_delta < 0 else 0
        
            if self.angular_speed > 0.5*Speed.ONE_DEGREE_MIL:
                self.angular_speed = 0.5*Speed.ONE_DEGREE_MIL
            elif self.angular_speed < -0.5*Speed.ONE_DEGREE_MIL:
                self.angular_speed = -0.5*Speed.ONE_DEGREE_MIL

            if (self.rotation >= 90 or self.rotation <= -90) and self.speed >= Speed.MAX_SPEED*3/4:
                self.capsized = True

            if self.capsized:
                self.angular_speed = 0
                self.speed = self.speed - (0.1*Speed.ONE_KMH*time_delta) if self.speed - (0.1*Speed.ONE_KMH*time_delta)> 0 else 0
                if self.rotation < 0 and self.speed > 0:
                    self.capsized_angle -= 0.8*Speed.ONE_DEGREE_MIL*time_delta
                elif self.rotation > 0 and self.speed > 0:
                    self.capsized_angle += 0.8*Speed.ONE_DEGREE_MIL*time_delta

                if self.speed == 0:
                    if(self.capsized_angle%360 < 45 and self.capsized_angle%360 > -45):
                        self.capsized_angle =  0
                    elif(self.capsized_angle%360 < 125 and self.capsized_angle > 0):
                        self.capsized_angle = 90
                    elif(self.capsized_angle%360 > -125 and self.capsized_angle < 0):
                        self.capsized_angle = -90
                    else:
                        self.capsized_angle = 180
        
        if(self.speed > 0):
            self.rotation += time_delta*self.angular_speed

        lateral_speed = Speed.PLAYER_LATERAL_SPEED#*(float(self.speed)/float(Speed.MAX_SPEED))
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
        elif (not self.crashed):
            self.lateral_speed = 0


        #if self.crashed:
        #    rotation_lateral_speed_increase_delta = math.sin(self.rotation)*0.01*Speed.ONE_KMH*time_delta
        #
        #    if self.rotation > 0 and self.lateral_speed - (self.rotation_lateral_speed_increase + rotation_lateral_speed_increase_delta) > -1*Speed.ONE_KMH:
        #        self.rotation_lateral_speed_increase += rotation_lateral_speed_increase_delta
        #        self.lateral_speed -= self.rotation_lateral_speed_increase
        #    if self.rotation < 0 and self.lateral_speed + self.rotation_lateral_speed_increase + rotation_lateral_speed_increase_delta < 1*Speed.ONE_KMH:
        #        self.rotation_lateral_speed_increase += rotation_lateral_speed_increase_delta
        #        self.lateral_speed += self.rotation_lateral_speed_increase
       
        horizontal_position_delta = time_delta*(self.speed-player_speed)
        vertical_position_delta = time_delta*(self.lateral_speed)

        #Corrections so as to not get stuck!
        for car in self.crashed_into:
            impactvector = []
            if car_circle_collision(self, car, impactvector, horizontal_position_delta, vertical_position_delta):
                if impactvector[2] > 0:
                    horizontal_position_delta -= (impactvector[0]*impactvector[2])
                    vertical_position_delta -= (impactvector[1]*impactvector[2])
                    car.horizontal_position += impactvector[0]*impactvector[2]
                    car.vertical_position += impactvector[1]*impactvector[2]

        self.vertical_position += vertical_position_delta
        self.horizontal_position += horizontal_position_delta 
        
        if self.vertical_position > RoadPositions.UPPER_LIMIT:
            self.vertical_position = RoadPositions.UPPER_LIMIT
        if self.vertical_position < RoadPositions.LOWER_LIMIT:
            self.vertical_position = RoadPositions.LOWER_LIMIT
        
        if self.skiding:
            if self.skid_mark == None and self.lateral_speed >= 0:
                self.skid_mark = SkidMarks.SKID_LEFT
            elif self.skid_mark == None and self.lateral_speed < 0:
                self.skid_mark = SkidMarks.SKID_RIGHT
            if self.skid_marks_y == 0:
                self.skid_marks_y = self.vertical_position
            if self.skid_marks_x == 0:
                self.skid_marks_x = self.horizontal_position
            else:
                self.skid_marks_x -= time_delta*(Speed.MAX_SPEED) 


class Road():
    def __init__(self, z=0):
        self.road = ms3d.ms3d("./road2.ms3d")
        self.length = 600 #calculated by measuring it in milkshape (see comment at beginning of file!)
        self.num_of_tiles = 6 #Needs to be a pair number!!
        self.maximum_rear_pos = ((-(self.num_of_tiles//2))-1)*self.length
        self.maximum_front_pos = ((self.num_of_tiles//2)-1)*self.length
        self.z = []
        for i in range(-self.num_of_tiles//2, self.num_of_tiles//2):
            self.z.append(z+i*self.length)
        #self.z = [z-3*, z-2*RoadPositions.LENGTH, z-RoadPositions.LENGTH,  z, z+RoadPositions.LENGTH, z+2*RoadPositions.LENGTH];

    def draw(self):
        for z in self.z:
            glPushMatrix()
            glTranslatef(0, 0, z)
            self.road.draw()
            glPopMatrix()

    def advance(self, time_delta):
        for i in range(self.num_of_tiles):
            if self.z[i] <= self.maximum_rear_pos:
                self.z[i] = self.maximum_front_pos - (self.maximum_rear_pos-self.z[i]) #Dont forget the correction factor because of big time_deltas
            self.z[i] -= time_delta*Speed.MAX_SPEED

class Game():

    class CarModels:
        GALLARDO = None
        RS4 = None
        Charger = None
        Murci = None
        M3 = None

    class Wheels:
        GALLARDO = None
        RS4 = None
        Charger = None
        M3 = None

    def __init__(self):
        pygame.init()
        pygame.display.init()
        self.init_display()

        self.available_vehicles = []
        self.available_player_vehicles = []
        self.load_resources()

        self.road = Road()
        self.players = []
        self.last_update_timestamp = -1

        self.previous_crash_count = 0
        self.npvs = []
        self.spawn_delay = 0
        self.droped_items = []
        self.paused = False 
        self.singlePlayer = True

        #self.players.append(Player(self.available_vehicles[0], 0, RoadPositions.MIDDLE_LANE, Speed.MAX_SPEED, 0))
        self.players.append(Player(self.available_player_vehicles[0], 0, RoadPositions.MIDDLE_LANE, Speed.MAX_SPEED, 0))

        while True:
            for event in pygame.event.get():
                self.handle_events(event)
            self.update()
            self.draw()

    def init_display(self):
        display = (Window.WIDTH, Window.HEIGHT)
        #pygame.display.gl_set_attribute(pygame.GL_SWAP_CONTROL, 1)
        #pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 4)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 8)
        if Window.FULLSCREEN:
            pygame.display.set_mode(display, pygame.DOUBLEBUF | pygame.OPENGL | pygame.HWSURFACE | pygame.FULLSCREEN)
        else:
            pygame.display.set_mode(display, pygame.DOUBLEBUF | pygame.OPENGL | pygame.HWSURFACE)# | pygame.FULLSCREEN)

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glDepthMask(GL_TRUE)
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        glEnable(GL_TEXTURE_2D);
        glHint(GL_PERSPECTIVE_CORRECTION_HINT,GL_NICEST);
        #glEnable(GL_MULTISAMPLE)
        glEnable(GL_LIGHTING);
        glEnable(GL_LIGHT0);

        glLightfv(GL_LIGHT0, GL_AMBIENT, (1, 1, 1, 1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))
        glLightfv(GL_LIGHT0, GL_SPECULAR, (0.5, 0.5, 0.5, 0.5))
        glLightfv(GL_LIGHT0, GL_POSITION, (0,0,-1,1))
                                                                    
        glClearDepth(1);
        glClearColor(0, 0, 0, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glEnable(GL_LIGHTING);
        glEnable(GL_LIGHT0);

        glLightfv(GL_LIGHT0, GL_AMBIENT, (1, 1, 1, 1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))
        glLightfv(GL_LIGHT0, GL_SPECULAR, (0.5, 0.5, 0.5, 0.5))
        glLightfv(GL_LIGHT0, GL_POSITION, (RoadPositions.MIDDLE_LANE,100,0,1))
        #glLightfv(GL_LIGHT0, GL_POSITION, (0,10,0,1))

        gluPerspective(25, Window.WIDTH/Window.HEIGHT, 1, 2400)
        #gluPerspective(90, Window.WIDTH/Window.HEIGHT, 1, 2400)
        gluLookAt(-200,450,0, RoadPositions.MIDDLE_LANE,0,0, 0,1,0)
        
        glLightfv(GL_LIGHT0, GL_AMBIENT, (1, 1, 1, 1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))
        glLightfv(GL_LIGHT0, GL_SPECULAR, (0.5, 0.5, 0.5, 0.5))
        #glLightfv(GL_LIGHT0, GL_POSITION, (0,0,-1,0))
        glLightfv(GL_LIGHT0, GL_POSITION, (0,100,0,1))
        glLightfv(GL_LIGHT1, GL_SPOT_CUTOFF, 45)
        glLightfv(GL_LIGHT1, GL_SPOT_DIRECTION, (0,0,-100))

        #self.night()

        
    def night(self):
        glDisable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        glEnable(GL_LIGHT2)
        glEnable(GL_LIGHT3)

        glLightfv(GL_LIGHT1, GL_AMBIENT, (1, 1, 0, 1))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, (1, 1, 0, 1))
        glLightfv(GL_LIGHT1, GL_SPECULAR, (0.5, 0.5, 0.5, 0.5))
        glLightfv(GL_LIGHT1, GL_POSITION, (RoadPositions.LEFT_LANE,50,-100,1))
        glLightfv(GL_LIGHT1, GL_SPOT_CUTOFF, 30)
        glLightfv(GL_LIGHT1, GL_SPOT_DIRECTION, (0,0,-100))

        glLightfv(GL_LIGHT2, GL_AMBIENT, (1, 1, 0, 1))
        glLightfv(GL_LIGHT2, GL_DIFFUSE, (1, 1, 0, 1))
        glLightfv(GL_LIGHT2, GL_SPECULAR, (0.5, 0.5, 0.5, 0.5))
        glLightfv(GL_LIGHT2, GL_POSITION, (RoadPositions.LEFT_LANE,50,0,1))
        glLightfv(GL_LIGHT2, GL_SPOT_CUTOFF, 30)
        glLightfv(GL_LIGHT2, GL_SPOT_DIRECTION, (0,0, 0))
        
        glLightfv(GL_LIGHT3, GL_AMBIENT, (1, 1, 0, 1))
        glLightfv(GL_LIGHT3, GL_DIFFUSE, (1, 1, 0, 1))
        glLightfv(GL_LIGHT3, GL_SPECULAR, (0.5, 0.5, 0.5, 0.5))
        glLightfv(GL_LIGHT3, GL_POSITION, (RoadPositions.LEFT_LANE,50,100,1))
        glLightfv(GL_LIGHT3, GL_SPOT_CUTOFF, 30)
        glLightfv(GL_LIGHT3, GL_SPOT_DIRECTION, (0,0, 100))


    def load_resources(self):
        def fill_wheel_positions(vehicle, model):
            for i in range(vehicle.wheel_count):
                vehicle.wheel_positions.append(model.getJointPosition("hub"+str(i)))

        SkidMarks.SKID_LEFT = ms3d.ms3d("./skid_left.ms3d")
        SkidMarks.SKID_RIGHT = ms3d.ms3d("./skid_right.ms3d")

        self.CarModels.GALLARDO = ms3d.ms3d("./Gallardo/gallardo_play.ms3d")
        self.Wheels.GALLARDO = ms3d.ms3d("./Gallardo/gallardoWheel.ms3d")
        gallardo = VehicleModel(self.CarModels.GALLARDO, self.Wheels.GALLARDO, 4)
        fill_wheel_positions(gallardo, self.CarModels.GALLARDO)
        self.available_player_vehicles.append(gallardo)

        self.CarModels.RS4 = ms3d.ms3d("./RS4/RS4.ms3d")
        self.Wheels.RS4 = ms3d.ms3d("./RS4/RS4Wheel.ms3d")
        rs4 = VehicleModel(self.CarModels.RS4, self.Wheels.RS4, 4)
        fill_wheel_positions(rs4, self.CarModels.RS4)
        self.available_vehicles.append(rs4)
        
        self.CarModels.Charger = ms3d.ms3d("./charger/charger_play.ms3d")
        self.Wheels.Charger = ms3d.ms3d("./charger/ChargerWheel.ms3d")
        charger = VehicleModel(self.CarModels.Charger, self.Wheels.Charger, 4)
        fill_wheel_positions(charger, self.CarModels.Charger)
        self.available_vehicles.append(charger)
        
        self.CarModels.Murci = ms3d.ms3d("./Murci/MurcielagoPlay.ms3d")
        murci = VehicleModel(self.CarModels.Murci, self.Wheels.GALLARDO, 4)
        fill_wheel_positions(murci, self.CarModels.Murci)
        self.available_vehicles.append(murci)
        
        self.CarModels.M3 = ms3d.ms3d("./M3E92/M3play.ms3d")
        self.Wheels.M3 = ms3d.ms3d("./M3E92/M3E92Wheel.ms3d")
        m3 = VehicleModel(self.CarModels.M3, self.Wheels.M3, 4)
        fill_wheel_positions(m3, self.CarModels.M3)
        self.available_vehicles.append(m3)
    
    
    def generateEmergencyVehicle(self, vertical_position):
            pass
            #self.npvs.append(NPV(CarModels.EMERGENCY_CARS[random.randrange(len(CarModels.EMERGENCY_CARS))], vertical_position, -20*Speed.ONE_KMH))

    def generateRandomNPV(self):
        #Select a random lane
        random_num = random.randrange(3)
        if random_num == 0:
            lane = RoadPositions.LEFT_LANE
        elif random_num == 1:
            lane = RoadPositions.MIDDLE_LANE
        else:
            lane = RoadPositions.RIGHT_LANE

        #Select a Speed
        speed = Speed.MAX_SPEED - Speed.ONE_KMH*(random.randrange(20) + 5) # -5 beacause we need the npvs to always be slower than the player

        #Select a car
        random_num = random.randrange(100)
        if random_num < 4:
            self.generateEmergencyVehicle(lane)
        #elif random_num < 10:
        #    self.npvs.append(Truck(CarModels.TRUCKS[random.randrange(len(CarModels.TRUCKS))], lane, speed, self))
        else:
            self.npvs.append(NPV(self.available_vehicles[random.randrange(len(self.available_vehicles))], lane, speed))

    def check_collision_circle(self, car1, car2, impact_vector):
        if(car1.horizontal_position > RoadPositions.COLLISION_HORIZON or car2.horizontal_position > RoadPositions.COLLISION_HORIZON): #If the cars have not yet appeared on screen then give them a chance of sorting it out
            return False
        return car_circle_collision(car1, car2, impact_vector)

    def check_collision_box(self, car1_x, car1_y, car1_w, car1_h, car2_x, car2_y, car2_w, car2_h):
        if(car1_x > RoadPositions.COLLISION_HORIZON or car2_x > RoadPositions.COLLISION_HORIZON): #If the cars have not yet appeared on screen then give them a chance of sorting it out
            return False
        return box_collision(car1_x, car1_y, car1_w, car1_h, car2_x, car2_y, car2_w, car2_h) 

    def update(self):
        current_time = pygame.time.get_ticks()
        if self.last_update_timestamp == -1:
            self.last_update_timestamp = current_time
        time_delta = (current_time - self.last_update_timestamp)

        self.road.advance(time_delta)
        
        #Update NPVs
        if self.spawn_delay > 0:
            self.spawn_delay -= time_delta
        #Delete NPVs that are behind us (not visible anymore)        
        for npv in self.npvs[:]:  #Mind the [:] its there so we iterate on a copy of the list
            if npv.horizontal_position <= RoadPositions.BEHIND_REAR_HORIZON:
                self.npvs.remove(npv)
                for player in self.players:
                    if npv in player.crashed_into:
                        player.crashed_into.remove(npv)
                #Just a reminder this is only feasable because were using really small lists THIS DOES NOT SCALE WELL!!
        #create new NPVs
        if len(self.npvs) < 5:
            if self.spawn_delay <= 0:
                self.generateRandomNPV()
                self.spawn_delay = 1300
        #Recalculate their position
        for npv in self.npvs:
            npv.check_overtake_need(self.npvs)# + self.players)
            npv.update(time_delta)
        
        #Check collisions
        #(between player and non-players)
        for player in self.players:
            if player.hydraulics:
                continue
            for npv in self.npvs[:]:
                if npv.capsized:
                    continue
                #if self.check_collision_box(player.horizontal_position, player.vertical_position, player.width_offset, player.height_offset, npv.horizontal_position, npv.vertical_position, npv.width_offset, npv.height_offset):
                impact_vector = []
                if car_circle_collision(player, npv, impact_vector):    
                    self.applyCollisionForces(player, npv, impact_vector)
                    if not player.shield:
                        if not npv.crashed:
                            #ParticleManager.add_new_emmitter(Minus10Points(player.horizontal_position, player.vertical_position, -player.speed, 0.2))
                            player.score -= 60
                            #if(player.crash_handler == None):
                            #    player.crash_handler = PlayerCrashHandler(player, npv.speed)
                    if not npv.crashed:
                        npv.crashed = True
                        #ParticleManager.add_new_emmitter(SmokeEmitter( npv.horizontal_position, npv.vertical_position-npv.height_offset, -npv.speed, 0))
                #if player.fire_phaser:
                #    if self.check_collision_box(player.horizontal_position, player.vertical_position, RoadPositions.COLLISION_HORIZON/2, player.height_offset, npv.horizontal_position, npv.vertical_position, npv.width_offset, npv.height_offset):
                #        ParticleManager.add_new_emmitter(SmokeEmitter( npv.horizontal_position, npv.vertical_position-npv.height_offset, 0, 0))
                #        self.npvs.remove(npv)
        
        #(between non-players themselves)
        for i in range(len(self.npvs) - 1):
            for j in range(i+1, len(self.npvs)):
                impact_vector = []
                if self.check_collision_circle(self.npvs[i], self.npvs[j], impact_vector):
                    self.applyCollisionForces(self.npvs[i], self.npvs[j], impact_vector)

        for player in self.players:
            player.update(time_delta)

        self.last_update_timestamp = current_time
    
    def applyCollisionForces(self, car1, car2, impact_vector):
        car1_speed = car1.speed
        car1_lateral_speed = car1.lateral_speed
        car2_speed = car2.speed
        car2_lateral_speed = car2.lateral_speed
        
        if not (car2 in car1.crashed_into):
            car1.crashed_into.append(car2)
        car1.applyCollisionForces(car2, car2_speed, car2_lateral_speed, impact_vector)
        car2.applyCollisionForces(car1, car1_speed, car1_lateral_speed, impact_vector)

    def draw(self):
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.road.draw()

        for player in self.players:
            player.draw()

        for npv in self.npvs:
            npv.draw()

        pygame.display.flip()
    
    
    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            self.on_key_press(event.key)
        elif event.type == pygame.KEYUP:
            self.on_key_release(event.key)
        elif event.type == pygame.QUIT:
            pygame.quit()
            quit()

    def on_key_press(self, key):
        for i in range(len(self.players)):
            if key == KeyboardKeys.KEY_LEFT[i]:
                self.players[i].apply_brakes = True
            elif key == KeyboardKeys.KEY_RIGHT[i]:
                self.players[i].apply_throttle = True
            elif key == KeyboardKeys.KEY_UP[i]:
                self.players[i].apply_left = True
                self.players[i].steer(Steering.TURN_LEFT)
            elif key == KeyboardKeys.KEY_DOWN[i]:
                self.players[i].apply_right = True
                self.players[i].steer(Steering.TURN_RIGHT)
    
    def on_key_release(self, key):
        for i in range(len(self.players)):
            if key == KeyboardKeys.KEY_LEFT[i]:
                self.players[i].release_brakes = True
            elif key == KeyboardKeys.KEY_RIGHT[i]:
                self.players[i].release_throttle = True 
            elif key == KeyboardKeys.KEY_UP[i]:
                self.players[i].release_left = True
                self.players[i].steer(Steering.CENTERED)
            elif key == KeyboardKeys.KEY_DOWN[i]:
                self.players[i].release_right = True
                self.players[i].steer(Steering.CENTERED)

game = Game()
