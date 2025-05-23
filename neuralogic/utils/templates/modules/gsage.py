from typing import List

from neuralogic.core import Atom, Template, Var, Aggregation, Activation, Metadata
from neuralogic.utils.templates.modules import AbstractModule


class SAGEConv(AbstractModule):
    def build(
        self, template: Template, layer_count: int, previous_names: List[str], feature_name: str, edge_name: str
    ) -> str:
        name = f"l{layer_count}_gsage" if self.name is None else self.name
        previous_name = feature_name if len(previous_names) == 0 else previous_names[-1]

        head_atom = Atom.get(name)(Var.X)[self.out_channels, self.in_channels]

        layer = head_atom <= (Atom.get(previous_name)(Var.Y), Atom.get(edge_name)(Var.X, Var.Y))
        template.add_rule(layer | Metadata(aggregation=Aggregation.AVG, activation=Activation.IDENTITY))

        layer = Atom.get(name)(Var.X)[self.out_channels, self.in_channels] <= Atom.get(previous_name)(Var.X)
        template.add_rule(layer | Metadata(activation=Activation.IDENTITY))

        template.add_rule(Atom.get(name) / 1 | Metadata(activation=self.activation))

        return name
