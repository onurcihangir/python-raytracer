import numpy as np

def phong_shading(hit_point, normal, view_dir, light, material, in_shadow=False):
    """
    Calculates shading using the Phong lighting model.
    The in_shadow parameter is used to check for shadows.
    """
    ambient = np.array(material["ambient"]) * np.array(light.intensity)
    
    # if in_shadow, return ambient light
    if in_shadow:
        return np.clip(ambient * 255, 0, 255).astype(np.uint8)
    
    # if not in_shadow, calculate diffuse and specular light

    light_dir = (light.position - hit_point).normalize()
    diff = max(normal.dot(light_dir), 0)
    diffuse = np.array(material["diffuse"]) * diff * np.array(light.intensity)

    reflect_dir = (normal * 2 * normal.dot(light_dir) - light_dir).normalize()
    spec = max(view_dir.dot(reflect_dir), 0) ** material["shininess"]
    specular = np.array(material["specular"]) * spec * np.array(light.intensity)

    color = ambient + diffuse + specular
    return np.clip(color * 255, 0, 255).astype(np.uint8)

def get_reflection_direction(incident, normal):
    """
    Calculates reflection vector: R = I - 2 * (I · N) * N
    """
    return incident - normal * 2 * incident.dot(normal)

def get_refraction_direction(incident, normal, n1, n2):
    """
    Uses Snell's Law to calculate the refraction direction.
    n1: refraction index of medium 1 (usually air, n1 = 1.0)
    n2: refraction index of medium 2
    
    Returns the refraction direction vector or None if total internal reflection occurs.
    """
    n = n1 / n2
    
    cos_i = -normal.dot(incident)
    
    sin2_t = n * n * (1.0 - cos_i * cos_i)
    if sin2_t > 1.0:
        return None  # Total internal reflection
    
    cos_t = (1.0 - sin2_t) ** 0.5
    
    return incident * n + normal * (n * cos_i - cos_t)