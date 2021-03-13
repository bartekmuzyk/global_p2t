# 1.0
import platform
import sys
import json
import math
import os
from typing import List, Dict, Optional, Any, TextIO, Final
from pathlib import Path
import pynput.keyboard as kb
from pynput.keyboard import Key
from PyQt5 import uic
from PyQt5.QtGui import QFontMetrics, QFont
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QRunnable, QThreadPool, QObject
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMessageBox as MsgBox
import pymsgbox

PERSIST_FILE: Final[str] = "persist"
persist_data: Dict[str, Any] = {}

if Path(PERSIST_FILE).exists():
    with open(PERSIST_FILE, "r") as f:
        persist_data = json.loads(f.read())
        print(persist_data)
        f.close()
else:
    persist_data = {}

target_os = "windows" or platform.system().lower()
SVV_PATH: Optional[str] = None

if target_os == "linux":
    from muter import Muter, Device
elif target_os == "windows":
    SVV_EXE: Final = "SoundVolumeView.exe"
    paths: List[str] = os.getenv("PATH").split(';')

    for path in paths:
        full_path: str = f"{path}{SVV_EXE}" if path.endswith('\\') else f"{path}\\{SVV_EXE}"
        if Path(full_path).is_file():
            SVV_PATH = full_path
            break

    if not SVV_PATH:
        SVV_PATH = pymsgbox.prompt(
            title="Nie znaleziono programu",
            text=f"Ta aplikacja wymaga narzędzia {SVV_EXE}, którego nie znaleziono.\nPodaj ścieżkę do programu tutaj.",
            default=f"C:\\Windows\\System32\\{SVV_EXE}"
        )
        if not SVV_PATH:
            sys.exit(0)

    while not Path(SVV_PATH).is_file():
        SVV_PATH = pymsgbox.prompt(
            title="Nie znaleziono programu",
            text=f"Ścieżka {SVV_PATH} jest niepoprawna.",
            default=SVV_PATH
        )
        if not SVV_PATH:
            sys.exit(0)

    persist_data["SVV"] = SVV_PATH

    from windows_muter import Muter, Device
else:
    pymsgbox.alert(
        title="Brak wsparcia",
        text=f"Ten program nie obsługuje twojego systemu ({target_os}).",
        button="Zamknij program"
    )
    sys.exit(1)


def get_persisted_device() -> Optional[str]:
    return persist_data.get("device", None)


def ellipsis_text(font: QFont, max_width: int, text: str) -> str:
    metrics = QFontMetrics(font)
    return metrics.elidedText(text, Qt.ElideRight, max_width)


class Communicator(QObject):
    shortcutPressed = pyqtSignal()
    shortcutReleased = pyqtSignal()


COM: Final = Communicator()


class ShortcutHandler(QRunnable):
    shortcut: Key = Key.f10
    paused: bool = False
    __pressed: bool = False

    def on_press(self, key):
        global COM
        if not self.paused and key == self.shortcut and not self.__pressed:
            COM.shortcutPressed.emit()
            self.__pressed = True

    def on_release(self, key):
        global COM
        if not self.paused and key == self.shortcut:
            COM.shortcutReleased.emit()
            self.__pressed = False

    @pyqtSlot()
    def run(self):
        listener = kb.Listener(on_press=self.on_press, on_release=self.on_release)
        listener.start()


class Ui(QMainWindow):
    muter = Muter("push2talk")
    devices: Dict[str, Device]
    currentSelection: Optional[str] = None
    enabledDeviceName: Optional[str] = None
    DEFAULT_TITLE: str

    shortcutHandler: ShortcutHandler
    keyboardThread = QThreadPool()

    centralwidget: QWidget
    inputList: QListWidget
    title: QLabel
    controlPanel: QFrame
    enableBtn: QPushButton
    volumeSlider: QSlider
    volumeDisplay: QLCDNumber

    actionRefreshDevices: QAction
    actionToggle: QAction

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("config_window.ui", self)
        self.setFixedSize(self.width(), self.height())  # Make window non-resizable
        self.DEFAULT_TITLE = self.title.text()
        self.show()
        self.__connect()
        self.__startup()

    def __connect(self):
        global COM
        self.inputList.itemSelectionChanged.connect(self.deviceSelected)
        self.enableBtn.clicked.connect(self.deviceEnabled)
        self.volumeSlider.sliderReleased.connect(self.volumeSet)

        self.actionRefreshDevices.triggered.connect(self.refreshDevicesAction)
        self.actionToggle.triggered.connect(self.toggleService)

        COM.shortcutPressed.connect(self.shortcutPressed)
        COM.shortcutReleased.connect(self.shortcutReleased)

    def __startup(self):
        self.refreshDevices()
        # Check if there's a default device set and if it's connected
        device_name: Optional[str] = get_persisted_device()
        if device_name is not None:
            if device_name in self.devices:
                self.enabledDeviceName = device_name
                self.muter.useDevice(self.devices[self.enabledDeviceName])
                self.muter.mute()
            else:
                MsgBox.warning(
                    self,
                    "Brak urządzenia",
                    f"Poprzednio ustawione urządzenie ({device_name}) nie jest podłączone."
                )
        self.inputList.addItems(self.devices.keys())
        if self.inputList.count() == 0:
            MsgBox.warning(
                self,
                "Global P2T",
                "Nie wykryto żadnych urządzeń wejściowych."
            )
        self.actionRefreshDevices.setEnabled(True)
        self.shortcutHandler = ShortcutHandler()
        self.keyboardThread.start(self.shortcutHandler)

    def __setTitle(self, text: str):
        _ = ellipsis_text(self.title.font(), self.title.width(), text)
        self.title.setText(_)

    def getVolumeOfSelectedDevice(self) -> int:
        return math.ceil(self.muter.getClient().volume_get_all_chans(self.selectedDevice) * 100)

    @property
    def selectedDevice(self) -> Device:
        return self.devices[self.currentSelection]

    def refreshDevices(self):
        self.controlPanel.setVisible(False)
        self.title.setText(self.DEFAULT_TITLE)
        self.devices = self.muter.getDevices()

    def updateInputList(self):
        self.inputList.clear()
        self.inputList.addItems(self.devices.keys())

    @pyqtSlot()
    def refreshDevicesAction(self):
        self.actionRefreshDevices.setEnabled(False)
        self.refreshDevices()
        self.updateInputList()
        self.actionRefreshDevices.setEnabled(True)

    @pyqtSlot()
    def toggleService(self):
        pause: bool = not self.actionToggle.isChecked()
        self.shortcutHandler.paused = pause
        if pause:
            self.actionRefreshDevices.setEnabled(False)
            self.centralwidget.hide()
            self.muter.unmute()
        else:
            self.actionRefreshDevices.setEnabled(True)
            self.centralwidget.show()
            self.muter.mute()

    @pyqtSlot()
    def deviceSelected(self):
        selection: str = self.inputList.currentItem().text()
        self.__setTitle(selection)
        self.currentSelection = selection
        self.controlPanel.setVisible(True)
        volume: int = self.getVolumeOfSelectedDevice()
        self.volumeSlider.setValue(volume)
        self.volumeDisplay.display(volume)
        if self.enabledDeviceName is not None:
            self.enableBtn.setEnabled(selection != self.enabledDeviceName)

    @pyqtSlot()
    def deviceEnabled(self):
        global persist_data
        selection: str = self.currentSelection
        persist_data["device"] = selection
        if self.muter.usedDevice is not None:
            self.muter.unmute()
        self.muter.useDevice(self.selectedDevice)
        self.enableBtn.setEnabled(False)
        self.muter.mute()
        self.enabledDeviceName = selection

    @pyqtSlot()
    def shortcutPressed(self):
        self.muter.unmute()

    @pyqtSlot()
    def shortcutReleased(self):
        self.muter.mute()

    @pyqtSlot()
    def volumeSet(self):
        volume: float = self.volumeSlider.value() / 100
        self.muter.getClient().volume_set_all_chans(self.selectedDevice, volume)


app = QApplication(sys.argv)
window = Ui()
app.exec_()

if persist_data != {}:
    with open(PERSIST_FILE, "w") as persist_file:
        serialized: str = json.dumps(persist_data)
        persist_file.write(serialized)
