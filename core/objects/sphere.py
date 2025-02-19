from typing import Union
from utils.vector import Vector3D
from ..ray import Ray

class Sphere:
    def __init__(self, center: Vector3D, radius: float, material):
        self.radius = radius
        self.center = center
        self.material = material

    def intersect(self, ray: Ray) -> Union[float, None]:
        l = self.center - ray.origin
        tc = l.dot(ray.direction)
        if tc < 0:
            return None
        d2 = l.dot(l) - tc * tc
        if d2 > self.radius * self.radius:
            return None
        thc = (self.radius * self.radius - d2) ** 0.5
        t1 = tc - thc
        t2 = tc + thc
        return t1 if t1 > 0 else t2
        
        
