# turbo_tosec/utils/deprecation.py
import warnings
import functools
import inspect
from typing import Any, Callable

def deprecated(reason: str) -> Callable:
    """
    Universal decorator to mark functions, methods, or classes as deprecated.
    Automatically adjusts to wrap the correct initialization logic.
    """
    def decorator(obj: Any) -> Any:
        
        # Class
        if inspect.isclass(obj):
            # Don't wrap the class itself, intercept its __init__ method
            original_init = obj.__init__
            
            @functools.wraps(original_init)
            def new_init(self, *args, **kwargs):
                warnings.warn(f"Class '{obj.__name__}' is deprecated. {reason}",
                              category=DeprecationWarning,
                              # stacklevel=2 points to the file where the user typed `MyClass()`
                              stacklevel=2)
                original_init(self, *args, **kwargs)
                
            # Replace the old init with warning-injected init
            obj.__init__ = new_init
            return obj

        # Function or Method
        else:
            @functools.wraps(obj)
            def wrapper(*args, **kwargs):
                warnings.warn(f"Call to deprecated function '{obj.__name__}'. {reason}",
                              category=DeprecationWarning,
                              # stacklevel=2 points to the file where the user called the func
                              stacklevel=2)
                return obj(*args, **kwargs)
                
            return wrapper

    return decorator
