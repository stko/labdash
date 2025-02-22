# LabDash - The Laboratory Dashboard

LabDash is, like many others, a python framework to generate a UI. But not like e.g. Qt, this generation is not done at compile time, but at runtime. It's also not a normal GUI window like e.g. Tinker, it is a webpage instead, where LabDash acts as the webserver to provides the page to the browser.

Through the webserver concept the display can be far away from the physical application, which can be e.g. build in as a black box an any industrial controls.

LabDash also covers the data transfer between page and software, so it takes the input events from the browser to the software and returns the results back into the browsers display elements.

By that the UI does not need to know the program internas and can be generic, and the application can concentrate on the pure data I/O and leaves the UI layout to the web designer.

## Installation

As Labdash can serve some functionalities to other programs, it's set up as a python module and runs also as a module

To install , use

    git clone https://github.com/stko/labdash.git
    cd labdash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install .

to run it

    python -m lapdash.labdash

## Once upon a time
Labdash can be seen as a rebirth of [OOBD](https://oobd.org). It uses the same princible and a part of the codebase, but it's much  slimmer and modernized by replacing the old lua compiling process by a JIT python runtime

## License
Labdash is released as LGPL + CC-BY-SA, so in can be use as library even in commercial proprietary closed projects, but with the CC-SA restriction: SHARE ALIKE: All modifications and additions to any generic functions must be published. This includes but is not limited to public available protocols (CANOpen, J1379, UDS etc.), system standard functionalities (IO, flashing, configuration, testing).
