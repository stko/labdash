from labdash.ldcanlisten import LDCANListen, rcv_collect
from abc import ABCMeta, abstractmethod

class LDModule(metaclass=ABCMeta):
    """Partly abstract class as base class for LabDash modules"""
    def __init__(self,name:str) -> None:
        self._name=name

    @property
    def name(self):
        return self._name


    @abstractmethod
    def hardware_ok():
        """
        returns true if the software decide that it's capable
        to handle the connected module
        """
        pass
    
    
    @abstractmethod
    def flash(self,url:str,flashing_process_indicator:function):
        """
        url: URL for download
        callback function
        flashing_process_indicator(progress_rate:int)
        progress_rate: Percentage 0-100
        
        In case of error, it raised a FLASH_ERROR exception
        
        """
        pass

    def parameterizing(self,tcpc:dict,parameter_template: dict,external_values: dict, parameter_set_selection:function):
        """
        tcpc: standarized vehicle option information dictionary
        parameter_template: the parameters of that module as template 
        external_values: additional information like VIN or date time
        
        callback function:
        parameter_set_selection(parameter_selection_list): selection
        The callback is called with a list of names to choose the wanted
        parameter set out of it.
        It returns the selected name
        
        In case of error, it raised a FLASH_PARAMETER exception
        
        """
        pass

    @abstractmethod
    def scan(self,bus, range=[]):
        '''
        scans on actual bus for modules in the range, if given
        returns a list of records containing id as bytearray and name as string, if available
        '''