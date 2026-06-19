import pkgutil
import importlib


for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    importlib.import_module(f".{module_name}", __package__)