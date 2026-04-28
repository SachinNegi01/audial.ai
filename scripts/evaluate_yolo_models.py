from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from ultralytics import YOLO


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_YAML = REPO_ROOT / "training" / "data.yaml"
DEFAULT_MODEL_DIR = REPO_ROOT / "models" / "yolo"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "reports" / "yolo_validation"


def as_float(value: Any) -> float:
    try:
        if hasattr(value, "item"):
            return float(value.item())
        return float(value)
    except Exception:
        return float("nan")


def extract_metrics(results: Any) -> dict[str, float]:
    metrics: dict[str, float] = {
        "precision": float("nan"),
        "recall": float("nan"),
        "map50": float("nan"),
        "map5095": float("nan"),
    }

    results_dict = getattr(results, "results_dict", None)
    if isinstance(results_dict, dict):
        key_map = {
            "precision": ["metrics/precision(B)", "metrics/precision"],
            "recall": ["metrics/recall(B)", "metrics/recall"],
            "map50": ["metrics/mAP50(B)", "metrics/mAP50"],
            "map5095": ["metrics/mAP50-95(B)", "metrics/mAP50-95"],
        }
        for metric_name, keys in key_map.items():
            for key in keys:
                if key in results_dict:
                    metrics[metric_name] = as_float(results_dict[key])
                    break

    box = getattr(results, "box", None)
    if box is not None:
        fallback_map = {
            "precision": ["mp", "precision"],
            "recall": ["mr", "recall"],
            "map50": ["map50"],
            "map5095": ["map"],
        }
        for metric_name, attrs in fallback_map.items():
            if metrics[metric_name] == metrics[metric_name]:
                continue
            for attr in attrs:
                if hasattr(box, attr):
                    metrics[metric_name] = as_float(getattr(box, attr))
                    break

    return metrics


def save_metric_chart(model_name: str, metrics: dict[str, float], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    chart_path = output_dir / f"{model_name}_metrics.png"

    labels = ["Precision", "Recall", "mAP50", "mAP50-95"]
    values = [
        metrics["precision"],
        metrics["recall"],
        metrics["map50"],
        metrics["map5095"],
    ]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values, color=["#2E86AB", "#F18F01", "#C73E1D", "#6A994E"])
    plt.ylim(0, 1)
    plt.title(f"Validation Metrics - {model_name}")
    plt.ylabel("Score")
    plt.grid(axis="y", linestyle="--", alpha=0.3)

    for bar, value in zip(bars, values, strict=False):
        if value == value:
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                min(value + 0.02, 1.0),
                f"{value:.3f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    plt.tight_layout()
    plt.savefig(chart_path, dpi=200)
    plt.close()
    return chart_path


def discover_models(model_dir: Path) -> list[Path]:
    return sorted(model_dir.glob("*.pt"))


def validate_model(model_path: Path, data_yaml: Path, output_dir: Path) -> tuple[dict[str, float], Path]:
    model = YOLO(str(model_path))
    run_name = model_path.stem
    run_dir = output_dir / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    results = model.val(
        data=str(data_yaml),
        split="val",
        imgsz=640,
        plots=True,
        project=str(run_dir),
        name="val",
        exist_ok=True,
        verbose=False,
    )

    metrics = extract_metrics(results)
    chart_path = save_metric_chart(run_name, metrics, run_dir)
    return metrics, chart_path


def write_summary_csv(summary_rows: list[dict[str, Any]], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "model_validation_summary.csv"
    fieldnames = ["model", "precision", "recall", "map50", "map5095", "chart_path"]

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in summary_rows:
            writer.writerow(row)

    return csv_path


def save_comparison_chart(summary_rows: list[dict[str, Any]], output_dir: Path) -> Path:
    comparison_path = output_dir / "model_comparison.png"
    labels = [row["model"] for row in summary_rows]
    map50_values = [as_float(row["map50"]) for row in summary_rows]
    map5095_values = [as_float(row["map5095"]) for row in summary_rows]

    x = range(len(labels))
    width = 0.35

    plt.figure(figsize=(10, 5))
    plt.bar([i - width / 2 for i in x], map50_values, width=width, label="mAP50", color="#2E86AB")
    plt.bar([i + width / 2 for i in x], map5095_values, width=width, label="mAP50-95", color="#6A994E")
    plt.xticks(list(x), labels, rotation=20, ha="right")
    plt.ylim(0, 1)
    plt.ylabel("Score")
    plt.title("YOLO Model Comparison")
    plt.grid(axis="y", linestyle="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(comparison_path, dpi=200)
    plt.close()
    return comparison_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate all YOLO models on the validation set.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_YAML, help="Path to data.yaml")
    parser.add_argument("--models", type=Path, default=DEFAULT_MODEL_DIR, help="Directory with .pt models")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for charts")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model_paths = discover_models(args.models)

    if not model_paths:
        raise SystemExit(f"No .pt model files found in: {args.models}")

    if not args.data.exists():
        raise SystemExit(f"Dataset config not found: {args.data}")

    summary_rows: list[dict[str, Any]] = []

    for model_path in model_paths:
        print(f"Validating model: {model_path.name}")
        metrics, chart_path = validate_model(model_path, args.data, args.output)

        summary_rows.append(
            {
                "model": model_path.stem,
                "precision": metrics["precision"],
                "recall": metrics["recall"],
                "map50": metrics["map50"],
                "map5095": metrics["map5095"],
                "chart_path": str(chart_path),
            }
        )

        print(
            f"  Precision={metrics['precision']:.4f}  "
            f"Recall={metrics['recall']:.4f}  "
            f"mAP50={metrics['map50']:.4f}  "
            f"mAP50-95={metrics['map5095']:.4f}"
        )

    summary_csv = write_summary_csv(summary_rows, args.output)
    comparison_chart = save_comparison_chart(summary_rows, args.output)

    print(f"\nSummary CSV saved to: {summary_csv}")
    print(f"Comparison chart saved to: {comparison_chart}")
    print(f"Per-model charts saved under: {args.output}")


if __name__ == "__main__":
    main()
