import csv
import math
import os
import sys
import warnings
from typing import List, Tuple

from PySide2.QtCore import Qt, QAbstractTableModel, QModelIndex, QTemporaryFile, Signal, Slot
from PySide2.QtGui import QKeySequence, QColor
from PySide2.QtSvg import QSvgWidget
from PySide2.QtWidgets import QApplication, QHBoxLayout, QGridLayout, QMainWindow, QAction, QWidget, QTableView, \
    QHeaderView, QFileDialog, QLabel, QSpinBox, QCheckBox, QColorDialog, QComboBox
from svgwrite import Drawing, shapes

warnings.filterwarnings("ignore", category=DeprecationWarning)

CountryData = List[Tuple[str, float]]


def read_data_txt(filename: str) -> CountryData:
    country_data: CountryData = []
    with open(filename) as f:
        for line in f:
            tokens: List[str] = line.rstrip().split('\t')
            country_data.append((tokens[0], float(tokens[1])))
    return country_data


def guess_csv_locale(filename: str) -> str:
    n_lines: int = 0
    n_lines_with_semicolon: int = 0
    with open(filename) as f:
        for line in f:
            n_lines += 1
            if line.count(';') > 0:
                n_lines_with_semicolon += 1
    if n_lines == 0:
        return 'eng'
    elif n_lines_with_semicolon > n_lines // 2:
        return 'rus'
    else:
        return 'eng'


def read_data_csv(filename: str) -> CountryData:
    country_data: CountryData = []
    loc: str = guess_csv_locale(filename)
    with open(filename) as f:
        if loc == 'rus':
            reader: csv.reader = csv.reader(f, delimiter=';')
            for line in reader:
                country_data.append((line[0], float(line[1].replace(',', '.'))))
        elif loc == 'eng':
            reader: csv.reader = csv.reader(f, delimiter=',')
            for line in reader:
                country_data.append((line[0], float(line[1])))
        else:
            raise RuntimeError('Unknown locale {}'.format(loc))
    return country_data


def read_data(filename: str) -> CountryData:
    ext: str = os.path.splitext(filename)[1]
    if ext == '.txt':
        return read_data_txt(filename)
    elif ext == '.csv':
        return read_data_csv(filename)
    else:
        raise RuntimeError('Cannot read data from file {}: unregistered extension'.format(filename))


class SvgStyle:
    def __init__(self):
        self.line_length = 200
        self.line_color = 'black'
        self.line_width = 2
        self.circle_rad = 10
        self.circle_rad_normalization = True
        self.circle_fill_color = 'blue'
        self.circle_stroke_color = 'black'
        self.circle_stroke_width = 2


class StyleWidget(QWidget):
    style_changed = Signal(SvgStyle)

    def __init__(self, parent=None):
        super(StyleWidget, self).__init__(parent)

        self.label_line_length = QLabel(u'Длина линии')
        self.spinbox_line_length = QSpinBox()
        self.spinbox_line_length.setMinimum(10)
        self.spinbox_line_length.setMaximum(250)
        self.spinbox_line_length.setSingleStep(10)
        self.spinbox_line_length.setValue(200)

        self.label_line_width = QLabel(u'Толщина линии')
        self.spinbox_line_width = QSpinBox()
        self.spinbox_line_width.setMinimum(1)
        self.spinbox_line_width.setMaximum(10)
        self.spinbox_line_width.setSingleStep(1)
        self.spinbox_line_width.setValue(2)

        self.label_circle_rad = QLabel(u'Радиус круга')
        self.spinbox_circle_rad = QSpinBox()
        self.spinbox_circle_rad.setMinimum(1)
        self.spinbox_circle_rad.setMaximum(30)
        self.spinbox_circle_rad.setSingleStep(1)
        self.spinbox_circle_rad.setValue(10)

        self.label_line_color = QLabel(u'Цвет линии')
        self.combobox_line_color = QComboBox()
        self.combobox_line_color.addItem(u'черный', 'black')
        self.combobox_line_color.addItem(u'красный', 'red')
        self.combobox_line_color.addItem(u'зеленый', 'green')
        self.combobox_line_color.addItem(u'синий', 'blue')

        self.checkbox_normalize_circle_rad = QCheckBox(u'Круги одинакового размера')

        layout = QGridLayout()
        layout.addWidget(self.label_line_length, 0, 0, Qt.AlignRight)
        layout.addWidget(self.spinbox_line_length, 0, 1)
        layout.addWidget(self.label_line_width, 1, 0, Qt.AlignRight)
        layout.addWidget(self.spinbox_line_width, 1, 1)
        layout.addWidget(self.label_circle_rad, 2, 0, Qt.AlignRight)
        layout.addWidget(self.spinbox_circle_rad, 2, 1)
        layout.addWidget(self.label_line_color, 3, 0, Qt.AlignRight)
        layout.addWidget(self.combobox_line_color, 3, 1)
        layout.addWidget(self.checkbox_normalize_circle_rad, 4, 0, 1, 2)
        layout.setRowStretch(5, 1)
        self.setLayout(layout)

        self.spinbox_line_length.valueChanged.connect(self.on_change)
        self.spinbox_line_width.valueChanged.connect(self.on_change)
        self.spinbox_circle_rad.valueChanged.connect(self.on_change)
        self.combobox_line_color.activated.connect(self.on_change)
        self.checkbox_normalize_circle_rad.stateChanged.connect(self.on_change)
        self.on_change()

    @Slot()
    def on_change(self):
        style = SvgStyle()
        style.line_length = self.spinbox_line_length.value()
        style.line_width = self.spinbox_line_width.value()
        style.circle_stroke_width = self.spinbox_line_width.value()
        style.circle_rad = self.spinbox_circle_rad.value()
        style.line_color = self.combobox_line_color.currentData(Qt.UserRole)
        style.circle_stroke_color = self.combobox_line_color.currentData(Qt.UserRole)
        style.circle_rad_normalization = not self.checkbox_normalize_circle_rad.isChecked()
        self.style_changed.emit(style)


class CustomTableModel(QAbstractTableModel):
    def __init__(self, country_data=None):
        QAbstractTableModel.__init__(self)
        if country_data:
            self.countries, self.values = zip(*country_data)
            self.countries = list(self.countries)
            self.values = list(self.values)
        else:
            self.countries = []
            self.values = []

    def rowCount(self, parent=QModelIndex()):
        return len(self.values)

    def columnCount(self, parent=QModelIndex()):
        return 2

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return ("Country", "Value")[section]
        else:
            return "{}".format(section)

    def data(self, index, role=Qt.DisplayRole):
        column = index.column()
        row = index.row()

        if role == Qt.DisplayRole:
            if column == 0:
                return "{}".format(self.countries[row])
            elif column == 1:
                return "{:.6f}".format(self.values[row])
        elif role == Qt.BackgroundRole:
            return QColor(Qt.white)
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignRight

        return None


class Form(QMainWindow):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.svg_style = SvgStyle()

        self.temp_svg_file = QTemporaryFile()
        if not self.temp_svg_file.open():  # need to obtain temp file name
            raise RuntimeError('Cannot create temporary file for svg object')
        self.temp_svg_file.close()

        self.setWindowTitle(u'Круговая диаграмма')

        self.model = CustomTableModel()
        self.table_view = QTableView()
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.widget_svg = QSvgWidget()
        self.widget_style = StyleWidget()
        self.widget_style.style_changed.connect(self.style_updated)

        # central widget layout
        layout = QHBoxLayout()
        # size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        # size.setHorizontalStretch(1)
        # self.table_view.setSizePolicy(size)
        layout.addWidget(self.table_view)
        layout.addWidget(self.widget_svg)
        layout.addWidget(self.widget_style)

        self.widget_svg.setFixedSize(500, 500)

        widget_central = QWidget()
        widget_central.setLayout(layout)

        self.setCentralWidget(widget_central)

        # main menu
        self.menu = self.menuBar()
        self.menu_file = self.menu.addMenu("File")

        # load QAction
        action_load = QAction('Open', self)
        action_load.setShortcut(QKeySequence.Open)
        action_load.triggered.connect(self.load_data)
        self.menu_file.addAction(action_load)

        self.statusBar()

        # exit QAction
        action_exit = QAction('Exit', self)
        action_exit.setShortcut(QKeySequence.Quit)
        action_exit.triggered.connect(self.close)
        self.menu_file.addAction(action_exit)

        # window dimensions
        # geometry = qApp.desktop().availableGeometry(self)
        # self.setFixedSize(geometry.width() * 0.5, geometry.height() * 0.5)

    def load_data(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "Load data", dir="./tests",
                                                  filter="Text files (*.txt);;Excel data (*csv)")
        if filename:
            country_data: CountryData = read_data(filename)
            self.model = CustomTableModel(country_data)
            self.table_view.setModel(self.model)
            self.statusBar().showMessage("Data loaded and plotted")
            self.draw_diagram()

    def load_svg(self, filename) -> None:
        self.widget_svg.load(filename)

    def draw_diagram(self) -> None:
        n_countries: int = self.model.rowCount()
        if n_countries > 0:
            style: SvgStyle = self.svg_style
            delta_angle: float = 2.0*math.pi/n_countries
            max_value: float = max(self.model.values)
            dwg = Drawing(self.temp_svg_file.fileName(), profile='tiny', viewBox='-250 -250 500 500')
            for idx, v in enumerate(self.model.values):
                x: float = style.line_length * v/max_value * math.sin(idx * delta_angle)
                y: float = -style.line_length * v/max_value * math.cos(idx * delta_angle)
                dwg.add(shapes.Line(start=(0, 0), end=(x, y),
                                    stroke=style.line_color, stroke_width=style.line_width))
                radius: float = style.circle_rad
                if style.circle_rad_normalization:
                    radius *= v/max_value
                dwg.add(shapes.Circle(center=(x, y), r=radius,
                                      stroke=style.circle_stroke_color, stroke_width=style.circle_stroke_width,
                                      fill=style.circle_fill_color))
            dwg.save(pretty=True)
            self.load_svg(self.temp_svg_file.fileName())

    @Slot()
    def style_updated(self, style: SvgStyle):
        self.svg_style = style
        self.draw_diagram()


if __name__ == '__main__':
    app: QApplication = QApplication()

    form: Form = Form()

    form.show()
    sys.exit(app.exec_())
