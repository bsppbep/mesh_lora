import warnings
from .interface import Interface
try:
    from .transceiver import Transceiver
except NotImplementedError:
    warnings.warn("board library can't be imported, ignore this warning if you are running a simulation")