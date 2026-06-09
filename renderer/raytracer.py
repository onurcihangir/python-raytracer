import numpy as np
from core.ray import Ray
import config
from utils.shading import diffuse_specular, get_reflection_direction, get_refraction_direction
from utils.vector import Vector3D
from core.bvh import BVHNode

def trace_ray(ray, objects, lights, depth=0):
    if depth >= config.MAX_DEPTH:
        return (0, 0, 0)

    closest_hit = None
    closest_obj = None

    for obj in objects:
        hit, leaf = obj.intersect_full(ray)
        if hit is not None and (closest_hit is None or hit < closest_hit):
            closest_hit = hit
            closest_obj = leaf

    if closest_hit is not None:
        hit_point = ray.origin + ray.direction * closest_hit

        # Get normal based on object type
        if hasattr(closest_obj, 'center'):
            normal = (hit_point - closest_obj.center).normalize()
        elif hasattr(closest_obj, 'normal'):
            normal = closest_obj.normal
        elif hasattr(closest_obj, 'get_normal_at_intersection'):
            normal = closest_obj.get_normal_at_intersection(hit_point)
        else:
            normal = Vector3D(0, 1, 0, 0)

        view_dir = -ray.direction
        material = closest_obj.material

        # Ambient once (0-1 scale)
        local = np.array(material["ambient"], dtype=np.float64)

        # Each light: own shadow test, then diffuse+specular contribution
        for light in lights:
            shadow_origin = hit_point + normal * 0.001  # Shadow acne bias
            light_dir = (light.position - hit_point).normalize()
            shadow_ray = Ray(shadow_origin, light_dir)
            light_distance = (light.position - hit_point).length()

            in_shadow = False
            for obj in objects:
                shadow_hit, _ = obj.intersect_full(shadow_ray)
                if shadow_hit is not None and shadow_hit < light_distance:
                    in_shadow = True
                    break

            if not in_shadow:
                local += diffuse_specular(hit_point, normal, view_dir, light, material)

        color = np.clip(local * 255, 0, 255).astype(np.float64)

        if material.get("reflectivity", 0) > 0:
            reflection_dir = get_reflection_direction(ray.direction, normal)
            reflection_origin = hit_point + normal * 0.001  # Reflection acne bias
            reflection_ray = Ray(reflection_origin, reflection_dir)

            reflection_color = trace_ray(reflection_ray, objects, lights, depth + 1)

            color = color * (1 - material["reflectivity"]) + np.array(reflection_color) * material["reflectivity"]

        if material.get("transparency", 0) > 0:
            is_inside = ray.direction.dot(normal) > 0
            refr_normal = -normal if is_inside else normal

            n1 = 1.0
            n2 = material.get("refractive_index", 1.5)
            if is_inside:
                n1, n2 = n2, n1

            refraction_dir = get_refraction_direction(ray.direction, refr_normal, n1, n2)

            if refraction_dir:
                refraction_origin = hit_point - refr_normal * 0.001  # Refraction acne bias
                refraction_ray = Ray(refraction_origin, refraction_dir)

                refraction_color = trace_ray(refraction_ray, objects, lights, depth + 1)

                fresnel = 0.1 + 0.9 * pow(1.0 - abs(view_dir.dot(normal)), 5.0)

                color = color * (1 - material["transparency"] * (1 - fresnel)) + \
                        np.array(refraction_color) * material["transparency"] * (1 - fresnel)

        return np.clip(color, 0, 255).astype(np.uint8)

    return (0, 0, 0)

def render_pixel_with_aa(x, y, width, height, camera, objects, lights):
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
            sample_color = trace_ray(ray, objects, lights)
            color_sum += sample_color

    return (color_sum / (config.AA_SAMPLES * config.AA_SAMPLES)).astype(np.uint8)


# --- Multiprocessing worker support -------------------------------------------
# The scene (camera, objects, light) is the same for every pixel. Passing it in
# each task tuple re-pickles the whole scene (including large mesh BVH trees) per
# pixel, which dominates render time. Instead the pool initializer ships it once
# per worker process and stores it in this module-level context; per-pixel tasks
# then carry only the (x, y) integer coordinates.
_worker_ctx = {}


def init_worker(width, height, camera, objects, lights):
    """Pool initializer: store the immutable scene once per worker process."""
    _worker_ctx["width"] = width
    _worker_ctx["height"] = height
    _worker_ctx["camera"] = camera
    _worker_ctx["objects"] = objects
    _worker_ctx["lights"] = lights


def render_pixel_coord(x, y):
    """Render one pixel using the worker's stored scene context."""
    c = _worker_ctx
    return render_pixel_with_aa(
        x, y, c["width"], c["height"], c["camera"], c["objects"], c["lights"])
