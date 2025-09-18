import numpy as np
from PIL import Image
import trimesh

def image_to_3d_relief(image_path, output_model="model.stl"):
    img = Image.open(image_path).convert("L")  # grayscale
    img = img.resize((100, 100))  # reduce size for performance
    data = np.array(img)

    height_map = data / 255.0 * 10.0  # height from 0 to 10 units

    vertices = []
    faces = []

    for y in range(height_map.shape[0] - 1):
        for x in range(height_map.shape[1] - 1):
            z1 = height_map[y, x]
            z2 = height_map[y, x+1]
            z3 = height_map[y+1, x]
            z4 = height_map[y+1, x+1]

            i = len(vertices)
            vertices += [
                [x, y, z1],
                [x+1, y, z2],
                [x, y+1, z3],
                [x+1, y+1, z4]
            ]
            faces += [
                [i, i+1, i+2],
                [i+1, i+3, i+2]
            ]

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    mesh.export(output_model)
    print(f"3D model exported: {output_model}")
