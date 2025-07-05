import shutil
import tempfile
import zipfile
import requests
import json

# for local file support, add https://pypi.org/project/requests-file/


class LDFirmware:
    """
    loads a firmware file and provides access to the firmware data
    """

    def __init__(self, url: str, *args, **kwargs):
        """
        initializes the firmware object with the given url
        supports all requests.get parameters
        """
        try:
            response = requests.get(url, *args, stream=True, **kwargs)
            self.temp_file = tempfile.TemporaryFile()
            shutil.copyfileobj(response.raw, self.temp_file)
            self.temp_file.seek(0)
            self.zip = zipfile.ZipFile(self.temp_file)
            self.zip_files = self.zip.namelist()
            if "firmware.json" in self.zip_files:
                f = self.zip.open("firmware.json")
                self.firmware_details = json.load(f)
            else:
                self.firmware_details = {}
            f = self.zip.open(self.zip_files[0])
        except Exception as e:
            print("Error: ", e)
            raise e

    def firmware_info(self, identifier: str, type: str) -> dict:
        """
        returns the firmware info of the given identifier, otherways none
        """
        if identifier in self.firmware_details:
            firmware_section = self.firmware_details[identifier]
            if type in firmware_section:
                return firmware_section[type]
        return None

    def fetch_firmware_stream(self, identifier: str, type: str) -> zipfile.ZipExtFile:
        """
        returns the firmware content of the given identifier and type as file stream object
        """
        section = self.firmware_info(identifier, type)
        if section and "firmware" in section:
            firmware_file_name = section["firmware"]
            if firmware_file_name in self.zip_files:
                f = self.zip.open(firmware_file_name)
                return f
        return None

    def retrieve_json_parameters(self, identifier: str, type: str) -> dict:
        """
        if the parameter file is a json file, it can be read directly as data object with this function

        if the identifier section contains its own parameter, then this is used, otherways the generic
        'parameter' directive

        if both conditions do not match, the function return None
        """
        section = self.firmware_info(identifier, type)
        if section and "parameter" in section:
            parameter_file_name = section["parameter"]
            if parameter_file_name in self.zip_files:
                return json.load(self.zip.open(parameter_file_name))
            # no specific parameters? Try to load the generic one
            if "parameter" in self.firmware_details:
                parameter_section = self.firmware_details["parameter"]
                if type in parameter_section:
                    parameter_file_name = parameter_section[type]
                    if parameter_file_name in self.zip_files:
                        return json.load(self.zip.open(parameter_file_name))
        return None

    def retrieve_parameter_node_id(self, identifier: str, type: str) -> dict:
        """
        reads the node_id to where the parameters shall be send to

        if the identifier section contains its own parameter, then this is used, otherways the generic
        'parameter' directive

        if both conditions do not match, the function return None
        """
        section = self.firmware_info(identifier, type)
        if section and "nodeid" in section:
            return section["nodeid"]
        # no specific parameters? Try to load the generic one
        if "nodeid" in self.firmware_details:
            return self.firmware_details["nodeid"]
        return None

    def fetch_parameters_stream(self, identifier: str, type: str) -> zipfile.ZipExtFile:
        """
        returns the parameter content of the given identifier and type as file stream object

        if the identifier section contains its own parameter, then this is used, otherways the generic
        'parameter' directive

        if both conditions do not match, the function return None
        """
        section = self.firmware_info(identifier, type)
        if section and "parameter" in section:
            parameter_file_name = section["parameter"]
            if parameter_file_name in self.zip_files:
                f = self.zip.open(parameter_file_name)
                return f
        # no specific parameters? Try to load the generic one
        if "parameter" in self.firmware_details:
            parameter_section = self.firmware_details["parameter"]
            if type in parameter_section:
                parameter_info = parameter_section[type]
                if "parameter" in parameter_info:
                    parameter_file_name = parameter_info["parameter"]
                    if parameter_file_name in self.zip_files:
                        f = self.zip.open(parameter_file_name)
                        return f
        return None

    def __del__(self):
        """
        destructor, closes the temporary file
        """
        try:
            self.temp_file.close()
        except Exception as e:
            pass


if __name__ == "__main__":
    try:
        # read the firmware file from the given url
        fw = LDFirmware("http://localhost:8000/firmware.zip")

        # get the firmware info of the given identifier and type
        fw_info = fw.firmware_info("default", "app")
        print(fw_info)

        # get the firmware file stream handle of the given identifier and type
        f = fw.fetch_firmware_stream("default", "app")
        print(f.read())

        # get the parameter data out of the json file of the given identifier and type
        parameter_object = fw.retrieve_json_parameters("default", "app")
        print(parameter_object)

        # get the file stream handle of the given identifier and type
        f = fw.fetch_parameters_stream("special", "app")
        print(f.read())
    except Exception as e:
        print("Error: ", e)
        raise e
