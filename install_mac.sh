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

# Python
# Link .dylib
# Apparently, they're the same file:
# https://groups.google.com/a/continuum.io/forum/#!topic/anaconda/4HKVl8Jhy9E
ln -s ~/.localpython3.7.7/lib/libpython3.7m.dylib ~/.localpython3.7.7/lib/libpython3.7.dylib
