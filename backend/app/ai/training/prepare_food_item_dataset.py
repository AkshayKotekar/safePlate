"""One-time, non-destructive prep of the food-waste-test dataset into a
YOLO-detection-ready layout for a fine-grained food-item detector (apple core,
egg shells, chicken bone, etc — spec §7/§31: identifies waste composition, is
NOT a pest or spoilage-severity detector).

Source: datasets/extracted/food_waste_test (clean bbox labels, but only
train/test splits — no validation split). This script carves out a validation
split from train (never touching the original extracted files) since
Ultralytics training needs one.

Output: datasets/prepared/food_item_detector/{train,valid,test}/{images,labels}
        + data.yaml

Usage:
    python -m app.ai.training.prepare_food_item_dataset
"""
import random
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
DATASETS_ROOT = REPO_ROOT / "datasets"

SRC = DATASETS_ROOT / "extracted" / "food_waste_test"
OUTPUT_ROOT = DATASETS_ROOT / "prepared" / "food_item_detector"

VAL_FRACTION = 0.15
SEED = 42


def _copy_split(image_paths: list[Path], src_lbl_dir: Path, split_name: str):
    out_img_dir = OUTPUT_ROOT / split_name / "images"
    out_lbl_dir = OUTPUT_ROOT / split_name / "labels"
    out_img_dir.mkdir(parents=True, exist_ok=True)
    out_lbl_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for img_path in image_paths:
        label_path = src_lbl_dir / (img_path.stem + ".txt")
        if not label_path.exists():
            continue
        shutil.copy(img_path, out_img_dir / img_path.name)
        shutil.copy(label_path, out_lbl_dir / label_path.name)
        count += 1
    return count


def main():
    if OUTPUT_ROOT.exists():
        print(f"Removing previous prepared dataset at {OUTPUT_ROOT} (source is untouched)...")
        shutil.rmtree(OUTPUT_ROOT)

    train_images = sorted((SRC / "train" / "images").glob("*.jpg"))
    test_images = sorted((SRC / "test" / "images").glob("*.jpg"))

    random.Random(SEED).shuffle(train_images)
    val_count = max(1, int(len(train_images) * VAL_FRACTION))
    val_images = train_images[:val_count]
    train_images = train_images[val_count:]

    n_train = _copy_split(train_images, SRC / "train" / "labels", "train")
    n_val = _copy_split(val_images, SRC / "train" / "labels", "valid")
    n_test = _copy_split(test_images, SRC / "test" / "labels", "test")

    classes = (SRC / "data.yaml").read_text()
    names_line = [l for l in classes.splitlines() if l.startswith("names:")][0]
    class_list = eval(names_line.split("names:", 1)[1].strip())  # trusted local file, roboflow-generated

    data_yaml = OUTPUT_ROOT / "data.yaml"
    data_yaml.write_text(
        f"path: {OUTPUT_ROOT.resolve().as_posix()}\n"
        "train: train/images\n"
        "val: valid/images\n"
        "test: test/images\n"
        f"nc: {len(class_list)}\n"
        f"names: {class_list}\n"
    )

    print(f"\n=== Prepared food_item_detector dataset ===")
    print(f"  train: {n_train} images")
    print(f"  valid: {n_val} images (carved from train, {VAL_FRACTION:.0%})")
    print(f"  test:  {n_test} images")
    print(f"Classes ({len(class_list)}): {class_list}")
    print(f"Written to: {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
