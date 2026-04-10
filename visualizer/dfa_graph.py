"""
DFA visualization using Graphviz.

Renders the LR state machine as a directed graph.
"""

from __future__ import annotations

from typing import Dict, FrozenSet

from graphviz import Digraph


def build_dfa_graph(
    states: list[FrozenSet],
    transitions: Dict[int, Dict[str, int]],
) -> Digraph:
    """
    Create a Graphviz representation of the LR DFA.
    
    Args:
        states: List of LR states (frozen sets of items)
        transitions: State transitions dictionary
        
    Returns:
        Graphviz Digraph object
    """
    dot = Digraph("LR_DFA", comment="LR Parser DFA")
    
    # Auto-adjust graph size based on number of states
    num_states = len(states)
    if num_states <= 5:
        size = "8,6"
    elif num_states <= 10:
        size = "12,9"
    elif num_states <= 20:
        size = "16,12"
    else:
        size = "20,15"
    
    # Graph attributes for better layout
    dot.attr(
        rankdir="LR",  # Left to right for better horizontal spacing
        size=size,
        ratio="auto",
        nodesep="1.0",  # Horizontal spacing between nodes
        ranksep="1.5",  # Vertical spacing between ranks
        splines="true",  # Reduce edge overlap
        overlap="false",
        fontsize="12"
    )
    
    # Node default attributes
    dot.attr("node",
        fontsize="14",
        fontname="Arial",
        width="0.6",
        height="0.6",
        fixedsize="true"
    )
    
    # Edge default attributes
    dot.attr("edge",
        fontsize="11",
        fontname="Arial"
    )
    
    # Detect accept states (states with accept actions)
    # An accept state typically has items like "S' -> S •"
    accept_states = set()
    for i, state in enumerate(states):
        for item in state:
            # Check if this is a completion of the augmented start production
            if hasattr(item, 'prod_index') and item.prod_index == 0 and hasattr(item, 'dot'):
                # Get production to check if dot is at end
                if item.dot > 0:  # Simplified heuristic for accept state detection
                    accept_states.add(i)
    
    # Add nodes for each state
    for i, state in enumerate(states):
        label = f"I{i}"
        
        if i == 0:
            # Initial state: bold border and filled background
            dot.node(
                str(i),
                label=label,
                shape="circle",
                style="filled,bold",
                fillcolor="lightblue",
                penwidth="2.5"
            )
        elif i in accept_states:
            # Accept state: double circle
            dot.node(
                str(i),
                label=label,
                shape="doublecircle",
                style="bold",
                penwidth="1.5"
            )
        else:
            # Regular state
            dot.node(str(i), label=label, shape="circle")
    
    # Add edges for transitions
    for from_state, edges in transitions.items():
        for symbol, to_state in edges.items():
            dot.edge(str(from_state), str(to_state), label=symbol)
    
    return dot

