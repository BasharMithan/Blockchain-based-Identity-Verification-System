from enum import Enum

"""
Date: 9/13/2026
Title: Configs
Description: A file that contains the settings and configs for the project.
Developer: Bashar Mithab
"""

class Performance(Enum):
    """Safety is the the setting class that controls how safe the project is.

    Args:
        Enum ()
    """

    safe = "SAFE"
    fast = "FAST"



class Settings(object):
    """A configuration class to control how the project behave.

    Args:
        object ()
    """

    class Ledger(object):
        difficulity: int = 4
        performance: Performance = Performance.safe


