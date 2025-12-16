from typing import List, Tuple
from utils.vector import Vector3D
from core.objects.mesh import Mesh


class OBJLoader:
    @staticmethod
    def load(filepath: str, material: dict, scale: float = 1.0, 
             position: Vector3D = None) -> Mesh:
        vertices = []
        normals = []
        faces = []
        
        if position is None:
            position = Vector3D(0, 0, 0, 1)
        
        print(f"Loading OBJ file: {filepath}")
        
        try:
            with open(filepath, 'r') as file:
                for line in file:
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split()
                    if not parts:
                        continue
                    
                    # Parse vertex positions
                    if parts[0] == 'v':
                        x = float(parts[1]) * scale + position.x
                        y = float(parts[2]) * scale + position.y
                        z = float(parts[3]) * scale + position.z
                        vertices.append(Vector3D(x, y, z, 1))
                    
                    # Parse vertex normals
                    elif parts[0] == 'vn':
                        x = float(parts[1])
                        y = float(parts[2])
                        z = float(parts[3])
                        normals.append(Vector3D(x, y, z, 0).normalize())
                    
                    # Parse faces
                    elif parts[0] == 'f':
                        face_vertices = []
                        face_normals = []
                        
                        for i in range(1, len(parts)):
                            # Face format can be: v, v/vt, v/vt/vn, or v//vn
                            indices = parts[i].split('/')
                            
                            # Vertex index (OBJ uses 1-based indexing)
                            v_idx = int(indices[0]) - 1
                            face_vertices.append(v_idx)
                            
                            # Normal index (if present)
                            if len(indices) >= 3 and indices[2]:
                                n_idx = int(indices[2]) - 1
                                face_normals.append(n_idx)
                        
                        # Store face
                        if len(face_vertices) >= 3:
                            # For now, we store vertex indices only
                            # Normal indices are handled separately if available
                            faces.append((face_vertices, face_normals if face_normals else None))
            
            print(f"Loaded: {len(vertices)} vertices, {len(normals)} normals, {len(faces)} faces")
            
            # Create mesh
            mesh = Mesh(material, name=filepath.split('/')[-1])
            
            # Build mesh from loaded data
            for face_data in faces:
                face_vertices, face_normals = face_data
                
                if len(face_vertices) == 3:
                    v0 = vertices[face_vertices[0]]
                    v1 = vertices[face_vertices[1]]
                    v2 = vertices[face_vertices[2]]
                    
                    # Use vertex normals if available
                    if face_normals and len(face_normals) == 3 and normals:
                        n0 = normals[face_normals[0]]
                        n1 = normals[face_normals[1]]
                        n2 = normals[face_normals[2]]
                        mesh.add_triangle(v0, v1, v2, n0, n1, n2)
                    else:
                        mesh.add_triangle(v0, v1, v2)
                
                # Triangulate faces with more than 3 vertices (fan triangulation)
                elif len(face_vertices) > 3:
                    v0 = vertices[face_vertices[0]]
                    for i in range(1, len(face_vertices) - 1):
                        v1 = vertices[face_vertices[i]]
                        v2 = vertices[face_vertices[i + 1]]
                        
                        if face_normals and len(face_normals) > i + 1 and normals:
                            n0 = normals[face_normals[0]]
                            n1 = normals[face_normals[i]]
                            n2 = normals[face_normals[i + 1]]
                            mesh.add_triangle(v0, v1, v2, n0, n1, n2)
                        else:
                            mesh.add_triangle(v0, v1, v2)
            
            print(f"Mesh created with {mesh.get_triangle_count()} triangles")
            return mesh
            
        except FileNotFoundError:
            print(f"Error: File not found: {filepath}")
            raise
        except Exception as e:
            print(f"Error loading OBJ file: {e}")
            raise
    
    @staticmethod
    def create_cube(material: dict, center: Vector3D = None, size: float = 1.0) -> Mesh:
        if center is None:
            center = Vector3D(0, 0, 0, 1)
        
        half = size / 2.0
        
        # Define 8 vertices of a cube
        vertices = [
            Vector3D(center.x - half, center.y - half, center.z - half, 1),  # 0
            Vector3D(center.x + half, center.y - half, center.z - half, 1),  # 1
            Vector3D(center.x + half, center.y + half, center.z - half, 1),  # 2
            Vector3D(center.x - half, center.y + half, center.z - half, 1),  # 3
            Vector3D(center.x - half, center.y - half, center.z + half, 1),  # 4
            Vector3D(center.x + half, center.y - half, center.z + half, 1),  # 5
            Vector3D(center.x + half, center.y + half, center.z + half, 1),  # 6
            Vector3D(center.x - half, center.y + half, center.z + half, 1),  # 7
        ]
        
        # Define 12 triangles (2 per face, 6 faces)
        faces = [
            # Front face
            (0, 1, 2), (0, 2, 3),
            # Back face
            (5, 4, 7), (5, 7, 6),
            # Top face
            (3, 2, 6), (3, 6, 7),
            # Bottom face
            (4, 5, 1), (4, 1, 0),
            # Right face
            (1, 5, 6), (1, 6, 2),
            # Left face
            (4, 0, 3), (4, 3, 7),
        ]
        
        mesh = Mesh(material, name="Cube")
        mesh.from_vertices_and_faces(vertices, faces)
        
        return mesh
    
    @staticmethod
    def create_tetrahedron(material: dict, center: Vector3D = None, size: float = 1.0) -> Mesh:
        if center is None:
            center = Vector3D(0, 0, 0, 1)
        
        # Define 4 vertices of a tetrahedron
        vertices = [
            Vector3D(center.x + size, center.y + size, center.z + size, 1),
            Vector3D(center.x + size, center.y - size, center.z - size, 1),
            Vector3D(center.x - size, center.y + size, center.z - size, 1),
            Vector3D(center.x - size, center.y - size, center.z + size, 1),
        ]
        
        # Define 4 triangular faces
        faces = [
            (0, 1, 2),
            (0, 3, 1),
            (0, 2, 3),
            (1, 3, 2),
        ]
        
        mesh = Mesh(material, name="Tetrahedron")
        mesh.from_vertices_and_faces(vertices, faces)
        
        return mesh