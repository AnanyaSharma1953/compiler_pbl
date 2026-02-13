"""
Parse tree data structure and visualization using Graphviz.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from graphviz import Digraph


@dataclass
class Node:
    """
    Represents a node in the parse tree.
    
    Attributes:
        label: The symbol (terminal or non-terminal)
        children: List of child nodes
    """
    label: str
    children: List["Node"] = field(default_factory=list)
    
    def __repr__(self) -> str:
        return f"Node({self.label}, {len(self.children)} children)"


def build_parse_tree_graph(root: Node | None) -> Digraph:
    """
    Create a Graphviz representation of the parse tree.
    
    Args:
        root: Root node of the parse tree (or None if empty)
        
    Returns:
        Graphviz Digraph object
    """
    dot = Digraph("ParseTree", comment="Parse Tree")
    dot.attr(rankdir="TB")
    
    if root is None:
        return dot
    
    node_counter = [0]  # Use list for closure
    
    def add_node_recursive(node: Node) -> str:
        """Recursively add nodes and edges to the graph."""
        node_id = f"n{node_counter[0]}"
        node_counter[0] += 1
        
        # Add this node
        dot.node(node_id, label=node.label, shape="ellipse")
        
        # Add children recursively
        for child in node.children:
            child_id = add_node_recursive(child)
            dot.edge(node_id, child_id)
        
        return node_id
    
    add_node_recursive(root)
    return dot

