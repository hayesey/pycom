# Pybytes library

MicroPython API for communication with Pybytes

### Debugging
There are multiple debug levels, 0 is warnings only, 6 is currently the highest used).

```
# use:
import pycom
pycom.nvs_set('pybytes_debug', debugLevel)

# e.g.
import pycom
pycom.nvs_set('pybytes_debug', 6)
```
