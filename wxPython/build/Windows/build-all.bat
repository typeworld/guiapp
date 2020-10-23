echo "Check if typeworld.api holds correct version number"
python wxPython\\build\\build-checkversionnumber.py %APP_BUILD_VERSION%

echo "Check if can upload to GCS"
python wxPython\\build\\build-canupload.py %APP_BUILD_VERSION% windows

REM  First round of main build with "Console" base, as error output will be routed to the
REM  console instead of popup message windows, to read output of self test in the build
echo "Main Build, Console base"
export BUILDBASE="Console"
wxPython\\build\\Windows\\build-main.bat
REM  %SHELL% wxPython\\build\\Windows\\build-main.sh

REM  Clear build folder
rmdir /s build
mkdir build

REM  Second round with "Win32GUI" base (no console window appears on Windows)
echo "Main Build, GUI base"
export BUILDBASE="Win32GUI"
%SHELL% wxPython\\build\\Windows\\build-main.sh

echo "Pack"
%SHELL% wxPython\\build\\Windows\\build-pack.sh

echo "Upload"
python wxPython\\build\\build-upload.py %APP_BUILD_VERSION% windows

echo "Upload Sparkle signature"
python wxPython\\build\\Windows\\build-uploadsignature.py %APP_BUILD_VERSION%

echo "Finished successfully."
