"""One-time, non-destructive merge of the two usable pest-related source
datasets into a single YOLO-detection-ready dataset with a class list that
actually matches SafePlate's target pests (spec: cockroach, rat, mouse, fly,
ant, worm).

Sources (never modified in place):
  datasets/extracted/pest_detection  — 19 classes, only 4 are real food-safety
                                        pests; the rest (Bee, Bird, Scorpion,
                                        Spider, Wasp, ...) are dropped.
  datasets/extracted/rat             — single class "kitchen-rodent", labels
                                        are mostly polygon segmentation and are
                                        converted to bounding boxes here.

IMPORTANT — "rat" and "mouse" are NOT trained as separate classes: the source
dataset never distinguishes them (its own label is the generic
"kitchen-rodent"), and inventing a rat/mouse split the data doesn't support
would violate "do not invent classes" (spec §13). The merged class is honestly
named "rodent" instead. Update SEVERITY_RULES in app/evidence/... equivalents
if you later obtain a dataset that does distinguish them.

Output: datasets/prepared/pest_detector/{train,valid,test}/{images,labels}
        + data.yaml

Usage:
    python -m app.ai.training.prepare_pest_dataset
"""
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]  # backend/app/ai/training -> repo root
DATASETS_ROOT = REPO_ROOT / "datasets"

PEST_DETECTION_SRC = DATASETS_ROOT / "extracted" / "pest_detection"
RAT_SRC = DATASETS_ROOT / "extracted" / "rat"
OUTPUT_ROOT = DATASETS_ROOT / "prepared" / "pest_detector"

# Unified class list — index is the new class id used in every output label.
CLASSES = ["cockroach", "ant", "fly", "worm", "rodent"]

# pest_detection's original class id -> new class name (everything else dropped)
PEST_DETECTION_KEEP = {
    0: "ant",
    6: "cockroach",
    7: "worm",
    9: "fly",
}

# rat dataset's only class -> new class name
RAT_KEEP = {0: "rodent"}

SPLIT_DIRS = ["train", "valid", "test"]


def _iter_split_files(dataset_root: Path, split: str):
    img_dir = dataset_root / split / "images"
    lbl_dir = dataset_root / split / "labels"
    if not img_dir.exists():
        return
    for img_path in sorted(img_dir.iterdir()):
        if img_path.suffix.lower() not in (".jpg", ".jpeg", ".png", ".bmp"):
            continue
        label_path = lbl_dir / (img_path.stem + ".txt")
        yield img_path, label_path


def _polygon_to_bbox(coords: list[float]) -> tuple[float, float, float, float]:
    xs, ys = coords[0::2], coords[1::2]
    x1, x2 = min(xs), max(xs)
    y1, y2 = min(ys), max(ys)
    return (x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1  # cx, cy, w, h


def _remap_pest_detection_label(line: str, class_map: dict[int, str]) -> str | None:
    parts = line.split()
    if len(parts) != 5:
        return None  # pest_detection is clean bbox-format; skip anything unexpected
    old_id = int(parts[0])
    if old_id not in class_map:
        return None
    new_id = CLASSES.index(class_map[old_id])
    return f"{new_id} {' '.join(parts[1:])}"


def _remap_rat_label(line: str, class_map: dict[int, str]) -> str | None:
    parts = line.split()
    if len(parts) < 5:
        return None
    old_id = int(parts[0])
    if old_id not in class_map:
        return None
    new_id = CLASSES.index(class_map[old_id])
    coords = [float(x) for x in parts[1:]]
    if len(parts) == 5:
        cx, cy, w, h = coords
    else:
        cx, cy, w, h = _polygon_to_bbox(coords)
    return f"{new_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}"


def _process_source(dataset_root: Path, prefix: str, class_map: dict[int, str], remap_fn, stats: dict):
    for split in SPLIT_DIRS:
        out_img_dir = OUTPUT_ROOT / split / "images"
        out_lbl_dir = OUTPUT_ROOT / split / "labels"
        out_img_dir.mkdir(parents=True, exist_ok=True)
        out_lbl_dir.mkdir(parents=True, exist_ok=True)

        for img_path, label_path in _iter_split_files(dataset_root, split):
            if not label_path.exists():
                continue
            raw_lines = [l for l in label_path.read_text().splitlines() if l.strip()]
            kept_lines = []
            for line in raw_lines:
                remapped = remap_fn(line, class_map)
                if remapped is not None:
                    kept_lines.append(remapped)

            if not kept_lines:
                continue  # image has no annotations we care about — don't copy it in

            new_stem = f"{prefix}_{img_path.stem}"
            shutil.copy(img_path, out_img_dir / f"{new_stem}{img_path.suffix}")
            (out_lbl_dir / f"{new_stem}.txt").write_text("\n".join(kept_lines) + "\n")

            stats.setdefault(split, {"images": 0, "annotations": 0})
            stats[split]["images"] += 1
            stats[split]["annotations"] += len(kept_lines)


def main():
    if OUTPUT_ROOT.exists():
        print(f"Removing previous prepared dataset at {OUTPUT_ROOT} (source datasets are untouched)...")
        shutil.rmtree(OUTPUT_ROOT)

    stats: dict = {}
    print(f"Processing pest_detection from {PEST_DETECTION_SRC} ...")
    _process_source(PEST_DETECTION_SRC, "pd", PEST_DETECTION_KEEP, _remap_pest_detection_label, stats)
    print(f"Processing rat from {RAT_SRC} ...")
    _process_source(RAT_SRC, "rat", RAT_KEEP, _remap_rat_label, stats)

    data_yaml = OUTPUT_ROOT / "data.yaml"
    # Ultralytics resolves relative train/val/test paths against its own global
    # datasets_dir setting, NOT against this file's location, unless an
    # absolute `path:` is given — so it must be absolute here.
    data_yaml.write_text(
        f"path: {OUTPUT_ROOT.resolve().as_posix()}\n"
        "train: train/images\n"
        "val: valid/images\n"
        "test: test/images\n"
        f"nc: {len(CLASSES)}\n"
        f"names: {CLASSES}\n"
    )

    print("\n=== Prepared pest_detector dataset ===")
    for split, counts in stats.items():
        print(f"  {split}: {counts['images']} images, {counts['annotations']} annotations")
    print(f"Classes: {CLASSES}")
    print(f"Written to: {OUTPUT_ROOT}")
    print(f"\nNext: python -m app.ai.training.dataset_inspector {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
