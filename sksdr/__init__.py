"""
API reference documentation for the `sksdr` package.
"""
import logging

from .agc import *
from .channels import *
from .coarse_freq_comp import *
from .fec import *
from .frame_sync import *
from .freq_sync import *
from .impairments import *
from .interp_decim import *
from .modulation import *
from .phase_offset_est import *
from .plotting import *
from .psk_trans import *
from .pulses import *
from .scrambling import *
from .sequences import *
from .symbol_sync import *
from .utils import *

_log = logging.getLogger(__name__)

def _setupLog():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    #'%(asctime)s:%(levelname)s: %(name)-15s; %(module)s %(message)s'
    _log.addHandler(handler)
    _log.setLevel(logging.DEBUG)

_setupLog()

# PEP0440 compatible formatted version, see:
# https://www.python.org/dev/peps/pep-0440/
#
# Generic release markers:
#   X.Y
#   X.Y.Z   # For bugfix releases
#
# Admissible pre-release markers:
#   X.YaN   # Alpha release
#   X.YbN   # Beta release
#   X.YrcN  # Release Candidate
#   X.Y     # Final release
#
# Dev branch marker is: 'X.Y.dev' or 'X.Y.devN' where N is an integer.
# 'X.Y.dev0' is the canonical version of 'X.Y.dev'
#
__version__ = '0.2.dev0'
