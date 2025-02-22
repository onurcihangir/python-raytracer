import math
from utils.vector import Vector3D
from .ray import Ray

class Camera:
    def __init__(self, position: Vector3D, look_at: Vector3D, up: Vector3D, fov: float, aspect_ratio: float):
        self.position = position
        self.look_at = look_at
        self.up = up
        self.fov = fov
        self.aspect_ratio = aspect_ratio
        self.calculate_camera_parameters()

    def calculate_camera_parameters(self):
        self.direction = (self.look_at - self.position).normalize()
        self.right = self.up.cross(self.direction).normalize()
        self.up = self.direction.cross(self.right).normalize()

        self.half_height = math.tan(math.radians(self.fov) / 2)
        self.half_width = self.aspect_ratio * self.half_height
        self.focal_length = 1

    def get_ray(self, u: float, v: float) -> Ray:
        horizontal = 2 * self.half_width * self.right * u
        vertical = 2 * self.half_height * self.up * v
        direction = (self.direction + horizontal + vertical).normalize()
        return Ray(self.position, direction)