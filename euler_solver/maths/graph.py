#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Graph data structure and algorithms."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Generator, TypeVar

T = TypeVar('T')


@dataclass(frozen=True, kw_only=True, slots=True, eq=True, order=False)
class Node[T]:
    id: T = field(compare=True, hash=True, )
    next: set[Node[T]] = field(default_factory=set, hash=False, compare=False, )
    previous: set[Node[T]] = field(default_factory=set, hash=False, compare=False, )

    @property
    def is_leaf(self) -> bool:
        return not self.next

    @property
    def is_root(self) -> bool:
        return not self.previous


@dataclass(frozen=True, kw_only=True, slots=True, eq=False, order=False)
class Graph[T]:
    nodes: dict[T, Node[T]] = field(default_factory=dict)

    def get_node(self, node_id: T) -> Node:
        if node_id not in self.nodes:
            self.nodes[node_id] = Node(id=node_id)
        return self.nodes[node_id]

    @staticmethod
    def add_edge(from_node: Node[T], to_node: Node[T]) -> tuple[Node[T], Node[T]]:
        from_node.next.add(to_node)
        to_node.previous.add(from_node)
        return from_node, to_node

    def validate(self) -> bool:
        for node in self.nodes.values():
            for neighbor in node.next:
                if node not in neighbor.previous:
                    return False
        return True

    def get_root_nodes(self) -> set[Node[T]]:
        return {node for node in self.nodes.values() if node.is_root}

    def get_leaf_nodes(self) -> set[Node[T]]:
        return {node for node in self.nodes.values() if node.is_leaf}

    def detect_cycle(self) -> bool:
        def visit(_node: Node[T], visiting: set[Node[T]], _visited: set[Node[T]]) -> bool:
            if _node in _visited:
                return False
            if _node in visiting:
                return True
            visiting.add(_node)
            for neighbor in _node.next:
                if visit(neighbor, visiting, _visited):
                    return True
            visiting.remove(_node)
            _visited.add(_node)
            return False

        visited = set()
        for node in self.nodes.values():
            if visit(node, set(), visited):
                return True
        return False

    @staticmethod
    def bfs(start_node: Node[T]) -> tuple[Node[T], ...]:
        visited = set()
        queue = deque([start_node])
        result = tuple()
        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            result += (node,)
            queue.extend(node.next - visited)
        return result

    @staticmethod
    def dfs(start_node: Node[T]) -> tuple[Node[T], ...]:
        visited = set()
        result = list()

        def visit(node: Node[T]):
            if node in visited:
                return
            visited.add(node)
            result.append(node)
            for neighbor in node.next:
                visit(neighbor)

        visit(start_node)
        return tuple(result)

    def connected_components(self) -> tuple[tuple[Node[T], ...], ...]:
        visited = set()
        components = []
        for node in self.nodes.values():
            if node not in visited:
                component = tuple(self.bfs(node))
                components.append(component)
                visited.update(component)
        return tuple(components)

    def reachable_nodes(self, start_node: Node[T]) -> tuple[Node[T], ...]:
        return tuple(self.bfs(start_node))

    @staticmethod
    def find_shortest_path(start_node: Node[T], end_node: Node[T]) -> tuple[Node[T], ...]:
        if start_node == end_node:
            return (start_node,)
        queue: deque[tuple[Node[T], tuple[Node[T], ...]]] = deque([(start_node, (start_node,))])
        visited = {start_node}
        while queue:
            current_node, path = queue.popleft()
            for next_node in current_node.next:
                if next_node in visited:
                    continue
                if next_node == end_node:
                    return path + (next_node,)
                visited.add(next_node)
                queue.append((next_node, path + (next_node,)))
        raise ValueError('No path exists between start_node and end_node.')

    @staticmethod
    def find_paths_of_max_length(start_node: Node[T], max_length: int) -> Generator[tuple[Node[T], ...], None, None]:
        if max_length < 1:
            return
        stack: list[tuple[Node[T], tuple[Node[T], ...]]] = [(start_node, (start_node,))]
        while stack:
            current_node, path = stack.pop()
            if len(path) > max_length:
                continue
            yield path
            for next_node in current_node.next:
                if next_node not in path:
                    stack.append((next_node, path + (next_node,)))

    @staticmethod
    def find_paths_of_length(start_node: Node[T], exact_length: int) -> Generator[tuple[Node[T], ...], None, None]:
        if exact_length < 1:
            return
        stack: list[tuple[Node[T], tuple[Node[T], ...]]] = [(start_node, (start_node,))]
        while stack:
            current_node, path = stack.pop()
            if len(path) == exact_length:
                yield path
                continue
            if len(path) > exact_length:
                continue
            for next_node in current_node.next:
                if next_node not in path:
                    stack.append((next_node, path + (next_node,)))

