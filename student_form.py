import tkinter as tk
from tkinter import messagebox, ttk

from models import CONFLICT_TYPES, Conflict, StudentResponse
from storage import load_course_request, save_student_response
from time_blocks import (
    DAY_ORDER,
    blocks_for_day_and_range,
    get_block_for_day_and_time,
    get_time_slot_options,
)


class StudentFormWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Student Availability Form")
        self.geometry("1040x780")

        self.conflicts: list[Conflict] = []

        course_request = load_course_request()
        self.include_evening = course_request.include_evening

        self.name_var = tk.StringVar()
        self.student_id_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.interested_var = tk.BooleanVar(value=True)
        self.evening_ok_var = tk.BooleanVar(value=False)
        self.athlete_var = tk.BooleanVar(value=False)

        self.time_mode_var = tk.StringVar(value="standard")
        self.time_slot_var = tk.StringVar()
        self.custom_start_var = tk.StringVar()
        self.custom_end_var = tk.StringVar()
        self.conflict_type_var = tk.StringVar(value=CONFLICT_TYPES[0])
        self.label_var = tk.StringVar()

        self.day_vars = {
            "Monday": tk.BooleanVar(value=False),
            "Tuesday": tk.BooleanVar(value=False),
            "Wednesday": tk.BooleanVar(value=False),
            "Thursday": tk.BooleanVar(value=False),
            "Friday": tk.BooleanVar(value=False),
        }

        self.time_slot_options = get_time_slot_options(include_evening=self.include_evening)

        self._build_ui()

    def _build_ui(self):
        top = tk.LabelFrame(self, text="Student Information", padx=12, pady=12)
        top.pack(fill="x", padx=12, pady=(12, 8))

        tk.Label(top, text="Name").grid(row=0, column=0, sticky="w", pady=4)
        tk.Entry(top, textvariable=self.name_var, width=30).grid(row=0, column=1, sticky="w", padx=6, pady=4)

        tk.Label(top, text="Student ID").grid(row=0, column=2, sticky="w", pady=4)
        tk.Entry(top, textvariable=self.student_id_var, width=22).grid(row=0, column=3, sticky="w", padx=6, pady=4)

        tk.Label(top, text="Email").grid(row=1, column=0, sticky="w", pady=4)
        tk.Entry(top, textvariable=self.email_var, width=30).grid(row=1, column=1, sticky="w", padx=6, pady=4)

        tk.Checkbutton(top, text="I am interested in taking this course", variable=self.interested_var).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=4
        )
        tk.Checkbutton(top, text="I am available for evening courses", variable=self.evening_ok_var).grid(
            row=2, column=2, columnspan=2, sticky="w", pady=4
        )
        tk.Checkbutton(top, text="I am a spring athlete", variable=self.athlete_var).grid(
            row=3, column=0, columnspan=2, sticky="w", pady=4
        )

        if self.include_evening:
            tk.Label(
                top,
                text="Instructor settings currently allow evening blocks.",
                fg="#555555"
            ).grid(row=4, column=0, columnspan=4, sticky="w", pady=(6, 0))
        else:
            tk.Label(
                top,
                text="Instructor settings currently allow daytime blocks only.",
                fg="#555555"
            ).grid(row=4, column=0, columnspan=4, sticky="w", pady=(6, 0))

        conflict_frame = tk.LabelFrame(self, text="Add a Conflict", padx=12, pady=12)
        conflict_frame.pack(fill="x", padx=12, pady=8)

        tk.Label(conflict_frame, text="Time Entry Type").grid(row=0, column=0, sticky="w", pady=4)

        mode_frame = tk.Frame(conflict_frame)
        mode_frame.grid(row=0, column=1, columnspan=3, sticky="w", pady=4)

        tk.Radiobutton(
            mode_frame,
            text="Standard Time Slot",
            variable=self.time_mode_var,
            value="standard"
        ).pack(side="left", padx=(0, 12))

        tk.Radiobutton(
            mode_frame,
            text="Custom Time Range",
            variable=self.time_mode_var,
            value="custom"
        ).pack(side="left")

        tk.Label(conflict_frame, text="Standard Time Slot").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Combobox(
            conflict_frame,
            textvariable=self.time_slot_var,
            values=self.time_slot_options,
            width=24,
            state="readonly",
        ).grid(row=1, column=1, sticky="w", padx=6, pady=4)

        tk.Label(conflict_frame, text="Custom Start").grid(row=1, column=2, sticky="w", pady=4)
        tk.Entry(conflict_frame, textvariable=self.custom_start_var, width=14).grid(row=1, column=3, sticky="w", padx=6, pady=4)

        tk.Label(conflict_frame, text="Conflict Type").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Combobox(
            conflict_frame,
            textvariable=self.conflict_type_var,
            values=CONFLICT_TYPES,
            width=22,
            state="readonly",
        ).grid(row=2, column=1, sticky="w", padx=6, pady=4)

        tk.Label(conflict_frame, text="Custom End").grid(row=2, column=2, sticky="w", pady=4)
        tk.Entry(conflict_frame, textvariable=self.custom_end_var, width=14).grid(row=2, column=3, sticky="w", padx=6, pady=4)

        tk.Label(conflict_frame, text="Activity / Course Name").grid(row=3, column=0, sticky="w", pady=4)
        tk.Entry(conflict_frame, textvariable=self.label_var, width=40).grid(row=3, column=1, sticky="w", padx=6, pady=4)

        days_frame = tk.LabelFrame(conflict_frame, text="Days", padx=10, pady=8)
        days_frame.grid(row=4, column=0, columnspan=4, sticky="w", pady=(10, 8))

        for index, day in enumerate(DAY_ORDER):
            tk.Checkbutton(days_frame, text=day, variable=self.day_vars[day]).grid(
                row=0, column=index, padx=8, sticky="w"
            )

        button_row = tk.Frame(conflict_frame)
        button_row.grid(row=5, column=0, columnspan=4, sticky="e", pady=(10, 0))

        tk.Button(button_row, text="Clear Days", command=self.clear_days, width=14).pack(side="left", padx=4)
        tk.Button(button_row, text="Add Conflict", command=self.add_conflict, width=14).pack(side="left", padx=4)

        help_frame = tk.LabelFrame(self, text="Instructions", padx=12, pady=12)
        help_frame.pack(fill="x", padx=12, pady=(0, 8))

        help_text = (
            "Use Standard Time Slot for normal class times.\n"
            "Use Custom Time Range for labs, long classes, work shifts, or other unusual conflicts.\n"
            "Custom times must use 24-hour format such as 13:00 or 16:15."
        )
        tk.Label(help_frame, text=help_text, justify="left", anchor="w").pack(fill="x")

        list_frame = tk.LabelFrame(self, text="Current Conflicts", padx=12, pady=12)
        list_frame.pack(fill="both", expand=True, padx=12, pady=8)

        content_frame = tk.Frame(list_frame)
        content_frame.pack(fill="both", expand=True)

        list_frame = tk.Frame(content_frame)
        list_frame.pack(side="left", fill="both", expand=True)

        self.listbox = tk.Listbox(list_frame, width=120, height=16)
        self.listbox.pack(fill="both", expand=True, side="left")

        scrollbar = tk.Scrollbar(list_frame, command=self.listbox.yview)
        scrollbar.pack(fill="y", side="right")
        self.listbox.config(yscrollcommand=scrollbar.set)

        side_buttons = tk.Frame(content_frame, padx=12, pady=12)
        side_buttons.pack(side="right", fill="y")

        tk.Button(
            side_buttons,
            text="Remove Selected Conflict",
            command=self.remove_selected,
            width=24
        ).pack(side="top", pady=4)

        tk.Button(
            side_buttons,
            text="Submit Availability Form",
            command=self.save_submission,
            width=24,
            bg="#d9ead3"
        ).pack(side="top", pady=4)

    def clear_days(self):
        for var in self.day_vars.values():
            var.set(False)

    def add_conflict(self):
        selected_days = [day for day, var in self.day_vars.items() if var.get()]
        if not selected_days:
            messagebox.showerror("Missing days", "Please check at least one day.")
            return

        label = self.label_var.get().strip()
        if not label:
            messagebox.showerror("Missing activity name", "Please enter the activity or course name.")
            return

        conflict_type = self.conflict_type_var.get().strip()
        if not conflict_type:
            messagebox.showerror("Missing type", "Please choose a conflict type.")
            return

        added_conflicts = []
        skipped_days = []

        if self.time_mode_var.get() == "standard":
            time_slot = self.time_slot_var.get().strip()
            if not time_slot:
                messagebox.showerror("Missing time slot", "Please choose a standard time slot.")
                return

            try:
                start, end = [part.strip() for part in time_slot.split("-")]
            except ValueError:
                messagebox.showerror("Invalid time slot", "The selected time slot is invalid.")
                return

            for day in selected_days:
                block = get_block_for_day_and_time(day, start, end)
                if block is None:
                    skipped_days.append(day)
                    continue

                conflict = Conflict(
                    block_code=block.code,
                    conflict_type=conflict_type,
                    label=label,
                )
                self.conflicts.append(conflict)
                added_conflicts.append(conflict)

                self.listbox.insert(
                    "end",
                    f"{day} | {time_slot} | {conflict.conflict_type} | {conflict.label} | {conflict.block_code}"
                )

        else:
            custom_start = self.custom_start_var.get().strip()
            custom_end = self.custom_end_var.get().strip()

            if not custom_start or not custom_end:
                messagebox.showerror(
                    "Missing custom time",
                    "Please enter both a custom start time and end time."
                )
                return

            try:
                start_parts = custom_start.split(":")
                end_parts = custom_end.split(":")
                if len(start_parts) != 2 or len(end_parts) != 2:
                    raise ValueError

                start_hour = int(start_parts[0])
                start_min = int(start_parts[1])
                end_hour = int(end_parts[0])
                end_min = int(end_parts[1])

                if not (0 <= start_hour <= 23 and 0 <= start_min <= 59):
                    raise ValueError
                if not (0 <= end_hour <= 23 and 0 <= end_min <= 59):
                    raise ValueError
                if (end_hour, end_min) <= (start_hour, start_min):
                    raise ValueError

            except ValueError:
                messagebox.showerror(
                    "Invalid custom time",
                    "Use 24-hour format like 13:00 or 16:15, and make sure end time is later than start time."
                )
                return

            for day in selected_days:
                matching_blocks = blocks_for_day_and_range(
                    day,
                    custom_start,
                    custom_end,
                    include_evening=self.include_evening
                )

                if not matching_blocks:
                    skipped_days.append(day)
                    continue

                for block in matching_blocks:
                    conflict = Conflict(
                        block_code=block.code,
                        conflict_type=conflict_type,
                        label=label,
                    )
                    self.conflicts.append(conflict)
                    added_conflicts.append(conflict)

                    self.listbox.insert(
                        "end",
                        f"{day} | {custom_start}-{custom_end} | {conflict.conflict_type} | {conflict.label} | {conflict.block_code}"
                    )

        if not added_conflicts:
            messagebox.showerror(
                "No matching blocks",
                "No schedule blocks matched the selected day(s) and time."
            )
            return

        if skipped_days:
            messagebox.showwarning(
                "Some days skipped",
                "No blocks matched for these day(s):\n" + ", ".join(skipped_days)
            )

        self.time_slot_var.set("")
        self.custom_start_var.set("")
        self.custom_end_var.set("")
        self.label_var.set("")
        self.clear_days()

    def remove_selected(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        del self.conflicts[index]
        self.listbox.delete(index)

    def build_review_text(self):
        lines = [
            f"Name: {self.name_var.get().strip()}",
            f"Student ID: {self.student_id_var.get().strip()}",
            f"Email: {self.email_var.get().strip() or 'Not provided'}",
            f"Interested: {'Yes' if self.interested_var.get() else 'No'}",
            f"Evening OK: {'Yes' if self.evening_ok_var.get() else 'No'}",
            f"Spring Athlete: {'Yes' if self.athlete_var.get() else 'No'}",
            "",
            f"Conflicts Entered: {len(self.conflicts)}",
        ]
        return "\n".join(lines)

    def save_submission(self):
        if not self.name_var.get().strip() or not self.student_id_var.get().strip():
            messagebox.showerror("Missing information", "Name and student ID are required.")
            return

        if not self.conflicts:
            proceed = messagebox.askyesno(
                "No conflicts entered",
                "No conflicts have been added yet. Do you want to submit anyway?"
            )
            if not proceed:
                return

        confirm = messagebox.askyesno(
            "Confirm Submission",
            self.build_review_text() + "\n\nSubmit this availability form?"
        )
        if not confirm:
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