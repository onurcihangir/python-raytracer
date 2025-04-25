import numpy as np 
from PIL import Image
import multiprocessing

from core.objects.sphere import Sphere
from core.objects.plane import Plane
from core.camera import Camera
from core.light import Light
from core.ray import Ray
from utils.vector import Vector3D
from utils.shading import phong_shading

def render_pixel(x, y, width, height, camera: Camera, objects, light: Light):
    u = (x / width) * 2 - 1
    v = 1 - (y / height) * 2

    ray = camera.get_ray(u, v)
    
    closest_hit = None
    closest_obj = None
    
    for obj in objects:
        hit = obj.intersect(ray)
        if hit and (closest_hit is None or hit < closest_hit):
            closest_hit = hit
            closest_obj = obj
    
    if closest_hit:
        hit_point = ray.origin + ray.direction * closest_hit

        if hasattr(closest_obj, 'center'):
            normal = (hit_point - closest_obj.center).normalize()
        elif hasattr(closest_obj, 'normal'):
            normal = closest_obj.normal

        view_dir = -ray.direction

        shadow_origin = hit_point + normal * 0.001  # Shadow acne bias
        light_dir = (light.position - hit_point).normalize()
        shadow_ray = Ray(shadow_origin, light_dir)
        
        light_distance = (light.position - hit_point).length()
        
        in_shadow = False
        for obj in objects:
            shadow_hit = obj.intersect(shadow_ray)
            if shadow_hit and shadow_hit < light_distance:
                in_shadow = True
                break
        
        color = phong_shading(hit_point, normal, view_dir, light, closest_obj.material, in_shadow)
        return tuple(color)  # RGB (0-255)

    return (0, 0, 0)

def render_scene(width, height, camera, objects, light):
    img = np.zeros((height, width, 3), dtype=np.uint8)
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    args = [(x, y, width, height, camera, objects, light) for y in range(height) for x in range(width)]
    results = pool.starmap(render_pixel, args)
    pool.close()
    pool.join()

    img = np.array(results, dtype=np.uint8).reshape((height, width, 3))

    image = Image.fromarray(img)
    image.save("output.png")

if __name__ == '__main__':
    # Camera Setup
    camera_position = Vector3D(0, 0, 0, 1)
    look_at = Vector3D(0, 0, -1, 0)
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
        "shininess": 32
    }
    sphere1 = Sphere(sphere1_center, sphere1_radius, sphere1_material)
    
    sphere2_center = Vector3D(2, 1, -6, 1)
    sphere2_radius = 1.2
    sphere2_material = {
        "ambient": (0.1, 0.1, 0.1),
        "diffuse": (0.0, 0.7, 0.0),
        "specular": (1.0, 1.0, 1.0),
        "shininess": 64
    }
    sphere2 = Sphere(sphere2_center, sphere2_radius, sphere2_material)
    
    plane_point = Vector3D(0, -1, 0, 1)
    plane_normal = Vector3D(0, 1, 0, 0)
    plane_material = {
        "ambient": (0.1, 0.1, 0.1),
        "diffuse": (0.5, 0.5, 0.5),
        "specular": (0.3, 0.3, 0.3),
        "shininess": 8
    }
    plane = Plane(plane_point, plane_normal, plane_material)
    
    objects = [sphere1, sphere2, plane]
    
    light = Light(Vector3D(5, 8, -2, 1), (1.0, 1.0, 1.0))

    render_scene(800, 600, camera, objects, light)
