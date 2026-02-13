"""
Grammar module for parsing and representing context-free grammars (CFG).

Handles:
- Parsing CFG from text format
- Storing productions in structured format
- Identifying terminals and non-terminals
- Grammar augmentation for parsing
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

# Special symbols
EPSILON = "ε"
ENDMARKER = "$"


@dataclass(frozen=True)
class Production:
    """Represents a single production rule A -> α."""
    lhs: str
    rhs: Tuple[str, ...]
    
    def __str__(self) -> str:
        """String representation of production."""
        if not self.rhs:
            return f"{self.lhs} -> ε"
        return f"{self.lhs} -> {' '.join(self.rhs)}"


class Grammar:
    """
    Represents a context-free grammar.
    
    Attributes:
        productions: List of all production rules
        start_symbol: The start symbol of the grammar
        nonterminals: Set of all non-terminal symbols
        terminals: Set of all terminal symbols
    """
    
    def __init__(self, productions: List[Production], start_symbol: str):
        """
        Initialize a grammar.
        
        Args:
            productions: List of Production objects
            start_symbol: The start non-terminal symbol
        """
        self.productions = productions
        self.start_symbol = start_symbol
        
        # Infer non-terminals from LHS of productions
        self.nonterminals = {p.lhs for p in productions}
        
        # Infer terminals from RHS (symbols not in non-terminals and not epsilon)
        self.terminals = self._infer_terminals()
        
        # Create index for quick lookup: nonterminal -> list of production indices
        self.prod_by_lhs: Dict[str, List[int]] = {}
        for i, p in enumerate(self.productions):
            self.prod_by_lhs.setdefault(p.lhs, []).append(i)

    def _infer_terminals(self) -> Set[str]:
        """Infer terminal symbols from productions."""
        terminals: Set[str] = set()
        for p in self.productions:
            for sym in p.rhs:
                # A symbol is terminal if it's not non-terminal and not epsilon
                if sym != EPSILON and sym not in self.nonterminals:
                    terminals.add(sym)
        return terminals

    @classmethod
    def from_text(cls, text: str) -> "Grammar":
        """
        Parse grammar from text format.
        
        Format:
            E -> E + T | T
            T -> T * F | F
            F -> ( E ) | id
        
        Args:
            text: Grammar string with productions
            
        Returns:
            Grammar object
            
        Raises:
            ValueError: If grammar format is invalid
        """
        productions: List[Production] = []
        start_symbol: Optional[str] = None
        
        for line in text.splitlines():
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            
            # Parse LHS and RHS
            if "->" in line:
                lhs, rhs_part = line.split("->", 1)
            elif "→" in line:
                lhs, rhs_part = line.split("→", 1)
            else:
                raise ValueError(f"Invalid production line: {line}")
            
            lhs = lhs.strip()
            
            # First LHS encountered is the start symbol
            if start_symbol is None:
                start_symbol = lhs
            
            # Parse alternatives (separated by |)
            alternatives = [alt.strip() for alt in rhs_part.split("|")]
            
            for alt in alternatives:
                # Handle epsilon productions
                if alt in ("", EPSILON, "epsilon"):
                    rhs: Tuple[str, ...] = tuple()
                else:
                    rhs = tuple(alt.split())
                
                productions.append(Production(lhs=lhs, rhs=rhs))
        
        if start_symbol is None:
            raise ValueError("No productions found in grammar.")
        
        return cls(productions, start_symbol)

    def augment(self) -> "Grammar":
        """
        Create augmented grammar with new start symbol.
        
        Adds production: S' -> S
        This is required for LR parsing to detect accept state.
        
        Returns:
            New augmented grammar
        """
        new_start = f"{self.start_symbol}'"
        augmented_prods = [Production(lhs=new_start, rhs=(self.start_symbol,))]
        augmented_prods.extend(self.productions)
        return Grammar(augmented_prods, new_start)

    def get_productions(self) -> List[Production]:
        """Get all productions."""
        return self.productions

    def get_terminals(self) -> Set[str]:
        """Get all terminal symbols."""
        return self.terminals

    def get_nonterminals(self) -> Set[str]:
        """Get all non-terminal symbols."""
        return self.nonterminals

    def get_start_symbol(self) -> str:
        """Get the start symbol."""
        return self.start_symbol

    def is_nonterminal(self, symbol: str) -> bool:
        """Check if symbol is a non-terminal."""
        return symbol in self.nonterminals

    def is_terminal(self, symbol: str) -> bool:
        """Check if symbol is a terminal."""
        return symbol in self.terminals

    def symbols(self) -> Set[str]:
        """Get all symbols (terminals + non-terminals)."""
        return self.nonterminals | self.terminals

    def __repr__(self) -> str:
        """String representation of grammar."""
        lines = [f"Grammar(start={self.start_symbol})"]
        for i, prod in enumerate(self.productions):
            lines.append(f"  {i}: {prod}")
        return "\n".join(lines)
