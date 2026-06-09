from typing import List, Union
from utils.vector import Vector3D
from core.ray import Ray
from core.objects.triangle import Triangle
from core.bvh import BVHNode


class Mesh:
    def __init__(self, material, name: str = "Mesh"):
        self.triangles: List[Triangle] = []
        self.material = material
        self.name = name
        self._bbox_min = None
        self._bbox_max = None
        self._bvh = None
        self._last_hit_triangle = None

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
    
    def build_bvh(self):
        """Build the internal triangle BVH. Call after all triangles are added."""
        if self.triangles:
            self._bvh = BVHNode.build(self.triangles)

    def intersect(self, ray: Ray) -> Union[float, None]:
        if not self.triangles:
            return None

        if self._bvh is not None:
            # Both BVHNode and a bare single Triangle implement intersect_full.
            t, tri = self._bvh.intersect_full(ray)
        else:
            # BVH not built — safety-net linear scan
            t, tri = self._linear_intersect(ray)

        if tri is not None:
            self._last_hit_triangle = tri
        return t

    def _linear_intersect(self, ray):
        """Fallback linear scan. Returns (closest_t, closest_triangle)."""
        closest_t = None
        closest_triangle = None
        for triangle in self.triangles:
            t = triangle.intersect(ray)
            if t is not None and (closest_t is None or t < closest_t):
                closest_t = t
                closest_triangle = triangle
        return closest_t, closest_triangle

    def intersect_full(self, ray):
        """Used by the scene-level BVH. Delegates to the BVH-aware intersect
        and returns (t, self) so the ray tracer reads the normal via
        self.get_normal_at_intersection (backed by _last_hit_triangle)."""
        t = self.intersect(ray)
        if t is None:
            return None, None
        return t, self

    def get_normal_at_intersection(self, hit_point: Vector3D) -> Vector3D:
        if self._last_hit_triangle is not None:
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
    
    def get_triangle_count(self) -> int:
        return len(self.triangles)
    
    def get_bounding_box(self) -> tuple:
        if self._bbox_min is None or self._bbox_max is None:
            raise ValueError(f"Mesh '{self.name}' has no triangles — cannot compute bounding box")
        return (self._bbox_min, self._bbox_max)