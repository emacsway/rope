import warnings


def saveit(func):
    """A decorator that caches the return value of a function"""

    name = '_' + func.__name__

    def _wrapper(self, *args, **kwds):
        if not hasattr(self, name):
            setattr(self, name, func(self, *args, **kwds))
        return getattr(self, name)
    return _wrapper

cacheit = saveit


def prevent_recursion(default):
    """A decorator that returns the return value of `default` in recursions"""
    def decorator(func):
        name = '_calling_%s_' % func.__name__

        def newfunc(self, *args, **kwds):
            if getattr(self, name, False):
                return default()
            setattr(self, name, True)
            try:
                return func(self, *args, **kwds)
            finally:
                setattr(self, name, False)
        return newfunc
    return decorator


def ignore_exception(exception_class):
    """A decorator that ignores `exception_class` exceptions"""
    def _decorator(func):
        def newfunc(*args, **kwds):
            try:
                return func(*args, **kwds)
            except exception_class:
                pass
        return newfunc
    return _decorator


def deprecated(message=None):
    """A decorator for deprecated functions"""
    def _decorator(func, message=message):
        if message is None:
            message = '%s is deprecated' % func.__name__

        def newfunc(*args, **kwds):
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return func(*args, **kwds)
        return newfunc
    return _decorator


def cached(size):
    """A caching decorator based on parameter objects"""
    def decorator(func):
        cached_func = _Cached(func, size)
        return lambda *a, **kw: cached_func(*a, **kw)
    return decorator


class _Cached(object):

    def __init__(self, func, size):
        self.func = func
        self.cache = dict()
        self.order = []
        self.size = size

    def __call__(self, *args, **kwds):
        key = to_hashable((args, kwds))
        try:
            result = self.cache[key]
        except KeyError:
            result = self.func(*args, **kwds)
            self.cache[key] = result
            self.order.insert(0, key)
            if len(self.cache) > self.size:
                del self.cache[self.order.pop()]
        else:
            self.order.remove(key)  # FIXME: avoid iteration
            self.order.insert(0, key)
        return result


def to_hashable(obj):
    """
    Makes a hashable object from a dictionary, list, tuple, set etc.
    """
    if isinstance(obj, (list, tuple)):
        return tuple(to_hashable(i) for i in obj)
    elif isinstance(obj, (set, frozenset)):
        return frozenset(to_hashable(i) for i in obj)
    elif isinstance(obj, dict):
        new_obj = {k: to_hashable(v) for k, v in obj.items()}
        return frozenset(new_obj.items())
    return obj
