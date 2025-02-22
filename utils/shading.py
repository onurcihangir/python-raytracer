import numpy as np

def phong_shading(hit_point, normal, view_dir, light, material):
    """
    Phong aydınlatma modeli ile gölgelendirme hesaplar.
    """
    # Ambient (Çevresel ışık)
    ambient = np.array(material["ambient"]) * np.array(light.intensity)

    # Diffuse (Dağınık ışık)
    light_dir = (light.position - hit_point).normalize()
    diff = max(normal.dot(light_dir), 0)
    diffuse = np.array(material["diffuse"]) * diff * np.array(light.intensity)

    # Specular (Yansıma)
    reflect_dir = (2 * normal.dot(light_dir) * normal - light_dir).normalize()
    spec = max(view_dir.dot(reflect_dir), 0) ** material["shininess"]
    specular = np.array(material["specular"]) * spec * np.array(light.intensity)

    # Son renk
    color = ambient + diffuse + specular
    return np.clip(color * 255, 0, 255).astype(np.uint8)
