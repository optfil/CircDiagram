from typing import List, Tuple
import os
import csv
import sys
from PySide2.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QAction, QWidget, QTableView, QHeaderView, \
    QSizePolicy, QFileDialog
from PySide2.QtGui import QKeySequence, QColor
from PySide2.QtCore import qApp, Qt, QAbstractTableModel, QModelIndex

import warnings
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


class CustomTableModel(QAbstractTableModel):
    def __init__(self, country_data=None):
        QAbstractTableModel.__init__(self)
        self.countries, self.values = zip(*country_data)
        self.countries = list(self.countries)
        self.values = list(self.values)

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

        self.setWindowTitle(u'Круговая диаграмма')

        # creating a QTableView
        self.table_view = QTableView()

        # QTableView headers
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # central widget layout
        central_layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size.setHorizontalStretch(1)
        self.table_view.setSizePolicy(size)
        central_layout.addWidget(self.table_view)

        central_widget = QWidget()
        central_widget.setLayout(central_layout)

        self.setCentralWidget(central_widget)

        # main menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        # load QAction
        load_action = QAction('Open', self)
        load_action.setShortcut(QKeySequence.Open)
        load_action.triggered.connect(self.load_data)
        self.file_menu.addAction(load_action)

        # exit QAction
        exit_action = QAction('Exit', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)

        # status Bar
        self.status = self.statusBar()
        self.status.showMessage("Data loaded and plotted")

        # window dimensions
        geometry = qApp.desktop().availableGeometry(self)
        self.setFixedSize(geometry.width() * 0.5, geometry.height() * 0.5)

    def load_data(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load data", dir="./tests",
                                                  filter="Text files (*.txt);;Excel data (*csv)")
        if filename:
            country_data: CountryData = read_data(filename)
            model = CustomTableModel(country_data)
            self.table_view.setModel(model)


if __name__ == '__main__':
    app: QApplication = QApplication()

    form: Form = Form()

    form.show()
    sys.exit(app.exec_())
