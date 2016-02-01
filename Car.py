from OpenGLContext import GL
from singletons import Steering, RoadPositions, Speed
from utils import box_collision, rotate_2d_vector
from VehicleModel import VehicleModel


class Car:
    class Wheel:
        FRONT_RIGHT = 0
        FRONT_LEFT = 1
        REAR_LEFT = 2
        REAR_RIGHT = 3

        def __init__(self, wheel_id, model, position, car):
            self.car = car  # type: Car
            self.wheel_id = wheel_id
            self.model = model
            self.position = position
            self.steering = Steering.CENTERED
            self.rotateAngle = 0

        def update(self):
            # Not realistic at all but who cares!!
            if self.rotateAngle >= 360:
                self.rotateAngle = 0
            if self.car.speed != 0:
                self.rotateAngle += 15

        def draw(self):
            GL.GLM.pushMatrix()
            GL.GLM.translate(self.position[0], self.position[1], self.position[2])
            if self.wheel_id == self.FRONT_LEFT or self.wheel_id == self.REAR_LEFT:
                GL.GLM.rotate(180, 0, 1, 0)
            if self.wheel_id == self.FRONT_LEFT or self.wheel_id == self.FRONT_RIGHT:
                if self.steering == Steering.TURN_LEFT:
                    GL.GLM.rotate(25, 0, 1, 0)
                elif self.steering == Steering.TURN_RIGHT:
                    GL.GLM.rotate(-25, 0, 1, 0)
            GL.GLM.rotate(self.rotateAngle, 1, 0, 0)
            self.model.drawGL3()
            GL.GLM.popMatrix()

    def __init__(self, vehicle, z, x, speed):
        self.vehicle = vehicle  # type: VehicleModel
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
        self.skidding = False
        self.skid_marks_x = 0
        self.skid_marks_y = 0
        self.skid_mark = None

        for i in range(vehicle.wheel_count):
            self.wheels.append(self.Wheel(i, vehicle.wheel, vehicle.wheel_positions[i], self))

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
            GL.GLM.pushMatrix()
            # glDisable(GL_LIGHTING)
            GL.GLM.translate(self.skid_marks_y, 0, self.skid_marks_x)
            self.skid_mark.drawGL3()
            #glEnable(GL_LIGHTING)
            GL.GLM.popMatrix()
        GL.GLM.pushMatrix()
        GL.GLM.translate(self.vertical_position, 0, self.horizontal_position)
        self.draw_car()
        GL.GLM.popMatrix()

    def draw_wheels(self):
        for wheel in self.wheels:
            wheel.draw()

    @staticmethod
    def check_collision_box(box_x, box_y, box_w, box_h, car):
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
