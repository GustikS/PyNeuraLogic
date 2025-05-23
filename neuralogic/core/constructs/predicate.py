from neuralogic.core.constructs.java_objects import get_java_factory, get_current_java_factory
from neuralogic.core.constructs.metadata import Metadata


class Predicate:
    """WeightedPredicate"""

    def __init__(self, name, arity, private=False, special=False):
        self.name = name
        self.arity = arity
        self.private = private
        self.special = special

        self.java_object = get_java_factory().get_predicate(self)

    def set_arity(self, arity):
        if self.arity == arity:
            return self

    def to_str(self):
        special = "@" if self.special else ""
        private = "*" if self.private else ""
        return f"{private}{special}{self.name}"

    def __str__(self):
        special = "@" if self.special else ""
        private = "*" if self.private else ""
        return f"{private}{special}{self.name}/{self.arity}"

    def __or__(self, other):
        if not isinstance(other, Metadata):
            raise NotImplementedError
        return PredicateMetadata(self, other)


class PredicateMetadata:
    def __init__(self, predicate: Predicate, metadata: Metadata):
        if metadata.aggregation is not None or metadata.learnable is not None:
            raise NotImplementedError

        self.predicate = predicate
        self.metadata = metadata

        self.java_object = get_java_factory().get_predicate_metadata_pair(self)

    def __str__(self):
        return f"{self.predicate} {self.metadata}"
