import os
import math


class SoundVolumeView:
    path: str

    def __init__(self, path: str):
        self.path = path

    def __execute(self, cmd: str, dev: str, *args) -> int:
        return os.system(f"{self.path} /{cmd} \"{dev}\" {' '.join(args)}") // 256

    def mute(self, device_name: str):
        self.__execute("Mute", device_name)

    def unmute(self, device_name: str):
        self.__execute("Unmute", device_name)

    def setVolume(self, device_name: str, volume: int):
        self.__execute("SetVolume", device_name, volume)

    def getVolume(self, device_name: str) -> int:
        return self.__execute("GetPercent", device_name)

    def isMuted(self, device_name: str) -> bool:
        return self.__execute("GetMute", device_name) == 1
