from typing import List, Optional, Dict
import dynet as dy
import numpy as np

from neuralogic.core.builder import Sample, Weight, Neuron
from neuralogic.core.settings import Settings
from neuralogic.nn.base import AbstractNeuraLogic


class NeuraLogic(AbstractNeuraLogic):
    activations = {
        "Sigmoid": dy.logistic,
        "Average": dy.average,
        "Maximum": dy.emax,
        "ReLu": dy.rectify,
        "Tanh": dy.tanh,
    }

    def __init__(self, model: List[Weight], template, settings: Optional[Settings] = None):
        super().__init__(template)

        if settings is None:
            settings = Settings()
        self.settings = settings

        self.model = dy.ParameterCollection()
        self.weights_meta = model
        self.weights: List[dy.Parameters] = []

        self.reset_parameters()

    def reset_parameters(self):
        self.weights = [
            self.model.add_parameters(weight.dimensions, init=np.array(weight.value))
            if weight.fixed
            else self.model.add_parameters(weight.dimensions, init="uniform")
            for weight in self.weights_meta
        ]

    def build_sample(self, sample: Sample) -> dy.Expression:
        self.hooks_set = len(self.hooks) != 0

        dynet_neurons: List[Optional[dy.Expression]] = [None] * len(sample.neurons)

        for neuron in sample.neurons:
            dynet_neurons[neuron.index] = self.to_dynet_expression(neuron, dynet_neurons, self.weights)
        return dynet_neurons[sample.neurons[-1].index]

    def __call__(self, sample: Sample) -> dy.Expression:
        return self.build_sample(sample)

    def state_dict(self) -> Dict:
        weights = {}

        for meta, weight in zip(self.weights_meta, self.weights):
            if not meta.fixed and meta.index >= 0:
                weights[meta.index] = weight if isinstance(weight, (int, float)) else weight.value()
        return {"weights": weights}

    def load_state_dict(self, state_dict: Dict):
        weight_dict = state_dict["weights"]

        for i, (meta, weight) in enumerate(zip(self.weights_meta, self.weights)):
            if meta.index < 0 or meta.fixed:
                continue

            if isinstance(weight, (int, float)):
                self.weights[i] = weight_dict[meta.index]
            else:
                weight.set_value(np.array(weight_dict[meta.index]).reshape(weight.shape()))

    @staticmethod
    def to_dynet_value(value) -> dy.Expression:
        dim = 1
        if hasattr(value, "__len__"):
            dim = len(value)
        if dim == 1:
            return dy.scalarInput(float(value))
        if dim > 1:
            res = dy.vecInput(dim)
            res.set(value)
            return res
        return dy.inputTensor(value, dim)

    def to_dynet_expression(self, neuron: Neuron, neurons: List[dy.Expression], weights: List):
        if neuron.inputs:
            out = self.process_neuron_inputs(neuron, neurons, weights)
        else:
            out = [NeuraLogic.to_dynet_value(neuron.value)]

        if neuron.activation:
            if not neuron.pooling:
                out = sum(out)
            out = NeuraLogic.activations[neuron.activation](out)
        else:
            out = sum(out)

        if self.hooks_set and neuron.hook_name is not None and neuron.hook_name in self.hooks:
            self.run_hook(neuron.hook_name, out.value())
        return out

    def process_neuron_inputs(self, neuron: Neuron, neurons: List, weights: List[dy.Parameters]) -> List[dy.Expression]:
        out = []

        if neuron.weights:
            for w, i in zip(neuron.weights, neuron.inputs):
                weight = weights[w]
                if self.weights_meta[w].fixed:
                    weight = dy.const_parameter(weight)
                if neurons[i].dim()[0] == (1,) and not isinstance(weight, int):
                    out.append(dy.cmult(weight, neurons[i]))
                else:
                    out.append(weight * neurons[i])
        else:
            for i in neuron.inputs:
                out.append(neurons[i])
        return out
