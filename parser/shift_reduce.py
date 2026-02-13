"""
Shift-Reduce parsing algorithm implementation.

Performs stack-based LR parsing using ACTION and GOTO tables.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from .grammar import ENDMARKER, Grammar
from .parsing_table import ParseTable
from visualizer.parse_tree import Node


@dataclass
class ParseStep:
    """Records a single step of the parsing process."""
    stack: str
    input_remaining: str
    action: str


def parse_input(
    grammar: Grammar,
    table: ParseTable,
    input_string: str,
) -> Tuple[List[ParseStep], bool, Optional[Node]]:
    """
    Parse an input string using shift-reduce parsing.
    
    Args:
        grammar: The grammar (used to access productions)
        table: The parse table (ACTION and GOTO)
        input_string: Space-separated tokens to parse
        
    Returns:
        Tuple of:
            - List of parse steps for tracing
            - Boolean: whether parsing succeeded
            - Parse tree root (or None if failed)
    """
    augmented = grammar.augment()
    
    # Tokenize input and add ENDMARKER
    tokens = input_string.split() if input_string.strip() else []
    tokens.append(ENDMARKER)
    
    # Initialize stacks
    state_stack: List[int] = [0]  # State stack
    symbol_stack: List[str] = []  # Symbol stack
    node_stack: List[Node] = []   # Parse tree nodes
    
    steps: List[ParseStep] = []
    input_idx = 0
    
    while True:
        current_state = state_stack[-1]
        current_token = tokens[input_idx]
        
        # Create trace strings
        state_str = " ".join(str(s) for s in state_stack)
        input_str = " ".join(tokens[input_idx:])
        
        # Look up action
        action_entry = table.action.get(current_state, {}).get(current_token)
        
        if action_entry is None:
            steps.append(ParseStep(state_str, input_str, "ERROR"))
            return steps, False, None
        
        action_type, value = action_entry
        
        if action_type == "shift":
            # Shift action
            next_state = int(value)
            prod_str = f"shift {next_state}"
            steps.append(ParseStep(state_str, input_str, prod_str))
            
            # Push symbol and state
            symbol_stack.append(current_token)
            node_stack.append(Node(current_token))
            state_stack.append(next_state)
            input_idx += 1
        
        elif action_type == "reduce":
            # Reduce action
            prod_index = int(value)
            prod = augmented.productions[prod_index]
            rhs_len = len(prod.rhs)
            
            prod_str = f"reduce {prod_index}: {prod.lhs} -> {' '.join(prod.rhs) if prod.rhs else 'ε'}"
            steps.append(ParseStep(state_str, input_str, prod_str))
            
            # Pop from stacks
            if rhs_len > 0:
                state_stack = state_stack[:-rhs_len]
                symbol_stack = symbol_stack[:-rhs_len]
                children = node_stack[-rhs_len:]
                node_stack = node_stack[:-rhs_len]
            else:
                children = [Node("ε")]
            
            # Create new parse tree node
            new_node = Node(prod.lhs, children)
            node_stack.append(new_node)
            symbol_stack.append(prod.lhs)
            
            # Look up goto
            new_state = state_stack[-1]
            next_state = table.goto.get(new_state, {}).get(prod.lhs)
            
            if next_state is None:
                steps.append(ParseStep(state_str, input_str, "ERROR (goto)"))
                return steps, False, None
            
            state_stack.append(next_state)
        
        elif action_type == "accept":
            # Accept action
            prod_str = "ACCEPT"
            steps.append(ParseStep(state_str, input_str, prod_str))
            
            # Return success
            root = node_stack[-1] if node_stack else None
            return steps, True, root
        
        else:
            steps.append(ParseStep(state_str, input_str, f"ERROR: unknown action {action_type}"))
            return steps, False, None

