# COMSC 330 Course Scheduling Analyzer

## File structure

- `main.py` - launcher with Student Mode and Instructor Mode
- `time_blocks.py` - Roger Williams academic blocks and filtering rules
- `models.py` - data classes for students, conflicts, and course settings
- `storage.py` - local JSON storage for submissions and settings
- `student_form.py` - student GUI for entering conflicts
- `instructor_settings.py` - instructor options for evening blocks and Wednesday iffy blocks
- `scheduler.py` - conflict analysis logic
- `ranking.py` - ranking order for best meeting times
- `instructor_dashboard.py` - instructor GUI for analysis and exports
- `report_export.py` - exports results to JSON, CSV, and TXT
- `data/submissions/` - where student JSON submissions are saved
- `data/exports/` - where analysis exports are saved

## Storage method

This project uses **local file-based storage with JSON**.
Each student submission is saved as a JSON file in `data/submissions/`.
The instructor settings are saved as `data/course_request.json`.

## How to run

From the project folder:

```bash
python main.py
```

## Workflow

1. Instructor opens **Instructor Settings** and chooses whether evening blocks and Wednesday iffy blocks are allowed.
2. Students open **Student Mode** and save their submissions.
3. Instructor opens **Instructor Mode**.
4. Instructor selects the submissions folder and runs analysis.
5. Instructor exports results.

## Notes

- The program is built with Python and Tkinter only.
- Wednesday afternoon blocks are marked as `iffy`.
- Evening blocks are included only when the instructor enables them.
