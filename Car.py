from OpenGL.raw.GL.VERSION.GL_1_0 import glPushMatrix, glTranslatef, glRotatef, glPopMatrix, glDisable, glEnable
from OpenGL.raw.GL.VERSION.GL_1_1 import GL_LIGHTING

from constants import Steering, RoadPositions, Speed
from utils import box_collision, rotate_2d_vector


class Car:
    class Wheel:
        FRONT_RIGHT = 0
        FRONT_LEFT = 1
        REAR_LEFT = 2
        REAR_RIGHT = 3

        def __init__(self, wheel_id, model, position):
            self.wheel_id = wheel_id
            self.model = model
            self.position = position
            self.steering = Steering.CENTERED
            self.rotateAngle = 0

        def update(self):
            # Not realistic at all but who cares!!
            if self.rotateAngle >= 360:
                self.rotateAngle = 0
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
        self.height = self.vehicle.height  # TODO #cairo.ImageSurface.get_height(model)
        self.width = self.vehicle.width  # TODO cairo.ImageSurface.get_width(model)
        self.height_offset = self.vehicle.height_offset
        self.radius = self.vehicle.radius
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

    def update(self, time_delta):
        self.front_circle = rotate_2d_vector(self.front_circle, self.rotation)
        self.rear_circle = rotate_2d_vector(self.rear_circle, self.rotation)
        self.update_car(time_delta)
        for wheel in self.wheels:
            wheel.update()

    def draw(self):
        if self.horizontal_position-self.width_offset > RoadPositions.FORWARD_LIMIT:
            pass
        if self.skid_mark is not None:
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
        box_x = other.horizontal_position + 5 * Speed.ONE_METER
        box_y = other.vertical_position
        box_h = other.height_offset
        box_w = other.width_offset + 5 * Speed.ONE_METER  # Distance to check for vehicles ahead
        return self.check_collision_box(box_x, box_y, box_w, box_h, self)

    def slower(self, other):
        return self.speed < other.speed

    def steer(self, side):
        self.wheels[self.Wheel.FRONT_LEFT].steering = side
        self.wheels[self.Wheel.FRONT_RIGHT].steering = side
