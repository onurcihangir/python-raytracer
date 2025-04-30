import numpy as np
from core.ray import Ray
import config
from utils.shading import phong_shading, get_reflection_direction, get_refraction_direction

def trace_ray(ray, objects, light, depth=0):
    """
    The function that traces the ray and returns the color value.
    """
    
    if depth >= config.MAX_DEPTH:
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

def render_pixel_with_aa(x, y, width, height, camera, objects, light):
    """
    Pixel rendering with anti-aliasing
    Calculates the average color by sending 4 rays for each pixel
    """
    color_sum = np.zeros(3, dtype=np.float64)
    
    # Loop through 2x2 grid
    for sx in range(config.AA_SAMPLES):
        for sy in range(config.AA_SAMPLES):
            # Offset in the sub-pixel
            offset_x = (sx + 0.5) / config.AA_SAMPLES
            offset_y = (sy + 0.5) / config.AA_SAMPLES
            
            # Pixel coordinate in NDC space (-1 to 1)
            u = ((x + offset_x) / width) * 2 - 1
            v = 1 - ((y + offset_y) / height) * 2
            
            ray = camera.get_ray(u, v)
            sample_color = trace_ray(ray, objects, light)
            color_sum += sample_color
    
    return (color_sum / (config.AA_SAMPLES * config.AA_SAMPLES)).astype(np.uint8)
