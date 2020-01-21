from typing import List, Tuple
import os
import csv
import sys
from PySide2.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QAction, QWidget, QTableView, QHeaderView, \
    QSizePolicy
from PySide2.QtGui import QKeySequence, QColor
from PySide2.QtCore import Slot, qApp, Qt, QAbstractTableModel, QModelIndex

CountryData = List[Tuple[str, float]]


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


class CentralWidget(QWidget):
    def __init__(self, country_data: CountryData):
        QWidget.__init__(self)

        # Getting the Model
        self.model = CustomTableModel(country_data)

        # Creating a QTableView
        self.table_view = QTableView()
        self.table_view.setModel(self.model)

        # QTableView Headers
        self.horizontal_header = self.table_view.horizontalHeader()
        self.vertical_header = self.table_view.verticalHeader()
        self.horizontal_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.vertical_header.setSectionResizeMode(QHeaderView.ResizeToContents)

        # QWidget Layout
        self.main_layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Left layout
        size.setHorizontalStretch(1)
        self.table_view.setSizePolicy(size)
        self.main_layout.addWidget(self.table_view)

        # Set the layout to the QWidget
        self.setLayout(self.main_layout)


class Form(QMainWindow):

    def __init__(self, central: QWidget, parent=None):
        super(Form, self).__init__(parent)

        self.setWindowTitle(u'Круговая диаграмма')
        self.setCentralWidget(central)
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        # Exit QAction
        exit_action = QAction('Exit', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)

        self.file_menu.addAction(exit_action)

        # Status Bar
        self.status = self.statusBar()
        self.status.showMessage("Data loaded and plotted")

        # Window dimensions
        geometry = qApp.desktop().availableGeometry(self)
        self.setFixedSize(geometry.width() * 0.5, geometry.height() * 0.5)

        # self.edit = QLineEdit("Write my name here", None)
        # self.button = QPushButton("Show Greetings", None)
        #
        # layout = QVBoxLayout()
        # layout.addWidget(self.edit)
        # layout.addWidget(self.button)
        #
        # self.setLayout(layout)
        #
        # self.button.clicked.connect(self.greetings)


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


if __name__ == '__main__':
    app: QApplication = QApplication()

    data: CountryData = read_data('tests/data.csv')
    central_widget: CentralWidget = CentralWidget(data)
    form: Form = Form(central_widget)

    form.show()
    sys.exit(app.exec_())
