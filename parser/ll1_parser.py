"""
LL(1) Parser Implementation

Implements top-down predictive parsing:
1. FIRST+ (FIRST and FOLLOW enhanced)
2. LL(1) parsing table construction
3. Conflict detection for LL(1)
4. Predictive parsing simulation
"""

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional
from parser.grammar import Grammar, Production
from parser.first_follow import compute_first_sets, compute_follow_sets


@dataclass
class LL1Conflict:
    """Represents a conflict in LL(1) parsing table."""
    nonterminal: str
    terminal: str
    production1: Production
    production2: Production
    conflict_type: str  # "multiple_productions"


@dataclass
class LL1ParseStep:
    """Represents a step in predictive parsing."""
    step_number: int
    stack: List[str]
    input_remaining: str
    action: str
    matched: Optional[str] = None
    production_used: Optional[Production] = None


@dataclass
class LL1TableEntry:
    """Entry in LL(1) parsing table."""
    production: Production
    production_index: int


class LL1Parser:
    """
    LL(1) Predictive Parser Implementation.
    
    Constructs LL(1) parsing table and performs top-down predictive parsing.
    """
    
    def __init__(self, grammar: Grammar):
        """
        Initialize LL(1) parser with a grammar.
        
        Args:
            grammar: Context-free grammar (should be transformed for LL(1) if needed)
        """
        self.grammar = grammar
        self.first_sets = compute_first_sets(grammar)
        self.follow_sets = compute_follow_sets(grammar)
        self.parsing_table: Dict[str, Dict[str, LL1TableEntry]] = {}
        self.conflicts: List[LL1Conflict] = []
        self.is_ll1 = False
        
        self._build_parsing_table()
    
    def _compute_first_plus(self, production: Production) -> Set[str]:
        """
        Compute FIRST+ for a production.
        
        FIRST+(A → α) = 
            if ε ∈ FIRST(α): FIRST(α) ∪ FOLLOW(A)
            else: FIRST(α)
        
        This determines which terminals can start a derivation using this production.
        """
        first_plus = set()
        rhs = production.rhs
        
        if rhs == ["ε"]:
            # ε production: use FOLLOW(A)
            first_plus = self.follow_sets.get(production.lhs, set()).copy()
        else:
            # Compute FIRST(α) for the RHS
            first_rhs = self._compute_first_of_sequence(rhs)
            first_plus = first_rhs.copy()
            
            # If ε ∈ FIRST(α), add FOLLOW(A)
            if "ε" in first_rhs:
                first_plus.discard("ε")
                first_plus.update(self.follow_sets.get(production.lhs, set()))
        
        return first_plus
    
    def _compute_first_of_sequence(self, sequence: List[str]) -> Set[str]:
        """
        Compute FIRST of a sequence of symbols.
        
        FIRST(X₁ X₂ ... Xₙ):
        - Add FIRST(X₁) - {ε}
        - If ε ∈ FIRST(X₁), add FIRST(X₂) - {ε}
        - Continue while ε is in FIRST of current symbol
        - If all symbols can derive ε, add ε
        """
        result = set()
        all_nullable = True
        
        for symbol in sequence:
            if symbol == "ε":
                result.add("ε")
                continue
            
            symbol_first = self.first_sets.get(symbol, {symbol})
            result.update(symbol_first - {"ε"})
            
            if "ε" not in symbol_first:
                all_nullable = False
                break
        
        if all_nullable:
            result.add("ε")
        
        return result
    
    def _build_parsing_table(self) -> None:
        """
        Build LL(1) parsing table.
        
        For each production A → α:
            For each terminal a in FIRST+(A → α):
                Add production to table[A, a]
        
        If multiple productions map to same cell, there's a conflict.
        """
        self.parsing_table = {}
        self.conflicts = []
        
        # Index productions for reporting
        production_index = {prod: i for i, prod in enumerate(self.grammar.productions)}
        
        for prod in self.grammar.productions:
            nonterminal = prod.lhs
            
            # Initialize table row for this non-terminal
            if nonterminal not in self.parsing_table:
                self.parsing_table[nonterminal] = {}
            
            # Compute FIRST+ for this production
            first_plus = self._compute_first_plus(prod)
            
            # Add entry for each terminal in FIRST+
            for terminal in first_plus:
                if terminal == "ε":
                    continue
                
                if terminal in self.parsing_table[nonterminal]:
                    # Conflict: multiple productions for same (nonterminal, terminal)
                    existing_entry = self.parsing_table[nonterminal][terminal]
                    conflict = LL1Conflict(
                        nonterminal=nonterminal,
                        terminal=terminal,
                        production1=existing_entry.production,
                        production2=prod,
                        conflict_type="multiple_productions"
                    )
                    self.conflicts.append(conflict)
                else:
                    # Add to parsing table
                    self.parsing_table[nonterminal][terminal] = LL1TableEntry(
                        production=prod,
                        production_index=production_index[prod]
                    )
        
        self.is_ll1 = len(self.conflicts) == 0
    
    def parse(self, input_string: str) -> Tuple[List[LL1ParseStep], bool]:
        """
        Perform predictive parsing on input string.
        
        Algorithm:
        1. Initialize stack with $ and start symbol
        2. While stack not empty:
            - If top = terminal: match with input
            - If top = non-terminal: use parsing table to expand
            - If mismatch or no table entry: error
        
        Returns: (parse_steps, accepted)
        """
        if not self.is_ll1:
            # Cannot parse if grammar is not LL(1)
            return [], False
        
        tokens = input_string.split()
        tokens.append("$")  # End marker
        
        # Initialize stack with $ and start symbol
        start_symbol = self.grammar.get_start_symbol()
        stack = ["$", start_symbol]
        input_idx = 0
        steps = []
        step_num = 1
        
        while len(stack) > 0:
            top = stack[-1]
            current_input = tokens[input_idx] if input_idx < len(tokens) else "$"
            
            # Record current state
            input_remaining = " ".join(tokens[input_idx:])
            
            if top == "$":
                # End of parsing
                if current_input == "$":
                    steps.append(LL1ParseStep(
                        step_number=step_num,
                        stack=stack.copy(),
                        input_remaining=input_remaining,
                        action="Accept"
                    ))
                    return steps, True
                else:
                    steps.append(LL1ParseStep(
                        step_number=step_num,
                        stack=stack.copy(),
                        input_remaining=input_remaining,
                        action=f"Error: Unexpected input '{current_input}'"
                    ))
                    return steps, False
            
            elif top in self.grammar.get_terminals():
                # Top is terminal: match with input
                if top == current_input:
                    steps.append(LL1ParseStep(
                        step_number=step_num,
                        stack=stack.copy(),
                        input_remaining=input_remaining,
                        action=f"Match '{top}'",
                        matched=top
                    ))
                    stack.pop()
                    input_idx += 1
                else:
                    steps.append(LL1ParseStep(
                        step_number=step_num,
                        stack=stack.copy(),
                        input_remaining=input_remaining,
                        action=f"Error: Expected '{top}', got '{current_input}'"
                    ))
                    return steps, False
            
            else:
                # Top is non-terminal: use parsing table
                if top in self.parsing_table and current_input in self.parsing_table[top]:
                    entry = self.parsing_table[top][current_input]
                    prod = entry.production
                    
                    # Pop non-terminal and push RHS in reverse order
                    stack.pop()
                    rhs = prod.rhs
                    if rhs != ["ε"]:
                        for symbol in reversed(rhs):
                            stack.append(symbol)
                    
                    steps.append(LL1ParseStep(
                        step_number=step_num,
                        stack=stack.copy(),
                        input_remaining=input_remaining,
                        action=f"Output {prod.lhs} → {' '.join(prod.rhs)}",
                        production_used=prod
                    ))
                else:
                    steps.append(LL1ParseStep(
                        step_number=step_num,
                        stack=stack.copy(),
                        input_remaining=input_remaining,
                        action=f"Error: No table entry for ({top}, {current_input})"
                    ))
                    return steps, False
            
            step_num += 1
        
        return steps, False
    
    def get_table_summary(self) -> Dict:
        """
        Get summary of parsing table for reporting.
        
        Returns structured dictionary with:
        - Table dimensions
        - Number of entries
        - Conflicts
        - Coverage statistics
        """
        terminals = self.grammar.get_terminals()
        nonterminals = self.grammar.get_nonterminals()
        
        total_cells = len(nonterminals) * len(terminals)
        filled_cells = sum(len(row) for row in self.parsing_table.values())
        
        return {
            "is_ll1": self.is_ll1,
            "nonterminals": len(nonterminals),
            "terminals": len(terminals),
            "total_cells": total_cells,
            "filled_cells": filled_cells,
            "empty_cells": total_cells - filled_cells,
            "coverage_percent": (filled_cells / total_cells * 100) if total_cells > 0 else 0,
            "conflicts": len(self.conflicts),
            "conflict_details": [
                {
                    "nonterminal": c.nonterminal,
                    "terminal": c.terminal,
                    "production1": f"{c.production1.lhs} → {' '.join(c.production1.rhs)}",
                    "production2": f"{c.production2.lhs} → {' '.join(c.production2.rhs)}"
                }
                for c in self.conflicts
            ]
        }
