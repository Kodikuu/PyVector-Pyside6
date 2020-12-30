__author__ = "Callum Watson"
__version__ = "0.0.1"
__license__ = "The Unlicense"

from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import *

class Visualiser(QWidget):
    def __init__(self, parent, taskbar=30):
        super().__init__()

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)

        self.parent = parent
        self.scr_width = self.parent.primaryScreen().size().width()
        self.scr_height = self.parent.primaryScreen().size().height()

        self.origin_y = self.scr_height - taskbar

        self.resize(self.scr_width, self.scr_height)


def main():
    app = QApplication()

    vis = Visualiser(app)
    vis.show()

    app.exec_()


if __name__ == "__main__":
    main()