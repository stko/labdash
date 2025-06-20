from labdash.ldcanlisten import LDCANListen, rcv_collect
from abc import ABCMeta, abstractmethod, abstractproperty
from collections.abc import Callable


class LDMNotImplemented(Exception):
    """
    the abstract model concept requires to implement all methods. So if a
    implementation does not support a     particular method, it has to throw this
    LDMNotImplemented inside its method implementation to indicate that a unsupported
    method is called
    """


class LDMFlashError(Exception):
    pass


class LDMParameterError(Exception):
    pass


class LDMEraseError(Exception):
    pass


class LDModule(metaclass=ABCMeta):
    """Partly abstract class as base class for LabDash modules"""

    def __init__(self, name: str) -> None:
        self._name = name
        self.closeHandlers = set()

    @property
    def name(self):
        return self._name

    @property
    @abstractmethod
    def bus(self):
        """
        returns the class specific communication bus, if any
        """

    @property
    @abstractmethod
    def protocol(self):
        """self
        returns the class specific protocol driver, if any
        """

    @abstractmethod
    def hardware_ok(self):
        """
        returns true if the software decide that it's capable
        to handle the connected module
        """

    @abstractmethod
    def flash(self, url: str, flashing_process_indicator: Callable):
        """
        url: URL for download
        callback function
        flashing_process_indicator(progress_rate:int)
        progress_rate: Percentage 0-100

        In case of error, it raises a LDMFlashError exception

        """

    @abstractmethod
    def parameterizing(
        self,
        tcpc: dict,
        parameter_template: dict,
        external_values: dict,
        parameter_set_selection: Callable,
    ) -> bool:
        """
        tcpc: standarized vehicle option information dictionary
        parameter_template: the parameters of that module as template
        external_values: additional information like VIN or date time

        callback function:
        parameter_set_selection(parameter_selection_list): selection
        The callback is called with a list of names to choose the wanted
        parameter set out of it.
        It returns the selected name

        In case of error, it raises a LDMParameterError exception

        """

    @abstractmethod
    def scan(self, scan_range: list = None) -> list:
        """
        scans on actual bus for modules in the range, if given
        returns a list of records containing id as bytearray and name as string, if available

        In case of error, it raises a FLASH_PARAMETER exception
        """

    @abstractmethod
    def erase(self, scan_range: list = None) -> bool:
        """
        scans on actual bus for modules in the range, if given
        returns a list of records containing id as bytearray and name as string, if available

        In case of error, it raises a LDMEraseError exception
        """

    @abstractmethod
    def write_parameters(self, parameters: dict) -> bool:
        """
        writes the given parameters to the module

        In case of error, it raises a LDMParameterError exception
        """

    def add_close_handler(self, close_handler):
        self.closeHandlers.add(close_handler)

    def stop(self, timeout=0):
        """stops the child thread. If timeout > 0, it will wait timeout secs for the thread to finish"""

        for handler in self.closeHandlers:
            print("close handler")
            handler()  # call all close handlers
