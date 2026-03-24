import csv
import json
from pathlib import Path
from typing import List

from storage import EXPORTS_DIR


def export_results_json(results: List[dict], filename: str = "results.json") -> Path:
    path = EXPORTS_DIR / filename
    with path.open("w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)
    return path


def export_results_csv(results: List[dict], filename: str = "results.csv") -> Path:
    path = EXPORTS_DIR / filename
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Block Code", "Label", "Conflicts", "Available", "Priority", "Evening", "Conflict Types"])
        for result in results:
            type_summary = "; ".join(f"{key}: {value}" for key, value in result.get("conflict_types", {}).items())
            writer.writerow([
                result.get("block_code"),
                result.get("label"),
                result.get("conflict_count"),
                result.get("available_count"),
                result.get("priority"),
                result.get("is_evening"),
                type_summary,
            ])
    return path


def export_results_txt(results: List[dict], filename: str = "results.txt") -> Path:
    path = EXPORTS_DIR / filename
    with path.open("w", encoding="utf-8") as handle:
        for index, result in enumerate(results, start=1):
            handle.write(f"{index}. {result['label']}\n")
            handle.write(f"   Conflicts: {result['conflict_count']}\n")
            handle.write(f"   Available: {result['available_count']}\n")
            handle.write(f"   Priority: {result['priority']}\n")
            if result.get("conflicts"):
                for conflict in result["conflicts"]:
                    handle.write(
                        f"   - {conflict['student']} | {conflict['conflict_type']} | {conflict['label']}\n"
                    )
            handle.write("\n")
    return path
