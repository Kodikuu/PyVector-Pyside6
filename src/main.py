__author__ = "Callum Watson"
__version__ = "0.0.1"
__license__ = "The Unlicense"

from PySide6.QtWidgets import QApplication, QWidget

class Visualiser(QWidget):
    def __init__(self, parent, taskbar=30):
        super().__init__()

        self.parent = parent
        self.scr_width = self.parent.primaryScreen().size().width()
        self.scr_height = self.parent.primaryScreen().size().height()

        self.origin_y = self.scr_height - taskbar


def main():
    app = QApplication()

    vis = Visualiser(app)
    vis.show()

    app.exec_()


if __name__ == "__main__":
    main()