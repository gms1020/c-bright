import datetime
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from instructor_settings import InstructorSettingsWindow
from report_export import export_results_csv, export_results_json, export_results_txt
from scheduler import analyze_schedules
from storage import SUBMISSIONS_DIR, load_all_student_responses, load_course_request


class InstructorDashboardWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Instructor Dashboard")
        self.geometry("1040x640")
        self.results = []
        self.loaded_folder = SUBMISSIONS_DIR
        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self, padx=12, pady=12)
        top.pack(fill="x")

        tk.Button(top, text="Instructor Settings", command=self.open_settings).pack(side="left", padx=4)
        tk.Button(top, text="Choose Submission Folder", command=self.choose_folder).pack(side="left", padx=4)
        tk.Button(top, text="Run Analysis", command=self.run_analysis).pack(side="left", padx=4)
        tk.Button(top, text="Export Results", command=self.export_results).pack(side="left", padx=4)

        self.folder_label = tk.Label(top, text=f"Folder: {self.loaded_folder}")
        self.folder_label.pack(side="right")

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

        details_frame = tk.LabelFrame(body, text="Block details", padx=8, pady=8)
        details_frame.pack(fill="x", padx=0, pady=(8, 0))
        self.details_text = tk.Text(details_frame, height=10, wrap="word")
        self.details_text.pack(fill="both", expand=True)

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
        course_request = load_course_request()
        self.results = analyze_schedules(students, course_request)
        self.render_schedule_grid()
        self.details_text.delete("1.0", "end")
        self.details_text.insert("end", f"Loaded {len(students)} student submission(s).\n\nClick a block to view details.")

    def show_details(self, _event=None):
        selection = self.tree.selection()
        if not selection or not self.results:
            return
        index = self.tree.index(selection[0])
        result = self.results[index]
        self.details_text.delete("1.0", "end")
        self.details_text.insert("end", f"{result['label']}\n")
        self.details_text.insert("end", f"Conflicts: {result['conflict_count']}\n")
        self.details_text.insert("end", f"Available: {result['available_count']}\n")
        status = "Open" if result["conflict_count"] == 0 else "Partial" if result["available_count"] > 0 else "Closed"
        self.details_text.insert("end", f"Status: {status}\n")
        self.details_text.insert("end", f"Priority: {result['priority']}\n\n")
        if not result["conflicts"]:
            self.details_text.insert("end", "No conflicts for this block.")
            return
        for conflict in result["conflicts"]:
            self.details_text.insert(
                "end",
                f"- {conflict['student']} | {conflict['conflict_type']} | {conflict['label']}\n",
            )

    def render_schedule_grid(self):
        for widget in self.schedule_grid_frame.winfo_children():
            widget.destroy()

        if not self.results:
            tk.Label(self.schedule_grid_frame, text="Run analysis to see the schedule.", padx=20, pady=20).grid(row=0, column=0)
            return

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        tk.Label(self.schedule_grid_frame, text="Time", relief="ridge", borderwidth=1, width=18, bg="#f0f0f0").grid(row=0, column=0, sticky="nsew")
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

        time_slots = sorted({(result["start"], result["end"]) for result in self.results}, key=lambda item: (item[0], item[1]))
        blocks_by_slot = {
            (result["day"], result["start"], result["end"]): result
            for result in self.results
        }

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
            ).grid(row=row_index, column=0, sticky="nsew")
            for col, day in enumerate(days, start=1):
                cell = tk.Label(
                    self.schedule_grid_frame,
                    text="",
                    relief="ridge",
                    borderwidth=1,
                    width=18,
                    height=4,
                    anchor="nw",
                    justify="left",
                    wraplength=130,
                )
                cell.grid(row=row_index, column=col, sticky="nsew", padx=1, pady=1)
                result = blocks_by_slot.get((day, start, end))
                if result:
                    status = "Open" if result["conflict_count"] == 0 else "Partial" if result["available_count"] > 0 else "Closed"
                    cell_text = f"{result['label']}\nAvail: {result['available_count']}\nConflicts: {result['conflict_count']}"
                    if result["priority"] != "preferred":
                        cell_text += f"\n{result['priority'].capitalize()}"
                    cell.config(text=cell_text, bg=status_colors[status])
                    cell.bind("<Button-1>", lambda event, res=result: self.show_block_cell(res))
                else:
                    cell.config(bg="#f0f0f0")

        for col in range(len(days) + 1):
            self.schedule_grid_frame.grid_columnconfigure(col, weight=1)

    @staticmethod
    def format_time_12h(time_str):
        dt = datetime.datetime.strptime(time_str, "%H:%M")
        return dt.strftime("%I:%M %p").lstrip("0")

    def show_block_cell(self, result):
        self.details_text.delete("1.0", "end")
        self.details_text.insert("end", f"{result['label']}\n")
        self.details_text.insert("end", f"Day: {result['day']}\n")
        self.details_text.insert("end", f"Time: {self.format_time_12h(result['start'])} - {self.format_time_12h(result['end'])}\n")
        self.details_text.insert("end", f"Conflicts: {result['conflict_count']}\n")
        self.details_text.insert("end", f"Available: {result['available_count']}\n")
        status = "Open" if result["conflict_count"] == 0 else "Partial" if result["available_count"] > 0 else "Closed"
        self.details_text.insert("end", f"Status: {status}\n")
        self.details_text.insert("end", f"Priority: {result['priority']}\n\n")
        if not result["conflicts"]:
            self.details_text.insert("end", "No conflicts for this block.")
            return
        for conflict in result["conflicts"]:
            self.details_text.insert(
                "end",
                f"- {conflict['student']} | {conflict['conflict_type']} | {conflict['label']}\n",
            )

    def export_results(self):
        if not self.results:
            messagebox.showerror("Nothing to export", "Run the analysis first.")
            return
        csv_path = export_results_csv(self.results)
        json_path = export_results_json(self.results)
        txt_path = export_results_txt(self.results)
        messagebox.showinfo(
            "Exported",
            f"Results exported to:\n{csv_path}\n{json_path}\n{txt_path}",
        )
