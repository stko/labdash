import time
from labdash.ldcanbus import LDCANBus
from labdash.ldmodule import LDModule


class LDMCANError(Exception):
    pass


class LDMCan(LDModule):
    """Extents the generic LDModule with a can bus connector"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bus = None
        
    def bus_init(self,controller, port=0, bitrate=250000):
        """
        Initialisation of the CAN bus
        """
        if not self._bus:
            print("Bus initialisation started")
            self._bus = LDCANBus(controller, port=port, bitrate=bitrate)
            time.sleep(0.5)
        if not self._bus:
            raise LDMCANError

    @property
    def bus(self):
        return self._bus


