import os
import yaml
import subprocess
import shutil
import sys

RECIPE_DIR = "recipes"
IMAGES_DIR = "images"
BUILD_DIR = "build/workspace"


def run(cmd, cwd=None):
    print(f"\n[CMD] {cmd}")
    subprocess.check_call(cmd, shell=True, cwd=cwd)


def load_recipe(name):
    path = os.path.join(RECIPE_DIR, f"{name}.yaml")

    if not os.path.exists(path):
        print(f"❌ Recipe not found: {path}")
        sys.exit(1)

    with open(path) as f:
        return yaml.safe_load(f)


def clone_source(recipe):
    repo = recipe["upstream"]["repo"]
    version = recipe["version"]

    src_dir = os.path.join(BUILD_DIR, "source")

    if os.path.exists(src_dir):
        shutil.rmtree(src_dir)

    print(f"\n📥 Cloning {repo} (version {version})...")
    run(f"git clone {repo} source", cwd=BUILD_DIR)

    print(f"🔀 Checking out tag {version}...")
    run(f"git checkout {recipe['upstream'].get('tagPrefix','')}{version}", cwd=src_dir)

    return src_dir


def apply_patches(image_path, source_dir):
    patches_dir = os.path.join(image_path, "patches")

    if not os.path.isdir(patches_dir):
        return

    patches = [p for p in os.listdir(patches_dir) if p.endswith(".patch")]

    if not patches:
        return

    print("\n🩹 Applying patches...")
    for patch in patches:
        patch_path = os.path.join(patches_dir, patch)
        run(f"git apply {patch_path}", cwd=source_dir)


def run_build_steps(recipe, source_dir):
    print("\n🔨 Running build steps...")

    for step in recipe["build"]["steps"]:
        run(step, cwd=source_dir)


def docker_build(image_name, version, image_path):
    print("\n🐳 Building Docker image...")

    full_tag = f"helmhub/{image_name}:{version}"

    run(f"docker build -t {full_tag} .", cwd=image_path)

    print(f"\n✅ Built image: {full_tag}")
    return full_tag


def prepare_workspace():
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    os.makedirs(BUILD_DIR)


def build(image_name):
    print(f"\n🚀 Building package: {image_name}")

    recipe = load_recipe(image_name)
    image_path = os.path.join(IMAGES_DIR, image_name)

    prepare_workspace()

    source_dir = clone_source(recipe)
    apply_patches(image_path, source_dir)
    run_build_steps(recipe, source_dir)

    # Copy source into Docker build context
    target_src = os.path.join(image_path, "source")
    if os.path.exists(target_src):
        shutil.rmtree(target_src)
    shutil.copytree(source_dir, target_src)

    docker_build(image_name, recipe["version"], image_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python build.py <image>")
        sys.exit(1)

    build(sys.argv[1])