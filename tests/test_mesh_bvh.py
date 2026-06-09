import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.vector import Vector3D
from core.objects.triangle import Triangle

MAT = {"ambient": (0.1, 0.1, 0.1), "diffuse": (0.7, 0.2, 0.2),
       "specular": (1, 1, 1), "shininess": 32, "reflectivity": 0.0,
       "transparency": 0.0, "refractive_index": 1.0}


def test_triangle_bounding_box():
    t = Triangle(Vector3D(0, 0, 0, 1), Vector3D(2, 1, -3, 1),
                 Vector3D(-1, 4, 2, 1), MAT)
    bb_min, bb_max = t.get_bounding_box()
    assert (bb_min.x, bb_min.y, bb_min.z) == (-1, 0, -3)
    assert (bb_max.x, bb_max.y, bb_max.z) == (2, 4, 2)


def _ref_linear_intersect(mesh, ray):
    """Reference: linear scan independent of the mesh's internal BVH."""
    closest_t, closest_tri = None, None
    for tri in mesh.triangles:
        t = tri.intersect(ray)
        if t is not None and (closest_t is None or t < closest_t):
            closest_t, closest_tri = t, tri
    return closest_t, closest_tri


def test_bvh_matches_linear_on_cube():
    from utils.obj_loader import OBJLoader
    from core.ray import Ray
    cube = OBJLoader.create_cube(MAT, Vector3D(0, 0, -3, 1), 2.0)  # builds BVH
    for i in range(-3, 4):
        for j in range(-3, 4):
            ox, oy = i * 0.4, j * 0.4
            ray = Ray(Vector3D(ox, oy, 5, 1), Vector3D(0, 0, -1, 0))
            bvh_t = cube.intersect(ray)
            ref_t, _ = _ref_linear_intersect(cube, ray)
            if ref_t is None:
                assert bvh_t is None, f"BVH hit but linear missed at {ox},{oy}"
            else:
                assert bvh_t is not None, f"BVH missed but linear hit at {ox},{oy}"
                assert abs(bvh_t - ref_t) < 1e-6, f"t mismatch at {ox},{oy}: {bvh_t} vs {ref_t}"


def test_normal_after_bvh_hit():
    from utils.obj_loader import OBJLoader
    from core.ray import Ray
    cube = OBJLoader.create_cube(MAT, Vector3D(0, 0, -3, 1), 2.0)
    ray = Ray(Vector3D(0, 0, 5, 1), Vector3D(0, 0, -1, 0))
    t = cube.intersect(ray)
    assert t is not None
    hit = Vector3D(0, 0, 5 - t, 1)
    n = cube.get_normal_at_intersection(hit)
    assert abs(n.x) < 1e-6 and abs(n.y) < 1e-6
    assert abs(abs(n.z) - 1.0) < 1e-6


def test_empty_mesh_returns_none():
    from core.objects.mesh import Mesh
    from core.ray import Ray
    mesh = Mesh(MAT, name="Empty")
    mesh.build_bvh()  # no triangles -> _bvh stays None
    ray = Ray(Vector3D(0, 0, 5, 1), Vector3D(0, 0, -1, 0))
    assert mesh.intersect(ray) is None


def test_single_triangle_mesh():
    from core.objects.mesh import Mesh
    from core.bvh import BVHNode
    from core.ray import Ray
    mesh = Mesh(MAT, name="OneTri")
    mesh.add_triangle(Vector3D(-1, -1, -3, 1), Vector3D(1, -1, -3, 1),
                      Vector3D(0, 1, -3, 1))
    mesh.build_bvh()
    assert not isinstance(mesh._bvh, BVHNode)
    ray = Ray(Vector3D(0, 0, 5, 1), Vector3D(0, 0, -1, 0))
    t = mesh.intersect(ray)
    assert t is not None and abs(t - 8.0) < 1e-6


def test_create_cube_builds_bvh():
    from utils.obj_loader import OBJLoader
    from core.bvh import BVHNode
    cube = OBJLoader.create_cube(MAT, Vector3D(0, 0, -3, 1), 2.0)
    assert isinstance(cube._bvh, BVHNode)


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"\n{len(fns)} tests passed")


if __name__ == "__main__":
    _run_all()
