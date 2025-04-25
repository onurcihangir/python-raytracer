import numpy as np 
from PIL import Image
import multiprocessing

from core.objects.sphere import Sphere
from core.objects.plane import Plane
from core.camera import Camera
from core.light import Light
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

        color = phong_shading(hit_point, normal, view_dir, light, closest_obj.material)
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


    # 📌 Örnek Kamera ve Küre Konumları
    camera_position = Vector3D(0, 0, 0, 1)   # Kamera (Origin)
    look_at = Vector3D(0, 0, -1, 0)          # Negatif Z yönüne bakıyor
    up = Vector3D(0, 1, 0, 0)                # Yukarı yön
    sphere_center = Vector3D(0, 0, -5, 1)     # Küre Z=-5'te
    sphere_radius = 1.0
    fov = 45                               # 45 derece görüş açısı
    aspect_ratio = 800 / 600               # 800x600 çözünürlük

    # Kamera ve küreyi oluştur
    sphere_material = {
        "ambient": (0.1, 0.1, 0.1),   # Çevresel ışık katkısı
        "diffuse": (0.7, 0.0, 0.0),   # Dağınık ışık (Kırmızı)
        "specular": (1.0, 1.0, 1.0),  # Parlak beyaz yansıma
        "shininess": 32               # Parlaklık katsayısı
    }

    sphere2_center = Vector3D(-1.25, 0, -4, 1)
    sphere2_radius = 0.75
    sphere2_material = {
        "ambient": (0.1, 0.1, 0.1),
        "diffuse": (0.0, 0.7, 0.0),
        "specular": (1.0, 1.0, 1.0),
        "shininess": 32
    }
    sphere2 = Sphere(sphere2_center, sphere2_radius, sphere2_material)
    camera = Camera(camera_position, look_at, up, fov, aspect_ratio)
    sphere = Sphere(sphere_center, sphere_radius, sphere_material)
    light = Light(Vector3D(5, 5, -3, 1), (1.0, 1.0, 1.0))

    plane_point = Vector3D(0, -1, 0, 1)
    plane_normal = Vector3D(0, 1, 0, 0)
    plane_material = {
        "ambient": (0.1, 0.1, 0.1),
        "diffuse": (0.4, 0.4, 0.4),
        "specular": (0.5, 0.5, 0.5),
        "shininess": 16
    }
    plane = Plane(plane_point, plane_normal, plane_material)

    objects = [sphere, sphere2, plane]

    render_scene(800, 600, camera, objects, light)
