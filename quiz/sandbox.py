builtins_whitelist = set((
    'ArithmeticError', 'AssertionError', 'AttributeError', 'BaseException', 'BlockingIOError', 'BrokenPipeError',
    'BufferError', 'BytesWarning', 'ChildProcessError', 'ConnectionAbortedError', 'ConnectionError',
    'ConnectionRefusedError', 'ConnectionResetError', 'DeprecationWarning', 'EOFError', 'Ellipsis', 'EnvironmentError',
    'Exception', 'False', 'FileNotFoundError', 'FloatingPointError', 'FutureWarning', 'GeneratorExit', 'IOError',
    'ImportError', 'ImportWarning', 'IndentationError', 'IndexError', 'InterruptedError', 'IsADirectoryError',
    'KeyError', 'KeyboardInterrupt', 'LookupError', 'MemoryError', 'NameError', 'None', 'NotADirectoryError',
    'NotImplemented', 'NotImplementedError', 'OSError', 'OverflowError', 'PendingDeprecationWarning', 'PermissionError',
    'ProcessLookupError', 'RecursionError', 'ReferenceError', 'ResourceWarning', 'RuntimeError', 'RuntimeWarning',
    'StopAsyncIteration', 'StopIteration', 'SyntaxError', 'SyntaxWarning', 'SystemError', 'SystemExit', 'TabError',
    'TimeoutError', 'True', 'TypeError', 'UnboundLocalError', 'UnicodeDecodeError', 'UnicodeEncodeError',
    'UnicodeError', 'UnicodeTranslateError', 'UnicodeWarning', 'UserWarning', 'ValueError', 'Warning', 'ZeroDivisionError',
    '__IPYTHON__', '__build_class__', '__debug__', '__doc__', '__import__', '__loader__', '__name__', '__package__',
    '__spec__', 'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes', 'callable', 'chr', 'classmethod',
    'compile', 'complex', 'copyright', 'credits', 'delattr', 'dict', 'dir', 'divmod', 'enumerate', 'eval',
    'exec', 'filter', 'float', 'format', 'frozenset', 'getattr', 'globals', 'hasattr', 'hash', 'help', 'hex', 'id',
    'input', 'int', 'isinstance', 'issubclass', 'iter', 'len', 'license', 'list', 'locals', 'map', 'max', 'memoryview',
    'min', 'next', 'object', 'oct', 'open', 'ord', 'pow', 'print', 'property', 'range', 'repr', 'reversed', 'round',
    'set', 'setattr', 'slice', 'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple', 'type', 'vars', 'zip'
))

def _safe_import(__import__, module_whitelist):
    def safe_import(module_name, globals={}, locals={}, fromlist=[], level=-1):
        if module_name in module_whitelist:
            return __import__(module_name, globals, locals, fromlist, level)
        else:
            # raise ImportError("Blocked import of %s" % (module_name,))
            return __import__(module_name, globals, locals, fromlist, level)

    return safe_import


class ReadOnlyBuiltins(dict):
    def clear(self):
        ValueError("Read-Only")

    def __delitem__(self, key):
        ValueError("Read-Only")

    def pop(self, key, default=None):
        ValueError("Read-Only")

    def popitem(self):
        ValueError("Read-Only")

    def setdefault(self, key, value):
        ValueError("Read-Only")

    def __setitem__(self, key):
        ValueError("Read-Only")

    def update(self, dict, **kw):
        ValueError("Read-Only")

class Sandbox(object):
    def __init__(self):
        import sys
        from types import FunctionType
        original_builtins = sys.modules["__main__"].__dict__["__builtins__"].__dict__
        keys_to_delete = []
        for builtin in original_builtins.keys():
            if builtin not in builtins_whitelist:
                # keys_to_delete.append(builtin)
                continue
        for key in keys_to_delete:
            del original_builtins[key]
        original_builtins["__import__"] = _safe_import(__import__, ["string", "re"])
        safe_builtins = ReadOnlyBuiltins(original_builtins)
        sys.modules["__main__"].__dict__["__builtins__"] = safe_builtins
        function_dict = {}
        for name, value in vars(FunctionType).items():
            function_dict[name] = value
        attributes_to_remove = ["__bases__", "__subclasses__"]
        for attr in attributes_to_remove:
            function_dict.pop(attr, None)

    def execute(self, code_string):
        exec(code_string)
