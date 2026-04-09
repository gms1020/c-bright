import tkinter as tk
from tkinter import messagebox

from models import CourseRequest
from storage import load_course_request, save_course_request


class InstructorSettingsWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Instructor Settings")
        self.geometry("420x220")
        self.resizable(False, False)

        current = load_course_request()

        self.course_name_var = tk.StringVar(value=current.course_name)
        self.include_evening_var = tk.BooleanVar(value=current.include_evening)

        self._build_ui()

    def _build_ui(self):
        frame = tk.Frame(self, padx=16, pady=16)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Course name:").grid(row=0, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.course_name_var, width=36).grid(row=0, column=1, sticky="ew", pady=4)

        tk.Checkbutton(
            frame,
            text="Allow evening courses",
            variable=self.include_evening_var,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=4)

        tk.Button(frame, text="Save Settings", command=self.save).grid(row=3, column=0, columnspan=2, pady=16)
        frame.columnconfigure(1, weight=1)

    def save(self):
        request = CourseRequest(
            course_name=self.course_name_var.get().strip() or "Special Topics Course",
            include_evening=self.include_evening_var.get(),
        )
        save_course_request(request)
        messagebox.showinfo("Saved", "Instructor settings saved.")
        self.destroy()
