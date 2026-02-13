"""
Unified LR Parser Module

Refactored bottom-up parser implementation with class-based architecture:
- LRParser: Base class for all LR parsers
- SLRParser: Simple LR(1) parser
- CLRParser: Canonical LR(1) parser
- LALRParser: Look-Ahead LR(1) parser

Separates logic from UI, returns structured data.
"""

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional
from abc import ABC, abstractmethod

from parser.grammar import Grammar, Production
from parser.first_follow import compute_first_sets, compute_follow_sets
from parser.lr_items import LR0Item, LR1Item, closure_lr0, closure_lr1, goto_lr0, goto_lr1
from parser.dfa_builder import build_lr0_automaton, build_lr1_automaton
from parser.parsing_table import ParseTable, ConflictDetail


@dataclass
class LRConflict:
    """Represents a conflict in LR parsing."""
    state: int
    symbol: str
    conflict_type: str  # "shift_reduce" or "reduce_reduce"
    existing_action: str
    new_action: str
    production1: Optional[Production] = None
    production2: Optional[Production] = None


@dataclass
class LRParseResult:
    """Result of LR parsing."""
    steps: List
    accepted: bool
    parse_tree: Optional[any] = None


class LRParser(ABC):
    """
    Base class for LR parsers.
    
    Provides common functionality for SLR, CLR, and LALR parsers.
    """
    
    def __init__(self, grammar: Grammar):
        """Initialize LR parser with grammar."""
        self.grammar = grammar
        self.augmented_grammar = grammar.augment()
        self.first_sets = compute_first_sets(grammar)
        self.follow_sets = compute_follow_sets(grammar)
        self.states: List[Set] = []
        self.transitions: Dict[Tuple[int, str], int] = {}
        self.action: Dict[int, Dict[str, Tuple[str, int]]] = {}
        self.goto: Dict[int, Dict[str, int]] = {}
        self.conflicts: List[LRConflict] = []
        self.is_conflict_free = False
        
        # Build the parser
        self._build()
    
    @abstractmethod
    def _build(self) -> None:
        """Build the parsing table. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def get_parser_type(self) -> str:
        """Return the parser type name."""
        pass
    
    def _detect_conflict_type(self, existing: Tuple[str, int], new: Tuple[str, int]) -> str:
        """Determine the type of conflict."""
        existing_action, _ = existing
        new_action, _ = new
        
        if existing_action == "shift" and new_action == "reduce":
            return "shift_reduce"
        elif existing_action == "reduce" and new_action == "shift":
            return "shift_reduce"
        elif existing_action == "reduce" and new_action == "reduce":
            return "reduce_reduce"
        else:
            return "other"
    
    def parse(self, input_string: str):
        """
        Parse input string using the constructed LR parser.
        
        Returns: LRParseResult with steps, accepted status, and parse tree
        """
        from parser.shift_reduce import parse_input
        
        # Create ParseTable object for compatibility
        table = ParseTable(
            action=self.action,
            goto=self.goto,
            conflicts=[],  # ConflictDetail list (will be empty if conflict_free)
            is_conflict_free=self.is_conflict_free,
            states=self.states,
            transitions=self.transitions
        )
        
        steps, accepted, parse_tree = parse_input(self.grammar, table, input_string)
        
        return LRParseResult(
            steps=steps,
            accepted=accepted,
            parse_tree=parse_tree
        )
    
    def get_summary(self) -> Dict:
        """
        Get structured summary of parser.
        
        Returns dictionary with:
        - Parser type
        - Number of states
        - Number of conflicts
        - Conflict details
        - Table size statistics
        """
        terminals = self.grammar.get_terminals()
        nonterminals = self.grammar.get_nonterminals()
        
        action_entries = sum(len(row) for row in self.action.values())
        goto_entries = sum(len(row) for row in self.goto.values())
        
        return {
            "parser_type": self.get_parser_type(),
            "is_conflict_free": self.is_conflict_free,
            "states": len(self.states),
            "transitions": len(self.transitions),
            "conflicts": len(self.conflicts),
            "conflict_details": [
                {
                    "state": c.state,
                    "symbol": c.symbol,
                    "type": c.conflict_type,
                    "existing_action": c.existing_action,
                    "new_action": c.new_action
                }
                for c in self.conflicts
            ],
            "terminals": len(terminals),
            "nonterminals": len(nonterminals),
            "action_entries": action_entries,
            "goto_entries": goto_entries,
            "total_table_entries": action_entries + goto_entries
        }


class SLRParser(LRParser):
    """
    Simple LR(1) Parser.
    
    Uses LR(0) items with FOLLOW sets for reduce decisions.
    Most basic LR parser, may have more conflicts than CLR/LALR.
    """
    
    def get_parser_type(self) -> str:
        return "SLR(1)"
    
    def _build(self) -> None:
        """Build SLR parsing table using LR(0) items and FOLLOW sets."""
        from parser.parsing_table import build_slr_table
        
        # Use existing implementation
        table = build_slr_table(self.grammar)
        
        # Copy results
        self.states = table.states
        self.transitions = table.transitions
        self.action = table.action
        self.goto = table.goto
        self.is_conflict_free = table.is_conflict_free
        
        # Convert conflicts to LRConflict format
        for conflict in table.conflicts:
            self.conflicts.append(LRConflict(
                state=conflict.state,
                symbol=conflict.symbol,
                conflict_type=self._detect_conflict_type(
                    conflict.existing_action,
                    conflict.new_action
                ),
                existing_action=str(conflict.existing_action),
                new_action=str(conflict.new_action)
            ))


class CLRParser(LRParser):
    """
    Canonical LR(1) Parser.
    
    Uses full LR(1) items with lookahead symbols.
    Most powerful LR parser, handles largest class of grammars.
    May have many more states than SLR/LALR.
    """
    
    def get_parser_type(self) -> str:
        return "CLR(1)"
    
    def _build(self) -> None:
        """Build CLR parsing table using LR(1) items."""
        from parser.parsing_table import build_clr_table
        
        # Use existing implementation
        table = build_clr_table(self.grammar)
        
        # Copy results
        self.states = table.states
        self.transitions = table.transitions
        self.action = table.action
        self.goto = table.goto
        self.is_conflict_free = table.is_conflict_free
        
        # Convert conflicts
        for conflict in table.conflicts:
            self.conflicts.append(LRConflict(
                state=conflict.state,
                symbol=conflict.symbol,
                conflict_type=self._detect_conflict_type(
                    conflict.existing_action,
                    conflict.new_action
                ),
                existing_action=str(conflict.existing_action),
                new_action=str(conflict.new_action)
            ))


class LALRParser(LRParser):
    """
    Look-Ahead LR(1) Parser.
    
    Merges LR(1) states with same core (LR(0) items).
    Balanced between SLR and CLR: more powerful than SLR, fewer states than CLR.
    Used by most parser generators (YACC, Bison).
    """
    
    def get_parser_type(self) -> str:
        return "LALR(1)"
    
    def _build(self) -> None:
        """Build LALR parsing table by merging LR(1) states."""
        from parser.parsing_table import build_lalr_table
        
        # Use existing implementation
        table = build_lalr_table(self.grammar)
        
        # Copy results
        self.states = table.states
        self.transitions = table.transitions
        self.action = table.action
        self.goto = table.goto
        self.is_conflict_free = table.is_conflict_free
        
        # Convert conflicts
        for conflict in table.conflicts:
            self.conflicts.append(LRConflict(
                state=conflict.state,
                symbol=conflict.symbol,
                conflict_type=self._detect_conflict_type(
                    conflict.existing_action,
                    conflict.new_action
                ),
                existing_action=str(conflict.existing_action),
                new_action=str(conflict.new_action)
            ))


def create_parser(grammar: Grammar, parser_type: str) -> LRParser:
    """
    Factory function to create appropriate parser.
    
    Args:
        grammar: Grammar to parse
        parser_type: One of "SLR", "CLR", "LALR"
    
    Returns: Appropriate LRParser subclass instance
    """
    parser_type = parser_type.upper()
    
    if parser_type in ["SLR", "SLR(1)"]:
        return SLRParser(grammar)
    elif parser_type in ["CLR", "CLR(1)"]:
        return CLRParser(grammar)
    elif parser_type in ["LALR", "LALR(1)"]:
        return LALRParser(grammar)
    else:
        raise ValueError(f"Unknown parser type: {parser_type}. Use SLR, CLR, or LALR.")
