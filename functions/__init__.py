__all__ = ["config", "include"]

import config, include

__function_objs = [config.Config(), include.Include()]

functions = dict(zip(__all__, __function_objs))
