from ldcanlisten import LDCANListen, rcv_collect
from abc import ABCMeta, abstractmethod

class LDModule(metaclass=ABCMeta):
    """Partly abstract class as base class for LabDash modules"""
    def __init__(self,name:str) -> None:
        self._name=name

    @property
    def name(self):
        return self._name

    @abstractmethod
    def flash(self,start,length,data:bytearray):
        pass

    @abstractmethod
    def scan(self,bus, range=[]):
        '''
        scans on actual bus for modules in the range, if given
        returns a list of records containing id as bytearray and name as string, if available
        '''