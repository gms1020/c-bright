import tkinter as tk
from tkinter import messagebox, ttk

from models import CONFLICT_TYPES, Conflict, StudentResponse
from storage import save_student_response
from time_blocks import get_block_options


class StudentFormWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Student Availability Form")
        self.geometry("820x560")
        self.conflicts: list[Conflict] = []

        self.name_var = tk.StringVar()
        self.student_id_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.interested_var = tk.BooleanVar(value=True)
        self.evening_ok_var = tk.BooleanVar(value=False)
        self.athlete_var = tk.BooleanVar(value=False)

        self.block_var = tk.StringVar()
        self.conflict_type_var = tk.StringVar(value=CONFLICT_TYPES[0])
        self.label_var = tk.StringVar()

        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self, padx=12, pady=12)
        top.pack(fill="x")

        tk.Label(top, text="Name").grid(row=0, column=0, sticky="w")
        tk.Entry(top, textvariable=self.name_var, width=28).grid(row=0, column=1, sticky="w", padx=4)
        tk.Label(top, text="Student ID").grid(row=0, column=2, sticky="w")
        tk.Entry(top, textvariable=self.student_id_var, width=20).grid(row=0, column=3, sticky="w", padx=4)
        tk.Label(top, text="Email").grid(row=1, column=0, sticky="w")
        tk.Entry(top, textvariable=self.email_var, width=28).grid(row=1, column=1, sticky="w", padx=4)

        tk.Checkbutton(top, text="Interested in the course", variable=self.interested_var).grid(row=2, column=0, columnspan=2, sticky="w")
        tk.Checkbutton(top, text="Evening courses are okay", variable=self.evening_ok_var).grid(row=2, column=2, columnspan=2, sticky="w")
        tk.Checkbutton(top, text="I am a spring athlete", variable=self.athlete_var).grid(row=3, column=0, columnspan=2, sticky="w")

        conflict_frame = tk.LabelFrame(self, text="Add a conflict", padx=12, pady=12)
        conflict_frame.pack(fill="x", padx=12, pady=8)

        tk.Label(conflict_frame, text="Academic block").grid(row=0, column=0, sticky="w")
        block_combo = ttk.Combobox(conflict_frame, textvariable=self.block_var, values=get_block_options(include_evening=True), width=42, state="readonly")
        block_combo.grid(row=0, column=1, sticky="w", padx=4)

        tk.Label(conflict_frame, text="Type").grid(row=0, column=2, sticky="w")
        type_combo = ttk.Combobox(conflict_frame, textvariable=self.conflict_type_var, values=CONFLICT_TYPES, width=18, state="readonly")
        type_combo.grid(row=0, column=3, sticky="w", padx=4)

        tk.Label(conflict_frame, text="Label").grid(row=1, column=0, sticky="w")
        tk.Entry(conflict_frame, textvariable=self.label_var, width=42).grid(row=1, column=1, sticky="w", padx=4)
        tk.Button(conflict_frame, text="Add Conflict", command=self.add_conflict).grid(row=1, column=3, sticky="e")

        list_frame = tk.LabelFrame(self, text="Current conflicts", padx=12, pady=12)
        list_frame.pack(fill="both", expand=True, padx=12, pady=8)

        self.listbox = tk.Listbox(list_frame, width=100, height=14)
        self.listbox.pack(fill="both", expand=True, side="left")
        scrollbar = tk.Scrollbar(list_frame, command=self.listbox.yview)
        scrollbar.pack(fill="y", side="right")
        self.listbox.config(yscrollcommand=scrollbar.set)

        bottom = tk.Frame(self, padx=12, pady=12)
        bottom.pack(fill="x")
        tk.Button(bottom, text="Remove Selected", command=self.remove_selected).pack(side="left")
        tk.Button(bottom, text="Save Submission", command=self.save_submission).pack(side="right")

    def add_conflict(self):
        block_display = self.block_var.get().strip()
        if not block_display:
            messagebox.showerror("Missing block", "Please choose an academic block.")
            return
        block_code = block_display.split(" - ")[0]
        label = self.label_var.get().strip()
        if not label:
            messagebox.showerror("Missing label", "Please enter a course, sport, or activity label.")
            return
        conflict = Conflict(
            block_code=block_code,
            conflict_type=self.conflict_type_var.get(),
            label=label,
        )
        self.conflicts.append(conflict)
        self.listbox.insert("end", f"{conflict.block_code} | {conflict.conflict_type} | {conflict.label}")
        self.block_var.set("")
        self.label_var.set("")

    def remove_selected(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        del self.conflicts[index]
        self.listbox.delete(index)

    def save_submission(self):
        if not self.name_var.get().strip() or not self.student_id_var.get().strip():
            messagebox.showerror("Missing information", "Name and student ID are required.")
            return
        student = StudentResponse(
            name=self.name_var.get().strip(),
            student_id=self.student_id_var.get().strip(),
            email=self.email_var.get().strip(),
            interested=self.interested_var.get(),
            evening_ok=self.evening_ok_var.get(),
            athlete=self.athlete_var.get(),
            conflicts=self.conflicts,
        )
        path = save_student_response(student)
        messagebox.showinfo("Saved", f"Submission saved to:\n{path}")
        self.destroy()
