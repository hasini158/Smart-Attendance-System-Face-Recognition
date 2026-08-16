"""
Reports/export_utils.py

Converts attendance report data (a list of sqlite3.Row objects) into
downloadable Excel (.xlsx) or PDF files, saved into
Dataset/attendance_logs/ (created if it doesn't exist).
"""

import os
from datetime import datetime

import openpyxl
from openpyxl.styles import Font
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_FOLDER = os.path.join(PROJECT_ROOT, "Dataset", "attendance_logs")
os.makedirs(LOGS_FOLDER, exist_ok=True)

COLUMN_HEADERS = ["Name", "Roll No", "Date", "Time In", "Status"]


def _rows_to_table_data(rows):
    """Converts sqlite3.Row objects into a list of plain lists for export."""
    table_data = [COLUMN_HEADERS]
    for row in rows:
        table_data.append([
            row["name"], row["roll_no"], row["date"], row["time_in"], row["status"]
        ])
    return table_data


def export_to_excel(rows, filename=None):
    """
    Exports attendance rows to an .xlsx file.

    Returns:
        The full path to the saved file, or None if there was nothing to export.
    """
    if not rows:
        return None

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"attendance_report_{timestamp}.xlsx"

    file_path = os.path.join(LOGS_FOLDER, filename)

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Attendance"

    # Header row, bold
    sheet.append(COLUMN_HEADERS)
    for cell in sheet[1]:
        cell.font = Font(bold=True)

    for row in rows:
        sheet.append([row["name"], row["roll_no"], row["date"], row["time_in"], row["status"]])

    # Auto-fit column widths roughly based on content length
    for column_cells in sheet.columns:
        max_length = max(len(str(cell.value)) for cell in column_cells if cell.value)
        sheet.column_dimensions[column_cells[0].column_letter].width = max_length + 4

    workbook.save(file_path)
    return file_path


def export_to_pdf(rows, filename=None, title="Attendance Report"):
    """
    Exports attendance rows to a .pdf file with a simple table layout.

    Returns:
        The full path to the saved file, or None if there was nothing to export.
    """
    if not rows:
        return None

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"attendance_report_{timestamp}.pdf"

    file_path = os.path.join(LOGS_FOLDER, filename)

    document = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [Paragraph(title, styles["Title"]), Spacer(1, 12)]

    table_data = _rows_to_table_data(rows)
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
    ]))

    elements.append(table)
    document.build(elements)
    return file_path


if __name__ == "__main__":
    # Manual test: python -m Reports.export_utils
    from Reports.report_generator import get_all_attendance

    rows = get_all_attendance()
    if not rows:
        print("No attendance records to export yet.")
    else:
        excel_path = export_to_excel(rows)
        pdf_path = export_to_pdf(rows)
        print(f"Excel report saved to: {excel_path}")
        print(f"PDF report saved to: {pdf_path}")