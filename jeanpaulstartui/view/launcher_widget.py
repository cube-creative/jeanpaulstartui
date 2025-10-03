import os
import logging
import functools

from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from .flow_layout import FlowLayout

from jeanpaulstartui import ROOT
from jeanpaulstartui.view.progress_label import ProgressLabel
from jeanpaulstartui.utils import window_cache


def _clear_layout(layout):
    for i in reversed(range(layout.count())):
        layout.itemAt(i).widget().deleteLater()


class LauncherWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        self.mouse_pressed = False
        self.offset = QCursor()
        self.window_icon = QIcon(ROOT + '/resources/ceci-n-est-pas-une-icone.png')
        window_cache.restore_window_geometry(self)

        self.setMouseTracking(True)
        self.setObjectName('LauncherWidget')
        self.setWindowTitle('Jean-Paul Start')
        self.setWindowIcon(self.window_icon)
        self.setMinimumSize(385, 144)

        batches_widget = QWidget()
        self.batches_layout = FlowLayout(parent=batches_widget, spacing=0)
        batches_widget.setLayout(self.batches_layout)
        batches_widget.setContentsMargins(16, 16, 16, 16)
        self.batches_layout.setSpacing(16)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(batches_widget)
        self.scroll_area.setWidgetResizable(True)

        self.status_progress_bar = ProgressLabel()
        self.status_progress_bar.setFixedHeight(15)
        self.status_progress_bar.setObjectName("status")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.status_progress_bar)
        self.main_layout.setContentsMargins(8, 8, 8, 8)

        self.controller = None

        self.show()

    def refresh(self):
        QApplication.processEvents()

    def set_hourglass(self, is_hourglass):
        if is_hourglass:
            QApplication.setOverrideCursor(Qt.WaitCursor)
        else:
            QApplication.restoreOverrideCursor()

    def set_status_message(self, message):
        self.status_progress_bar.setText(message)

    def set_progress(self, value):
        self.status_progress_bar.set_progress(value)

    def set_version(self, version):
        self.set_status_message(version)

    def show(self):
        return QWidget.show(self)

    def closeEvent(self, event):
        window_cache.save_window_geometry(self)
        event.accept()

    def showNormal(self):
        self.activateWindow()
        return QWidget.showNormal(self)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F5:
            self.reload_batches()
        QWidget.keyPressEvent(self, event)

    def reload_batches(self):
        self.showNormal()
        QApplication.setOverrideCursor(Qt.BusyCursor)
        self.controller.update()
        QApplication.restoreOverrideCursor()

    def populate_layout(self, batches):
        _clear_layout(self.batches_layout)
        for batch in batches:
            batch_button = self._make_batch_button(batch)
            self.batches_layout.addWidget(batch_button)

    def _make_batch_button(self, batch):
        button = QPushButton(self)
        button_icon = QLabel()
        dpix = self.physicalDpiX()

        image_path = os.path.expandvars(batch.icon_path)
        if os.path.isfile(image_path):
            image = QImage(image_path)
        else:
            image = QImage(2, 2, QImage.Format_RGB16)
            logging.warning("Impossible to find " + image_path)
        button_icon.setPixmap(QPixmap.fromImage(image.scaled(
            dpix/2.4 if batch.version else dpix/2,
            dpix/2.4 if batch.version else dpix/2,
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )))

        button_icon.setAlignment(Qt.AlignCenter)
        button_icon.setTextInteractionFlags(Qt.NoTextInteraction)
        button_icon.setMouseTracking(False)
        button_icon.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button_icon.setContentsMargins(0, 8, 0, 0)

        label = self._setup_label_name(batch.name, batch.version and batch.stagings is None)
        if batch.description:
            button.setToolTip(batch.description)

        if batch.version:
            self._setup_version_label(batch.version, button_icon, dpix)

        button_layout = QVBoxLayout()

        button_layout.addWidget(button_icon)
        button_layout.addWidget(label)
        button_layout.setSpacing(0)
        button_layout.setContentsMargins(4, 4, 4, 4)

        button.setText('')
        button.setDefault(True)
        button.setFixedSize(dpix, dpix)
        button.setObjectName(batch.name + '_button')
        button.setLayout(button_layout)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.batch = batch
        self._setup_menu(batch, button, label)
        on_click = functools.partial(self.controller.batch_clicked, batch, batch.version)
        button.clicked.connect(on_click)
        return button

    def _setup_label_name(self, text, as_button=False):
        """ Create a label with a text and a word wrap.
        If as_button is True, the label will be a button.
        
        Args:
            text (str): Text to display
            as_button (bool): If True, the label will be a button
            
        Returns:
            QWidget: Label with the text

        """
        if not as_button:
            label = QLabel(text)
            label.setAlignment(Qt.AlignCenter | Qt.AlignBottom)
            label.setWordWrap(True)
            label.setTextInteractionFlags(Qt.NoTextInteraction)
            label.setMouseTracking(False)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        else:
            label = QPushButton(_add_return_line(text, 15))
            label.setMouseTracking(False)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            label.setStyleSheet('QPushButton::menu-indicator { image: none; width: 0px; }')
        return label

    def _setup_version_label(self, version, parent_widget, dpix):
        """ Create a label with a version text.
        Print it on the top right corner of the parent widget.
        """
        version_text = QLabel(version, parent=parent_widget)
        version_text.setAlignment(Qt.AlignRight | Qt.AlignTop)
        version_text.setTextInteractionFlags(Qt.NoTextInteraction)
        version_text.setMouseTracking(False)
        version_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        version_text.setGeometry(0, 0, dpix - 10, dpix)
        version_text.setStyleSheet('QLabel { color: #808080; }')

    def _setup_menu(self, batch, button, label):
        """ Create a menu for the button.
        If the batch has options, create a menu with the options (old staging system).
        If the batch has stagings, create a menu with the stagings.
        If the batch has old versions, create a menu with the versions.
        """
        if batch.options:
            options_menu = QMenu(button)
            for option in batch.options:
                option_action = options_menu.addAction(option.name)
                on_click = functools.partial(self.controller.batch_clicked, batch, option.name)
                option_action.triggered.connect(on_click)
            button.setMenu(options_menu)
        elif batch.stagings is not None:
            staging_menu = QMenu(button)
            for staging in batch.stagings:
                staging_action = staging_menu.addAction(staging)
                on_click = functools.partial(self.controller.batch_clicked, batch, staging)
                staging_action.triggered.connect(on_click)
            button.setMenu(staging_menu)
        elif batch.old_versions:
            versions_menu = QMenu(button)
            for version in batch.old_versions:
                version_action = versions_menu.addAction(version)
                on_click = functools.partial(self.controller.batch_clicked, batch, version)
                version_action.triggered.connect(on_click)
            label.setMenu(versions_menu)

def _add_return_line(string, length):
    """ Add return line at given string each time it reaches a given length
    Return line is add at the last space before the given length
    
    Args:
        string (str): String to add return line.
        length (int): Length at which return line is added.
        
    Returns:
        str: String with return line added
    """
    return_line = '\n'
    if len(string) > length:
        last_space = string.rfind(' ', 0, length)
        if last_space != -1:
            string = string[:last_space] + return_line + _add_return_line(string[last_space + 1:], length)
    return string

