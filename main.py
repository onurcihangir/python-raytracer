import numpy as np 
from PIL import Image
from core.camera import Camera
from core.objects.sphere import Sphere
import multiprocessing

from utils.vector import Vector3D

def render_pixel(x, y, width, height, camera: Camera, sphere: Sphere):
    u = (x / width) * 2 - 1
    v = 1 - (y / height) * 2

    ray = camera.get_ray(u, v)
    hit = sphere.intersect(ray)
    if hit:
        return (255, 0, 0)

    return (0, 0, 0)

def render_scene(width, height, camera, sphere):
    img = np.zeros((height, width, 3), dtype=np.uint8)
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    args = [(x, y, width, height, camera, sphere) for y in range(height) for x in range(width)]
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
    camera = Camera(camera_position, look_at, up, fov, aspect_ratio)
    sphere = Sphere(sphere_center, sphere_radius, None)

    render_scene(800, 600, camera, sphere)
