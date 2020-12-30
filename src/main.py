__author__ = "Callum Watson"
__version__ = "0.0.1"
__license__ = "The Unlicense"

from PySide6.QtWidgets import QApplication, QWidget

class Visualiser(QWidget):
    def __init__(self):
        super().__init__()


def main():
    app = QApplication()

    vis = Visualiser()
    vis.show()

    app.exec_()


if __name__ == "__main__":
    main()