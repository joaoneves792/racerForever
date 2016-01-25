# import pygame2
# pygame_sdl2.import_as_pygame()

import random

import pygame
from OpenGL.GL import *
from ms3d import ms3d, Tex

import ParticleManager
# 11 MS3D Unit = 1 meter = 20 OpenGL units
from AI import AI
from MessageEmitter import HolyShit, Mayhem, Annihilation
from Player import Player
from PointsEmitter import Minus10Points
from Road import Road
from SmokeEmitter import SmokeEmitter
from Truck import Truck
from VehicleModel import VehicleModel
from constants import Window, HUD, KeyboardKeys, RoadPositions, Speed, Steering, SkidMarks, Sounds, PowerUps
from utils import car_circle_collision, drawText, draw_rectangle, box_collision

class Game():

    def __init__(self):
        pygame.init()
        pygame.display.init()
        self.init_display()
        pygame.mixer.init()

        self.available_vehicles = []
        self.available_trucks = []
        self.emergency_vehicles = []
        self.available_player_vehicles = []
        self.draw_loading_screen()
        self.load_resources()

        self.road = Road()
        
        #Setup the HUD light
        glLightfv(GL_LIGHT7, GL_AMBIENT, (1, 1, 1, 1))
        glLightfv(GL_LIGHT7, GL_DIFFUSE, (1,1,1,1))
        glLightfv(GL_LIGHT7, GL_SPECULAR, (1,1,1,1))
        glLightfv(GL_LIGHT7, GL_POSITION, (0,0,1,0))
        
        self.players = []
        self.last_update_timestamp = -1

        self.previous_crash_count = 0
        self.npvs = []
        self.spawn_delay = 0
        self.droped_items = []
        self.paused = False 
        self.singlePlayer = True

        Sounds.ACCEL.play(-1)

        #self.players.append(Player(self.available_vehicles[0], 0, RoadPositions.MIDDLE_LANE, Speed.MAX_SPEED, 0))
        self.players.append(Player(self.available_player_vehicles[0], 0, RoadPositions.MIDDLE_LANE, Speed.MAX_SPEED, 0))
        
        #self.players.append(Player(self.available_player_vehicles[0], 0, RoadPositions.RIGHT_LANE, Speed.MAX_SPEED, 1))


        while True:
            for event in pygame.event.get():
                self.handle_events(event)
            self.update()
            self.draw()

    def init_display(self):
        display = (Window.WIDTH, Window.HEIGHT)
        pygame.mouse.set_visible(False)
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

        glClearDepth(1);
        glClearColor(0, 0, 0, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glMatrixMode(GL_PROJECTION)
        #gluPerspective(90, Window.WIDTH/Window.HEIGHT, 1, 2400)
        #gluPerspective(25, Window.WIDTH/Window.HEIGHT, 1, 2400)
        #gluLookAt(-200,450,0, RoadPositions.MIDDLE_LANE,0,0, 0,1,0)
        #gluLookAt(RoadPositions.MIDDLE_LANE, 30, RoadPositions.REAR_LIMIT-100, RoadPositions.MIDDLE_LANE,30,0, 0,1,0)
        #gluLookAt(RoadPositions.MIDDLE_LANE, 30, -150, RoadPositions.MIDDLE_LANE,30,RoadPositions.BEYOND_HORIZON, 0,1,0)
        #gluLookAt(RoadPositions.MIDDLE_LANE+8, 18, -2.3, RoadPositions.MIDDLE_LANE,30,RoadPositions.BEYOND_HORIZON, 0,1,0)
        glMatrixMode(GL_MODELVIEW)
        

    def load_resources(self):
        def fill_wheel_positions(vehicle, model):
            for i in range(vehicle.wheel_count):
                vehicle.wheel_positions.append(model.getJointPosition("hub"+str(i)))
    
        def load_vehicle(car_model, wheel_model, num_wheels, lod="./Cars/RS4/RS4_LOD.ms3d"):
            ms3d_car = ms3d(car_model)
            ms3d_lod = ms3d(lod)
            ms3d_wheel = ms3d(wheel_model)
            vehicle = VehicleModel(ms3d_car, ms3d_lod, ms3d_wheel, num_wheels)
            fill_wheel_positions(vehicle, ms3d_car)
            return vehicle

        Sounds.ACCEL = pygame.mixer.Sound("./Sound/accelarating2.wav")
        Sounds.BRAKE = pygame.mixer.Sound("./Sound/tiresqueal.wav")
        Sounds.CRASH = pygame.mixer.Sound("./Sound/crash.wav")
        Sounds.ROLLOVER = pygame.mixer.Sound("./Sound/rollover.wav")
        Sounds.SIREN = pygame.mixer.Sound("./Sound/siren.wav")
        Sounds.HORN = pygame.mixer.Sound("./Sound/horn.wav")

        Sounds.HOLY = pygame.mixer.Sound("./Sound/holy.wav")
        Sounds.MAYHEM = pygame.mixer.Sound("./Sound/mayhem.wav")
        Sounds.ANNIHILATION = pygame.mixer.Sound("./Sound/total2.wav")

        SkidMarks.SKID_LEFT = ms3d("./Road/skid_left.ms3d")
        SkidMarks.SKID_RIGHT = ms3d("./Road/skid_right.ms3d")
        SkidMarks.SKID_STRAIGHT = ms3d("./Road/skid_straight.ms3d")

        self.pointsHUD = ms3d("./HUD/pointsHUD.ms3d")
        self.powerupsHUD = ms3d("./HUD/powerupsHUD.ms3d")

        Particles.POINTS = ms3d("./HUD/pointsParticle.ms3d")
        Particles.PLUS_100_POINTS = ms3d("./HUD/plus100Particle.ms3d")
        Particles.MINUS_100_POINTS = ms3d("./HUD/minus100Particle.ms3d")
        Particles.HOLY_SHIT = ms3d("./HUD/holy.ms3d")
        Particles.MAYHEM = ms3d("./HUD/mayhem.ms3d")
        Particles.ANNIHILATION = ms3d("./HUD/annihilation.ms3d")

        Particles.SMOKE = Tex("./smoke_particle.png").getTexture()


        PowerUps.CRATE = ms3d("./Powerups/crate/crate.ms3d")
        PowerUps.ENERGY_SHIELD = ms3d("./Powerups/energy_shield.ms3d")
        PowerUps.PHASER_FIRE = Tex("./Powerups/phaser_fire.png").getTexture()
        PowerUps.EMPTY = Tex("./Powerups/empty.png").getTexture()
        PowerUps.CALL_911 = Tex("./Powerups/911.png").getTexture()
        PowerUps.HYDRAULICS = Tex("./Powerups/Hydraulics.png").getTexture()
        PowerUps.PHASER = Tex("./Powerups/phaser.png").getTexture()
        PowerUps.SHIELD = Tex("./Powerups/shield.png").getTexture()
        PowerUps.SHRINK = Tex("./Powerups/shrink.png").getTexture()


        self.available_player_vehicles.append(load_vehicle("./Cars/Gallardo/gallardo_play_optimized.ms3d", "./Cars/Gallardo/gallardoWheel.ms3d", 4))

        self.emergency_vehicles.append(load_vehicle("./Cars/Cop1/copplay_optimized.ms3d", "./Cars/Cop1/copwheels.ms3d", 4, "./Cars/Cop1/coplod.ms3d"))
        self.emergency_vehicles.append(load_vehicle("./Cars/Ambulance/ambulance_optimized.ms3d", "./Cars/Ambulance/ambulance_wheel.ms3d", 4, "./Cars/Ambulance/ambulance_lod.ms3d"))

        self.available_trucks.append(load_vehicle("./Cars/Rumpo/rumpo_optimized.ms3d", "./Cars/Rumpo/rumpo_wheel.ms3d", 4,  "./Cars/Rumpo/rumpo_LOD.ms3d"))

        self.available_vehicles.append(load_vehicle("./Cars/RS4/RS4_optimized.ms3d", "./Cars/RS4/RS4Wheel.ms3d", 4, "./Cars/RS4/RS4_LOD.ms3d"))
        self.available_vehicles.append(load_vehicle("./Cars/charger/charger_play_optimized.ms3d", "./Cars/charger/ChargerWheel.ms3d", 4, "./Cars/charger/charger_lod.ms3d"))
        self.available_vehicles.append(load_vehicle("./Cars/Murci/MurcielagoPlay_optimized.ms3d", "./Cars/Gallardo/gallardoWheel.ms3d", 4, "./Cars/Murci/Murcielago_LOD.ms3d"))
        self.available_vehicles.append(load_vehicle("./Cars/M3E92/M3play_optimized.ms3d", "./Cars/M3E92/M3E92Wheel.ms3d", 4, "Cars/M3E92/M3Lod.ms3d"))
        self.available_vehicles.append(load_vehicle("./Cars/NSX/NSXplay_optimized.ms3d", "./Cars/NSX/NSXWheel.ms3d" , 4, "./Cars/NSX/NSXlod.ms3d"))
        self.available_vehicles.append(load_vehicle("./Cars/Skyline/skylineplay_optimized.ms3d", "./Cars/Skyline/skyline_wheel.ms3d" , 4, "./Cars/Skyline/skylinelod.ms3d"))
        self.available_vehicles.append(load_vehicle("./Cars/LP570_S/LP570play_optimized.ms3d", "./Cars/LP570_S/LP570wheel.ms3d" , 4, "./Cars/LP570_S/LP570lod.ms3d"))
        
    def generateEmergencyVehicle(self, vertical_position):
        Sounds.SIREN.play()    
        self.npvs.append(AI(self.emergency_vehicles[random.randrange(len(self.emergency_vehicles))], vertical_position, -20 * Speed.ONE_KMH))

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
        speed = Speed.MAX_SPEED - Speed.ONE_KMH * (random.randrange(20) + 5) # -5 beacause we need the npvs to always be slower than the player

        #Select a car
        random_num = random.randrange(100)
        if random_num < 4:
            self.generateEmergencyVehicle(lane)
        elif random_num < 10:
            self.npvs.append(
                Truck(self.available_trucks[random.randrange(len(self.available_trucks))], lane, speed, self))
        else:
            self.npvs.append(AI(self.available_vehicles[random.randrange(len(self.available_vehicles))], lane, speed))

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

        if self.paused:
            self.last_update_timestamp = current_time
            return       
        
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
        if len(self.npvs) < 12:
            if self.spawn_delay <= 0:
                self.generateRandomNPV()
                self.spawn_delay = 1900
        #Recalculate their position
        for npv in self.npvs:
            npv.check_overtake_need(self.npvs + self.players)
            npv.update(time_delta)
        
        #Check collisions
        #(between player and non-players)
        for player in self.players:
            if player.hydraulics:
                continue
            for npv in self.npvs[:]:
                if npv.capsized:
                    continue
                impact_vector = []
                if car_circle_collision(player, npv, impact_vector):    
                    self.applyCollisionForces(player, npv, impact_vector)
                    if not player.shield:
                        if not npv.crashed:
                            ParticleManager.add_new_emmitter(
                                Minus10Points(player.horizontal_position, player.vertical_position, -0.3, -0.2, size=100, shape=Particles.POINTS))
                            player.score -= 60
                    Sounds.CRASH.stop()
                    Sounds.CRASH.play()
                    Sounds.BRAKE.stop()
                    Sounds.BRAKE.play()
                    if not npv.crashed:
                        ParticleManager.add_new_3d_emmiter(
                            SmokeEmitter(npv.horizontal_position, npv.vertical_position, -npv.speed, 0))
                        npv.crashed = True
                if player.fire_phaser:
                    if npv.horizontal_position > player.horizontal_position:
                        if self.check_collision_box(player.horizontal_position, player.vertical_position, RoadPositions.COLLISION_HORIZON, player.height_offset, npv.horizontal_position, npv.vertical_position, npv.width_offset, npv.height_offset):
                            ParticleManager.add_new_3d_emmiter(
                                SmokeEmitter(npv.horizontal_position, npv.vertical_position, -npv.speed, 0))
                            self.npvs.remove(npv)
        
        #(between non-players themselves)
        for i in range(len(self.npvs) - 1):
            for j in range(i+1, len(self.npvs)):
                impact_vector = []
                if self.check_collision_circle(self.npvs[i], self.npvs[j], impact_vector):
                    self.applyCollisionForces(self.npvs[i], self.npvs[j], impact_vector)
                    if not self.npvs[i].crashed:
                        ParticleManager.add_new_3d_emmiter(
                            SmokeEmitter(self.npvs[i].horizontal_position, self.npvs[i].vertical_position, -self.npvs[i].speed, 0))
                    if not self.npvs[j].crashed:
                        ParticleManager.add_new_3d_emmiter(
                            SmokeEmitter(self.npvs[j].horizontal_position, self.npvs[j].vertical_position, -self.npvs[j].speed, 0))
                        Sounds.CRASH.play()
                        Sounds.BRAKE.play()
                    self.npvs[i].crashed = True
                    self.npvs[j].crashed = True
        
        #between players
        for i in range(len(self.players) - 1):
            for j in range(i+1, len(self.players)):
                if self.players[i].hydraulics or self.players[j].hydraulics:
                    continue
                impact_vector = []
                if self.check_collision_circle(self.players[i], self.players[j], impact_vector):
                    self.applyCollisionForces(self.players[i], self.players[j], impact_vector)
                    Sounds.CRASH.play()

        for player in self.players:
            player.update(time_delta)
        
        #Messages
        current_crashed_count = 0
        for npv in self.npvs:
            if npv.crashed:
                 current_crashed_count += 1

        if current_crashed_count > self.previous_crash_count:
            if current_crashed_count == 3:
                ParticleManager.add_new_emmitter(HolyShit(Particles.HOLY_SHIT))
                Sounds.HOLY.stop()
                Sounds.HOLY.play()
            elif current_crashed_count == 4:
                ParticleManager.add_new_emmitter(Mayhem(Particles.MAYHEM))
                Sounds.HOLY.stop()
                Sounds.MAYHEM.stop()
                Sounds.MAYHEM.play()
            elif current_crashed_count > 4:
                ParticleManager.add_new_emmitter(Annihilation(Particles.ANNIHILATION))
                Sounds.HOLY.stop()
                Sounds.MAYHEM.stop()
                Sounds.ANNIHILATION.stop()
                Sounds.ANNIHILATION.play()
            
        self.previous_crash_count = current_crashed_count

        for player in self.players:
            for item in self.droped_items:
                if self.check_collision_box(player.horizontal_position, player.vertical_position, player.width, player.height, item.x, item.y, PowerUps.SIZE, PowerUps.SIZE):
                    item.picked_up_by(player)
        
        for item in self.droped_items:
            item.update(time_delta)
        
        ParticleManager.update(time_delta)

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

    def draw_loading_screen(self):
        picture = Tex("./HUD/loading.png").getTexture()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, Window.WIDTH, 0, Window.HEIGHT, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, picture)
        glMaterialfv(GL_FRONT, GL_AMBIENT, (1, 1, 1, 1))
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (1, 1, 1, 1))
        glMaterialfv(GL_FRONT, GL_SPECULAR, (1, 1, 1, 1))
        glMaterialfv(GL_FRONT, GL_EMISSION, (0.5, 0.5, 0.5, 1))
        glMaterialfv(GL_FRONT, GL_SHININESS, 0.0)

        glBegin(GL_TRIANGLES)
        glNormal3f(0,0, 1)
        glTexCoord2f(0, 1)
        glVertex3f(0, 0, 0)
        glNormal3f(0, 0, 1)
        glTexCoord2f(1, 1)
        glVertex3f(Window.WIDTH, 0, 0) 
        glNormal3f(0, 0, 1)
        glTexCoord2f(0, 0)
        glVertex3f(0,Window.HEIGHT,0)    

        glNormal3f(0,0, 1)
        glTexCoord2f(1, 1)
        glVertex3f(Window.WIDTH, 0, 0)    
        glNormal3f(0, 0, 1)
        glTexCoord2f(0, 0)
        glVertex3f(0, Window.HEIGHT, 0)    
        glNormal3f(0, 0, 1)
        glTexCoord2f(1, 0)
        glVertex3f(Window.WIDTH, Window.HEIGHT, 0)    
        glEnd()
        
        glDisable(GL_TEXTURE_2D)

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        pygame.display.flip()
    def draw(self):
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        for player in self.players:
            player.draw()
        
        self.road.draw()


        for npv in self.npvs:
            npv.draw()
       
        for item in self.droped_items:
            item.draw()

        ParticleManager.draw_3d()

        self.draw_hud()
        
        pygame.display.flip()
 
    def draw_hud(self): 
        sun = False
        lamps = False
        if glIsEnabled(GL_LIGHT0):
            sun = True
        if glIsEnabled(GL_LIGHT1):
            lamps = True
        
        
        glDisable(GL_DEPTH_TEST)
        glDepthMask(GL_FALSE)
        #glDisable(GL_LIGHTING)
        #glDisable(GL_BLEND)
        if sun:
            glDisable(GL_LIGHT0)
        if lamps:
            glDisable(GL_LIGHT1)
            glDisable(GL_LIGHT2)
            glDisable(GL_LIGHT3)
            glDisable(GL_LIGHT4)
        
        glEnable(GL_LIGHT7)
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, Window.WIDTH, Window.HEIGHT, 0, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glColor3f(0, 0, 0)
        for player in self.players:
            glPushMatrix()
            color = (255, 255, 255, 255)
            if(player.score <= 0):
                color = (255, 0, 0, 255)
            glPushMatrix()
            glTranslatef(HUD.SCORE_HUD_POS_X[player.player_id], HUD.SCORE_HUD_POS_Y[player.player_id], 0)
            self.pointsHUD.draw()
            glPopMatrix()
            glDisable(GL_TEXTURE_2D)
            drawText(HUD.SCORE_POS_X[player.player_id], HUD.SCORE_POS_Y[player.player_id], color, (20, 20, 20, 0), "SCORE: " + str(int(player.score)))
            glPushMatrix()
            glTranslatef(HUD.INVENTORY_X[player.player_id], Window.HEIGHT - 55, 0)
            self.powerupsHUD.draw()
            glPushMatrix()
            glTranslatef(-10, 40, 0)
            glRotatef(180, 1, 0, 0)
            for i in range(PowerUps.INVENTORY_SIZE):
                glTranslatef(58, 0, 0)
                if i < len(player.inventory):
                    draw_rectangle(32, 32, player.inventory[i].icon)
                else:
                    draw_rectangle(32, 32, PowerUps.EMPTY)
            glPopMatrix()
            glPopMatrix()
            glPopMatrix()
        
        glPopMatrix()
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()

        glPushMatrix()
        glLoadIdentity()
        #glOrtho(RoadPositions.REAR_LIMIT, RoadPositions.FORWARD_LIMIT, 0, RoadPositions.UPPER_LIMIT, -1, 1)
        glOrtho(-Window.WIDTH//2, Window.WIDTH//2, 0, Window.HEIGHT, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        ParticleManager.draw()
        
        glPopMatrix()

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()


        if self.paused:
            self.draw_paused_menu()

        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glDisable(GL_LIGHT7)
        if sun:
            glEnable(GL_LIGHT0)
        if lamps:
            glEnable(GL_LIGHT1)
            glEnable(GL_LIGHT2)
            glEnable(GL_LIGHT3)
            glEnable(GL_LIGHT4)
        
        glDepthMask(GL_TRUE)
        glEnable(GL_BLEND)
    
    def draw_paused_menu(self):
        picture = Tex("./HUD/paused.png").getTexture()
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, Window.WIDTH, 0, Window.HEIGHT, -1, 1)
        glMatrixMode(GL_MODELVIEW)

        glPushMatrix()

        glTranslatef(Window.WIDTH/2-256, Window.HEIGHT/2-128, 0)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, picture)
        glMaterialfv(GL_FRONT, GL_AMBIENT, (1, 1, 1, 1))
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (1, 1, 1, 1))
        glMaterialfv(GL_FRONT, GL_SPECULAR, (1, 1, 1, 1))
        glMaterialfv(GL_FRONT, GL_EMISSION, (0.5, 0.5, 0.5, 1))
        glMaterialfv(GL_FRONT, GL_SHININESS, 0.0)

        glBegin(GL_TRIANGLES)
        glNormal3f(0,0, 1)
        glTexCoord2f(0, 1)
        glVertex3f(0, 0, 0)
        glNormal3f(0, 0, 1)
        glTexCoord2f(1, 1)
        glVertex3f(512, 0, 0) 
        glNormal3f(0, 0, 1)
        glTexCoord2f(0, 0)
        glVertex3f(0,256,0)    

        glNormal3f(0,0, 1)
        glTexCoord2f(1, 1)
        glVertex3f(512, 0, 0)    
        glNormal3f(0, 0, 1)
        glTexCoord2f(0, 0)
        glVertex3f(0, 256, 0)    
        glNormal3f(0, 0, 1)
        glTexCoord2f(1, 0)
        glVertex3f(512, 256, 0)    
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)


    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            self.on_key_press(event.key)
        elif event.type == pygame.KEYUP:
            self.on_key_release(event.key)
        elif event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.MOUSEMOTION:
            for i in range(len(self.players)):
                self.players[i].update_mouse(pygame.mouse.get_rel())

    def on_key_press(self, key):
        if key == KeyboardKeys.KEY_ESC:
            if self.paused:
                pygame.mixer.unpause()
            else:
                pygame.mixer.pause()
            self.paused = not self.paused
        if key == KeyboardKeys.KEY_Y and self.paused:
            pygame.quit()
            quit()
       
        for i in range(len(self.players)):
            if key == KeyboardKeys.KEY_LEFT[i]:
                self.players[i].apply_left = True
                self.players[i].steer(Steering.TURN_LEFT)
            elif key == KeyboardKeys.KEY_RIGHT[i]:
                self.players[i].apply_right = True
                self.players[i].steer(Steering.TURN_RIGHT)
            elif key == KeyboardKeys.KEY_UP[i]:
                self.players[i].apply_throttle = True
            elif key == KeyboardKeys.KEY_DOWN[i]:
                self.players[i].apply_brakes = True
            elif key >= KeyboardKeys.KEY_ONE[i] and key <= KeyboardKeys.KEY_FIVE[i]:
                self.players[i].usePowerUp(key - KeyboardKeys.KEY_TO_NUM[i])
    
    def on_key_release(self, key):
        for i in range(len(self.players)):
            if key == KeyboardKeys.KEY_LEFT[i]:
                self.players[i].release_left = True
                self.players[i].steer(Steering.CENTERED)
            elif key == KeyboardKeys.KEY_RIGHT[i]:
                self.players[i].release_right = True
                self.players[i].steer(Steering.CENTERED)
            elif key == KeyboardKeys.KEY_UP[i]:
                self.players[i].release_throttle = True 
            elif key == KeyboardKeys.KEY_DOWN[i]:
                self.players[i].release_brakes = True

game = Game()
