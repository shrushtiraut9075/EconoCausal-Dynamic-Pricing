"""EconoCausal — Causal-AI dynamic pricing engine.

Double ML (EconML + DoWhy) for individual treatment effect estimation
and SciPy optimisation for budget-constrained discount allocation.
"""

# Backward compatibility shim for DoWhy with scikit-learn >= 1.2
import functools as _ft
from typing import Any

# Pre-import lightgbm before other C-extensions to ensure clean OpenMP initialization on Windows
import lightgbm as _lgb  # noqa: F401
import sklearn.preprocessing as _sk_prep

_orig_ohe_init = _sk_prep.OneHotEncoder.__init__


@_ft.wraps(_orig_ohe_init)
def _compat_ohe_init(self: Any, *args: Any, **kwargs: Any) -> Any:
    if "sparse" in kwargs:
        kwargs["sparse_output"] = kwargs.pop("sparse")
    return _orig_ohe_init(self, *args, **kwargs)


_sk_prep.OneHotEncoder.__init__ = _compat_ohe_init  # type: ignore


__version__ = "1.0.0"
__author__ = "Infotact Solutions — Data Associate L1"
