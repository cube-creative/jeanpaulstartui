from Qt5 import QtCore, QtWidgets, QtGui


class ProgressLabel(QtWidgets.QLabel):

    def __init__(self, parent=None):
        super(ProgressLabel, self).__init__(parent=parent)
        self._progress = 0.0

    def set_progress(self, value):
        self._progress = value

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QColor(61, 174, 233))
        painter.drawRect(event.rect().adjusted(0, 13, -self.width()*(1 - self._progress), 0))
        painter.end()

        super(ProgressLabel, self).paintEvent(event)
