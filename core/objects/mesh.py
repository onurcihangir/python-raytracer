from typing import List, Union
from utils.vector import Vector3D
from core.ray import Ray
from core.objects.triangle import Triangle


class Mesh:
    def __init__(self, material, name: str = "Mesh"):
        self.triangles: List[Triangle] = []
        self.material = material
        self.name = name
        self._bbox_min = None
        self._bbox_max = None
    
    def add_triangle(self, v0: Vector3D, v1: Vector3D, v2: Vector3D,
                     n0: Vector3D = None, n1: Vector3D = None, n2: Vector3D = None):
        triangle = Triangle(v0, v1, v2, self.material, n0, n1, n2)
        self.triangles.append(triangle)
        self._update_bounding_box(v0, v1, v2)
    
    def from_vertices_and_faces(self, vertices: List[Vector3D], faces: List[tuple],
                                normals: List[Vector3D] = None):
        for face in faces:
            if len(face) == 3:
                v0, v1, v2 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
                
                if normals and len(normals) > max(face):
                    n0, n1, n2 = normals[face[0]], normals[face[1]], normals[face[2]]
                    self.add_triangle(v0, v1, v2, n0, n1, n2)
                else:
                    self.add_triangle(v0, v1, v2)
            else:
                # For faces with more than 3 vertices, triangulate (simple fan triangulation)
                v0 = vertices[face[0]]
                for i in range(1, len(face) - 1):
                    v1, v2 = vertices[face[i]], vertices[face[i + 1]]
                    self.add_triangle(v0, v1, v2)
    
    def intersect(self, ray: Ray) -> Union[float, None]:
        closest_t = None
        closest_triangle = None
        
        # Quick bounding box test (if available)
        if self._bbox_min and self._bbox_max:
            if not self._intersect_bbox(ray):
                return None
        
        for triangle in self.triangles:
            t = triangle.intersect(ray)
            if t is not None:
                if closest_t is None or t < closest_t:
                    closest_t = t
                    closest_triangle = triangle
        
        # Store the intersected triangle for normal calculation
        if closest_triangle:
            self._last_hit_triangle = closest_triangle
        
        return closest_t
    
    def get_normal_at_intersection(self, hit_point: Vector3D) -> Vector3D:
        if hasattr(self, '_last_hit_triangle'):
            return self._last_hit_triangle.get_normal_at_intersection(hit_point)
        return Vector3D(0, 1, 0, 0)  # Default up vector
    
    def _update_bounding_box(self, v0: Vector3D, v1: Vector3D, v2: Vector3D):
        vertices = [v0, v1, v2]
        
        if self._bbox_min is None:
            self._bbox_min = Vector3D(
                min(v.x for v in vertices),
                min(v.y for v in vertices),
                min(v.z for v in vertices),
                1
            )
            self._bbox_max = Vector3D(
                max(v.x for v in vertices),
                max(v.y for v in vertices),
                max(v.z for v in vertices),
                1
            )
        else:
            self._bbox_min = Vector3D(
                min(self._bbox_min.x, min(v.x for v in vertices)),
                min(self._bbox_min.y, min(v.y for v in vertices)),
                min(self._bbox_min.z, min(v.z for v in vertices)),
                1
            )
            self._bbox_max = Vector3D(
                max(self._bbox_max.x, max(v.x for v in vertices)),
                max(self._bbox_max.y, max(v.y for v in vertices)),
                max(self._bbox_max.z, max(v.z for v in vertices)),
                1
            )
    
    def _intersect_bbox(self, ray: Ray) -> bool:
        if not self._bbox_min or not self._bbox_max:
            return True
        
        tmin = (self._bbox_min.x - ray.origin.x) / (ray.direction.x if ray.direction.x != 0 else 1e-8)
        tmax = (self._bbox_max.x - ray.origin.x) / (ray.direction.x if ray.direction.x != 0 else 1e-8)
        
        if tmin > tmax:
            tmin, tmax = tmax, tmin
        
        tymin = (self._bbox_min.y - ray.origin.y) / (ray.direction.y if ray.direction.y != 0 else 1e-8)
        tymax = (self._bbox_max.y - ray.origin.y) / (ray.direction.y if ray.direction.y != 0 else 1e-8)
        
        if tymin > tymax:
            tymin, tymax = tymax, tymin
        
        if (tmin > tymax) or (tymin > tmax):
            return False
        
        if tymin > tmin:
            tmin = tymin
        if tymax < tmax:
            tmax = tymax
        
        tzmin = (self._bbox_min.z - ray.origin.z) / (ray.direction.z if ray.direction.z != 0 else 1e-8)
        tzmax = (self._bbox_max.z - ray.origin.z) / (ray.direction.z if ray.direction.z != 0 else 1e-8)
        
        if tzmin > tzmax:
            tzmin, tzmax = tzmax, tzmin
        
        if (tmin > tzmax) or (tzmin > tmax):
            return False
        
        return True
    
    def get_triangle_count(self) -> int:
        return len(self.triangles)
    
    def get_bounding_box(self) -> tuple:
        return (self._bbox_min, self._bbox_max)