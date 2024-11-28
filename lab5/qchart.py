from PyQt5.QtWidgets import QDialog, QHBoxLayout, QApplication
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QPieSeries, QBarCategoryAxis, QValueAxis
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter

from lab5.utils import BaseDialog


class ChartDialog(BaseDialog):
    def __init__(self, title, data, total, parent=None):
        super().__init__(800, 400, title, modal=False, parent=parent)

        self.colors = [
            QColor("#3498db"), QColor("#e74c3c"),
            QColor("#2ecc71"), QColor("#5a46a6"),
            QColor("#c4b03b"), QColor("#a23bc4"),
            QColor("#bd3164"), QColor("#bd3164"),
            QColor("#2c1ea8"), QColor("#bf7128"),
        ]
        self.data = data
        self.total = total

        self.init_ui()

    def init_ui(self):
        # Main Layout
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        #Create Bar Chart
        bar_chart = self.create_bar_chart()
        bar_chart_view = QChartView(bar_chart)
        bar_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        main_layout.addWidget(bar_chart_view)

        # Create Pie Chart
        pie_chart = self.create_pie_chart()
        pie_chart_view = QChartView(pie_chart)
        print(pie_chart_view)
        pie_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        main_layout.addWidget(pie_chart_view)

    def create_bar_chart(self):
        # Create bar set
        bar_set = QBarSet("Entities")
        values = []
        categories = []
        for idx, (label, value) in enumerate(self.data):
            bar_set.append(value)
            bar_set.setColor(self.colors[idx % len(self.colors)])  # Assign color from palette
            values.append(value)
            categories.append(label)

        # Add percentages to categories
        percentages = [f"{label} ({round((value / self.total) * 100, 2)}%)" for label, value in self.data]

        # Create series
        series = QBarSeries()
        series.append(bar_set)

        # Create chart
        chart = QChart()
        chart.addSeries(series)
        chart.setAnimationOptions(QChart.SeriesAnimations)

        # Create X-axis (categories)
        axis_x = QBarCategoryAxis()
        axis_x.append(percentages)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        # Create Y-axis (values)
        axis_y = QValueAxis()
        axis_y.setRange(0, max(values) + 2)  # Set range slightly above max value for padding
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

        # Display the chart
        chart.legend().setVisible(False)
        return chart

    def create_pie_chart(self):
        # Create pie series
        pie_series = QPieSeries()
        for idx, (label, value) in enumerate(self.data):
            percentage = round((value / self.total) * 100, 2)
            slice = pie_series.append(f"{label} ({percentage}%)", value)
            slice.setBrush(self.colors[idx % len(self.colors)])  # Assign color from palette
            slice.setLabelVisible(True)

        # Create chart
        chart = QChart()
        chart.addSeries(pie_series)

        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setAlignment(Qt.AlignRight)
        return chart


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    # Example Data
    entity_data = [('LOC', 14), ('PERS', 43), ('ORG', 20), ('MISC', 2)]
    total_entities = 79

    # Create and show dialog
    dialog = ChartDialog(entity_data, total_entities)
    dialog.exec_()

    sys.exit(app.exec_())
