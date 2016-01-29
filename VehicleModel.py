class VehicleModel:
    def __init__(self, model, lod, wheel, wheel_count):
        self.model = model
        self.lod = lod
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

    def testDraw(self):
        self.model.drawGL3()