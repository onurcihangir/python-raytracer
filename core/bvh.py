from utils.vector import Vector3D


def _compute_aabb(objects):
    """Return (min, max) AABB encompassing all objects."""
    mins = [obj.get_bounding_box()[0] for obj in objects]
    maxs = [obj.get_bounding_box()[1] for obj in objects]
    return (
        Vector3D(min(v.x for v in mins), min(v.y for v in mins), min(v.z for v in mins), 1),
        Vector3D(max(v.x for v in maxs), max(v.y for v in maxs), max(v.z for v in maxs), 1),
    )


def _intersect_aabb(aabb_min, aabb_max, ray):
    """Slab method AABB test. Returns True if ray intersects the box."""
    tmin, tmax = -1e18, 1e18

    for attr in ('x', 'y', 'z'):
        d = getattr(ray.direction, attr)
        if d == 0.0:
            # Ray parallel to slab — check if origin is inside
            o = getattr(ray.origin, attr)
            if o < getattr(aabb_min, attr) or o > getattr(aabb_max, attr):
                return False
            continue
        inv_d = 1.0 / d
        t0 = (getattr(aabb_min, attr) - getattr(ray.origin, attr)) * inv_d
        t1 = (getattr(aabb_max, attr) - getattr(ray.origin, attr)) * inv_d
        if inv_d < 0:
            t0, t1 = t1, t0
        tmin = max(tmin, t0)
        tmax = min(tmax, t1)
        if tmax < tmin:
            return False
    return tmax > 0


class BVHNode:
    def __init__(self, aabb_min, aabb_max, left, right):
        self.aabb_min = aabb_min
        self.aabb_max = aabb_max
        self._left = left
        self._right = right
        # Expose material=None so trace_ray's closest_obj.material access
        # won't crash before the leaf-unwrap step.
        self.material = None

    @classmethod
    def build(cls, objects):
        """Recursively build a BVH from a list of scene objects."""
        if len(objects) == 0:
            return None
        if len(objects) == 1:
            if hasattr(objects[0], 'get_bounding_box'):
                objects[0].get_bounding_box()  # validate — raises ValueError for empty mesh
            return objects[0]  # leaf — plain scene object

        aabb_min, aabb_max = _compute_aabb(objects)

        # Choose the widest axis
        spans = (
            aabb_max.x - aabb_min.x,
            aabb_max.y - aabb_min.y,
            aabb_max.z - aabb_min.z,
        )
        axis = ('x', 'y', 'z')[spans.index(max(spans))]

        # Sort by centroid on that axis and split at midpoint
        def centroid(obj):
            bb = obj.get_bounding_box()
            return (getattr(bb[0], axis) + getattr(bb[1], axis)) * 0.5

        sorted_objs = sorted(objects, key=centroid)
        mid = len(sorted_objs) // 2

        left = cls.build(sorted_objs[:mid])
        right = cls.build(sorted_objs[mid:])

        return cls(aabb_min, aabb_max, left, right)

    def intersect_full(self, ray):
        """Return (t, leaf_object) for closest hit, or (None, None) on miss."""
        if not _intersect_aabb(self.aabb_min, self.aabb_max, ray):
            return None, None

        t_left, leaf_left = None, None
        if self._left is not None:
            t_left, leaf_left = self._left.intersect_full(ray)

        t_right, leaf_right = None, None
        if self._right is not None:
            t_right, leaf_right = self._right.intersect_full(ray)

        if t_left is None and t_right is None:
            return None, None
        if t_left is not None and (t_right is None or t_left <= t_right):
            return t_left, leaf_left
        return t_right, leaf_right

    def intersect(self, ray):
        """Return closest hit distance, or None. Thin wrapper over intersect_full."""
        t, _ = self.intersect_full(ray)
        return t
