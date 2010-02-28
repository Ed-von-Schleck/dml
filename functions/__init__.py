__all__ = ["meta"]

import meta

__function_parsers = [meta.meta]
functions = dict(zip(__all__, __function_parsers))
