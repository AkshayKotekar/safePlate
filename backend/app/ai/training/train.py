"""Milestone 19-22: configurable YOLO training + evaluation + versioning.

Requires requirements-ml.txt to be installed. Run:

    python -m app.ai.training.train --data /path/to/dataset/data.yaml --name pest_detector

This does NOT run automatically and does NOT block the rest of the app —
nothing else in SafePlate depends on this having been run.
"""
import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

MODELS_ROOT = Path(__file__).resolve().parents[4] / "models"  # repo_root/models


def parse_args():
    p = argparse.ArgumentParser(description="Train a YOLO model for SafePlate")
    p.add_argument("--data", required=True, help="Path to YOLO data.yaml")
    p.add_argument("--name", required=True, help="Model name, e.g. pest_detector")
    p.add_argument("--base-model", default="yolov8n.pt", help="Base weights to fine-tune from")
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--batch", type=int, default=16)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--lr0", type=float, default=0.01)
    p.add_argument("--optimizer", default="auto")
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--device", default=None, help="'0' for first GPU, 'cpu' to force CPU, None = auto-detect")
    p.add_argument("--augment", action="store_true", default=True)
    p.add_argument("--conf", type=float, default=0.5, help="Confidence threshold used at inference time")
    p.add_argument("--iou", type=float, default=0.5, help="IoU threshold used for NMS at inference time")
    return p.parse_args()


def _next_version(model_dir: Path) -> str:
    existing = [int(p.name[1:]) for p in model_dir.glob("v*") if p.name[1:].isdigit()] if model_dir.exists() else []
    return f"v{max(existing, default=0) + 1}"


def main():
    from ultralytics import YOLO  # local import: only required once you actually train

    args = parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        raise FileNotFoundError(f"data.yaml not found: {data_path}")

    model = YOLO(args.base_model)
    device = args.device
    if device is None:
        import torch
        device = "0" if torch.cuda.is_available() else "cpu"
        if device == "cpu":
            print("WARNING: No GPU detected. Training on CPU will be significantly slower. "
                  "Consider reducing --epochs/--imgsz/--batch for a practical CPU run.")

    results = model.train(
        data=str(data_path),
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        lr0=args.lr0,
        optimizer=args.optimizer,
        workers=args.workers,
        device=device,
        augment=args.augment,
        project=str(MODELS_ROOT / ".runs"),
        name=args.name,
    )

    metrics = model.val()

    model_dir = MODELS_ROOT / args.name
    version = _next_version(model_dir)
    version_dir = model_dir / version
    version_dir.mkdir(parents=True, exist_ok=True)

    best_weights = Path(results.save_dir) / "weights" / "best.pt"
    shutil.copy(best_weights, version_dir / "best.pt")

    metadata = {
        "model_name": args.name,
        "version": version,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "dataset_reference": str(data_path),
        "base_model": args.base_model,
        "classes": list(model.names.values()),
        "training_params": {
            "epochs": args.epochs, "batch": args.batch, "imgsz": args.imgsz,
            "lr0": args.lr0, "optimizer": args.optimizer, "device": device,
            "augment": args.augment,
        },
        "inference_defaults": {"confidence_threshold": args.conf, "iou_threshold": args.iou},
        "evaluation_metrics": {
            "precision": float(metrics.box.mp),
            "recall": float(metrics.box.mr),
            "mAP50": float(metrics.box.map50),
            "mAP50_95": float(metrics.box.map),
        },
    }
    (version_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    print(f"\nTraining complete. Model saved to: {version_dir}")
    print(f"Evaluation: {json.dumps(metadata['evaluation_metrics'], indent=2)}")
    print(f"\nTo activate this model, set in backend/.env:\n  ACTIVE_MODEL_PATH={version_dir / 'best.pt'}")


if __name__ == "__main__":
    main()
