import numpy as np

def phong_shading(hit_point, normal, view_dir, light, material, in_shadow=False):
    """
    Calculates shading using the Phong lighting model.
    The in_shadow parameter is used to check for shadows.
    """
    ambient = np.array(material["ambient"]) * np.array(light.intensity)
    
    # Eğer gölgedeyse, sadece ambient ışığı döndür
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