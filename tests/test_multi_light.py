import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from utils.vector import Vector3D
from core.light import Light
from utils.shading import diffuse_specular

MAT = {"ambient": (0.1, 0.1, 0.1), "diffuse": (0.8, 0.0, 0.0),
       "specular": (1.0, 1.0, 1.0), "shininess": 32, "reflectivity": 0.0,
       "transparency": 0.0, "refractive_index": 1.0}


def test_diffuse_specular_lit_face():
    # Surface at origin, normal +z, light straight in front, viewer in front.
    hit = Vector3D(0, 0, 0, 1)
    normal = Vector3D(0, 0, 1, 0)
    view_dir = Vector3D(0, 0, 1, 0)
    light = Light(Vector3D(0, 0, 5, 1), (1.0, 1.0, 1.0))
    c = diffuse_specular(hit, normal, view_dir, light, MAT)
    # Diffuse red channel should be positive (light faces the surface).
    assert c[0] > 0.0
    # Returned in 0-1 scale (not multiplied by 255): red <= diffuse(0.8)+specular(1.0)
    assert c[0] <= 1.8 + 1e-9


def test_diffuse_specular_backface_zero_diffuse():
    # Light behind the surface -> normal.dot(light_dir) <= 0 -> no diffuse.
    hit = Vector3D(0, 0, 0, 1)
    normal = Vector3D(0, 0, 1, 0)
    view_dir = Vector3D(0, 0, 1, 0)
    light = Light(Vector3D(0, 0, -5, 1), (1.0, 1.0, 1.0))
    c = diffuse_specular(hit, normal, view_dir, light, MAT)
    assert c[0] == 0.0 and c[1] == 0.0 and c[2] == 0.0


def test_two_lights_brighter_than_one():
    from core.ray import Ray
    from core.objects.sphere import Sphere
    from core.bvh import BVHNode
    from renderer.raytracer import trace_ray
    s = Sphere(Vector3D(0, 0, -3, 1), 1.0, MAT)
    objs = [BVHNode.build([s])]
    L1 = Light(Vector3D(5, 5, 5, 1), (1, 1, 1))
    L2 = Light(Vector3D(-5, 5, 5, 1), (1, 1, 1))
    ray = Ray(Vector3D(0, 0, 5, 1), Vector3D(0, 0, -1, 0))
    one = np.array(trace_ray(ray, objs, [L1]), dtype=np.int64)
    two = np.array(trace_ray(ray, objs, [L1, L2]), dtype=np.int64)
    # Two lights illuminate at least as brightly as one (red channel).
    assert two[0] >= one[0]


def test_zero_lights_is_ambient_only():
    from core.ray import Ray
    from core.objects.sphere import Sphere
    from core.bvh import BVHNode
    from renderer.raytracer import trace_ray
    s = Sphere(Vector3D(0, 0, -3, 1), 1.0, MAT)
    objs = [BVHNode.build([s])]
    ray = Ray(Vector3D(0, 0, 5, 1), Vector3D(0, 0, -1, 0))
    color = np.array(trace_ray(ray, objs, []), dtype=np.int64)
    # Ambient is material["ambient"] (0.1) * 255 ~= 25 on each channel.
    assert all(abs(int(c) - 25) <= 1 for c in color)


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"\n{len(fns)} tests passed")


if __name__ == "__main__":
    _run_all()
