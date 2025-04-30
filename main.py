import numpy as np 
from PIL import Image
import multiprocessing

from core.objects.sphere import Sphere
from core.objects.plane import Plane
from core.camera import Camera
from core.light import Light
from core.ray import Ray
from utils.vector import Vector3D
from utils.shading import phong_shading, get_reflection_direction, get_refraction_direction

# Maximum depth limit for recursion
MAX_DEPTH = 5
# Anti-aliasing samples
AA_SAMPLES = 2

def trace_ray(ray, objects, light, depth=0):
    """
    The function that traces the ray and returns the color value.
    """
    if depth >= MAX_DEPTH:
        return (0, 0, 0)
    
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
        
        local_color = phong_shading(hit_point, normal, view_dir, light, closest_obj.material, in_shadow)
        
        color = np.array(local_color, dtype=np.float64)
        
        material = closest_obj.material
        
        if material.get("reflectivity", 0) > 0:
            reflection_dir = get_reflection_direction(ray.direction, normal)
            reflection_origin = hit_point + normal * 0.001  # Reflection acne bias
            reflection_ray = Ray(reflection_origin, reflection_dir)
            
            reflection_color = trace_ray(reflection_ray, objects, light, depth + 1)
            
            color = color * (1 - material["reflectivity"]) + np.array(reflection_color) * material["reflectivity"]
        
        if material.get("transparency", 0) > 0:
            # Determining if the ray is inside or outside the object
            is_inside = ray.direction.dot(normal) > 0
            refr_normal = -normal if is_inside else normal
            
            n1 = 1.0
            n2 = material.get("refractive_index", 1.5)
            
            # Change 'n1' and 'n2' if the ray is inside the object
            if is_inside:
                n1, n2 = n2, n1
            
            refraction_dir = get_refraction_direction(ray.direction, refr_normal, n1, n2)
            
            # If not total internal reflection
            if refraction_dir:
                refraction_origin = hit_point - refr_normal * 0.001  # Refraction acne bias
                refraction_ray = Ray(refraction_origin, refraction_dir)
                
                refraction_color = trace_ray(refraction_ray, objects, light, depth + 1)
                
                fresnel = 0.1 + 0.9 * pow(1.0 - abs(view_dir.dot(normal)), 5.0)
                
                color = color * (1 - material["transparency"] * (1 - fresnel)) + \
                        np.array(refraction_color) * material["transparency"] * (1 - fresnel)
        
        return np.clip(color, 0, 255).astype(np.uint8)

    return (0, 0, 0)

def render_pixel(x, y, width, height, camera: Camera, objects, light):
    u = (x / width) * 2 - 1
    v = 1 - (y / height) * 2

    ray = camera.get_ray(u, v)
    return trace_ray(ray, objects, light)

def render_pixel_with_aa(x, y, width, height, camera: Camera, objects, light):
    """
    Pixel rendering with anti-aliasing
    Calculates the average color by sending 4 rays for each pixel
    """
    color_sum = np.zeros(3, dtype=np.float64)
    
    # Loop through 2x2 grid
    for sx in range(AA_SAMPLES):
        for sy in range(AA_SAMPLES):
            # Offset in the sub-pixel
            offset_x = (sx + 0.5) / AA_SAMPLES
            offset_y = (sy + 0.5) / AA_SAMPLES
            
            # Pixel coordinate in NDC space (-1 to 1)
            u = ((x + offset_x) / width) * 2 - 1
            v = 1 - ((y + offset_y) / height) * 2
            
            ray = camera.get_ray(u, v)
            sample_color = trace_ray(ray, objects, light)
            color_sum += sample_color
    
    return (color_sum / (AA_SAMPLES * AA_SAMPLES)).astype(np.uint8)

def render_scene(width, height, camera, objects, light):
    img = np.zeros((height, width, 3), dtype=np.uint8)
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    args = [(x, y, width, height, camera, objects, light) for y in range(height) for x in range(width)]
    results = pool.starmap(render_pixel_with_aa, args)
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
    
    objects = [sphere1, sphere2, plane]
    
    light = Light(Vector3D(5, 8, -2, 1), (1.0, 1.0, 1.0))

    render_scene(800, 600, camera, objects, light)