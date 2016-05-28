#! /bin/python3


import random
import pygame
from OpenGL.GL import *

from XboxController import XboxController
from ms3d import ms3d, Tex, shader, Lights, GLM, Shadows, Text, MATRIX

from OpenGLContext import GL
import ParticleManager
from AI import AI
from MessageEmitter import HolyShit, Mayhem, Annihilation
from Player import Player
from PointsEmitter import Minus10Points
from Road import Road
from SmokeEmitter import SmokeEmitter
from Truck import Truck
from VehicleModel import VehicleModel
from singletons import Window, HUD, KeyboardKeys, RoadPositions, Speed, Steering, SkidMarks, Sounds, PowerUps, LightPositions, Controller
from utils import car_circle_collision, box_collision, text_to_texture

# 11 MS3D Unit = 1 meter = 20 OpenGL units


class Game:

    def __init__(self):
        pygame.init()
        pygame.display.init()
        pygame.display.set_caption("RACER Forever")

        pygame.mixer.init()

        self.available_vehicles = []
        self.available_trucks = []
        self.emergency_vehicles = []
        self.available_player_vehicles = []

        self.init_display()
        self.draw_loading_screen()
        self.load_resources()

        GL.GLM.selectMatrix(MATRIX.PROJECTION)
        GL.GLM.perspective(25, Window.WIDTH/Window.HEIGHT, 1, 15000)
        GL.GLM.selectMatrix(MATRIX.MODEL)
        GL.GLM.loadIdentity()

        GL.Lights.enableLighting()

        self.road = Road()
        
        self.players = []
        self.last_update_timestamp = -1

        self.previous_crash_count = 0
        self.ai = []
        self.spawn_delay = 0
        self.dropped_items = []
        self.paused = False 
        self.singlePlayer = True

        Sounds.ACCEL.play(-1)

        self.players.append(Player(self.available_player_vehicles[0], 0, RoadPositions.MIDDLE_LANE, Speed.PLAYER_SPEED, 0))

        # self.players[0].addPowerUp(Phaser(self, self.players[0]))

        if Controller.ENABLED:
            self.xboxCont = XboxController(self.handle_xbox_controller, deadzone=30, scale=100, invertYAxis=True)
            self.xboxCont.start()

        while True:
            if not Controller.ENABLED:
                for event in pygame.event.get():
                    self.handle_events(event)
            self.update()
            self.draw()

    @staticmethod
    def init_display():
        display = (Window.WIDTH, Window.HEIGHT)
        pygame.mouse.set_visible(False)
        # pygame.display.gl_set_attribute(pygame.GL_SWAP_CONTROL, 1)
        # pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 4)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 8)

        if Window.FULLSCREEN:
            pygame.display.set_mode(display, pygame.DOUBLEBUF | pygame.OPENGL | pygame.HWSURFACE | pygame.FULLSCREEN)
        else:
            pygame.display.set_mode(display, pygame.DOUBLEBUF | pygame.OPENGL | pygame.HWSURFACE)  # | pygame.FULLSCREEN)

        ms3d.initGlew()  # VERY FUCKING IMPORTANT TO DO THIS HERE!!!!

        GL.Shader = shader("./shaders/vert.shader", "./shaders/frag.shader")
        GL.Depth_shader = shader("./shaders/shadow_vert.shader", "./shaders/shadow_frag.shader")
        GL.Shader.use()
        GL.GLM = GLM(GL.Shader)
        GL.Lights = Lights(GL.Shader)
        GL.Shadows = Shadows(GL.GLM, GL.Shader, GL.Depth_shader, Window.WIDTH, Window.HEIGHT, 8192, 8192)
        GL.Shadows.changeOrthoBox(-2000, 2000, -2000, 2000, -1000, 1000)

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glDepthMask(GL_TRUE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_TEXTURE_2D)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glEnable(GL_MULTISAMPLE)

        glEnable(GL_CULL_FACE)
        
        glClearDepth(1)
        glClearColor(0, 0, 0, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def load_resources(self):
        def fill_wheel_positions(vehicle, model):
            for i in range(vehicle.wheel_count):
                vehicle.wheel_positions.append(model.getJointPosition("hub"+str(i)))
    
        def load_vehicle(car_model, wheel_model, num_wheels, lod="./Cars/RS4/RS4_LOD.ms3d"):
            ms3d_car = ms3d(car_model)
            ms3d_car.prepare(GL.Shader)
            ms3d_lod = ms3d(lod)
            ms3d_lod.prepare(GL.Shader)
            ms3d_wheel = ms3d(wheel_model)
            ms3d_wheel.prepare(GL.Shader)
            vehicle = VehicleModel(ms3d_car, ms3d_lod, ms3d_wheel, num_wheels)
            fill_wheel_positions(vehicle, ms3d_car)
            return vehicle

        Sounds.ACCEL = pygame.mixer.Sound("./Sound/accelerating2.wav")
        Sounds.BRAKE = pygame.mixer.Sound("./Sound/tire_squeal.wav")
        Sounds.CRASH = pygame.mixer.Sound("./Sound/crash.wav")
        Sounds.ROLLOVER = pygame.mixer.Sound("./Sound/rollover.wav")
        Sounds.SIREN = pygame.mixer.Sound("./Sound/siren.wav")
        Sounds.HORN = pygame.mixer.Sound("./Sound/horn.wav")

        Sounds.HOLY = pygame.mixer.Sound("./Sound/holy.wav")
        Sounds.MAYHEM = pygame.mixer.Sound("./Sound/mayhem.wav")
        Sounds.ANNIHILATION = pygame.mixer.Sound("./Sound/total2.wav")

        SkidMarks.SKID_LEFT = ms3d("./Road/skid_left.ms3d")
        SkidMarks.SKID_LEFT.prepare(GL.Shader)
        SkidMarks.SKID_RIGHT = ms3d("./Road/skid_right.ms3d")
        SkidMarks.SKID_RIGHT.prepare(GL.Shader)
        SkidMarks.SKID_STRAIGHT = ms3d("./Road/skid_straight.ms3d")
        SkidMarks.SKID_STRAIGHT.prepare(GL.Shader)

        HUD.POINTS_HUD = ms3d("./HUD/pointsHUD.ms3d")
        HUD.POINTS_HUD.prepare(GL.Shader)
        HUD.POWERUPS_HUD = ms3d("./HUD/powerupsHUD.ms3d")
        HUD.POWERUPS_HUD.prepare(GL.Shader)
        HUD.PAUSED_MENU = Tex("./HUD/paused.png").getTexture()
        HUD.PAUSED_MENU_RECTANGLE = ms3d()
        HUD.PAUSED_MENU_RECTANGLE.createRectangle(512, 256, HUD.PAUSED_MENU)
        HUD.PAUSED_MENU_RECTANGLE.prepare(GL.Shader)
        HUD.UBUNTU_MONO_WHITE = Text("./HUD/font.png", 512, 512, 8, 8, 40, 24, 44)
        HUD.UBUNTU_MONO_RED = Text("./HUD/font_red.png", 512, 512, 8, 8, 40, 24, 44)

        ParticleManager.Particles.POINTS = ms3d("./HUD/pointsParticle.ms3d")
        ParticleManager.Particles.POINTS.prepare(GL.Shader)
        ParticleManager.Particles.PLUS_100_POINTS = ms3d("./HUD/plus100Particle.ms3d")
        ParticleManager.Particles.PLUS_100_POINTS.prepare(GL.Shader)
        ParticleManager.Particles.MINUS_100_POINTS = ms3d("./HUD/minus100Particle.ms3d")
        ParticleManager.Particles.MINUS_100_POINTS.prepare(GL.Shader)
        ParticleManager.Particles.HOLY_SHIT = ms3d("./HUD/holy.ms3d")
        ParticleManager.Particles.HOLY_SHIT.prepare(GL.Shader)
        ParticleManager.Particles.MAYHEM = ms3d("./HUD/mayhem.ms3d")
        ParticleManager.Particles.MAYHEM.prepare(GL.Shader)
        ParticleManager.Particles.ANNIHILATION = ms3d("./HUD/annihilation.ms3d")
        ParticleManager.Particles.ANNIHILATION.prepare(GL.Shader)

        ParticleManager.Particles.SMOKE = ms3d("./smoke.ms3d")
        ParticleManager.Particles.SMOKE.prepare(GL.Shader)

        PowerUps.CRATE = ms3d("./PowerUps/crate/crate.ms3d")
        PowerUps.CRATE.prepare(GL.Shader)
        PowerUps.ENERGY_SHIELD = ms3d("./PowerUps/energy_shield.ms3d")
        PowerUps.ENERGY_SHIELD.prepare(GL.Shader)
        PowerUps.PHASER_FIRE = Tex("./PowerUps/phaser_fire.png").getTexture()
        PowerUps.EMPTY = Tex("./PowerUps/empty.png").getTexture()
        PowerUps.CALL_911 = Tex("./PowerUps/911.png").getTexture()
        PowerUps.HYDRAULICS = Tex("./PowerUps/Hydraulics.png").getTexture()
        PowerUps.PHASER = Tex("./PowerUps/phaser.png").getTexture()
        PowerUps.SHIELD = Tex("./PowerUps/shield.png").getTexture()
        PowerUps.SHRINK = Tex("./PowerUps/shrink.png").getTexture()
        PowerUps.INVENTORY_ICON_RECTANGLE = ms3d()
        PowerUps.INVENTORY_ICON_RECTANGLE.createRectangle(32, 32, PowerUps.EMPTY)
        PowerUps.INVENTORY_ICON_RECTANGLE.prepare(GL.Shader)
        PowerUps.PHASER_RECTANGLE = ms3d()
        PowerUps.PHASER_RECTANGLE.createRectangle(25, 2500, PowerUps.PHASER_FIRE)
        PowerUps.PHASER_RECTANGLE.prepare(GL.Shader)

        self.available_player_vehicles.append(load_vehicle("./Cars/Gallardo/gallardo_play_optimized.ms3d", "./Cars/Gallardo/gallardoWheel.ms3d", 4))

        self.emergency_vehicles.append(load_vehicle("./Cars/Cop1/copplay_optimized.ms3d", "./Cars/Cop1/copwheels.ms3d", 4, "./Cars/Cop1/coplod.ms3d"))
        self.emergency_vehicles.append(load_vehicle("./Cars/Ambulance/ambulance_optimized.ms3d", "./Cars/Ambulance/ambulance_wheel.ms3d", 4, "./Cars/Ambulance/ambulance_lod.ms3d"))

        self.available_trucks.append(load_vehicle("./Cars/Rumpo/rumpo_optimized.ms3d", "./Cars/Rumpo/rumpo_wheel.ms3d", 4,  "./Cars/Rumpo/rumpo_LOD.ms3d"))

        self.available_vehicles.append(load_vehicle("./Cars/RS4/RS4_optimized.ms3d", "./Cars/RS4/RS4Wheel.ms3d", 4, "./Cars/RS4/RS4_LOD.ms3d"))
        self.available_vehicles.append(load_vehicle("./Cars/charger/charger_play_optimized.ms3d", "./Cars/charger/ChargerWheel.ms3d", 4, "./Cars/charger/charger_lod.ms3d"))
        self.available_vehicles.append(load_vehicle("./Cars/Murci/MurcielagoPlay_optimized.ms3d", "./Cars/Gallardo/gallardoWheel.ms3d", 4, "./Cars/Murci/Murcielago_LOD.ms3d"))
        self.available_vehicles.append(load_vehicle("./Cars/M3E92/M3play_optimized.ms3d", "./Cars/M3E92/M3E92Wheel.ms3d", 4, "Cars/M3E92/M3Lod.ms3d"))
        self.available_vehicles.append(load_vehicle("./Cars/NSX/NSXplay_optimized.ms3d", "./Cars/NSX/NSXWheel.ms3d", 4, "./Cars/NSX/NSXlod.ms3d"))
        self.available_vehicles.append(load_vehicle("./Cars/Skyline/skylineplay_optimized.ms3d", "./Cars/Skyline/skyline_wheel.ms3d", 4, "./Cars/Skyline/skylinelod.ms3d"))
        self.available_vehicles.append(load_vehicle("./Cars/LP570_S/LP570play_optimized.ms3d", "./Cars/LP570_S/LP570wheel.ms3d", 4, "./Cars/LP570_S/LP570lod.ms3d"))
        self.available_vehicles.append(load_vehicle("./Cars/SL65/sl65play_optimized.ms3d", "./Cars/SL65/sl65Wheel.ms3d", 4, "./Cars/SL65/sl65Lod.ms3d"))
        self.available_vehicles.append(load_vehicle("./Cars/F430Scuderia/F430Soptimized.ms3d", "./Cars/F430Scuderia/F430Wheel.ms3d", 4, "./Cars/F430Scuderia/F430lod.ms3d"))
        self.available_vehicles.append(load_vehicle("./Cars/GT3RS/GT3RSoptimized.ms3d", "./Cars/GT3RS/GT3RSWheel.ms3d", 4, "./Cars/GT3RS/GT3RSlod.ms3d"))
        self.available_vehicles.append(load_vehicle("./Cars/2010Mustang/Mustangoptimized.ms3d", "./Cars/2010Mustang/MustangWheel.ms3d", 4, "./Cars/2010Mustang/MustangLod.ms3d"))

    def generate_emergency_vehicle(self, vertical_position):
        Sounds.SIREN.play()    
        self.ai.append(AI(self.emergency_vehicles[random.randrange(len(self.emergency_vehicles))], vertical_position, -20 * Speed.ONE_KMH))

    def generate_random_ai(self):
        # Select a random lane
        random_num = random.randrange(3)
        if random_num == 0:
            lane = RoadPositions.LEFT_LANE
        elif random_num == 1:
            lane = RoadPositions.MIDDLE_LANE
        else:
            lane = RoadPositions.RIGHT_LANE

        # Select a Speed
        speed = Speed.NORMAL_SPEED - Speed.ONE_KMH * (random.randrange(20) + 5)  # -5 because we need the ai to always be slower than the player

        # Select a car
        random_num = random.randrange(100)
        if random_num < 4:
            self.generate_emergency_vehicle(lane)
        elif random_num < 10:
            self.ai.append(
                Truck(self.available_trucks[random.randrange(len(self.available_trucks))], lane, speed, self))
        else:
            self.ai.append(AI(self.available_vehicles[random.randrange(len(self.available_vehicles))], lane, speed))

    @staticmethod
    def check_collision_circle(car1, car2, impact_vector):
        # If the cars have not yet appeared on screen then give them a chance of sorting it out
        if car1.horizontal_position > RoadPositions.COLLISION_HORIZON or car2.horizontal_position > RoadPositions.COLLISION_HORIZON:
            return False
        return car_circle_collision(car1, car2, impact_vector)

    @staticmethod
    def check_collision_box(car1_x, car1_y, car1_w, car1_h, car2_x, car2_y, car2_w, car2_h):
        # If the cars have not yet appeared on screen then give them a chance of sorting it out
        if car1_x > RoadPositions.COLLISION_HORIZON or car2_x > RoadPositions.COLLISION_HORIZON:
            return False
        return box_collision(car1_x, car1_y, car1_w, car1_h, car2_x, car2_y, car2_w, car2_h) 

    def update(self):
        current_time = pygame.time.get_ticks()
        if self.last_update_timestamp == -1:
            self.last_update_timestamp = current_time
        time_delta = (current_time - self.last_update_timestamp)

        if self.paused:
            self.last_update_timestamp = current_time
            for player in self.players:
                player.update_camera()
            return       
        
        self.road.advance(time_delta)
        
        # Update NPVs
        if self.spawn_delay > 0:
            self.spawn_delay -= time_delta
        # Delete NPVs that are behind us (not visible anymore)
        for npv in self.ai[:]:  # Mind the [:] its there so we iterate on a copy of the list
            if npv.horizontal_position <= RoadPositions.BEHIND_REAR_HORIZON:
                self.ai.remove(npv)
                for player in self.players:
                    if npv in player.crashed_into:
                        player.crashed_into.remove(npv)
                # Just a reminder this is only feasable because were using really small lists THIS DOES NOT SCALE WELL!!
        # create new NPVs
        if len(self.ai) < 12:
            if self.spawn_delay <= 0:
                self.generate_random_ai()
                self.spawn_delay = 1900
        # Recalculate their position
        for npv in self.ai:
            npv.check_overtake_need(self.ai + self.players)
            npv.update(time_delta)
        
        # Check collisions
        # (between player and non-players)
        for player in self.players:
            if player.hydraulics:
                continue
            for npv in self.ai[:]:
                if npv.capsized:
                    continue
                impact_vector = []
                if car_circle_collision(player, npv, impact_vector):    
                    self.apply_collision_forces(player, npv, impact_vector)
                    if not player.shield:
                        if not npv.crashed:
                            ParticleManager.add_new_emitter(
                                Minus10Points(player.horizontal_position, player.vertical_position, -0.3, -0.2, size=250, shape=ParticleManager.Particles.POINTS))
                            player.score -= 60
                    Sounds.CRASH.stop()
                    Sounds.CRASH.play()
                    Sounds.BRAKE.stop()
                    Sounds.BRAKE.play()
                    if not npv.crashed:
                        ParticleManager.add_new_3d_emitter(
                            SmokeEmitter(npv.vertical_position, 20, npv.horizontal_position, -npv.speed ))
                        npv.crashed = True
                if player.fire_phaser:
                    if npv.horizontal_position > player.horizontal_position:
                        if self.check_collision_box(player.horizontal_position, player.vertical_position, RoadPositions.COLLISION_HORIZON, player.height_offset, npv.horizontal_position, npv.vertical_position, npv.width_offset, npv.height_offset):
                            ParticleManager.add_new_3d_emitter(
                                SmokeEmitter(npv.vertical_position, 20, npv.horizontal_position, 0)) # -npv.speed))
                            self.ai.remove(npv)
        
        # (between non-players themselves)
        for i in range(len(self.ai) - 1):
            for j in range(i+1, len(self.ai)):
                impact_vector = []
                if self.check_collision_circle(self.ai[i], self.ai[j], impact_vector):
                    self.apply_collision_forces(self.ai[i], self.ai[j], impact_vector)
                    if not self.ai[i].crashed:
                        ParticleManager.add_new_3d_emitter(
                            SmokeEmitter(self.ai[i].vertical_position, 20, self.ai[i].horizontal_position, -self.ai[i].speed))
                    if not self.ai[j].crashed:
                        ParticleManager.add_new_3d_emitter(
                            SmokeEmitter(self.ai[i].vertical_position, 20, self.ai[i].horizontal_position, -self.ai[i].speed))
                        Sounds.CRASH.play()
                        Sounds.BRAKE.play()
                    self.ai[i].crashed = True
                    self.ai[j].crashed = True

        # between players
        for i in range(len(self.players) - 1):
            for j in range(i+1, len(self.players)):
                if self.players[i].hydraulics or self.players[j].hydraulics:
                    continue
                impact_vector = []
                if self.check_collision_circle(self.players[i], self.players[j], impact_vector):
                    self.apply_collision_forces(self.players[i], self.players[j], impact_vector)
                    Sounds.CRASH.play()

        for player in self.players:
            player.update(time_delta)
        
        # Messages
        current_crashed_count = 0
        for npv in self.ai:
            if npv.crashed:
                current_crashed_count += 1

        if current_crashed_count > self.previous_crash_count:
            if current_crashed_count == 3:
                ParticleManager.add_new_emitter(HolyShit(ParticleManager.Particles.HOLY_SHIT))
                Sounds.HOLY.stop()
                Sounds.HOLY.play()
            elif current_crashed_count == 4:
                ParticleManager.add_new_emitter(Mayhem(ParticleManager.Particles.MAYHEM))
                Sounds.HOLY.stop()
                Sounds.MAYHEM.stop()
                Sounds.MAYHEM.play()
            elif current_crashed_count > 4:
                ParticleManager.add_new_emitter(Annihilation(ParticleManager.Particles.ANNIHILATION))
                Sounds.HOLY.stop()
                Sounds.MAYHEM.stop()
                Sounds.ANNIHILATION.stop()
                Sounds.ANNIHILATION.play()
            
        self.previous_crash_count = current_crashed_count

        for player in self.players:
            for item in self.dropped_items:
                if self.check_collision_box(player.horizontal_position, player.vertical_position, player.width, player.height, item.x, item.y, PowerUps.SIZE, PowerUps.SIZE):
                    item.picked_up_by(player)
        
        for item in self.dropped_items:
            item.update(time_delta)
        
        ParticleManager.update(time_delta)

        self.last_update_timestamp = current_time
    
    @staticmethod
    def apply_collision_forces(car1, car2, impact_vector):
        car1_speed = car1.speed
        car1_lateral_speed = car1.lateral_speed
        car2_speed = car2.speed
        car2_lateral_speed = car2.lateral_speed
        
        if not (car2 in car1.crashed_into):
            car1.crashed_into.append(car2)
        car1.apply_collision_forces(car2_speed, car2_lateral_speed, impact_vector)
        car2.apply_collision_forces(car1_speed, car1_lateral_speed, impact_vector)

    @staticmethod
    def draw_loading_screen():
        picture = Tex("./HUD/loading.png").getTexture()
        rectangle = ms3d()
        rectangle.createRectangle(Window.WIDTH, Window.HEIGHT, picture)
        rectangle.prepare(GL.Shader)

        glClearColor(0, 0, 0, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        GL.GLM.selectMatrix(MATRIX.PROJECTION)
        GL.GLM.loadIdentity()
        GL.GLM.otho(0, Window.WIDTH, 0, Window.HEIGHT, 1, -1)
        GL.GLM.selectMatrix(MATRIX.MODEL)
        GL.Lights.disableLighting()

        rectangle.drawGL3()

        pygame.display.flip()

    def draw(self):

        # Do a shadow pass first
        GL.Depth_shader.use()
        if LightPositions.LAMPS:
            GL.Shadows.prepareToMapDepth(50, LightPositions.LAMP_Y, 0)
            GL.Shadows.changeOrthoBox(-2000, 100, -500, 0, -200, 0)
        else:
            GL.Shadows.prepareToMapDepth(-LightPositions.SUN_X, LightPositions.SUN_Y, LightPositions.SUN_Z)
            GL.Shadows.changeOrthoBox(-2000, 2000, -2000, 2000, -1000, 1000)

        GL.GLM.selectMatrix(MATRIX.MODEL)
        GL.GLM.pushMatrix()
        GL.GLM.translate(0, -5, 0)  # try to compensate for peter panning

        for player in self.players:
            player.draw_shadow_pass()
        for npv in self.ai:
            npv.draw()
        for item in self.dropped_items:
            item.draw()
        self.road.draw_shadow_pass()

        GL.GLM.popMatrix()

        # Now do the actual drawing
        GL.Shader.use()
        GL.Shadows.returnToNormalDrawing()

        self.road.draw()

        for player in self.players:
            player.draw()

        for npv in self.ai:
            npv.draw()
       
        for item in self.dropped_items:
            item.draw()

        GL.Lights.disableLighting()

        ParticleManager.draw_3d()
        self.draw_hud()
        GL.Lights.enableLighting()

        pygame.display.flip()

    def draw_hud(self): 
        GL.Lights.disableLighting()

        GL.GLM.selectMatrix(MATRIX.PROJECTION)
        GL.GLM.pushMatrix()
        GL.GLM.loadIdentity()
        GL.GLM.otho(0, Window.WIDTH, Window.HEIGHT, 0, -1, 1)

        GL.GLM.selectMatrix(MATRIX.VIEW)
        GL.GLM.loadIdentity()

        GL.GLM.selectMatrix(MATRIX.MODEL)
        GL.GLM.pushMatrix()
        GL.GLM.loadIdentity()

        for player in self.players:
            GL.GLM.pushMatrix()
            GL.GLM.scale(1, -1, 1)
            HUD.POINTS_HUD.drawGL3()
            GL.GLM.popMatrix()

            GL.GLM.pushMatrix()
            GL.GLM.translate(30, 45, 0.5)
            GL.GLM.scale(1, -1, 1)
            if player.score >= 0:
                HUD.UBUNTU_MONO_WHITE.drawTextLine("SCORE:" + str(int(player.score)), 24)
            else:
                HUD.UBUNTU_MONO_RED.drawTextLine("SCORE:" + str(int(player.score)), 24)
            GL.GLM.popMatrix()

            GL.GLM.pushMatrix()
            GL.GLM.translate(0, Window.HEIGHT, 0)
            GL.GLM.scale(1, -1, 1)
            HUD.POWERUPS_HUD.drawGL3()

            if player.powerUpTimeOut > 0:
                GL.GLM.pushMatrix()
                GL.GLM.translate(30, 53, 0.5)
                HUD.UBUNTU_MONO_RED.drawTextLine("0:" + str(int(player.powerUpTimeOut/1000)), 24)
                GL.GLM.popMatrix()

            GL.GLM.pushMatrix()
            GL.GLM.translate(-10, 10, 0.5)
            for i in range(PowerUps.INVENTORY_SIZE):
                GL.GLM.translate(58, 0, 0)
                if i < len(player.inventory):
                    PowerUps.INVENTORY_ICON_RECTANGLE.changeRectangleTexture(player.inventory[i].icon)
                    PowerUps.INVENTORY_ICON_RECTANGLE.drawGL3()
                else:
                    PowerUps.INVENTORY_ICON_RECTANGLE.changeRectangleTexture(PowerUps.EMPTY)
                    PowerUps.INVENTORY_ICON_RECTANGLE.drawGL3()
            GL.GLM.popMatrix()

            GL.GLM.popMatrix()

        ParticleManager.draw()

        GL.GLM.popMatrix()
        GL.GLM.selectMatrix(MATRIX.PROJECTION)
        GL.GLM.popMatrix()

        if self.paused:
            self.draw_paused_menu()

        GL.GLM.selectMatrix(MATRIX.MODEL)

        GL.Lights.enableLighting()

    @staticmethod
    def draw_paused_menu():
        GL.GLM.selectMatrix(MATRIX.PROJECTION)
        GL.GLM.pushMatrix()
        GL.GLM.loadIdentity()
        GL.GLM.otho(0, Window.WIDTH, 0, Window.HEIGHT, -1, 1)
        GL.GLM.selectMatrix(MATRIX.MODEL)

        GL.GLM.pushMatrix()
        GL.GLM.translate(Window.WIDTH/2-256, Window.HEIGHT/2-128, 0)
        HUD.PAUSED_MENU_RECTANGLE.drawGL3()
        GL.GLM.popMatrix()

        GL.GLM.selectMatrix(MATRIX.PROJECTION)
        GL.GLM.popMatrix()
        GL.GLM.selectMatrix(MATRIX.MODEL)

    def handle_xbox_controller(self, control_id, value):
        if control_id == XboxController.XboxControls.START and value == 1:
            if self.paused:
                pygame.mixer.unpause()
            else:
                pygame.mixer.pause()
            self.paused = not self.paused

        if control_id == XboxController.XboxControls.Y and value == 1 and self.paused:
            self.xboxCont.stop()
            pygame.quit()
            quit()

        with self.players[0].input_lock:
            if control_id == XboxController.XboxControls.RTRIGGER:
                self.players[0].apply_throttle = (value + 100)/200
                self.players[0].apply_brakes = 0
            if control_id == XboxController.XboxControls.LTRIGGER:
                self.players[0].apply_brakes = value/100
                self.players[0].apply_throtle = 0
            if control_id == XboxController.XboxControls.LTHUMBX:
                if value > 0:
                    self.players[0].apply_right = value/100
                    self.players[0].apply_left = 0
                else:
                    self.players[0].apply_left = -(value/100)
                    self.players[0].apply_right = 0

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
                self.players[i].apply_left = 1
                self.players[i].steer(Steering.TURN_LEFT)
            elif key == KeyboardKeys.KEY_RIGHT[i]:
                self.players[i].apply_right = 1
                self.players[i].steer(Steering.TURN_RIGHT)
            elif key == KeyboardKeys.KEY_UP[i]:
                self.players[i].apply_throttle = 1
            elif key == KeyboardKeys.KEY_DOWN[i]:
                self.players[i].apply_brakes = 1
            elif KeyboardKeys.KEY_ONE[i] <= key <= KeyboardKeys.KEY_FIVE[i]:
                self.players[i].usePowerUp(key - KeyboardKeys.KEY_TO_NUM[i])
    
    def on_key_release(self, key):
        for i in range(len(self.players)):
            if key == KeyboardKeys.KEY_LEFT[i]:
                self.players[i].apply_left = 0
                self.players[i].steer(Steering.CENTERED)
            elif key == KeyboardKeys.KEY_RIGHT[i]:
                self.players[i].apply_right = 0
                self.players[i].steer(Steering.CENTERED)
            elif key == KeyboardKeys.KEY_UP[i]:
                self.players[i].apply_throttle = 0
            elif key == KeyboardKeys.KEY_DOWN[i]:
                self.players[i].apply_brakes = 0

# game = Game()
