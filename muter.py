from typing import List, Dict, Optional
import pulsectl

Device = pulsectl.PulseSourceInfo


class Muter:
    __client: pulsectl.Pulse
    usedDevice: Optional[Device] = None

    def __init__(self, client_name: str):
        self.__client = pulsectl.Pulse(client_name)

    @property
    def inputs(self) -> List[Device]:
        return self.__client.source_list()

    def getDevices(self) -> Dict[str, Device]:
        return {
            d.description: d
            for d in self.inputs
        }

    def useDevice(self, device: Device):
        self.usedDevice = device

    def mute(self):
        self.__client.mute(self.usedDevice, True)

    def unmute(self):
        self.__client.mute(self.usedDevice, False)

    def getClient(self) -> pulsectl.Pulse:
        return self.__client
