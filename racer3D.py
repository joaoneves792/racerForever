import pygame_sdl2
pygame_sdl2.import_as_pygame()
import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

import ms3d

import random

#1 MS3D Unit = 1 meter = 20 OpenGL units

class Window:
    WIDTH = 1920
    HEIGHT = 1080
    FULLSCREEN = True

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
    
    BEYOND_HORIZON = 400 
    BEHIND_REAR_HORIZON = -800
    COLLISION_HORIZON = Window.WIDTH + 100

class Speed_old:
    ONE_METER = 36
    KMH_TO_MS = 0.2777
    MS_TO_PMIL =  0.036 #m/s tp pixels per milisecond
    KMH_TO_PMIL = KMH_TO_MS*MS_TO_PMIL
    SIXTY_KMH = 60*KMH_TO_PMIL
    ONE_KMH = KMH_TO_PMIL
    ONE_RADMIL = 0.001 
    MAX_KMH = 80
    MAX_WOBBLE_ROTATION = 0.52359
    MAX_SPEED = MAX_KMH*ONE_KMH
    BASE_CRASH_SPEED_DECREASE = (10*ONE_KMH) 

class Speed:
    ONE_METER = 20
    KMH_TO_MS = 0.2777
    MS_TO_GLMIL = 0.02
    KMH_TO_GLMIL = KMH_TO_MS*MS_TO_GLMIL
    ONE_KMH = KMH_TO_GLMIL
    MAX_KMH = 80
    MAX_SPEED = MAX_KMH*ONE_KMH
    BASE_CRASH_SPEED_DECREASE = (10*ONE_KMH) 
    RAD_TO_DEGREE = 57.2958
    MAX_WOBBLE_ROTATION = 0.52359*RAD_TO_DEGREE
    ONE_RADMIL = 0.001*RAD_TO_DEGREE
    
class Steering:
    CENTERED = 0
    TURN_LEFT = -1
    TURN_RIGHT = 1
    
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
        self.radius = self.height_offset
        self.calculate_collision_circles()

    def calculate_dimensions(self):
        rear_right = self.model.getJointPosition("col0")
        front_left = self.model.getJointPosition("col1")
        self.height = abs(rear_right[0])+abs(front_left[0])
        self.width = abs(rear_right[2])+abs(front_left[2])
        self.height_offset = self.height/2
        self.width_offset = self.width/2

    def calculate_collision_circles(self):
        self.rear_circle.append(-self.width/4) 
        self.rear_circle.append(0)
        self.front_circle.append(+self.width/4)
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
        self.rotation = 0
        self.wheels = []

        for i in range(vehicle.wheel_count):
            self.wheels.append(self.Wheel(i, vehicle.wheel, vehicle.wheel_positions[i]))


    def update(self,time_delta):
        self.update_car(time_delta) 
        for wheel in self.wheels:
            wheel.update()

    def draw(self):
        glPushMatrix()
        glTranslatef(self.vertical_position, 0, self.horizontal_position)
        self.draw_car()
        glPopMatrix()

    def draw_wheels(self):
        for wheel in self.wheels:
            wheel.draw()


    def check_collision_box(self, box_x, box_y, box_w, box_h, car):
        box_x = box_x - box_w
        box_y = box_y + box_h
        box_w = box_w*2
        box_h = box_h*2
        if ((box_x < car.horizontal_position + car.width) #if box is before end of car
                and (box_x + box_w > car.horizontal_position) #if front of box is ahead of car back
                and (box_y < car.vertical_position + car.height) #if box is below passanger side of car
                and (box_y + box_h > car.vertical_position)): #if box overlaps car by the side
            return True
        else:
            return False

    def ahead(self, other):
        box_x = other.horizontal_position
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
        self.up = False
        self.down = False
        self.forward = False
        self.braking = False
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

    def update_car(self, time_delta):
        #for i in range(self.score_hundreds - int(self.score / 100)):
        #    ParticleManager.add_new_emmitter(Minus100Points(HUD.POINTS100_X[self.player_id], HUD.POINTS100_SPEED_DIRECTION[self.player_id]*Speed.MAX_SPEED))
        self.score += 0.01 * time_delta
        old_score_hundreds = self.score_hundreds
        self.score_hundreds = int(self.score / 100)
        #for i in range(self.score_hundreds-old_score_hundreds):
        #    ParticleManager.add_new_emmitter(Plus100Points(HUD.POINTS100_X[self.player_id], HUD.POINTS100_SPEED_DIRECTION[self.player_id]*Speed.MAX_SPEED))
        
        #Adjust postition to user input
        if self.up and self.vertical_position < RoadPositions.UPPER_LIMIT - self.height_offset:
            self.vertical_position += 5 if not self.shrunk else 2
        elif self.down and self.vertical_position > RoadPositions.LOWER_LIMIT + self.height_offset:
            self.vertical_position -= 5 if not self.shrunk else 2
        
        if self.forward and self.horizontal_position < RoadPositions.FORWARD_LIMIT:
            self.horizontal_position += 5 if not self.shrunk else 2
        elif self.braking and self.horizontal_position > RoadPositions.REAR_LIMIT:
            self.horizontal_position -= 5 if not self.shrunk else 2

        if self.speed < Speed.MAX_SPEED:
            displacement = (Speed.MAX_SPEED - self.speed)*time_delta
            self.horizontal_position -= displacement if (self.horizontal_position - displacement) >= 0 else 0 

        

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
        self.wobbling = False
        self.wobbling_side = True #True = Left False=Right
        self.original_lane = self.vertical_position
        self.switching_to_left_lane = False
        self.switching_to_right_lane = False
        self.skiding = False
        self.skid_marks_x = 0
        self.skid_marks_y = 0
        self.skid_mark = None
        self.crashed = False

    def check_overtake_need(self, cars):
        if self.skiding or (self.switching_to_left_lane or self.switching_to_right_lane):
            return
        for car in cars:
            if car == self:
                continue
            if car.ahead(self) and car.slower(self):
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
        if len(cars) == 0:
            return True
        box_x = self.horizontal_position;
        box_y = lane;  
        box_w = self.width_offset + 20 #give it some clearance
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

    def hit_from_behind(self):
        if self.speed > 0:
            self.speed = (Speed.MAX_KMH - 5)*Speed.ONE_KMH
        elif self.speed == 0:
            self.speed = Speed.SIXTY_KMH
        elif self.speed < 0: #ambulances
            self.speed += 10*Speed.ONE_KMH
            
        if random.randrange(2) == 0:
            self.angular_speed += (0.5*Speed.ONE_RADMIL)
        else:
            self.angular_speed -= (0.3*Speed.ONE_RADMIL)
        self.skiding = True
        self.swerve()

    def wobble(self):
        self.wobbling = True
        self.wobbling_side = (random.randrange(2) == 0)
        self.skiding = True
        self.swerve()

    def draw_car(self):
        glPushMatrix()
        glRotatef(self.rotation, 0, 1, 0)
        self.vehicle.model.draw()
        self.draw_wheels()
        glPopMatrix()
        
        #if self.skid_mark != None:
        #    cr.save()
        #    cr.translate(self.skid_marks_x, self.skid_marks_y-self.height_offset)
        #    cr.set_source_surface(self.skid_mark, 0, 0)
        #    cr.paint()
        #    cr.restore()
        
        #cr.save()
        #cr.translate(self.horizontal_position, self.vertical_position - self.height_offset);
        #x = self.width / 2.0
        #y = self.height / 2.0
        #cr.translate(x, y)
        #cr.rotate(self.rotation)
        #cr.translate(-x, -y)
        #cr.set_source_surface(self.model, 0, 0)
        #cr.paint()
        #cr.restore()
    

    def update_car(self, time_delta):
        player_speed = Speed.MAX_SPEED
        horizontal_position_delta = time_delta*(self.speed-player_speed)
        self.horizontal_position += horizontal_position_delta 
        self.rotation += time_delta*self.angular_speed
        if self.rotation != 0:
            self.speed -= 1*Speed.ONE_KMH if self.speed > 3*Speed.ONE_KMH else 0
        
        if self.wobbling:
            if self.rotation >= Speed.MAX_WOBBLE_ROTATION or self.rotation <= -Speed.MAX_WOBBLE_ROTATION:
                self.wobbling_side = not self.wobbling_side
                self.angular_speed = 0
            if self.wobbling_side == True:
                self.angular_speed += 0.2*Speed.ONE_RADMIL
            else:
                self.angular_speed -= 0.2*Speed.ONE_RADMIL

        lateral_speed = 5*(float(self.speed)/float(Speed.MAX_SPEED))
        if self.switching_to_left_lane:
            if self.original_lane == RoadPositions.RIGHT_LANE:
                if self.vertical_position >= RoadPositions.MIDDLE_LANE:
                    self.switching_to_left_lane = False
                    self.vertical_position = RoadPositions.MIDDLE_LANE
                else:
                    self.vertical_position += lateral_speed
            else:
                if self.vertical_position >= RoadPositions.LEFT_LANE:
                    self.switching_to_left_lane = False
                    self.vertical_position = RoadPositions.LEFT_LANE
                else:
                    self.vertical_position += lateral_speed
        elif self.switching_to_right_lane:
            if self.original_lane == RoadPositions.LEFT_LANE:
                if self.vertical_position <= RoadPositions.MIDDLE_LANE:
                    self.switching_to_right_lane = False
                    self.vertical_position = RoadPositions.MIDDLE_LANE
                else:
                    self.vertical_position -= lateral_speed
            else:
                if self.vertical_position <= RoadPositions.RIGHT_LANE:
                    self.switching_to_right_lane = False
                    self.vertical_position = RoadPositions.RIGHT_LANE
                else:
                    self.vertical_position -= lateral_speed
        #if self.skiding:
        #    if self.skid_mark == None and self.switching_to_left_lane:
        #        self.skid_mark = SkidMarks.SKID_LEFT
        #    elif self.skid_mark == None and self.switching_to_right_lane:
        #        self.skid_mark = SkidMarks.SKID_RIGHT
        #    if self.skid_marks_y == 0:
        #        self.skid_marks_y = self.vertical_position
        #    if self.skid_marks_x == 0:
        #        self.skid_marks_x = self.horizontal_position
        #    else:
        #        self.skid_marks_x += time_delta*(-player_speed) 


class Road():
    def __init__(self, z=0):
        self.road = ms3d.ms3d("./road.ms3d")
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

    class Wheels:
        GALLARDO = None
        RS4 = None
        Charger = None


    def __init__(self):
        pygame.init()
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
        if Window.FULLSCREEN:
            pygame.display.set_mode(display, DOUBLEBUF | OPENGL | pygame.HWSURFACE | pygame.FULLSCREEN)
        else:
            pygame.display.set_mode(display, DOUBLEBUF | OPENGL | pygame.HWSURFACE)# | pygame.FULLSCREEN)

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glDepthMask(GL_TRUE)
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        glEnable(GL_TEXTURE_2D);
        glHint(GL_PERSPECTIVE_CORRECTION_HINT,GL_NICEST);
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
        glLightfv(GL_LIGHT0, GL_POSITION, (0,0,-1,0))
        #glLightfv(GL_LIGHT0, GL_POSITION, (0,10,0,1))

        gluPerspective(25, Window.WIDTH/Window.HEIGHT, 1, 2400)
        gluLookAt(-200,450,0, RoadPositions.MIDDLE_LANE,0,0, 0,1,0)
        
        
    def load_resources(self):
        def fill_wheel_positions(vehicle, model):
            for i in range(vehicle.wheel_count):
                vehicle.wheel_positions.append(model.getJointPosition("hub"+str(i)))

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

    def check_collision_box(self, box_x, box_y, box_w, box_h, car2_x, car2_y, car2_w, car2_h):
        box_x = box_x - box_w
        box_y = box_y + box_h
        box_w = box_w*2
        box_h = box_h*2
        car2_x -= car2_w
        car2_y -= car2_y 
        car2_w *=2
        car2_h *=2
        if ((box_x < car2_x + car2_w) #if box is before end of car
                and (box_x + box_w > car2_x) #if front of box is ahead of car back
                and (box_y < car2_y + car2_h) #if box is below passanger side of car
                and (box_y + box_h > car2_y)): #if box overlaps car by the side
            return True
        else:
            return False

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
                #Just a reminder this is only feasable because were using really small lists THIS DOES NOT SCALE WELL!!
        #create new NPVs
        if len(self.npvs) < 5:
            if self.spawn_delay <= 0:
                self.generateRandomNPV()
                self.spawn_delay = 900
        #Recalculate their position
        for npv in self.npvs:
            npv.check_overtake_need(self.npvs)
            npv.update(time_delta)
        
        #Check collisions
        
        #(between non-players themselves)
        for i in range(len(self.npvs) - 1):
            for j in range(i+1, len(self.npvs)):
                if self.check_collision_box(self.npvs[i].horizontal_position, self.npvs[i].vertical_position, self.npvs[i].width_offset, self.npvs[i].height_offset, self.npvs[j].horizontal_position, self.npvs[j].vertical_position, self.npvs[j].width_offset, self.npvs[j].height_offset):
                    self.npv_collision(self.npvs[i], self.npvs[j])

        for player in self.players:
            player.update(time_delta)

        self.last_update_timestamp = current_time
    
    def npv_collision(self, car1, car2):
        if(car1.vertical_position == car2.vertical_position):
            if(car1.horizontal_position <= car2.horizontal_position):
                car2.hit_from_behind()
            else:
                car1.hit_from_behind()
        else:
            if (not car1.crashed) and (not car2.crashed):
                #ParticleManager.add_new_emmitter(SmokeEmitter(car1.horizontal_position, car1.vertical_position-car1.height_offset, -car1.speed, 0))
                car1.crashed = True
                car2.crashed = True
            car1.wobble()
            car2.wobble()


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
                self.players[i].braking = True
            elif key == KeyboardKeys.KEY_RIGHT[i]:
                self.players[i].forward = True
            elif key == KeyboardKeys.KEY_UP[i]:
                self.players[i].up = True
                self.players[i].steer(Steering.TURN_LEFT)
            elif key == KeyboardKeys.KEY_DOWN[i]:
                self.players[i].down = True
                self.players[i].steer(Steering.TURN_RIGHT)
    
    def on_key_release(self, key):
        for i in range(len(self.players)):
            if key == KeyboardKeys.KEY_LEFT[i]:
                self.players[i].braking = False
            elif key == KeyboardKeys.KEY_RIGHT[i]:
                self.players[i].forward = False
            elif key == KeyboardKeys.KEY_UP[i]:
                self.players[i].up = False
                self.players[i].steer(Steering.CENTERED)
            elif key == KeyboardKeys.KEY_DOWN[i]:
                self.players[i].down = False
                self.players[i].steer(Steering.CENTERED)

game = Game()
