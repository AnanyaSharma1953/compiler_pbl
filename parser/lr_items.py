"""
LR(0) and LR(1) item management.

LR items represent parser states and are used to build the LR DFA.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, Iterable, Set, Tuple

from .first_follow import first_of_sequence
from .grammar import EPSILON, Grammar


@dataclass(frozen=True)
class LR0Item:
    """
    An LR(0) item represents a position in a production.
    
    Format: A -> α • β
    - prod_index: Index in grammar.productions
    - dot: Position of the dot (0 to len(rhs))
    """
    prod_index: int
    dot: int
    
    def next_symbol(self, grammar: Grammar) -> str | None:
        """Get the symbol immediately after the dot, or None if at end."""
        rhs = grammar.productions[self.prod_index].rhs
        if self.dot < len(rhs):
            return rhs[self.dot]
        return None
    
    def advance(self) -> "LR0Item":
        """Return new item with dot moved one position right."""
        return LR0Item(self.prod_index, self.dot + 1)
    
    def is_complete(self, grammar: Grammar) -> bool:
        """Check if dot is at the end (item is complete)."""
        return self.dot >= len(grammar.productions[self.prod_index].rhs)


@dataclass(frozen=True)
class LR1Item:
    """
    An LR(1) item is an LR(0) item plus a lookahead terminal.
    
    Format: [A -> α • β, a] where a is the lookahead
    """
    prod_index: int
    dot: int
    lookahead: str
    
    def next_symbol(self, grammar: Grammar) -> str | None:
        """Get the symbol immediately after the dot."""
        rhs = grammar.productions[self.prod_index].rhs
        if self.dot < len(rhs):
            return rhs[self.dot]
        return None
    
    def advance(self) -> "LR1Item":
        """Return new item with dot moved one position right."""
        return LR1Item(self.prod_index, self.dot + 1, self.lookahead)
    
    def is_complete(self, grammar: Grammar) -> bool:
        """Check if dot is at the end."""
        return self.dot >= len(grammar.productions[self.prod_index].rhs)
    
    def core(self) -> Tuple[int, int]:
        """Return the core (prod_index, dot) without lookahead."""
        return (self.prod_index, self.dot)


def closure_lr0(items: Iterable[LR0Item], grammar: Grammar) -> FrozenSet[LR0Item]:
    """
    Compute the LR(0) closure of a set of items.
    
    For each item [A -> α • B β], add all items [B -> • γ] to the closure.
    
    Args:
        items: Set of LR(0) items
        grammar: The grammar
        
    Returns:
        Frozen set of all closure items
    """
    closure: Set[LR0Item] = set(items)
    added = True
    
    while added:
        added = False
        for item in list(closure):
            sym = item.next_symbol(grammar)
            
            # If next symbol is non-terminal, add all productions for it
            if sym and grammar.is_nonterminal(sym):
                for prod_idx in grammar.prod_by_lhs.get(sym, []):
                    new_item = LR0Item(prod_idx, 0)
                    if new_item not in closure:
                        closure.add(new_item)
                        added = True
    
    return frozenset(closure)


def goto_lr0(state: FrozenSet[LR0Item], symbol: str, grammar: Grammar) -> FrozenSet[LR0Item]:
    """
    Compute the GOTO function for LR(0).
    
    GOTO(I, X) = closure({[A -> αX • β] | [A -> α • Xβ] in I})
    
    Args:
        state: Set of LR(0) items
        symbol: Grammar symbol
        grammar: The grammar
        
    Returns:
        The GOTO state
    """
    moved = [item.advance() for item in state if item.next_symbol(grammar) == symbol]
    if not moved:
        return frozenset()
    return closure_lr0(moved, grammar)


def closure_lr1(items: Iterable[LR1Item], grammar: Grammar, first_sets: Dict[str, Set[str]]) -> FrozenSet[LR1Item]:
    """
    Compute the LR(1) closure of a set of items.
    
    For each item [A -> α • B β, a], add items [B -> • γ, b] where
    b ∈ FIRST(βa).
    
    Args:
        items: Set of LR(1) items
        grammar: The grammar
        first_sets: Precomputed FIRST sets
        
    Returns:
        Frozen set of all closure items
    """
    closure: Set[LR1Item] = set(items)
    added = True
    
    while added:
        added = False
        for item in list(closure):
            sym = item.next_symbol(grammar)
            
            # If next symbol is non-terminal
            if sym and grammar.is_nonterminal(sym):
                # Get symbols after sym
                rhs = grammar.productions[item.prod_index].rhs
                beta = rhs[item.dot + 1:]
                
                # Compute FIRST(βa)
                lookaheads = first_of_sequence(list(beta) + [item.lookahead], first_sets)
                
                # Remove epsilon from lookaheads
                if EPSILON in lookaheads:
                    lookaheads = lookaheads - {EPSILON}
                
                # Add [B -> • γ, b] for each production B and each b in FIRST(βa)
                for prod_idx in grammar.prod_by_lhs.get(sym, []):
                    for la in lookaheads:
                        new_item = LR1Item(prod_idx, 0, la)
                        if new_item not in closure:
                            closure.add(new_item)
                            added = True
    
    return frozenset(closure)


def goto_lr1(state: FrozenSet[LR1Item], symbol: str, grammar: Grammar, first_sets: Dict[str, Set[str]]) -> FrozenSet[LR1Item]:
    """
    Compute the GOTO function for LR(1).
    
    Args:
        state: Set of LR(1) items
        symbol: Grammar symbol
        grammar: The grammar
        first_sets: Precomputed FIRST sets
        
    Returns:
        The GOTO state
    """
    moved = [item.advance() for item in state if item.next_symbol(grammar) == symbol]
    if not moved:
        return frozenset()
    return closure_lr1(moved, grammar, first_sets)

