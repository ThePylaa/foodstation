To get picam running you have to install libcap dev headers:

```sudo apt-get install build-essential libcap-dev -y```

and

```sudo apt install -y python3-libcamera```

Also if you want to use picam in a venv you have to create the venv with ```--system-site-package``` f.e.

```python -m venv .venv --system-site-packages```

If you get an numpy error, telling you:

>ImportError: Error importing numpy: you should not try to import numpy from
    its source directory; please exit the numpy source tree, and relaunch
    your python intepreter from there.

try this:

```sudo apt-get install libopenblas-dev```