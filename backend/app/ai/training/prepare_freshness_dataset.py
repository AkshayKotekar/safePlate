"""One-time, non-destructive prep of the fresh/rotten produce dataset into a
YOLO-classification-ready layout (spec §9/§23: 'visible spoilage detection',
not a claim of detecting bacteria/pathogens — this only classifies visible
produce condition).

Source: datasets/extracted/fresh_rotten_produce/Unified_Dataset/<produce>/<fresh|rotten>/*
  14 produce types x 2 conditions = 28 classes, ~29k images total.

Classes are named "<produce>_<condition>" (e.g. "apple_fresh", "apple_rotten")
rather than collapsed to a generic fresh/rotten binary — this preserves the
produce-type signal the dataset actually provides. A generic "is this rotten"
check can just group any class ending in "_rotten" at inference time; that
grouping lives in application code, not in retrained classes.

Output: datasets/prepared/freshness_classifier/{train,val}/<produce>_<condition>/*
  (YOLO classification format — Ultralytics infers classes from folder names,
  no data.yaml needed)

Usage:
    python -m app.ai.training.prepare_freshness_dataset
"""
import random
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
DATASETS_ROOT = REPO_ROOT / "datasets"

SRC = DATASETS_ROOT / "extracted" / "fresh_rotten_produce" / "Unified_Dataset"
OUTPUT_ROOT = DATASETS_ROOT / "prepared" / "freshness_classifier"

VAL_FRACTION = 0.15
SEED = 42
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def main():
    if OUTPUT_ROOT.exists():
        print(f"Removing previous prepared dataset at {OUTPUT_ROOT} (source is untouched)...")
        shutil.rmtree(OUTPUT_ROOT)

    rng = random.Random(SEED)
    stats = {}

    for produce_dir in sorted(SRC.iterdir()):
        if not produce_dir.is_dir():
            continue
        for condition_dir in sorted(produce_dir.iterdir()):
            if not condition_dir.is_dir() or condition_dir.name.lower() not in ("fresh", "rotten"):
                continue
            class_name = f"{produce_dir.name}_{condition_dir.name.lower()}"
            images = [p for p in condition_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS]
            rng.shuffle(images)

            val_count = max(1, int(len(images) * VAL_FRACTION))
            val_images, train_images = images[:val_count], images[val_count:]

            for split_name, split_images in (("train", train_images), ("val", val_images)):
                out_dir = OUTPUT_ROOT / split_name / class_name
                out_dir.mkdir(parents=True, exist_ok=True)
                for img_path in split_images:
                    shutil.copy(img_path, out_dir / img_path.name)

            stats[class_name] = (len(train_images), len(val_images))

    print(f"\n=== Prepared freshness_classifier dataset ===")
    total_train = total_val = 0
    for class_name, (n_train, n_val) in stats.items():
        print(f"  {class_name}: {n_train} train, {n_val} val")
        total_train += n_train
        total_val += n_val
    print(f"\nTotal: {total_train} train, {total_val} val, {len(stats)} classes")
    print(f"Written to: {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
