import datetime
import tkinter as tk
from collections import defaultdict
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from instructor_settings import InstructorSettingsWindow
from report_export import export_results_csv, export_results_json, export_results_txt
from scheduler import analyze_schedules
from storage import SUBMISSIONS_DIR, load_all_student_responses, load_course_request


class InstructorDashboardWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Instructor Dashboard")
        self.geometry("1320x860")

        self.results = []
        self.visible_results = []
        self.loaded_folder = SUBMISSIONS_DIR
        self.loaded_students = []
        self.interested_count = 0
        self.filter_var = tk.StringVar(value="all")

        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self, padx=12, pady=12)
        top.pack(fill="x")

        tk.Button(top, text="Instructor Settings", command=self.open_settings, width=18).pack(side="left", padx=4)
        tk.Button(top, text="Open Student Submissions", command=self.choose_folder, width=22).pack(side="left", padx=4)
        tk.Button(top, text="Find Best Time Blocks", command=self.run_analysis, width=18).pack(side="left", padx=4)
        tk.Button(top, text="Export Summary", command=self.export_results, width=15).pack(side="left", padx=4)

        self.folder_label = tk.Label(top, text=f"Folder: {self.loaded_folder}", anchor="e")
        self.folder_label.pack(side="right", fill="x", expand=True)

        summary_frame = tk.LabelFrame(self, text="Summary", padx=10, pady=10)
        summary_frame.pack(fill="x", padx=12, pady=(0, 8))

        self.summary_loaded_var = tk.StringVar(value="0")
        self.summary_interested_var = tk.StringVar(value="0")
        self.summary_best_var = tk.StringVar(value="Not analyzed yet")
        self.summary_open_var = tk.StringVar(value="0")
        self.summary_partial_var = tk.StringVar(value="0")
        self.summary_closed_var = tk.StringVar(value="0")

        self._make_summary_box(summary_frame, 0, 0, "Submissions Loaded", self.summary_loaded_var)
        self._make_summary_box(summary_frame, 0, 1, "Interested Students", self.summary_interested_var)
        self._make_summary_box(summary_frame, 0, 2, "Best Block", self.summary_best_var)
        self._make_summary_box(summary_frame, 0, 3, "Open Blocks", self.summary_open_var)
        self._make_summary_box(summary_frame, 0, 4, "Partial Blocks", self.summary_partial_var)
        self._make_summary_box(summary_frame, 0, 5, "Closed Blocks", self.summary_closed_var)

        for col in range(6):
            summary_frame.grid_columnconfigure(col, weight=1)

        controls_frame = tk.LabelFrame(self, text="Display Options", padx=10, pady=10)
        controls_frame.pack(fill="x", padx=12, pady=(0, 8))

        tk.Label(controls_frame, text="Show in Grid:").pack(side="left", padx=(0, 8))
        filter_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.filter_var,
            values=["all", "open_only", "open_and_partial"],
            state="readonly",
            width=18,
        )
        filter_combo.pack(side="left")
        filter_combo.bind("<<ComboboxSelected>>", lambda event: self.refresh_view())

        tk.Label(
            controls_frame,
            text="all = all blocks | open_only = only fully open | open_and_partial = hides closed",
            fg="#666666"
        ).pack(side="left", padx=12)

        recommendations_frame = tk.LabelFrame(self, text="Top Recommendations", padx=10, pady=10)
        recommendations_frame.pack(fill="x", padx=12, pady=(0, 8))

        self.recommendations_text = tk.Text(recommendations_frame, height=6, wrap="word")
        self.recommendations_text.pack(fill="both", expand=True)

        body = tk.Frame(self, padx=12, pady=12)
        body.pack(fill="both", expand=True)

        schedule_container = tk.Frame(body)
        schedule_container.pack(fill="both", expand=True)

        self.schedule_canvas = tk.Canvas(schedule_container, borderwidth=0, highlightthickness=0)
        self.schedule_canvas.pack(side="left", fill="both", expand=True)

        schedule_scroll = tk.Scrollbar(schedule_container, orient="vertical", command=self.schedule_canvas.yview)
        schedule_scroll.pack(side="right", fill="y")
        self.schedule_canvas.configure(yscrollcommand=schedule_scroll.set)

        self.schedule_grid_frame = tk.Frame(self.schedule_canvas)
        self.schedule_canvas.create_window((0, 0), window=self.schedule_grid_frame, anchor="nw")

        self.schedule_grid_frame.bind(
            "<Configure>",
            lambda event: self.schedule_canvas.configure(scrollregion=self.schedule_canvas.bbox("all")),
        )

        details_frame = tk.LabelFrame(body, text="Selected Time Block", padx=10, pady=10)
        details_frame.pack(fill="x", padx=0, pady=(10, 0))

        self.details_text = tk.Text(details_frame, height=14, wrap="word")
        self.details_text.pack(fill="both", expand=True)

        self.details_text.insert(
            "end",
            "Run the analysis to load student submissions and view recommended time blocks."
        )

    def _make_summary_box(self, parent, row, column, title, variable):
        card = tk.Frame(parent, relief="ridge", borderwidth=1, padx=8, pady=8, bg="#fafafa")
        card.grid(row=row, column=column, sticky="nsew", padx=4, pady=4)

        tk.Label(card, text=title, font=(None, 9, "bold"), bg="#fafafa").pack(anchor="w")
        tk.Label(
            card,
            textvariable=variable,
            font=(None, 12),
            bg="#fafafa",
            justify="left",
            wraplength=180
        ).pack(anchor="w", pady=(4, 0))

    def open_settings(self):
        InstructorSettingsWindow(self)

    def choose_folder(self):
        selected = filedialog.askdirectory(initialdir=str(self.loaded_folder))
        if selected:
            self.loaded_folder = Path(selected)
            self.folder_label.config(text=f"Folder: {self.loaded_folder}")

    def run_analysis(self):
        students = load_all_student_responses(self.loaded_folder)
        if not students:
            messagebox.showerror("No submissions", "No student JSON files were found in the selected folder.")
            return

        self.loaded_students = students
        self.interested_count = sum(1 for student in students if getattr(student, "interested", False))

        course_request = load_course_request()
        self.results = analyze_schedules(students, course_request)

        self.refresh_view()

        self.details_text.delete("1.0", "end")
        self.details_text.insert(
            "end",
            f"Loaded {len(students)} student submission(s).\n"
            f"Interested students: {self.interested_count}\n\n"
            "Click a time block in the grid to view more detail."
        )

    def refresh_view(self):
        self.update_summary_cards()
        self.update_recommendations()
        self.apply_filter()
        self.render_schedule_grid()

    def apply_filter(self):
        mode = self.filter_var.get()

        if mode == "open_only":
            self.visible_results = [r for r in self.results if self.get_status(r) == "Open"]
        elif mode == "open_and_partial":
            self.visible_results = [r for r in self.results if self.get_status(r) in {"Open", "Partial"}]
        else:
            self.visible_results = list(self.results)

    def update_summary_cards(self):
        self.summary_loaded_var.set(str(len(self.loaded_students)))
        self.summary_interested_var.set(str(self.interested_count))

        open_results = [r for r in self.results if self.get_status(r) == "Open"]
        partial_results = [r for r in self.results if self.get_status(r) == "Partial"]
        closed_results = [r for r in self.results if self.get_status(r) == "Closed"]

        self.summary_open_var.set(str(len(open_results)))
        self.summary_partial_var.set(str(len(partial_results)))
        self.summary_closed_var.set(str(len(closed_results)))

        if self.results:
            best = self.results[0]
            best_text = (
                f"{best['day']} {self.format_time_12h(best['start'])}-{self.format_time_12h(best['end'])}\n"
                f"Avail: {best['available_count']}"
            )
            self.summary_best_var.set(best_text)
        else:
            self.summary_best_var.set("No results")

    def update_recommendations(self):
        self.recommendations_text.delete("1.0", "end")

        if not self.results:
            self.recommendations_text.insert("end", "Run analysis to view recommendations.")
            return

        top_results = self.results[:3]

        self.recommendations_text.insert("end", "Top recommended blocks:\n\n")
        for index, result in enumerate(top_results, start=1):
            status = self.get_status(result)
            recommendation = (
                f"#{index} {result['day']} "
                f"{self.format_time_12h(result['start'])}-{self.format_time_12h(result['end'])} "
                f"| Available: {result['available_count']} "
                f"| Conflicts: {result['conflict_count']} "
                f"| Status: {status}\n"
            )
            self.recommendations_text.insert("end", recommendation)

    def render_schedule_grid(self):
        for widget in self.schedule_grid_frame.winfo_children():
            widget.destroy()

        if not self.visible_results:
            tk.Label(
                self.schedule_grid_frame,
                text="No blocks match the current filter. Change the display option or run analysis again.",
                padx=20,
                pady=20
            ).grid(row=0, column=0)
            return

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

        tk.Label(
            self.schedule_grid_frame,
            text="Time",
            relief="ridge",
            borderwidth=1,
            width=18,
            bg="#f0f0f0",
            font=(None, 10, "bold")
        ).grid(row=0, column=0, sticky="nsew")

        for col, day in enumerate(days, start=1):
            tk.Label(
                self.schedule_grid_frame,
                text=day,
                relief="ridge",
                borderwidth=1,
                width=18,
                bg="#e8e8e8",
                font=(None, 10, "bold"),
            ).grid(row=0, column=col, sticky="nsew")

        time_slots = sorted(
            {(result["start"], result["end"]) for result in self.visible_results},
            key=lambda item: (item[0], item[1])
        )

        blocks_by_slot = {
            (result["day"], result["start"], result["end"]): result
            for result in self.visible_results
        }

        best_key = None
        if self.results:
            best = self.results[0]
            best_key = (best["day"], best["start"], best["end"])

        status_colors = {
            "Open": "#d4f5d4",
            "Partial": "#fff2cc",
            "Closed": "#f8d7da",
        }

        for row_index, (start, end) in enumerate(time_slots, start=1):
            tk.Label(
                self.schedule_grid_frame,
                text=f"{self.format_time_12h(start)} - {self.format_time_12h(end)}",
                relief="ridge",
                borderwidth=1,
                width=18,
                bg="#f0f0f0",
                font=(None, 10)
            ).grid(row=row_index, column=0, sticky="nsew")

            for col, day in enumerate(days, start=1):
                result = blocks_by_slot.get((day, start, end))

                cell = tk.Label(
                    self.schedule_grid_frame,
                    text="",
                    relief="ridge",
                    borderwidth=1,
                    width=18,
                    height=5,
                    anchor="nw",
                    justify="left",
                    wraplength=150,
                    padx=6,
                    pady=6,
                )
                cell.grid(row=row_index, column=col, sticky="nsew", padx=1, pady=1)

                if result:
                    status = self.get_status(result)
                    is_best = best_key == (day, start, end)

                    if is_best:
                        cell_text = (
                            "#1 Best Choice\n"
                            f"{result['label']}\n"
                            f"Avail: {result['available_count']}"
                        )
                        cell.config(
                            text=cell_text,
                            bg="#cfe2f3",
                            borderwidth=3,
                            font=(None, 9, "bold"),
                        )
                    else:
                        cell_text = (
                            f"{result['label']}\n"
                            f"Avail: {result['available_count']}\n"
                            f"{status}"
                        )
                        cell.config(
                            text=cell_text,
                            bg=status_colors[status]
                        )

                    cell.bind("<Button-1>", lambda event, res=result: self.show_block_cell(res))
                else:
                    cell.config(bg="#f7f7f7", text="")

        for col in range(len(days) + 1):
            self.schedule_grid_frame.grid_columnconfigure(col, weight=1)

    def show_block_cell(self, result):
        status = self.get_status(result)
        priority_text = self.get_priority_text(result.get("priority", "preferred"))
        breakdown = self.build_conflict_breakdown(result)
        grouped_conflicts = self.build_grouped_conflict_lines(result)

        self.details_text.delete("1.0", "end")
        self.details_text.insert("end", "Selected Time Block\n")
        self.details_text.insert("end", f"{result['label']}\n\n")

        self.details_text.insert("end", f"Day: {result['day']}\n")
        self.details_text.insert(
            "end",
            f"Time: {self.format_time_12h(result['start'])} - {self.format_time_12h(result['end'])}\n"
        )
        self.details_text.insert("end", f"Status: {status}\n")
        self.details_text.insert("end", f"Recommendation Level: {priority_text}\n")
        self.details_text.insert("end", f"Available Students: {result['available_count']}\n")
        self.details_text.insert("end", f"Students with Conflicts: {result['conflict_count']}\n\n")

        self.details_text.insert("end", "Conflict Breakdown\n")
        if breakdown:
            for conflict_type, count in breakdown.items():
                self.details_text.insert("end", f"- {conflict_type}: {count}\n")
        else:
            self.details_text.insert("end", "No conflicts for this block.\n")

        self.details_text.insert("end", "\nStudents in Conflict\n")
        if not grouped_conflicts:
            self.details_text.insert("end", "No students are blocked during this time.")
            return

        for line in grouped_conflicts:
            self.details_text.insert("end", f"- {line}\n")

    def build_conflict_breakdown(self, result):
        counts = {}
        for conflict in result.get("conflicts", []):
            conflict_type = conflict.get("conflict_type", "Other")
            counts[conflict_type] = counts.get(conflict_type, 0) + 1
        return counts

    def build_grouped_conflict_lines(self, result):
        grouped = defaultdict(int)
        for conflict in result.get("conflicts", []):
            key = (
                conflict.get("student", "Unknown"),
                conflict.get("conflict_type", "Other"),
                conflict.get("label", ""),
            )
            grouped[key] += 1

        lines = []
        for (student, conflict_type, label), count in grouped.items():
            if count > 1:
                lines.append(f"{student} | {conflict_type} | {label} | Multiple matching entries ({count})")
            else:
                lines.append(f"{student} | {conflict_type} | {label}")

        return sorted(lines)

    @staticmethod
    def get_status(result):
        if result["conflict_count"] == 0:
            return "Open"
        if result["available_count"] > 0:
            return "Partial"
        return "Closed"

    @staticmethod
    def get_priority_text(priority):
        mapping = {
            "preferred": "Preferred",
            "iffy": "Less Ideal",
            "optional": "Optional",
        }
        return mapping.get(priority, str(priority).capitalize())

    @staticmethod
    def format_time_12h(time_str):
        dt = datetime.datetime.strptime(time_str, "%H:%M")
        return dt.strftime("%I:%M %p").lstrip("0")

    def export_results(self):
        if not self.results:
            messagebox.showerror("Nothing to export", "Run the analysis first.")
            return

        csv_path = export_results_csv(self.results)
        json_path = export_results_json(self.results)
        txt_path = export_results_txt(
            self.results,
            total_submissions=len(self.loaded_students),
            interested_count=self.interested_count
        )

        messagebox.showinfo(
            "Exported",
            f"Summary exported to:\n{csv_path}\n{json_path}\n{txt_path}",
        )