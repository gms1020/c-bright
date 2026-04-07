import tkinter as tk

from instructor_dashboard import InstructorDashboardWindow
from student_form import StudentFormWindow


class LauncherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Course Scheduling Analyzer")
        self.geometry("420x220")
        self.resizable(False, False)
        self._build_ui()

    def _build_ui(self):
        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame,
            text="Course Scheduling Analyzer",
            font=("Arial", 14, "bold"),
        ).pack(pady=(0, 10))

        tk.Label(
            frame,
            text="Choose a mode to begin.",
        ).pack(pady=(0, 18))

        tk.Button(frame, text="Student Mode", width=24, command=self.open_student).pack(pady=6)
        tk.Button(frame, text="Instructor Mode", width=24, command=self.open_instructor ).pack(pady=6)
        tk.Button(frame, text="Exit", width=24, command=self.destroy).pack(pady=6)

    def open_student(self):
        StudentFormWindow(self)

    def open_instructor(self):
        InstructorDashboardWindow(self)


if __name__ == "__main__":
    app = LauncherApp()
    app.mainloop()
