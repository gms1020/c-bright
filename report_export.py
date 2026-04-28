import csv
import json
from datetime import datetime
from pathlib import Path


EXPORTS_DIR = Path("exports")
EXPORTS_DIR.mkdir(exist_ok=True)


def _timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def export_results_csv(results):
    path = EXPORTS_DIR / f"schedule_results_{_timestamp()}.csv"

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Day",
            "Start",
            "End",
            "Label",
            "Available",
            "Conflicts",
            "Status",
            "Priority",
        ])

        for result in results:
            writer.writerow([
                result.get("day", ""),
                result.get("start", ""),
                result.get("end", ""),
                result.get("label", ""),
                result.get("available_count", 0),
                result.get("conflict_count", 0),
                get_status(result),
                result.get("priority", ""),
            ])

    return path


def export_results_json(results):
    path = EXPORTS_DIR / f"schedule_results_{_timestamp()}.json"

    with open(path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)

    return path


def export_results_txt(results, total_submissions=0, interested_count=0):
    path = EXPORTS_DIR / f"schedule_summary_{_timestamp()}.txt"

    open_count = sum(1 for r in results if get_status(r) == "Open")
    partial_count = sum(1 for r in results if get_status(r) == "Partial")
    closed_count = sum(1 for r in results if get_status(r) == "Closed")

    best = results[0] if results else None
    backup = results[1] if len(results) > 1 else None

    with open(path, "w", encoding="utf-8") as file:
        file.write("COURSE SCHEDULING SUMMARY\n")
        file.write("=" * 60 + "\n\n")

        file.write(f"Total submissions loaded: {total_submissions}\n")
        file.write(f"Interested students: {interested_count}\n")
        file.write(f"Open blocks: {open_count}\n")
        file.write(f"Partial blocks: {partial_count}\n")
        file.write(f"Closed blocks: {closed_count}\n\n")

        if best:
            file.write("Best recommended block:\n")
            file.write(
                f"- {best.get('day', '')} "
                f"{format_time_12h(best.get('start', ''))}-{format_time_12h(best.get('end', ''))} "
                f"| Available: {best.get('available_count', 0)} "
                f"| Conflicts: {best.get('conflict_count', 0)} "
                f"| Status: {get_status(best)}\n\n"
            )

        if backup:
            file.write("Backup recommended block:\n")
            file.write(
                f"- {backup.get('day', '')} "
                f"{format_time_12h(backup.get('start', ''))}-{format_time_12h(backup.get('end', ''))} "
                f"| Available: {backup.get('available_count', 0)} "
                f"| Conflicts: {backup.get('conflict_count', 0)} "
                f"| Status: {get_status(backup)}\n\n"
            )

        file.write("TOP RESULTS\n")
        file.write("-" * 60 + "\n")
        for index, result in enumerate(results[:10], start=1):
            file.write(
                f"#{index} "
                f"{result.get('day', '')} "
                f"{format_time_12h(result.get('start', ''))}-{format_time_12h(result.get('end', ''))} "
                f"| Available: {result.get('available_count', 0)} "
                f"| Conflicts: {result.get('conflict_count', 0)} "
                f"| Status: {get_status(result)} "
                f"| Priority: {result.get('priority', '')}\n"
            )

    return path


def get_status(result):
    if result.get("conflict_count", 0) == 0:
        return "Open"
    if result.get("available_count", 0) > 0:
        return "Partial"
    return "Closed"


def format_time_12h(time_str):
    if not time_str:
        return ""
    dt = datetime.strptime(time_str, "%H:%M")
    return dt.strftime("%I:%M %p").lstrip("0")