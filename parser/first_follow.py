"""
FIRST and FOLLOW set computation for context-free grammars.

Implements standard algorithms from compiler theory:
- FIRST sets: Terminals that can appear at start of derivation
- FOLLOW sets: Terminals that can appear after a non-terminal
"""

from __future__ import annotations

from typing import Dict, Sequence, Set

from .grammar import EPSILON, ENDMARKER, Grammar


class FirstFollowAnalyzer:
    """Computes FIRST and FOLLOW sets for a grammar."""
    
    def __init__(self, grammar: Grammar):
        """
        Initialize analyzer and compute sets.
        
        Args:
            grammar: The grammar to analyze
        """
        self.grammar = grammar
        self.first_sets: Dict[str, Set[str]] = {}
        self.follow_sets: Dict[str, Set[str]] = {}
        self._compute_first()
        self._compute_follow()
    
    def _compute_first(self) -> None:
        """Compute FIRST sets for all symbols using fixed-point iteration."""
        # Initialize FIRST sets
        self.first_sets = {sym: set() for sym in self.grammar.symbols()}
        
        # FIRST[terminal] = {terminal}
        for terminal in self.grammar.terminals:
            self.first_sets[terminal].add(terminal)
        
        # Add ENDMARKER
        self.first_sets[ENDMARKER] = {ENDMARKER}
        
        # Iteratively add to FIRST sets until no changes
        changed = True
        while changed:
            changed = False
            
            for prod in self.grammar.productions:
                lhs = prod.lhs
                
                # For each symbol in RHS
                add_epsilon = True
                for sym in prod.rhs:
                    # Add FIRST[sym] - {epsilon} to FIRST[lhs]
                    for token in self.first_sets[sym] - {EPSILON}:
                        if token not in self.first_sets[lhs]:
                            self.first_sets[lhs].add(token)
                            changed = True
                    
                    # If epsilon not in FIRST[sym], stop
                    if EPSILON not in self.first_sets[sym]:
                        add_epsilon = False
                        break
                
                # If all symbols derive epsilon, add epsilon to FIRST[lhs]
                if add_epsilon and EPSILON not in self.first_sets[lhs]:
                    self.first_sets[lhs].add(EPSILON)
                    changed = True
    
    def _compute_follow(self) -> None:
        """Compute FOLLOW sets for all non-terminals using fixed-point iteration."""
        # Initialize FOLLOW sets for non-terminals
        self.follow_sets = {nt: set() for nt in self.grammar.nonterminals}
        
        # FOLLOW[start_symbol] contains ENDMARKER
        self.follow_sets[self.grammar.start_symbol].add(ENDMARKER)
        
        # Iteratively add to FOLLOW sets until no changes
        changed = True
        while changed:
            changed = False
            
            for prod in self.grammar.productions:
                lhs = prod.lhs
                rhs = prod.rhs
                
                # For each symbol in RHS
                for i, sym in enumerate(rhs):
                    if sym not in self.grammar.nonterminals:
                        continue
                    
                    # Get symbols after sym
                    beta = rhs[i + 1:]
                    
                    # Get FIRST[beta]
                    first_beta = self._first_of_sequence(beta)
                    
                    # Add FIRST[beta] - {epsilon} to FOLLOW[sym]
                    before_size = len(self.follow_sets[sym])
                    self.follow_sets[sym].update(first_beta - {EPSILON})
                    
                    # If epsilon in FIRST[beta], add FOLLOW[lhs] to FOLLOW[sym]
                    if EPSILON in first_beta or not beta:
                        self.follow_sets[sym].update(self.follow_sets[lhs])
                    
                    if len(self.follow_sets[sym]) != before_size:
                        changed = True
    
    def _first_of_sequence(self, sequence: Sequence[str]) -> Set[str]:
        """
        Compute FIRST set for a sequence of symbols.
        
        Args:
            sequence: Sequence of symbols
            
        Returns:
            FIRST set of the sequence
        """
        if not sequence:
            return {EPSILON}
        
        result: Set[str] = set()
        for sym in sequence:
            result.update(self.first_sets[sym] - {EPSILON})
            if EPSILON not in self.first_sets[sym]:
                return result
        
        # All symbols derive epsilon
        result.add(EPSILON)
        return result
    
    def get_first(self, symbol: str) -> Set[str]:
        """
        Get FIRST set for a symbol.
        
        Args:
            symbol: The symbol
            
        Returns:
            FIRST set (set of terminals)
        """
        return self.first_sets.get(symbol, set())
    
    def get_follow(self, symbol: str) -> Set[str]:
        """
        Get FOLLOW set for a non-terminal.
        
        Args:
            symbol: The non-terminal
            
        Returns:
            FOLLOW set (set of terminals)
        """
        return self.follow_sets.get(symbol, set())
    
    def get_all_first_sets(self) -> Dict[str, Set[str]]:
        """Get all FIRST sets."""
        return self.first_sets.copy()
    
    def get_all_follow_sets(self) -> Dict[str, Set[str]]:
        """Get all FOLLOW sets."""
        return self.follow_sets.copy()


# Convenience functions for backward compatibility
def compute_first_sets(grammar: Grammar) -> Dict[str, Set[str]]:
    """
    Compute FIRST sets for grammar.
    
    Args:
        grammar: The grammar
        
    Returns:
        Dictionary mapping symbols to their FIRST sets
    """
    analyzer = FirstFollowAnalyzer(grammar)
    return analyzer.get_all_first_sets()


def compute_follow_sets(grammar: Grammar, first_sets: Dict[str, Set[str]] | None = None) -> Dict[str, Set[str]]:
    """
    Compute FOLLOW sets for grammar.
    
    Args:
        grammar: The grammar
        first_sets: Precomputed FIRST sets (optional, unused)
        
    Returns:
        Dictionary mapping non-terminals to their FOLLOW sets
    """
    analyzer = FirstFollowAnalyzer(grammar)
    return analyzer.get_all_follow_sets()


def first_of_sequence(sequence: Sequence[str], first_sets: Dict[str, Set[str]]) -> Set[str]:
    """
    Compute FIRST set for a sequence of symbols.
    
    Args:
        sequence: Sequence of symbols
        first_sets: Dictionary of precomputed FIRST sets
        
    Returns:
        FIRST set of the sequence
    """
    if not sequence:
        return {EPSILON}
    
    result: Set[str] = set()
    for sym in sequence:
        result.update(first_sets.get(sym, set()) - {EPSILON})
        if EPSILON not in first_sets.get(sym, set()):
            return result
    
    result.add(EPSILON)
    return result
