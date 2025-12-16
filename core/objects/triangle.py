from typing import Union, Tuple
from utils.vector import Vector3D
from core.ray import Ray


class Triangle:
    def __init__(self, v0: Vector3D, v1: Vector3D, v2: Vector3D, material, 
                 n0: Vector3D = None, n1: Vector3D = None, n2: Vector3D = None):
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.material = material
        
        # Calculate edges
        self.edge1 = v1 - v0
        self.edge2 = v2 - v0
        
        # Calculate face normal
        self.face_normal = self.edge1.cross(self.edge2).normalize()
        
        # Vertex normals for smooth shading (if provided)
        self.n0 = n0 if n0 else self.face_normal
        self.n1 = n1 if n1 else self.face_normal
        self.n2 = n2 if n2 else self.face_normal
        
        self.use_smooth_shading = (n0 is not None and n1 is not None and n2 is not None)
    
    def intersect(self, ray: Ray) -> Union[float, None]:
        EPSILON = 1e-8
        
        # Calculate determinant
        pvec = ray.direction.cross(self.edge2)
        det = self.edge1.dot(pvec)
        
        # Ray is parallel to triangle
        if abs(det) < EPSILON:
            return None
        
        inv_det = 1.0 / det
        
        # Calculate u parameter
        tvec = ray.origin - self.v0
        u = tvec.dot(pvec) * inv_det
        
        # Check if intersection is outside triangle
        if u < 0.0 or u > 1.0:
            return None
        
        # Calculate v parameter
        qvec = tvec.cross(self.edge1)
        v = ray.direction.dot(qvec) * inv_det
        
        # Check if intersection is outside triangle
        if v < 0.0 or u + v > 1.0:
            return None
        
        # Calculate t (distance along ray)
        t = self.edge2.dot(qvec) * inv_det
        
        if t > EPSILON:
            # Store barycentric coordinates for normal interpolation
            self._last_u = u
            self._last_v = v
            return t
        
        return None
    
    def get_normal_at_intersection(self, hit_point: Vector3D = None) -> Vector3D:
        if not self.use_smooth_shading:
            return self.face_normal
        
        # Interpolate vertex normals using barycentric coordinates
        u = getattr(self, '_last_u', 0)
        v = getattr(self, '_last_v', 0)
        w = 1.0 - u - v
        
        # Barycentric interpolation
        normal = self.n0 * w + self.n1 * u + self.n2 * v
        return normal.normalize()
    
    def get_centroid(self) -> Vector3D:
        return (self.v0 + self.v1 + self.v2) / 3.0
    
    def get_area(self) -> float:
        return self.edge1.cross(self.edge2).length() * 0.5