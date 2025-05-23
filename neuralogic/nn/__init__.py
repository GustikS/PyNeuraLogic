from typing import Optional

from neuralogic.core.builder import Backend
from neuralogic.nn.base import AbstractEvaluator
from neuralogic.core import Template
from neuralogic.core.settings import Settings


def get_neuralogic_layer(backend: Backend, native_backend_models: bool = False):
    if backend == Backend.DYNET:
        from neuralogic.nn.dynet import NeuraLogic  # type: ignore

        return NeuraLogic
    if backend == Backend.DGL:
        from neuralogic.nn.dgl import NeuraLogicLayer  # type: ignore

        return NeuraLogicLayer
    if backend == Backend.JAVA:
        from neuralogic.nn.java import NeuraLogic  # type: ignore

        return NeuraLogic
    if backend == Backend.PYG:
        if native_backend_models:
            from neuralogic.nn.native.torch import NeuraLogic

            return NeuraLogic
    raise NotImplementedError


def get_evaluator(
    backend: Backend,
    template: Template,
    settings: Optional[Settings] = None,
    *,
    native_backend_models=False,
):
    if settings is None:
        if template is not None:
            settings = template.java_factory.settings
        else:
            settings = Settings()

    if backend == Backend.DYNET:
        from neuralogic.nn.evaluators.dynet import DynetEvaluator

        return DynetEvaluator(template, settings)
    if backend == Backend.JAVA:
        from neuralogic.nn.evaluators.java import JavaEvaluator

        return JavaEvaluator(template, settings)
