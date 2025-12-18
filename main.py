import sys
from core.objects.sphere import Sphere
from core.objects.plane import Plane
from core.camera import Camera
from core.light import Light
from utils.vector import Vector3D
from renderer.ui.gui import start_gui
from utils.obj_loader import OBJLoader

def main():
    # Camera Setup
    camera_position = Vector3D(0, 3, 8, 1)
    look_at = Vector3D(0, 1, 0, 0)
    up = Vector3D(0, 1, 0, 0)
    fov = 45
    aspect_ratio = 800 / 600

    camera = Camera(camera_position, look_at, up, fov, aspect_ratio)
    
    sphere1_center = Vector3D(0, 1, -5, 1)
    sphere1_radius = 1.0
    sphere1_material = {
        "ambient": (0.1, 0.1, 0.1),
        "diffuse": (0.7, 0.0, 0.0),
        "specular": (1.0, 1.0, 1.0),
        "shininess": 32,
        "reflectivity": 0.5,
        "transparency": 0.0,
        "refractive_index": 1.0
    }
    sphere1 = Sphere(sphere1_center, sphere1_radius, sphere1_material)
    
    sphere2_center = Vector3D(2, 1, -6, 1)
    sphere2_radius = 1.2
    sphere2_material = {
        "ambient": (0.1, 0.1, 0.1),
        "diffuse": (0.0, 0.7, 0.0),
        "specular": (1.0, 1.0, 1.0),
        "shininess": 64,
        "reflectivity": 0.2,
        "transparency": 0.8,
        "refractive_index": 1.5
    }
    sphere2 = Sphere(sphere2_center, sphere2_radius, sphere2_material)
    
    plane_point = Vector3D(0, -1, 0, 1)
    plane_normal = Vector3D(0, 1, 0, 0)
    plane_material = {
        "ambient": (0.1, 0.1, 0.1),
        "diffuse": (0.5, 0.5, 0.5),
        "specular": (0.3, 0.3, 0.3),
        "shininess": 8,
        "reflectivity": 0.3,
        "transparency": 0.0,
        "refractive_index": 1.0
    }
    plane = Plane(plane_point, plane_normal, plane_material)

    bunny = OBJLoader.load(
        filepath='models/bunny.obj',
        material={
            "ambient": (0.1, 0.1, 0.1),
            "diffuse": (0.8, 0.7, 0.6),
            "specular": (0.5, 0.5, 0.5),
            "shininess": 16,
            "reflectivity": 0.1,
            "transparency": 0.0,
            "refractive_index": 1.0
        },
        scale=30.0,
        position=Vector3D(0, 0, -2, 1)
    )

    bbox_min, bbox_max = bunny.get_bounding_box()
    print(f"Bunny bounds: {bbox_min} to {bbox_max}")


    objects = [plane, bunny]

    light = Light(Vector3D(3, 5, 2, 1), (1.0, 1.0, 1.0))

    start_gui(400, 300, camera, objects, light)

if __name__ == '__main__':
    main()