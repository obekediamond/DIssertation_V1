from django.shortcuts import render
from .models import *
from .forms import *
from django.views.generic import FormView
from io import StringIO
import contextlib
from RestrictedPython.PrintCollector import PrintCollector
from RestrictedPython import compile_restricted
from RestrictedPython import safe_globals, safe_builtins
from RestrictedPython.Eval import default_guarded_getiter,default_guarded_getitem
from RestrictedPython.Guards import guarded_iter_unpack_sequence,safer_getattr
import math, matplotlib, numpy, numba, pandas, random, datetime, difflib


def _import(name, globals=None, locals=None, fromlist=(), level=0):
    safe_modules = ["math", "matplotlib", "numpy", "numba", "pandas", "random", "datetime", "tkinter", "matplotlib.pyplot"]
    if name in safe_modules:
       globals[name] = __import__(name, globals, locals, fromlist, level)
    else:
        raise Exception("This module incorrect or not allowed: {0}".format(name))


def custom_inplacevar(op, x, y):
    globs = {'x': x, 'y': y}
    exec('x' + op + 'y', globs)
    return globs['x']


safe_builtins['__import__'] = _import # Must be a part of builtins
safe_builtins['_inplacevar_'] = custom_inplacevar # Must be a part of builtins
safe_globals['_inplacevar_'] = custom_inplacevar
safe_globals['_print_'] = PrintCollector
safe_globals['_getattr_'] = safer_getattr
safe_globals['_getitem_'] = default_guarded_getitem
safe_globals['_getiter_'] = default_guarded_getiter
safe_globals['dir'] = dir
safe_globals['math'] = math
safe_globals['_iter_unpack_sequence_'] = guarded_iter_unpack_sequence
safe_globals['matplotlib'] = matplotlib
safe_globals['numpy'] = numpy
safe_globals['numba'] = numba
safe_globals['pandas'] = pandas
safe_globals['random'] = random
safe_globals['datetime'] = datetime
safe_globals['__builtins__'] = safe_builtins
safe_globals['__metaclass__'] = type


def execute_code(request):
    if request.method == 'POST':
        form = CodeForm(request.POST)
        if form.is_valid():
            user_code = form.cleaned_data['code']
            output = StringIO()
            error = StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
                try:
                    loc = {}
                    u_code = user_code + '\nscores = printed'
                    user_cc = compile_restricted(u_code, '<inline>', 'exec')
                    exec(user_cc, safe_globals, loc)
                    print(loc)
                    printed = loc['scores']
                    if printed:
                        result = f"Code executed successfully. Output:\n{printed}"
                    else:
                        result = "Code executed successfully. (No output)"
                except Exception as e:
                    result = f"Error: {str(e)}"
                output_str = output.getvalue()
                error_str = error.getvalue()
    else:
        form = CodeForm()
        result = ""
        output_str = ""
        error_str = ""

    return render(request, 'execute_code1.html', {'form': form, 'result': result, 'output': output_str, 'error': error_str})
