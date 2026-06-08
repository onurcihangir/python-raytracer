import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from renderer.ui.scene_builder import build_object, make_material, build_scene
from core.objects.sphere import Sphere
from core.objects.plane import Plane
from core.objects.mesh import Mesh
from core.bvh import BVHNode


def test_make_material_has_all_keys():
    m = make_material((0.8, 0.2, 0.2), 0.5)
    for key in ("ambient", "diffuse", "specular", "shininess",
                "reflectivity", "transparency", "refractive_index"):
        assert key in m, f"missing key {key}"
    assert m["diffuse"] == (0.8, 0.2, 0.2)
    assert m["reflectivity"] == 0.5


def test_build_sphere():
    spec = {"type": "sphere", "position": (1, 2, 3), "radius": 2.0,
            "material": make_material((1, 0, 0), 0.0)}
    obj = build_object(spec)
    assert isinstance(obj, Sphere)
    assert obj.radius == 2.0
    assert obj.center.x == 1 and obj.center.y == 2 and obj.center.z == 3


def test_build_plane():
    spec = {"type": "plane", "point": (0, -1, 0), "normal": (0, 1, 0),
            "material": make_material((0.5, 0.5, 0.5), 0.0)}
    obj = build_object(spec)
    assert isinstance(obj, Plane)


def test_build_cube():
    spec = {"type": "cube", "center": (0, 0, 0), "size": 2.0,
            "material": make_material((0, 1, 0), 0.0)}
    obj = build_object(spec)
    assert isinstance(obj, Mesh)
    assert obj.get_triangle_count() == 12


def test_build_tetra():
    spec = {"type": "tetra", "center": (0, 0, 0), "size": 1.0,
            "material": make_material((0, 0, 1), 0.0)}
    obj = build_object(spec)
    assert isinstance(obj, Mesh)
    assert obj.get_triangle_count() == 4


def test_build_scene_empty():
    camera, objects, light = build_scene(400, 300, [], (3, 5, 2))
    assert objects == []
    assert abs(camera.aspect_ratio - 400 / 300) < 1e-9
    assert light.position.x == 3 and light.position.y == 5 and light.position.z == 2


def test_build_scene_only_plane():
    specs = [{"type": "plane", "point": (0, -1, 0), "normal": (0, 1, 0),
              "material": make_material((0.5, 0.5, 0.5), 0.0)}]
    camera, objects, light = build_scene(400, 300, specs, (3, 5, 2))
    assert len(objects) == 1
    assert isinstance(objects[0], Plane)


def test_build_scene_only_sphere():
    specs = [{"type": "sphere", "position": (0, 0, -3), "radius": 1.0,
              "material": make_material((1, 0, 0), 0.0)}]
    camera, objects, light = build_scene(400, 300, specs, (3, 5, 2))
    # single finite object: BVHNode.build returns the bare object as leaf
    assert len(objects) == 1
    assert isinstance(objects[0], Sphere)


def test_build_scene_mixed():
    specs = [
        {"type": "sphere", "position": (-2, 0, -3), "radius": 1.0,
         "material": make_material((1, 0, 0), 0.0)},
        {"type": "sphere", "position": (2, 0, -3), "radius": 1.0,
         "material": make_material((0, 1, 0), 0.0)},
        {"type": "plane", "point": (0, -1, 0), "normal": (0, 1, 0),
         "material": make_material((0.5, 0.5, 0.5), 0.0)},
    ]
    camera, objects, light = build_scene(400, 300, specs, (3, 5, 2))
    # two finite objects -> a BVHNode; one plane -> separate
    assert len(objects) == 2
    assert isinstance(objects[0], BVHNode)
    assert isinstance(objects[1], Plane)


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"\n{len(fns)} tests passed")


if __name__ == "__main__":
    _run_all()
