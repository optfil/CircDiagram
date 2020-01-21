from typing import List, Tuple
import sys
from PySide2.QtWidgets import QLineEdit, QPushButton, QApplication, QVBoxLayout, QDialog

CountryData = List[Tuple[str, float]]


class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.edit = QLineEdit("Write my name here")
        self.button = QPushButton("Show Greetings")

        layout = QVBoxLayout()
        layout.addWidget(self.edit)
        layout.addWidget(self.button)

        self.setLayout(layout)

        self.button.clicked.connect(self.greetings)

    def greetings(self):
        print("Hello %s" % self.edit.text())


def read_data(filename: str) -> CountryData:
    data: CountryData = []
    with open(filename) as f:
        for line in f:
            tokens: List[str] = line.rstrip().split('\t')
            data.append((tokens[0], float(tokens[1])))
    return data


def main() -> None:
    print(read_data('tests/data.txt'))


if __name__ == '__main__':
    app = QApplication()
    form: Form = Form()
    form.show()
    sys.exit(app.exec_())
