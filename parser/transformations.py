"""
Grammar Transformation Module

Implements transformations required for top-down parsing:
1. Left recursion elimination (direct and indirect)
2. Left factoring
3. Grammar normalization

All transformations preserve language recognition while making grammar suitable for LL(1) parsing.
"""

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple
from parser.grammar import Grammar, Production


@dataclass
class TransformationResult:
    """Result of a grammar transformation."""
    original_grammar: Grammar
    transformed_grammar: Grammar
    transformations_applied: List[str]
    left_recursion_removed: bool
    left_factored: bool
    new_nonterminals: Set[str]
    transformation_details: Dict[str, str]


class GrammarTransformer:
    """Handles grammar transformations for top-down parsing."""
    
    def __init__(self, grammar: Grammar):
        self.original_grammar = grammar
        self.new_nonterminal_counter = 0
        self.transformations = []
        self.transformation_details = {}
        self.new_nonterminals = set()
    
    def _generate_new_nonterminal(self, base: str) -> str:
        """Generate a new unique non-terminal symbol."""
        self.new_nonterminal_counter += 1
        new_nt = f"{base}'"
        while new_nt in self.original_grammar.get_nonterminals() or new_nt in self.new_nonterminals:
            new_nt += "'"
        self.new_nonterminals.add(new_nt)
        return new_nt
    
    def detect_direct_left_recursion(self, nonterminal: str, productions: List[Production]) -> Tuple[bool, List[Production], List[Production]]:
        """
        Detect direct left recursion in productions for a non-terminal.
        
        Returns: (has_recursion, recursive_productions, non_recursive_productions)
        
        Direct left recursion: A → A α | β
        """
        recursive = []
        non_recursive = []
        
        for prod in productions:
            if len(prod.rhs) > 0 and prod.rhs[0] == nonterminal:
                # Direct left recursion: A → A α
                recursive.append(prod)
            else:
                # Non-recursive: A → β
                non_recursive.append(prod)
        
        return len(recursive) > 0, recursive, non_recursive
    
    def eliminate_direct_left_recursion(self, nonterminal: str, productions: List[Production]) -> List[Production]:
        """
        Eliminate direct left recursion.
        
        Transform:
            A → A α₁ | A α₂ | ... | A αₘ | β₁ | β₂ | ... | βₙ
        Into:
            A → β₁ A' | β₂ A' | ... | βₙ A'
            A' → α₁ A' | α₂ A' | ... | αₘ A' | ε
        """
        has_recursion, recursive, non_recursive = self.detect_direct_left_recursion(nonterminal, productions)
        
        if not has_recursion:
            return productions
        
        if len(non_recursive) == 0:
            # All productions are left-recursive, add epsilon
            non_recursive = [Production(nonterminal, ["ε"])]
        
        # Create new non-terminal A'
        new_nt = self._generate_new_nonterminal(nonterminal)
        
        # Transform A → β₁ | β₂ | ... → A → β₁ A' | β₂ A' | ...
        new_productions = []
        for prod in non_recursive:
            rhs = list(prod.rhs) if prod.rhs != ["ε"] else []
            new_productions.append(Production(nonterminal, rhs + [new_nt]))
        
        # Transform A → A α₁ | A α₂ | ... → A' → α₁ A' | α₂ A' | ...
        for prod in recursive:
            # Remove the leading A from A α
            alpha = list(prod.rhs[1:])  # α is everything after A
            new_productions.append(Production(new_nt, alpha + [new_nt]))
        
        # Add A' → ε
        new_productions.append(Production(new_nt, ["ε"]))
        
        detail = f"Eliminated direct left recursion in {nonterminal}, created {new_nt}"
        self.transformations.append(detail)
        self.transformation_details[nonterminal] = detail
        
        return new_productions
    
    def eliminate_indirect_left_recursion(self) -> Grammar:
        """
        Eliminate indirect left recursion using algorithm from Aho/Ullman.
        
        Algorithm:
        1. Order non-terminals: A₁, A₂, ..., Aₙ
        2. For i = 1 to n:
            For j = 1 to i-1:
                Replace Aᵢ → Aⱼ γ with Aᵢ → δ₁ γ | δ₂ γ | ... for all Aⱼ → δ₁ | δ₂ | ...
            Eliminate direct left recursion for Aᵢ
        """
        # Get ordered list of non-terminals
        nonterminals = sorted(self.original_grammar.get_nonterminals())
        
        # Group productions by LHS
        productions_dict = {}
        for prod in self.original_grammar.productions:
            if prod.lhs not in productions_dict:
                productions_dict[prod.lhs] = []
            productions_dict[prod.lhs].append(prod)
        
        new_productions = []
        
        for i, A_i in enumerate(nonterminals):
            if A_i not in productions_dict:
                continue
            
            current_prods = productions_dict[A_i].copy()
            
            # Substitute productions from earlier non-terminals
            for j in range(i):
                A_j = nonterminals[j]
                
                if A_j not in productions_dict:
                    continue
                
                # Check if any production has form A_i → A_j γ
                substituted = []
                remaining = []
                
                for prod in current_prods:
                    if len(prod.rhs) > 0 and prod.rhs[0] == A_j:
                        # Substitute: A_i → A_j γ becomes A_i → δ γ for each A_j → δ
                        gamma = list(prod.rhs[1:])
                        for A_j_prod in productions_dict[A_j]:
                            new_rhs = list(A_j_prod.rhs) + gamma
                            substituted.append(Production(A_i, new_rhs))
                    else:
                        remaining.append(prod)
                
                if substituted:
                    current_prods = remaining + substituted
                    self.transformations.append(f"Substituted {A_j} in {A_i} productions")
            
            # Eliminate direct left recursion for A_i
            current_prods = self.eliminate_direct_left_recursion(A_i, current_prods)
            productions_dict[A_i] = current_prods
        
        # Collect all productions
        for nt in productions_dict:
            new_productions.extend(productions_dict[nt])
        
        return Grammar(new_productions, self.original_grammar.start_symbol)
    
    def detect_left_factoring_opportunities(self, nonterminal: str, productions: List[Production]) -> List[Tuple[str, List[Production]]]:
        """
        Detect productions that share a common prefix and can be left-factored.
        
        Returns list of (common_prefix, productions_with_prefix)
        """
        # Group productions by their first symbol
        prefix_groups = {}
        
        for prod in productions:
            if len(prod.rhs) == 0 or prod.rhs == ["ε"]:
                continue
            
            first_symbol = prod.rhs[0]
            if first_symbol not in prefix_groups:
                prefix_groups[first_symbol] = []
            prefix_groups[first_symbol].append(prod)
        
        # Find groups with multiple productions (need factoring)
        opportunities = []
        for prefix, prods in prefix_groups.items():
            if len(prods) > 1:
                opportunities.append((prefix, prods))
        
        return opportunities
    
    def apply_left_factoring(self, nonterminal: str, productions: List[Production]) -> List[Production]:
        """
        Apply left factoring to productions.
        
        Transform:
            A → α β₁ | α β₂ | ... | α βₙ | γ
        Into:
            A → α A' | γ
            A' → β₁ | β₂ | ... | βₙ
        """
        opportunities = self.detect_left_factoring_opportunities(nonterminal, productions)
        
        if not opportunities:
            return productions
        
        new_productions = []
        factored_prods = set()
        
        for prefix, prods_with_prefix in opportunities:
            # Create new non-terminal
            new_nt = self._generate_new_nonterminal(nonterminal)
            
            # A → α A'
            new_productions.append(Production(nonterminal, [prefix, new_nt]))
            
            # A' → β₁ | β₂ | ... (suffixes after common prefix)
            for prod in prods_with_prefix:
                suffix = list(prod.rhs[1:])  # Everything after the common prefix
                if len(suffix) == 0:
                    suffix = ["ε"]
                new_productions.append(Production(new_nt, suffix))
                factored_prods.add(id(prod))
            
            detail = f"Left factored {nonterminal} with prefix '{prefix}', created {new_nt}"
            self.transformations.append(detail)
            self.transformation_details[f"{nonterminal}_factor"] = detail
        
        # Add productions that weren't factored
        for prod in productions:
            if id(prod) not in factored_prods:
                new_productions.append(prod)
        
        return new_productions
    
    def transform_for_ll1(self) -> TransformationResult:
        """
        Apply all necessary transformations to make grammar suitable for LL(1) parsing.
        
        Steps:
        1. Eliminate left recursion (indirect then direct)
        2. Apply left factoring
        """
        self.transformations = []
        self.transformation_details = {}
        self.new_nonterminals = set()
        self.new_nonterminal_counter = 0
        
        # Step 1: Eliminate all left recursion
        transformed = self.eliminate_indirect_left_recursion()
        left_recursion_removed = len(self.transformations) > 0
        
        # Step 2: Apply left factoring
        productions_dict = {}
        for prod in transformed.productions:
            if prod.lhs not in productions_dict:
                productions_dict[prod.lhs] = []
            productions_dict[prod.lhs].append(prod)
        
        factored_productions = []
        for nt in productions_dict:
            factored = self.apply_left_factoring(nt, productions_dict[nt])
            factored_productions.extend(factored)
        
        left_factored = len([t for t in self.transformations if "Left factored" in t]) > 0
        
        final_grammar = Grammar(factored_productions, self.original_grammar.start_symbol)
        
        return TransformationResult(
            original_grammar=self.original_grammar,
            transformed_grammar=final_grammar,
            transformations_applied=self.transformations.copy(),
            left_recursion_removed=left_recursion_removed,
            left_factored=left_factored,
            new_nonterminals=self.new_nonterminals.copy(),
            transformation_details=self.transformation_details.copy()
        )
