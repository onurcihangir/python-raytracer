from utils.vector import Vector3D
from core.objects.sphere import Sphere
from core.objects.plane import Plane
from utils.obj_loader import OBJLoader
from core.camera import Camera
from core.light import Light
from core.bvh import BVHNode


def make_material(diffuse, reflectivity):
    """Build a full material dict from a diffuse RGB tuple (0-1) and reflectivity (0-1)."""
    return {
        "ambient": (0.1, 0.1, 0.1),
        "diffuse": diffuse,
        "specular": (1.0, 1.0, 1.0),
        "shininess": 32,
        "reflectivity": reflectivity,
        "transparency": 0.0,
        "refractive_index": 1.0,
    }


def build_object(spec):
    """Map a single object-spec dict to a scene object.

    Supported types: sphere, cube, tetra, plane, obj.
    Raises ValueError on unknown type; propagates OBJLoader errors for obj.
    """
    t = spec["type"]
    material = spec["material"]

    if t == "sphere":
        center = Vector3D(*spec["position"], 1)
        return Sphere(center, spec["radius"], material)

    if t == "plane":
        point = Vector3D(*spec["point"], 1)
        normal = Vector3D(*spec["normal"], 0)
        return Plane(point, normal, material)

    if t == "cube":
        center = Vector3D(*spec["center"], 1)
        return OBJLoader.create_cube(material, center, spec["size"])

    if t == "tetra":
        center = Vector3D(*spec["center"], 1)
        return OBJLoader.create_tetrahedron(material, center, spec["size"])

    if t == "obj":
        position = Vector3D(*spec["position"], 1)
        return OBJLoader.load(spec["path"], material, spec["scale"], position)

    raise ValueError(f"Unknown object type: {t}")


def build_scene(width, height, object_specs, light_pos):
    """Build (camera, objects, light) from object specs and global settings.

    Finite objects (sphere/cube/tetra/obj) go into a BVH; planes are kept
    separate (infinite, excluded from the BVH).
    """
    camera_position = Vector3D(0, 3, 8, 1)
    look_at = Vector3D(0, 1, 0, 0)
    up = Vector3D(0, 1, 0, 0)
    fov = 45
    aspect_ratio = width / height
    camera = Camera(camera_position, look_at, up, fov, aspect_ratio)

    finite_objects = []
    planes = []
    for spec in object_specs:
        obj = build_object(spec)
        if isinstance(obj, Plane):
            planes.append(obj)
        else:
            finite_objects.append(obj)

    objects = []
    if finite_objects:
        bvh = BVHNode.build(finite_objects)
        objects.append(bvh)
    objects.extend(planes)

    light = Light(Vector3D(light_pos[0], light_pos[1], light_pos[2], 1),
                  (1.0, 1.0, 1.0))

    return camera, objects, light
