"""
GUI/reports_window.py

Displays all attendance records in a table inside the app, with
buttons to export the currently displayed data to Excel or PDF.
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt

from Reports.report_generator import get_all_attendance
from Reports.export_utils import export_to_excel, export_to_pdf
from Utils.logger import get_logger

logger = get_logger(__name__)

TABLE_HEADERS = ["Name", "Roll No", "Department", "Date", "Time In", "Status"]


class ReportsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.current_rows = []
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle("Attendance Reports")
        self.resize(650, 450)

        title_label = QLabel("Attendance Report - All Records")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setProperty("role", "title")

        self.table = QTableWidget()
        self.table.setColumnCount(len(TABLE_HEADERS))
        self.table.setHorizontalHeaderLabels(TABLE_HEADERS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # read-only table

        refresh_button = QPushButton("Refresh")
        refresh_button.setProperty("role", "secondary")
        refresh_button.clicked.connect(self.load_data)

        export_excel_button = QPushButton("Export to Excel")
        export_excel_button.clicked.connect(self.handle_export_excel)

        export_pdf_button = QPushButton("Export to PDF")
        export_pdf_button.clicked.connect(self.handle_export_pdf)

        back_button = QPushButton("Back to Dashboard")
        back_button.setProperty("role", "secondary")
        back_button.clicked.connect(self.close)

        button_row = QHBoxLayout()
        button_row.addWidget(refresh_button)
        button_row.addWidget(export_excel_button)
        button_row.addWidget(export_pdf_button)

        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(self.table)
        layout.addLayout(button_row)
        layout.addWidget(back_button)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        self.setLayout(layout)

    def load_data(self):
        """Fetches all attendance records and fills the table."""
        self.current_rows = get_all_attendance()
        self.table.setRowCount(len(self.current_rows))

        for row_index, row in enumerate(self.current_rows):
            self.table.setItem(row_index, 0, QTableWidgetItem(row["name"]))
            self.table.setItem(row_index, 1, QTableWidgetItem(row["roll_no"]))
            self.table.setItem(row_index, 2, QTableWidgetItem(row["department"] or ""))
            self.table.setItem(row_index, 3, QTableWidgetItem(row["date"]))
            self.table.setItem(row_index, 4, QTableWidgetItem(row["time_in"]))
            self.table.setItem(row_index, 5, QTableWidgetItem(row["status"]))

        logger.info(f"Reports window loaded {len(self.current_rows)} record(s).")

    def handle_export_excel(self):
        if not self.current_rows:
            QMessageBox.information(self, "No Data", "There are no attendance records to export.")
            return

        file_path = export_to_excel(self.current_rows)
        QMessageBox.information(self, "Export Successful", f"Excel report saved to:\n{file_path}")
        logger.info(f"Exported attendance to Excel: {file_path}")

    def handle_export_pdf(self):
        if not self.current_rows:
            QMessageBox.information(self, "No Data", "There are no attendance records to export.")
            return

        file_path = export_to_pdf(self.current_rows)
        QMessageBox.information(self, "Export Successful", f"PDF report saved to:\n{file_path}")
        logger.info(f"Exported attendance to PDF: {file_path}")


if __name__ == "__main__":
    # Manual test: python -m GUI.reports_window
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = ReportsWindow()
    window.show()
    sys.exit(app.exec_())