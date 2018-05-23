from flask import request
import functools


def require(*required_args):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            for arg in required_args:
                # if arg not in request.json:
                #     return "400: the parameter is fail"
                if request.form is None or arg not in request.form.keys():
                    return "400: the parameter is not correct"

            return func(*args, **kw)

        return wrapper

    return decorator
