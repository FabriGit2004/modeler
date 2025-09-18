import os
import trimesh

def show_3d_model(path):
    try:
        mesh = trimesh.load(path)
        mesh.show()
    except Exception as e:
        print(f"Error showing model: {e}")

def list_models(folder):
    files = [f for f in os.listdir(folder) if f.endswith(".stl")]
    if not files:
        print("No models available.")
        return []
    
    print("\nAvailable models:")
    for idx, file in enumerate(files):
        print(f"{idx + 1}. {file}")
    return files
