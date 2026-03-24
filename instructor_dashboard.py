import tkinter as tk
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

        columns = ("block", "conflicts", "available", "priority", "types")
        self.tree = ttk.Treeview(body, columns=columns, show="headings")
        self.tree.heading("block", text="Block")
        self.tree.heading("conflicts", text="Conflicts")
        self.tree.heading("available", text="Available")
        self.tree.heading("priority", text="Priority")
        self.tree.heading("types", text="Conflict Types")
        self.tree.column("block", width=280)
        self.tree.column("conflicts", width=80, anchor="center")
        self.tree.column("available", width=80, anchor="center")
        self.tree.column("priority", width=100, anchor="center")
        self.tree.column("types", width=260)
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.show_details)

        scrollbar = tk.Scrollbar(body, command=self.tree.yview)
        scrollbar.pack(side="left", fill="y")
        self.tree.config(yscrollcommand=scrollbar.set)

        details_frame = tk.LabelFrame(body, text="Block details", padx=8, pady=8)
        details_frame.pack(side="right", fill="both", expand=True, padx=8)
        self.details_text = tk.Text(details_frame, width=48, height=28, wrap="word")
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
        self.tree.delete(*self.tree.get_children())
        for result in self.results:
            type_summary = ", ".join(f"{k}: {v}" for k, v in result["conflict_types"].items()) or "None"
            self.tree.insert(
                "",
                "end",
                values=(result["label"], result["conflict_count"], result["available_count"], result["priority"], type_summary),
            )
        self.details_text.delete("1.0", "end")
        self.details_text.insert("end", f"Loaded {len(students)} student submission(s).\n\nSelect a block to view details.")

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
