# Mac Code Signing
sh install_mac_codesigning.sh

# Common
sh install_common.sh

# Python requirements
python -m pip install -r requirements_mac.txt
python -c 'import zmq; print("zmq"); print(zmq.zmq_version()); print(zmq.pyzmq_version())'

# Download Sparkle
curl -O -L https://github.com/sparkle-project/Sparkle/releases/download/1.23.0/Sparkle-1.23.0.tar.bz2
mkdir sparkle
tar -xf Sparkle-1.23.0.tar.bz2 --directory sparkle

# Copy ynlib
export SITEPACKAGES=`python -c 'import site; print(site.getsitepackages()[0])'`
cp -R ynlib/Lib/ynlib $SITEPACKAGES

# Python
# Link .dylib
# Apparently, they're the same file:
# https://groups.google.com/a/continuum.io/forum/#!topic/anaconda/4HKVl8Jhy9E
ln -s ~/.localpython3.7.11/lib/libpython3.7m.dylib ~/.localpython3.7.9/lib/libpython3.7.dylib

# Use Python Framework build for testing
# https://wiki.wxpython.org/wxPythonVirtualenvOnMac
echo "Python Framework Build Hack"

# # what real Python executable to use
# PYVER=3.7
# PYTHON=/Library/Frameworks/Python.framework/Versions/$PYVER/bin/python$PYVER

# # find the root of the virtualenv, it should be the parent of the dir this script is in
# ENV=`$PYTHON -c "import os; print(os.path.abspath(os.path.join(os.path.dirname(\"$0\"), '..')))"`

# # now run Python with the virtualenv set as Python's HOME
# export PYTHONHOME=$ENV 
# echo $PYTHONHOME

# pip3 install wxPython

export PYTHONHOME=`dirname "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"`
python --version
which python

# python -c "import sys; print(sys.base_prefix)"
# python -c "import sys; print(sys.prefix)"
