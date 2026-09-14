
from enum import Enum
from pydantic_settings import BaseSettings


"""
Date: 9/13/2026
Title: Configs
Description: A file that contains the settings and configs for the project.
Developer: Bashar Mithan
"""

class Performance(Enum):
    """Safety is the the setting class that controls how safe the project is.

    Args:
        Enum ()
    """

    safe = "SAFE"
    fast = "FAST"



class LedgerCofigs(BaseSettings):
    ...


class ConnectionCofigs(BaseSettings):
    ...



class Settings(BaseSettings):
    """A configuration class to control how the project behave.

    Args:
        object ()
    """

    
    difficulity: int = 4
    performance: Performance = Performance.safe

    ledger: LedgerCofigs
    connection: ConnectionCofigs





defaultSettings = Settings(ledger=LedgerCofigs(), connection=ConnectionCofigs())
