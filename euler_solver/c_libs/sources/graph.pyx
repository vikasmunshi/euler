# distutils: language = c
# cython: boundscheck=False, wraparound=False, cdivision=True, language_level=3


from dataclasses import dataclass, field
from typing import Generator, Sequence


@dataclass(frozen=True, kw_only=True, slots=True, eq=True, order=True)
class Node:
    value: int
    neighbors: set['Node'] = field(default_factory=set, compare=False, hash=False)

    def __post_init__(self):
        if not isinstance(self.value, int):
            raise TypeError("Node value must be an integer.")

    @property
    def is_leaf(self) -> bool:
        """Determine if the node is a leaf."""
        return not self.neighbors

    @classmethod
    def from_value(cls, value: int, neighbors: Sequence['Node'] | None = None) -> 'Node':
        """Create a new Node instance with a given value."""
        if neighbors is None:
            _neighbors: set['Node'] = set()
        else:
            _neighbors = set(neighbors)
        return cls(value=value, neighbors=_neighbors)

    def add_neighbor(self, neighbor: 'Node')-> None:
        """Add a neighbor to the node."""
        self.neighbors.add(neighbor)


@dataclass(frozen=True, kw_only=True, slots=True)
class Graph:
    nodes: dict[int, Node] = field(default_factory=dict)

    def get_node(self, node_value: int)-> Node:
        return self.nodes.get(node_value) or Node.from_value(node_value)

    def update_node(self, node_value: int, neighbor_values: Sequence[int] = tuple())-> None:
        node: 'Node' = self.get_node(node_value)
        for neighbor_value in neighbor_values:
            neighbor_node: 'Node' = self.get_node(neighbor_value)
            node.add_neighbor(neighbor_node)

    def find_paths_of_length(self, length: int)-> Generator[list['Node'], None, None]:
        """Find all paths of a specific length in a graph."""
        if length < 0:
            raise ValueError('Length of paths must be non-negative.')

        def _dfs(current_node: Node, path: list[Node], remaining_length: int):
            if remaining_length == 0:
                yield path.copy()
                return

            for neighbor in current_node.neighbors:
                if neighbor not in path:  # Avoid cycles
                    path.append(neighbor)
                    yield from _dfs(neighbor, path, remaining_length - 1)
                    path.pop()

        for start_node in self.nodes.values():
            yield from _dfs(start_node, [start_node], length)


def graph()-> 'Graph':
    """Factory function for creating an empty graph."""
    return Graph()

__pyi__ = (
    'class Node:\n'
    '    value: int\n'
    '    neighbors: list[Node]\n'
    '    @property\n'
    '    def is_leaf(self) -> bool: ...\n'
    '    @classmethod\n'
    '    def from_value(cls, value: int, neighbors: Sequence[Node] | None = ...) -> Node: ...\n'
    '    def add_neighbor(self, neighbor: Node) -> None: ...\n\n'
    'class Edge:\n'
    '    start: Node\n'
    '    end: Node\n\n'
    'class Graph:\n'
    '    nodes: list[Node]\n'
    '    edges: list[Edge]\n'
    '    def get_node(self, node_value: int) -> Node: ...\n'
    '    def update_node(self, node_value: int, neighbor_values: Sequence[int] = ...) -> None: ...\n'
    '    def find_paths_of_length(self, length: int) -> Generator[list[Node], None, None]: ...\n\n'
    'def graph() -> Graph: ...\n\n'
)
