import os
import sys
import logging
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from jeanpaulstartui import ROOT, launch_widget


if __name__ == '__main__':
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    app = QApplication(sys.argv)
    with open(ROOT + '/resources/stylesheet.css', 'r') as f_stylesheet:
        stylesheet = str(f_stylesheet.read())
    app.setStyleSheet(stylesheet)

    launch_widget()

    app.exec_()
