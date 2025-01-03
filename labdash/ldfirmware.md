# LDFirmware - a Helper Class to read Firmware and Parameters out of a Firmware Pack file

All electronic control modules (ECU) which are not hardwired need at least some firmware software. Additionally, several other software packs may come on top, like e.g. primary and secondary bootloaders. All these packets might need to have some parameters, which are stored again as additional files. Finally, each software might be needed in different compiled versions for different hardware platforms or hardware revisions it should run on.


This all gives a quite wide bunch of several files which needs to be handled to fill an ECU with all its different variants of software and parameters.

This is where LDFirmware comes in place. Instead of locally handle all these files independandly, they can be all stored together in a single zip file on a server. LDFirmware downloads the file by its URL and provide functions to access its content. LDFirmware uses only temporary files and remove them again at exit.


The knowledge about which file variants are to be used is still with the application itself, LDFirmware only provide the methods to access the different variants.

## The Variant Addressing Scheme
The scheme splits basically into two parts: The type of the software and its unique identifier.

To explain, let's say we have (at least) three different software blocks: A primary bootloader, a secondary bootloader and the application itself. All this is made for a special hardware variant which is called `special`

As the software blocks are mostly repeats between all kind of modules, we can standarize their names to avoid too much individual creative inventions. So it is highly recommended to use these standard names (the `type`) in all applications. If something is missing, please request an update of this list:

|   Type    | Function / Meaning     |
| :-------: | ---------------------- |
| prim_boot | Primary Bootloader     |
| sec_boot  | Secondary Bootloader   |
|    app    | The application itself |


## Usage
### Open a remote Firmware pack

Open a remote firmware pack is easy, as its URL is straight used in the class constructor. The constructor supports all additional parameters of the [requests.get()](https://requests.readthedocs.io/en/latest/api/#requests.get) function

    try:
        # read the firmware file from the given url
        fw=LDFirmware("http://localhost:8000/firmware.zip")

    except Exception as e:
        print("Error: ", e)
        raise e

Please note the surrounding Try/Except - Handler: For transperency reasons, LDFirmware does not catch exceptions by itself, but forwards them all to the main application, where they need to be handled.


After calling the constructor as above, the firmware is already temporary downloaded and can now accessed by some methods:

### Read the firmware Info

    # get the firmware info of the given identifier and type
    fw_info=fw.firmware_info("default","app")
    print(fw_info)

    {'firmware': 'firmware.bin', 'version': '1.0.0', 'date': '2020-01-01', 'size': 123456, 'parameter': 'parameter.json'}

This returns the info set which the author of the firmware pack has given as information

### Get a firmware file stream

    # get the firmware file stream handle of the given identifier and type
    f=fw.fetch_fileware_stream("default","app")
    print(f.read())

This return a read only file handle of the addressed firmware. If e.g. its file size is needed, then `firmware_info()` need to be called before and the size need to be read out of that.

### Get a Parameter data object

    # get the parameter data out of the json file of the given identifier and type
    parameter_object=fw.retrieve_json_parameters("default","app")
    print(parameter_object)

If the parameter file in the pack is a json file, then its data can be read directly as data object.

Please note that for parameters an automatic fallback mechanism comes in place: If the addressed firmware section does not have its dedicated parameter value, LDParameters searches for a generic `parameter`section and takes the parameters from there. This is mainly to just declare one parameter set for all the different variants of the same software, if applicable.

### Get a Parameter file stream

    # get the file stream handle of the given identifier and type
    f=fw.fetch_parameters_stream("special","app")
    print(f.read())
    
If the parameter file in the pack is any proprietary file format, then this function provides a read only file handle stream to it.

The fallback mechanism works in the same way as in `retrieve_json_parameters()`

## The Firmware Pack Format

The firmware pack file is a normal zip file containing all firmware binaries and parameter files.

As key element it also contains a file named `firmware.json` which contains all reference information for LDFirmware in the following format:

    {
        "default": {
            "app": {
                "firmware": "firmware.bin",
                "version": "1.0.0",
                "date": "2020-01-01",
                "size": 123456,
                "parameter": "parameter.json"
            }
        },
        "special": {
            "app": {
                "firmware": "special.bin",
                "version": "1.0.0",
                "date": "2020-01-01",
                "size": 123456
            }
        },
        "parameter": {
            "app": {
                "parameter": "parameter.mtpx"
            }
        }
    }

The top level identifiers (here the `default` and `special`) are the unique identifiers for the different software version. The top level identifier `parameter`is reserved for overall parameter sets.

The second level identifier is one of the standarized types (see section above), which address the final data set. Inside this data set the following key names are reserved:

| Key       | Function /Meaning                                                          |
| --------- | -------------------------------------------------------------------------- |
| firmware  | the name of the firmware file inside the zip archive. Optional, if needed  |
| size      | the size of the firmware file inside the zip archive. Optional, if needed  |
| parameter | the name of the parameter file inside the zip archive. Optional, if needed |

