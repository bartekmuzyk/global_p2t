from typing import List, Dict, Optional, Final
import speech_recognition as sr
from svv import SoundVolumeView


SVV: SoundVolumeView


class Device:
    name: str
    __volume: float = .0,
    __muted: bool = False

    def __init__(self, name: str):
        self.name = name

    @property
    def volume(self) -> float:
        return self.__volume

    @volume.setter
    def volume(self, val: float):
        SVV.setVolume(self.name, val)
        self.__volume = val

    @property
    def muted(self) -> bool:
        return self.__muted

    @muted.setter
    def muted(self, val: bool):
        global SVV
        SVV.mute(self.name) if val else SVV.unmute(self.name)
        self.__muted = val

    def __repr__(self):
        return f"<windows_muter.Device {self.id=} {self.name=} {self.volume=} {self.muted=}>"


class Client:
    def volume_set_all_chans(self, device: Device, volume: float):
        device.volume = volume

    def volume_get_all_chans(self, device: Device) -> float:
        return device.volume / 100

    def mute(self, device: Device, mute: bool):
        device.muted = mute

    def source_list(self) -> List[Device]:
        input_list: List[str] = sr.Microphone.list_microphone_names()
        return [Device(device_name) for device_name in input_list]


class Muter:
    __client: Client
    __nir: str
    usedDevice: Optional[Device] = None

    def __init__(self, _: str, svv_path: str):
        global SVV
        self.__client = Client()
        SVV = SoundVolumeView(svv_path)

    @property
    def inputs(self) -> List[Device]:
        return self.__client.source_list()

    def getDevices(self) -> Dict[str, Device]:
        return {
            d.name: d
            for d in self.inputs
        }

    def useDevice(self, device: Device):
        self.usedDevice = device

    def mute(self):
        self.__client.mute(self.usedDevice, True)

    def unmute(self):
        self.__client.mute(self.usedDevice, False)

    def getClient(self) -> Client:
        return self.__client
