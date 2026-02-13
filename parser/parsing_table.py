"""
Generate LR parsing tables (ACTION and GOTO).

Implements SLR(1), CLR(1), and LALR(1) table generation algorithms.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Set, Tuple

from .dfa_builder import build_lr0_automaton, build_lr1_automaton
from .first_follow import compute_first_sets, compute_follow_sets
from .grammar import ENDMARKER, Grammar
from .lr_items import LR0Item, LR1Item

# Action entry: ("shift", state_id) | ("reduce", prod_index) | ("accept", None) | ("error", None)
ActionEntry = Tuple[str, int | None]


@dataclass
class ConflictDetail:
    """Represents a single parsing table conflict."""
    state: int
    symbol: str
    existing_action: ActionEntry
    new_action: ActionEntry


@dataclass
class ParseTable:
    """
    Represents an LR parsing table.
    
    Attributes:
        action: ACTION table - state -> symbol -> (action_type, value)
        goto: GOTO table - state -> nonterminal -> next_state
        conflicts: List of conflicts (shift/reduce, reduce/reduce)
        is_conflict_free: True if no conflicts found
        states: List of all LR states
        transitions: State transitions dictionary
    """
    action: Dict[int, Dict[str, ActionEntry]]
    goto: Dict[int, Dict[str, int]]
    conflicts: List[ConflictDetail]
    is_conflict_free: bool
    states: List[FrozenSet]
    transitions: Dict[int, Dict[str, int]]


def _set_action(
    action: Dict[int, Dict[str, ActionEntry]],
    state: int,
    symbol: str,
    entry: ActionEntry,
    conflicts: List[ConflictDetail],
) -> None:
    """
    Safely set an action entry, detecting conflicts.
    
    Args:
        action: ACTION table
        state: State number
        symbol: Symbol (terminal)
        entry: New action entry
        conflicts: List to append conflicts to
    """
    action.setdefault(state, {})
    if symbol in action[state]:
        existing = action[state][symbol]
        if existing != entry:
            conflicts.append(
                ConflictDetail(
                    state=state,
                    symbol=symbol,
                    existing_action=existing,
                    new_action=entry,
                )
            )
            return
    action[state][symbol] = entry


def build_slr_table(grammar: Grammar) -> ParseTable:
    """
    Build SLR(1) parsing table.
    
    SLR uses FOLLOW sets for reduce actions (simpler but less powerful than CLR).
    
    Args:
        grammar: The input grammar
        
    Returns:
        ParseTable with ACTION and GOTO entries
    """
    augmented = grammar.augment()
    states, transitions = build_lr0_automaton(grammar)
    first_sets = compute_first_sets(augmented)
    follow_sets = compute_follow_sets(augmented, first_sets)
    
    action: Dict[int, Dict[str, ActionEntry]] = {}
    goto_table: Dict[int, Dict[str, int]] = {}
    conflicts: List[ConflictDetail] = []
    
    # Fill tables from LR(0) states
    for state_id, state in enumerate(states):
        for item in state:
            prod = augmented.productions[item.prod_index]
            
            # Shift entries: if next symbol is terminal
            if item.dot < len(prod.rhs):
                sym = prod.rhs[item.dot]
                if sym in augmented.terminals:
                    to_state = transitions.get(state_id, {}).get(sym)
                    if to_state is not None:
                        _set_action(action, state_id, sym, ("shift", to_state), conflicts)
            
            # Reduce or Accept entries: if item is complete
            else:
                if prod.lhs == augmented.start_symbol:
                    # Accept action
                    _set_action(action, state_id, ENDMARKER, ("accept", None), conflicts)
                else:
                    # Reduce using FOLLOW set
                    for follow_sym in follow_sets[prod.lhs]:
                        _set_action(action, state_id, follow_sym, ("reduce", item.prod_index), conflicts)
        
        # GOTO entries: non-terminals
        for sym in augmented.nonterminals:
            to_state = transitions.get(state_id, {}).get(sym)
            if to_state is not None:
                goto_table.setdefault(state_id, {})[sym] = to_state
    
    return ParseTable(action, goto_table, conflicts, len(conflicts) == 0, states, transitions)


def build_clr_table(grammar: Grammar) -> ParseTable:
    """
    Build CLR(1) parsing table (Canonical LR).
    
    CLR uses LR(1) items with explicit lookahead (most powerful LR variant).
    
    Args:
        grammar: The input grammar
        
    Returns:
        ParseTable with ACTION and GOTO entries
    """
    augmented = grammar.augment()
    states, transitions = build_lr1_automaton(grammar)
    
    action: Dict[int, Dict[str, ActionEntry]] = {}
    goto_table: Dict[int, Dict[str, int]] = {}
    conflicts: List[ConflictDetail] = []
    
    # Fill tables from LR(1) states
    for state_id, state in enumerate(states):
        for item in state:
            prod = augmented.productions[item.prod_index]
            
            # Shift entries: if next symbol is terminal
            if item.dot < len(prod.rhs):
                sym = prod.rhs[item.dot]
                if sym in augmented.terminals:
                    to_state = transitions.get(state_id, {}).get(sym)
                    if to_state is not None:
                        _set_action(action, state_id, sym, ("shift", to_state), conflicts)
            
            # Reduce or Accept entries: if item is complete
            else:
                if prod.lhs == augmented.start_symbol:
                    # Accept action
                    _set_action(action, state_id, ENDMARKER, ("accept", None), conflicts)
                else:
                    # Reduce using lookahead from LR(1) item
                    _set_action(action, state_id, item.lookahead, ("reduce", item.prod_index), conflicts)
        
        # GOTO entries: non-terminals
        for sym in augmented.nonterminals:
            to_state = transitions.get(state_id, {}).get(sym)
            if to_state is not None:
                goto_table.setdefault(state_id, {})[sym] = to_state
    
    return ParseTable(action, goto_table, conflicts, len(conflicts) == 0, states, transitions)


def build_lalr_table(grammar: Grammar) -> ParseTable:
    """
    Build LALR(1) parsing table.
    
    LALR merges LR(1) states with the same core, reducing table size while
    keeping most of CLR's power.
    
    Args:
        grammar: The input grammar
        
    Returns:
        ParseTable with ACTION and GOTO entries
    """
    augmented = grammar.augment()
    clr_states, clr_transitions = build_lr1_automaton(grammar)
    
    # Map cores to merged state index
    core_map: Dict[Tuple[Tuple[int, int], ...], int] = {}
    merged_states: List[Set[LR1Item]] = []
    
    # Merge LR(1) states by core
    for state in clr_states:
        core = tuple(sorted({item.core() for item in state}))
        if core not in core_map:
            core_map[core] = len(merged_states)
            merged_states.append(set())
        idx = core_map[core]
        merged_states[idx].update(state)
    
    # Build transitions for merged states
    transitions: Dict[int, Dict[str, int]] = {}
    for i, state in enumerate(clr_states):
        core = tuple(sorted({item.core() for item in state}))
        from_idx = core_map[core]
        transitions.setdefault(from_idx, {})
        
        for sym, to_state in clr_transitions.get(i, {}).items():
            to_core = tuple(sorted({item.core() for item in clr_states[to_state]}))
            transitions[from_idx][sym] = core_map[to_core]
    
    # Fill ACTION and GOTO tables
    action: Dict[int, Dict[str, ActionEntry]] = {}
    goto_table: Dict[int, Dict[str, int]] = {}
    conflicts: List[ConflictDetail] = []
    
    for state_id, state in enumerate(merged_states):
        for item in state:
            prod = augmented.productions[item.prod_index]
            
            # Shift entries: if next symbol is terminal
            if item.dot < len(prod.rhs):
                sym = prod.rhs[item.dot]
                if sym in augmented.terminals:
                    to_state = transitions.get(state_id, {}).get(sym)
                    if to_state is not None:
                        _set_action(action, state_id, sym, ("shift", to_state), conflicts)
            
            # Reduce or Accept entries: if item is complete
            else:
                if prod.lhs == augmented.start_symbol:
                    _set_action(action, state_id, ENDMARKER, ("accept", None), conflicts)
                else:
                    _set_action(action, state_id, item.lookahead, ("reduce", item.prod_index), conflicts)
        
        # GOTO entries
        for sym in augmented.nonterminals:
            to_state = transitions.get(state_id, {}).get(sym)
            if to_state is not None:
                goto_table.setdefault(state_id, {})[sym] = to_state
    
    # Convert merged_states to frozen sets for consistency
    merged_frozen = [frozenset(state) for state in merged_states]
    
    return ParseTable(action, goto_table, conflicts, len(conflicts) == 0, merged_frozen, transitions)
