import importlib

def import_obj(path):
    parts = path.split('.')
    module_path = '.'.join(parts[:-1])
    class_name = parts[-1]
    m = importlib.import_module(module_path)
    obj = getattr(m, class_name)
    return obj

def dumb_argparse(args):
    params = {}
    for arg in args:
        if '=' in arg:
            key, value = arg.split('=')
            params[key] = value
    return params
    
