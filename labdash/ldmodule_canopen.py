from labdash.ldmodule_can import LDMCan

class LDMCANOpenError(Exception):
    pass


class LDMCanOpen(LDMCan):
    """
    uses the LDCANBus, but provides also a CanOpen Protocol
    """


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._protocol = None
        
    def protocol_init(self,controller, port=0, bitrate=250000):
        """
        Initialisation of the CANOpen protocol
        """
        if not self._protocol:
            print("Protocol initialisation started")

        if not self._protocol:
            raise LDMCANOpenError

    @property
    def protocol(self):
        return self._protocol


