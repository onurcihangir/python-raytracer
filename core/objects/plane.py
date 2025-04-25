from typing import Union
from utils.vector import Vector3D
from core.ray import Ray

class Plane:
    def __init__(self, point: Vector3D, normal: Vector3D, material):
        self.point = point      # any point ont plane
        self.normal = normal.normalize()  # normal vector of the plane
        self.material = material
    
    def intersect(self, ray: Ray) -> Union[float, None]:
        denom = self.normal.dot(ray.direction)
        
        # if ray is parallel to the plane, no intersection
        if abs(denom) < 1e-6:
            return None
        
        p0l0 = self.point - ray.origin
        
        # intersection distance
        t = p0l0.dot(self.normal) / denom
        
        # if t is negative, the plane is behind the ray
        if t < 0:
            return None
            
        return t