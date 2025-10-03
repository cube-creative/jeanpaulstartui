from PySide6.QtCore import Qt, QRect


class WindowPosition:
    @staticmethod
    def restore(widget, data):
        if data['maximized']:
            widget.setWindowState(Qt.WindowMaximized)
        else:
            geometry = QRect()
            geometry.setCoords(*data['geometry'])
            widget.setGeometry(geometry)

    @staticmethod
    def save(widget):
        return {
            'geometry': widget.geometry().getCoords(),
            'maximized': bool(widget.windowState() & Qt.WindowMaximized)
        }
