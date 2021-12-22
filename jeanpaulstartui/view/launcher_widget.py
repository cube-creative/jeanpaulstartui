import os
import sys
import logging
from Qt5 import QtWidgets, QtCore, QtGui

from jeanpaulstartui import ROOT
from jeanpaulstartui.view.flow_layout import FlowLayout
from jeanpaulstartui.view.progress_label import ProgressLabel


def _clear_layout(layout):
    for i in reversed(range(layout.count())):
        layout.itemAt(i).widget().deleteLater()


class LauncherWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(LauncherWidget, self).__init__(parent=parent)

        self.mouse_pressed = False
        self.offset = QtGui.QCursor()
        self.window_icon = QtGui.QIcon(ROOT + '/resources/ceci-n-est-pas-une-icone.png')

        self.settings = QtCore.QSettings('CubeCreative', 'JeanPaulStart')
        
        geometry = self.settings.value('geometry', '')
        if not isinstance(geometry, QtCore.QByteArray):
            geometry = QtCore.QByteArray(geometry.encode("utf-8"))
        self.restoreGeometry(geometry)

        self.setMouseTracking(True)
        self.setObjectName('LauncherWidget')
        self.setWindowTitle('Jean-Paul Start')
        self.setWindowIcon(self.window_icon)
        self.setMinimumSize(376, 144)
        self.setWindowFlags(
            QtCore.Qt.CustomizeWindowHint |
            QtCore.Qt.Dialog |
            QtCore.Qt.WindowCloseButtonHint |
            QtCore.Qt.WindowMinimizeButtonHint |
            QtCore.Qt.WindowSystemMenuHint
        )

        batches_widget = QtWidgets.QWidget()
        self.batches_layout = FlowLayout(parent=batches_widget, spacing=0)
        batches_widget.setLayout(self.batches_layout)
        batches_widget.setContentsMargins(16, 16, 16, 16)
        self.batches_layout.setSpacing(16)

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidget(batches_widget)
        self.scroll_area.setWidgetResizable(True)

        self.status_progress_bar = ProgressLabel()
        self.status_progress_bar.setFixedHeight(15)
        self.status_progress_bar.setObjectName("status")

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.status_progress_bar)
        self.main_layout.setContentsMargins(8, 8, 8, 8)

        self.controller = None

        self.tray = QtWidgets.QSystemTrayIcon()
        self.tray.setIcon(self.window_icon)
        self.tray.setToolTip('Jean-Paul Start')
        self.tray.setVisible(True)
        self.tray.activated.connect(self.showNormalReason)

        menu = QtWidgets.QMenu()
        self.version_menu = menu.addAction('')
        self.version_menu.setDisabled(True)
        menu.addSeparator()
        open_action = menu.addAction("Open Jean-Paul Start")
        open_action.triggered.connect(self.showNormal)
        reload_action = menu.addAction("Reload batches")
        reload_action.triggered.connect(self.reload_batches)
        menu.addSeparator()
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(sys.exit)
        self.tray.setContextMenu(menu)

    def refresh(self):
        QtWidgets.QApplication.processEvents()

    def set_hourglass(self, is_hourglass):
        if is_hourglass:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        else:
            QtWidgets.QApplication.restoreOverrideCursor()

    def set_status_message(self, message):
        self.status_progress_bar.setText(message)

    def set_progress(self, value):
        self.status_progress_bar.set_progress(value)

    def set_version(self, version):
        self.version_menu.setText(version)
        self.set_status_message(version)

    def show(self):
        self.tray.show()
        return super(LauncherWidget, self).show()

    def showNormal(self):
        self.activateWindow()
        return super(LauncherWidget, self).showNormal()

    def showNormalReason(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger:
            self.showNormal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F5:
            self.reload_batches()
        super(LauncherWidget, self).keyPressEvent(event)

    def reload_batches(self):
        self.showNormal()
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.BusyCursor)
        self.controller.update()
        QtWidgets.QApplication.restoreOverrideCursor()

    def populate_layout(self, batches):
        _clear_layout(self.batches_layout)
        for batch in batches:
            batch_button = self._make_batch_button(batch)
            self.batches_layout.addWidget(batch_button)

    def _make_batch_button(self, batch):
        button = QtWidgets.QPushButton(self)
        button_icon = QtWidgets.QLabel()

        image_path = os.path.expandvars(batch.icon_path)
        if os.path.isfile(image_path):
            image = QtGui.QImage(image_path)
        else:
            image = QtGui.QImage(2, 2, QtGui.QImage.Format_RGB16)
            logging.warn("Impossible to find " + image_path)
        button_icon.setPixmap(QtGui.QPixmap.fromImage(image.scaled(
            48,
            48,
            QtCore.Qt.KeepAspectRatioByExpanding,
            QtCore.Qt.SmoothTransformation
        )))

        button_icon.setAlignment(QtCore.Qt.AlignCenter)
        button_icon.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        button_icon.setMouseTracking(False)
        button_icon.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        button_icon.setContentsMargins(0, 8, 0, 0)

        batch_name = batch.name
        button_text = QtWidgets.QLabel(batch_name)
        button_text.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom)
        button_text.setWordWrap(True)
        button_text.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        button_text.setMouseTracking(False)
        button_text.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        button_layout = QtWidgets.QVBoxLayout()
        button_layout.addWidget(button_icon)
        button_layout.addWidget(button_text)
        button_layout.setSpacing(0)
        button_layout.setContentsMargins(4, 4, 4, 4)

        button.setText('')
        button.setDefault(True)
        button.setFixedSize(96, 96)
        button.setObjectName(batch.name + '_button')
        button.setLayout(button_layout)
        button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        button.batch = batch
        button.clicked.connect(self._batch_clicked)

        return button

    def closeEvent(self, event):
        self.settings.setValue('geometry', self.saveGeometry())
        self.hide()
        event.ignore()

    def _batch_clicked(self):
        batch_button = self.sender()
        self.controller.batch_clicked(batch_button.batch)
