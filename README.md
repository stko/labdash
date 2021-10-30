# LabDash - The Laboratory Dashboard

LabDash is, like many others, a python framework to generate a UI. But not like e.g. Qt, this generation is not done at compile time, but at runtime. It's also not a normal GUI window like e.g. Tinker, it is a webpage instead, where LabDash acts as the webserver to provides the page to the browser.

Through the webserver concept the display can be far away from the physical application, which can be e.g. build in as a black box an any industrial controls.

LabDash also covers the data transfer between page and software, so it takes the input events from the browser to the software and returns the results back into the browsers display elements.

By that the UI does not need to know the program internas and can be generic, and the application can concentrate on the pure data I/O and leaves the UI layout to the web designer.


## Once upon a time
Labdash can be seen as a rebirth of [OOBD](https://oobd.org). It uses the same princible and a part of the codebase, but it's much  slimmer and modernized by replacing the old lua compiling process by a JIT python runtime