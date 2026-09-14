from configs.baseConfigs import Settings, Performance
from configs.handler import ConfigurationHandler

__handler = ConfigurationHandler()
settings = __handler.load()
