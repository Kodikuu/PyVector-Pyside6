__author__ = "Callum Watson"
__version__ = "0.0.1"
__license__ = "The Unlicense"

from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPaintEvent, QPainter, QPen, QBrush, QColor

import signal

class Visualiser(QWidget):
    def __init__(self, parent, taskbar=30, colour=(255, 255, 255)):
        super().__init__()

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)

        self.parent = parent
        self.scr_width = self.parent.primaryScreen().size().width()
        self.scr_height = self.parent.primaryScreen().size().height()

        self.resize(self.scr_width, self.scr_height)

        self.origin_y = self.scr_height - taskbar
        self.colour = colour
    
        timer = QTimer(self)
        timer.timeout.connect(self.update)
        timer.start()
    
    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setPen(QPen(QColor("#00000000")))
        painter.setBrush(QBrush(QColor(*self.colour)))



def main():
    signal.signal(signal.SIGINT, lambda x, y: QApplication.quit())
    app = QApplication()

    vis = Visualiser(app)
    vis.show()

    app.exec_()


if __name__ == "__main__":
    main()