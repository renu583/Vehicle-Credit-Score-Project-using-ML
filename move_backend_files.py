import os
import shutil

source_folder = "backend"
destination_folder = "."

def move_all_files(src, dst):
    for root, dirs, files in os.walk(src):
        for file in files:
            src_path = os.path.join(root, file)
            relative_path = os.path.relpath(src_path, src)
            dst_path = os.path.join(dst, relative_path)

            dst_dir = os.path.dirname(dst_path)
            os.makedirs(dst_dir, exist_ok=True)

            if not os.path.exists(dst_path):
                print(f"Moving: {relative_path}")
                shutil.move(src_path, dst_path)
            else:
                print(f"Skipped (already exists): {relative_path}")

    try:
        shutil.rmtree(src)
        print(f"\n✅ Deleted '{src}' folder after moving.")
    except Exception as e:
        print(f"\n❌ Failed to delete '{src}': {e}")

if __name__ == "__main__":
    move_all_files(source_folder, destination_folder)
