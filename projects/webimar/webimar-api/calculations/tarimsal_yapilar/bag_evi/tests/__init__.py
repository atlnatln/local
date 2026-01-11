"""
Bağ Evi Modülü Test Paketi
Bu paket bag_evi modülünün tüm bileşenleri için unit testleri içerir
"""

# Test configuration
import sys
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import all test modules
from .test_core import *
from .test_config import *
from .test_messages import *
from .test_hotfix_adapter import *
