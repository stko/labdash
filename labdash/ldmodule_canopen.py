import time
import can
import canopen
from labdash.ldmodule_can import LDMCan


class LDMCANOpenError(Exception):
    pass


class LDMCANMissing(Exception):
    pass


class LDMCANOpenMissing(Exception):
    pass


class LDMCanOpen(LDMCan):
    """
    uses the LDCANBus, but provides also a CanOpen Protocol
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._protocol = None
        self._listeners = None
        self._notifier = None
        self.node_id = 0

    def protocol_init(self, node_id: int):
        """
        Initialisation of the CANOpen protocol
        """
        if not self.bus:
            raise LDMCANMissing("No initialized CAN Bus for CANOpen")
        self.node_id = node_id
        if not self._protocol:
            print("Protocol initialisation started")
            self._protocol = canopen.Network()
            self._protocol.bus = self.bus

            self._listeners = [can.Printer()] + self._protocol.listeners
            self._notifier = can.Notifier(self._protocol.bus, self._listeners, 0.5)

        if not self._protocol:
            raise LDMCANOpenError

    @property
    def protocol(self):
        return self._protocol

    def scan(self) -> list:
        if not self._protocol:
            raise LDMCANOpenMissing("No initialized CANOpen protocol")
        self._protocol.scanner.reset()
        self._protocol.scanner.search()
        time.sleep(0.05)
        return self._protocol.scanner.nodes

    def shutdown(self):
        if self._protocol:
            self._protocol.disconnect()
