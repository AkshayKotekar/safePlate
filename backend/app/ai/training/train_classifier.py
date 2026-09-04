"""Trains a YOLO image classifier (e.g. the fresh/rotten produce dataset).
Separate from train.py because classification uses a different task, base
model, and evaluation metrics (top-1/top-5 accuracy, not box mAP) than object
detection.

Requires requirements-ml.txt. Run:

    python -m app.ai.training.train_classifier \\
        --data ../datasets/prepared/freshness_classifier --name freshness_classifier

`--data` points at the dataset ROOT (containing train/ and val/ subfolders of
class-named directories) — unlike train.py, there is no data.yaml for
classification tasks.
"""
import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

MODELS_ROOT = Path(__file__).resolve().parents[4] / "models"


def parse_args():
    p = argparse.ArgumentParser(description="Train a YOLO classifier for SafePlate")
    p.add_argument("--data", required=True, help="Path to dataset root (contains train/, val/)")
    p.add_argument("--name", required=True, help="Model name, e.g. freshness_classifier")
    p.add_argument("--base-model", default="yolov8n-cls.pt", help="Base weights to fine-tune from")
    p.add_argument("--epochs", type=int, default=25)
    p.add_argument("--batch", type=int, default=32)
    p.add_argument("--imgsz", type=int, default=224)
    p.add_argument("--lr0", type=float, default=0.01)
    p.add_argument("--optimizer", default="auto")
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--device", default=None, help="'0' for first GPU, 'cpu' to force CPU, None = auto-detect")
    return p.parse_args()


def _next_version(model_dir: Path) -> str:
    existing = [int(p.name[1:]) for p in model_dir.glob("v*") if p.name[1:].isdigit()] if model_dir.exists() else []
    return f"v{max(existing, default=0) + 1}"


def main():
    from ultralytics import YOLO

    args = parse_args()
    data_path = Path(args.data)
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset root not found: {data_path}")

    model = YOLO(args.base_model)
    device = args.device
    if device is None:
        import torch
        device = "0" if torch.cuda.is_available() else "cpu"
        if device == "cpu":
            print("WARNING: No GPU detected. Training on CPU will be significantly slower.")

    results = model.train(
        data=str(data_path.resolve()),
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        lr0=args.lr0,
        optimizer=args.optimizer,
        workers=args.workers,
        device=device,
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
        "task": "classify",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "dataset_reference": str(data_path),
        "base_model": args.base_model,
        "classes": list(model.names.values()),
        "training_params": {
            "epochs": args.epochs, "batch": args.batch, "imgsz": args.imgsz,
            "lr0": args.lr0, "optimizer": args.optimizer, "device": device,
        },
        "evaluation_metrics": {
            "top1_accuracy": float(metrics.top1),
            "top5_accuracy": float(metrics.top5),
        },
    }
    (version_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    print(f"\nTraining complete. Model saved to: {version_dir}")
    print(f"Evaluation: {json.dumps(metadata['evaluation_metrics'], indent=2)}")


if __name__ == "__main__":
    main()
