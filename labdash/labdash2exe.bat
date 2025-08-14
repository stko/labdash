rem Labdash muss per "pip install ." installiert sein, sonst geht's irgendwie nicht ?!?


pyinstaller labdash.py ^
--log-level WARN ^
--collect-submodules labdash ^
--hiddenimport bitarray ^
--hiddenimport uuid ^
--hiddenimport bitstring ^
--collect-submodules canopen ^
--collect-submodules flask ^
--hiddenimport  flask_sockets ^
--hiddenimport lxml ^
--hiddenimport oyaml ^
--collect-submodules python-can ^
--collect-submodules python-lin ^
--collect-submodules python-uds ^
--collect-submodules requests ^
--hiddenimport rich ^
--hiddenimport xmltodict 
mkdir dist\labdash\_internal\labdash\plugins
mkdir dist\labdash\_internal\web
xcopy plugins  dist\labdash\_internal\labdash\plugins /s /y
xcopy ..\web\  dist\labdash\_internal\web /s /y
xcopy ..\..\..\gitlab\inhouse\labdash_internal  dist\labdash\_internal\web\examples /s /y
rem del /s /f /q dist\labdash\_internal\labdash\plugins\labdash\__pycache__

