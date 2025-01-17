# -*- coding: utf-8 -*-
from IPython import InteractiveShell

import ipyflow.api
from ipyflow.api import *
from ipyflow.kernel import IPyflowKernel
from ipyflow.models import cells, namespaces, scopes, statements, symbols, timestamps
from ipyflow.singletons import flow, tracer


# Jupyter Extension points
def _jupyter_nbextension_paths():
    return [
        dict(
            section="notebook",
            # the path is relative to the `my_fancy_module` directory
            src="resources/nbextension",
            # directory in the `nbextension/` namespace
            dest="ipyflow",
            # _also_ in the `nbextension/` namespace
            require="ipyflow/index",
        )
    ]


def load_jupyter_server_extension(nbapp):
    pass


def load_ipython_extension(ipy: InteractiveShell) -> None:
    cur_kernel_cls = ipy.kernel.__class__  # type: ignore
    if cur_kernel_cls is IPyflowKernel:
        IPyflowKernel.replacement_class = None  # type: ignore
        return
    IPyflowKernel.inject(prev_kernel_class=cur_kernel_cls)  # type: ignore


def unload_ipython_extension(ipy: InteractiveShell) -> None:
    assert isinstance(ipy.kernel, IPyflowKernel)  # type: ignore
    assert IPyflowKernel.prev_kernel_class is not None  # type: ignore
    IPyflowKernel.replacement_class = IPyflowKernel.prev_kernel_class  # type: ignore


from . import _version
__version__ = _version.get_versions()['version']


__all__ = ipyflow.api.__all__ + ["__version__"]
