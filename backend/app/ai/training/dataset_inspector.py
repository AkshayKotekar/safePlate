"""Milestone 17-18: dataset inspection/validation.

Run this FIRST against any dataset before training. It never modifies the
dataset — only reports on it. Usage:

    python -m app.ai.training.dataset_inspector /path/to/dataset

Expects a YOLO-style layout (customize `_find_split_dirs` if your dataset
differs):

    dataset/
        images/{train,val,test}/*.jpg
        labels/{train,val,test}/*.txt
        data.yaml   (optional — class names)
"""
import sys
from collections import Counter
from pathlib import Path

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}


def _find_split_dirs(dataset_root: Path) -> dict[str, tuple[Path, Path]]:
    """Supports both common YOLO export layouts:
    type-first  (images/train, labels/train  — e.g. hand-built datasets)
    split-first ({split}/images, {split}/labels — Roboflow's default export)
    """
    splits = {}
    for split in ("train", "val", "valid", "test"):
        type_first_img = dataset_root / "images" / split
        type_first_lbl = dataset_root / "labels" / split
        split_first_img = dataset_root / split / "images"
        split_first_lbl = dataset_root / split / "labels"

        if type_first_img.exists():
            splits[split] = (type_first_img, type_first_lbl)
        elif split_first_img.exists():
            splits[split] = (split_first_img, split_first_lbl)
    return splits


def _read_classes(dataset_root: Path) -> list[str] | None:
    yaml_path = dataset_root / "data.yaml"
    if not yaml_path.exists():
        return None
    try:
        import yaml
        data = yaml.safe_load(yaml_path.read_text())
        return data.get("names")
    except Exception:
        return None


def inspect_dataset(dataset_path: str) -> dict:
    root = Path(dataset_path)
    if not root.exists():
        raise FileNotFoundError(f"Dataset path does not exist: {dataset_path}")

    splits = _find_split_dirs(root)
    class_names = _read_classes(root)

    report = {
        "dataset_path": str(root),
        "declared_classes": class_names,
        "splits": {},
        "issues": [],
    }

    class_counter: Counter = Counter()
    total_images = 0
    total_annotations = 0

    for split, (img_dir, lbl_dir) in splits.items():
        images = [p for p in img_dir.rglob("*") if p.suffix.lower() in IMAGE_EXTS]
        missing_labels = []
        invalid_labels = []
        empty_labels = []
        split_annotations = 0
        split_polygon_lines = 0

        for img_path in images:
            label_path = lbl_dir / (img_path.stem + ".txt")
            if not label_path.exists():
                missing_labels.append(img_path.name)
                continue
            lines = [l for l in label_path.read_text().splitlines() if l.strip()]
            if not lines:
                empty_labels.append(img_path.name)
                continue
            for line in lines:
                parts = line.split()
                # 5 fields = bbox (class x y w h). >=7 odd fields = polygon segmentation
                # (class x1 y1 x2 y2 ... xn yn) — a valid YOLO-seg format, not garbage.
                if len(parts) >= 7 and len(parts) % 2 == 1:
                    try:
                        cls_id = int(parts[0])
                        coords = [float(x) for x in parts[1:]]
                        if all(0.0 <= c <= 1.0 for c in coords):
                            class_counter[cls_id] += 1
                            split_annotations += 1
                            split_polygon_lines += 1
                            continue
                    except ValueError:
                        pass
                    invalid_labels.append(f"{img_path.name}: '{line}'")
                    continue
                if len(parts) != 5:
                    invalid_labels.append(f"{img_path.name}: '{line}'")
                    continue
                try:
                    cls_id = int(parts[0])
                    coords = [float(x) for x in parts[1:]]
                    if not all(0.0 <= c <= 1.0 for c in coords):
                        invalid_labels.append(f"{img_path.name}: out-of-range coords '{line}'")
                        continue
                    class_counter[cls_id] += 1
                    split_annotations += 1
                except ValueError:
                    invalid_labels.append(f"{img_path.name}: '{line}'")

        total_images += len(images)
        total_annotations += split_annotations

        report["splits"][split] = {
            "image_count": len(images),
            "annotation_count": split_annotations,
            "polygon_annotation_count": split_polygon_lines,
            "missing_labels": len(missing_labels),
            "empty_labels": len(empty_labels),
            "invalid_label_lines": len(invalid_labels),
            "missing_labels_sample": missing_labels[:10],
            "invalid_labels_sample": invalid_labels[:10],
        }
        if split_polygon_lines:
            report["issues"].append(
                f"[{split}] {split_polygon_lines} annotations are polygon segmentation format, not plain "
                f"bounding boxes — train.py's plain-detection YOLO training needs these converted to boxes first"
            )
        if missing_labels:
            report["issues"].append(f"[{split}] {len(missing_labels)} images have no label file")
        if invalid_labels:
            report["issues"].append(f"[{split}] {len(invalid_labels)} invalid annotation lines")

    report["total_images"] = total_images
    report["total_annotations"] = total_annotations
    report["class_distribution"] = dict(sorted(class_counter.items()))

    if class_names:
        used_ids = set(class_counter.keys())
        declared_ids = set(range(len(class_names)))
        unused = declared_ids - used_ids
        undeclared = used_ids - declared_ids
        if unused:
            report["issues"].append(f"Declared classes with zero annotations: {sorted(unused)}")
        if undeclared:
            report["issues"].append(f"Annotation class IDs not declared in data.yaml: {sorted(undeclared)}")

    if class_counter:
        max_count, min_count = max(class_counter.values()), min(class_counter.values())
        if min_count > 0 and max_count / min_count > 10:
            report["issues"].append(
                f"Significant class imbalance detected (max/min ratio {max_count / min_count:.1f}x)"
            )

    if not splits:
        report["issues"].append("No images/{train,val,test} directories found — check dataset layout.")

    return report


def print_report(report: dict) -> None:
    print(f"\n=== Dataset Inspection Report: {report['dataset_path']} ===")
    print(f"Declared classes: {report['declared_classes']}")
    print(f"Total images: {report['total_images']}, total annotations: {report['total_annotations']}")
    print(f"Class distribution (by class id): {report['class_distribution']}")
    for split, info in report["splits"].items():
        print(f"\n  [{split}] images={info['image_count']} annotations={info['annotation_count']} "
              f"missing_labels={info['missing_labels']} empty_labels={info['empty_labels']} "
              f"invalid_lines={info['invalid_label_lines']}")
    if report["issues"]:
        print("\nIssues found:")
        for issue in report["issues"]:
            print(f"  - {issue}")
    else:
        print("\nNo issues found.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m app.ai.training.dataset_inspector /path/to/dataset")
        sys.exit(1)
    print_report(inspect_dataset(sys.argv[1]))
