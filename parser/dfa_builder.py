"""
Build LR(0) and LR(1) deterministic finite automata (DFA).

Creates the canonical collection of LR states and state transitions.
"""

from __future__ import annotations

from typing import Dict, FrozenSet, List

from .first_follow import compute_first_sets
from .grammar import Grammar
from .lr_items import LR0Item, LR1Item, closure_lr0, closure_lr1, goto_lr0, goto_lr1


def build_lr0_automaton(grammar: Grammar) -> tuple[List[FrozenSet[LR0Item]], Dict[int, Dict[str, int]]]:
    """
    Build the LR(0) automaton (canonical collection of LR(0) states).
    
    Args:
        grammar: The input grammar (will be augmented)
        
    Returns:
        Tuple of:
            - List of LR(0) states (as frozen sets of items)
            - Dictionary of transitions: state_id -> {symbol -> next_state_id}
    """
    augmented = grammar.augment()
    
    # Start with closure of [S' -> • S]
    start_item = LR0Item(0, 0)
    start_state = closure_lr0([start_item], augmented)
    
    states: List[FrozenSet[LR0Item]] = [start_state]
    transitions: Dict[int, Dict[str, int]] = {}
    
    # Build states using BFS
    added = True
    while added:
        added = False
        for i, state in list(enumerate(states)):
            transitions.setdefault(i, {})
            
            # For each symbol, compute GOTO
            for symbol in augmented.symbols():
                goto_state = goto_lr0(state, symbol, augmented)
                
                if not goto_state:
                    continue
                
                # Add new state if not seen
                if goto_state not in states:
                    states.append(goto_state)
                    added = True
                
                # Record transition
                transitions[i][symbol] = states.index(goto_state)
    
    return states, transitions


def build_lr1_automaton(grammar: Grammar) -> tuple[List[FrozenSet[LR1Item]], Dict[int, Dict[str, int]]]:
    """
    Build the LR(1) automaton (canonical collection of LR(1) states).
    
    Args:
        grammar: The input grammar (will be augmented)
        
    Returns:
        Tuple of:
            - List of LR(1) states (as frozen sets of items)
            - Dictionary of transitions: state_id -> {symbol -> next_state_id}
    """
    augmented = grammar.augment()
    first_sets = compute_first_sets(augmented)
    
    # Start with closure of [S' -> • S, $]
    start_item = LR1Item(0, 0, "$")
    start_state = closure_lr1([start_item], augmented, first_sets)
    
    states: List[FrozenSet[LR1Item]] = [start_state]
    transitions: Dict[int, Dict[str, int]] = {}
    
    # Build states using BFS
    added = True
    while added:
        added = False
        for i, state in list(enumerate(states)):
            transitions.setdefault(i, {})
            
            # For each symbol, compute GOTO
            for symbol in augmented.symbols():
                goto_state = goto_lr1(state, symbol, augmented, first_sets)
                
                if not goto_state:
                    continue
                
                # Add new state if not seen
                if goto_state not in states:
                    states.append(goto_state)
                    added = True
                
                # Record transition
                transitions[i][symbol] = states.index(goto_state)
    
    return states, transitions
