"""
Report Generator

Generates structured reports for grammar analysis and parsing results.
Separates data from presentation, allowing flexible output formats.
"""

from typing import Dict, List, Any
from dataclasses import asdict
from parser.grammar import Grammar
from parser.transformations import TransformationResult


class ReportGenerator:
    """Generates structured reports for parsing framework."""
    
    @staticmethod
    def grammar_summary(grammar: Grammar) -> Dict:
        """
        Generate summary of grammar properties.
        
        Returns:
            Dictionary with grammar statistics and properties
        """
        productions = grammar.get_productions()
        terminals = grammar.get_terminals()
        nonterminals = grammar.get_nonterminals()
        
        return {
            "start_symbol": grammar.get_start_symbol(),
            "productions_count": len(productions),
            "terminals_count": len(terminals),
            "nonterminals_count": len(nonterminals),
            "terminals": sorted(list(terminals)),
            "nonterminals": sorted(list(nonterminals)),
            "productions": [
                {
                    "index": i,
                    "lhs": prod.lhs,
                    "rhs": " ".join(prod.rhs),
                    "formatted": f"{prod.lhs} → {' '.join(prod.rhs)}"
                }
                for i, prod in enumerate(productions)
            ]
        }
    
    @staticmethod
    def transformation_report(result: TransformationResult) -> Dict:
        """
        Generate report of grammar transformations.
        
        Args:
            result: TransformationResult from GrammarTransformer
        
        Returns:
            Dictionary with before/after grammar and transformation details
        """
        return {
            "transformations_applied": result.transformations_applied,
            "left_recursion_removed": result.left_recursion_removed,
            "left_factored": result.left_factored,
            "new_nonterminals": sorted(list(result.new_nonterminals)),
            "new_nonterminals_count": len(result.new_nonterminals),
            "original_grammar": ReportGenerator.grammar_summary(result.original_grammar),
            "transformed_grammar": ReportGenerator.grammar_summary(result.transformed_grammar),
            "transformation_details": result.transformation_details
        }
    
    @staticmethod
    def first_follow_report(first_sets: Dict, follow_sets: Dict) -> Dict:
        """
        Generate report of FIRST and FOLLOW sets.
        
        Args:
            first_sets: Dictionary of FIRST sets
            follow_sets: Dictionary of FOLLOW sets
        
        Returns:
            Formatted dictionary with FIRST and FOLLOW information
        """
        return {
            "first_sets": {
                nt: sorted(list(first_set))
                for nt, first_set in sorted(first_sets.items())
            },
            "follow_sets": {
                nt: sorted(list(follow_set))
                for nt, follow_set in sorted(follow_sets.items())
            },
            "first_count": len(first_sets),
            "follow_count": len(follow_sets)
        }
    
    @staticmethod
    def ll1_report(ll1_parser, include_table: bool = True) -> Dict:
        """
        Generate report for LL(1) parser.
        
        Args:
            ll1_parser: LL1Parser instance
            include_table: Whether to include full parsing table
        
        Returns:
            Dictionary with LL(1) parser information
        """
        report = {
            "parser_type": "LL(1)",
            "is_ll1": ll1_parser.is_ll1,
            "conflicts": ll1_parser.conflicts,
            "conflict_count": len(ll1_parser.conflicts),
            "summary": ll1_parser.get_table_summary()
        }
        
        if include_table:
            # Format parsing table for display
            table_data = {}
            for nonterminal, row in ll1_parser.parsing_table.items():
                table_data[nonterminal] = {
                    terminal: {
                        "production": f"{entry.production.lhs} → {' '.join(entry.production.rhs)}",
                        "production_index": entry.production_index
                    }
                    for terminal, entry in row.items()
                }
            report["parsing_table"] = table_data
        
        return report
    
    @staticmethod
    def lr_report(lr_parser, include_tables: bool = False) -> Dict:
        """
        Generate report for LR parser (SLR/CLR/LALR).
        
        Args:
            lr_parser: LRParser instance
            include_tables: Whether to include full ACTION/GOTO tables
        
        Returns:
            Dictionary with LR parser information
        """
        report = {
            "parser_type": lr_parser.get_parser_type(),
            "is_conflict_free": lr_parser.is_conflict_free,
            "summary": lr_parser.get_summary(),
            "conflicts": [
                {
                    "state": c.state,
                    "symbol": c.symbol,
                    "type": c.conflict_type,
                    "existing": c.existing_action,
                    "new": c.new_action
                }
                for c in lr_parser.conflicts
            ]
        }
        
        if include_tables:
            report["action_table"] = lr_parser.action
            report["goto_table"] = lr_parser.goto
            report["states_count"] = len(lr_parser.states)
            report["transitions_count"] = len(lr_parser.transitions)
        
        return report
    
    @staticmethod
    def comparison_report(
        grammar: Grammar,
        ll1_result: Dict,
        slr_result: Dict,
        clr_result: Dict,
        lalr_result: Dict
    ) -> Dict:
        """
        Generate comparison report across all parser types.
        
        Args:
            grammar: Original grammar
            ll1_result: LL(1) parser report
            slr_result: SLR parser report
            clr_result: CLR parser report
            lalr_result: LALR parser report
        
        Returns:
            Comprehensive comparison dictionary
        """
        parsers = {
            "LL(1)": ll1_result,
            "SLR(1)": slr_result,
            "CLR(1)": clr_result,
            "LALR(1)": lalr_result
        }
        
        # Determine which parsers work for this grammar
        conflict_free = {
            parser_type: result.get("is_ll1" if parser_type == "LL(1)" else "is_conflict_free", False)
            for parser_type, result in parsers.items()
        }
        
        # Best parser recommendation
        best_parser = None
        if conflict_free["LL(1)"]:
            best_parser = "LL(1)"
        elif conflict_free["SLR(1)"]:
            best_parser = "SLR(1)"
        elif conflict_free["LALR(1)"]:
            best_parser = "LALR(1)"
        elif conflict_free["CLR(1)"]:
            best_parser = "CLR(1)"
        
        return {
            "grammar": ReportGenerator.grammar_summary(grammar),
            "parsers": parsers,
            "conflict_free_parsers": conflict_free,
            "working_parsers": [p for p, works in conflict_free.items() if works],
            "failed_parsers": [p for p, works in conflict_free.items() if not works],
            "best_parser": best_parser,
            "recommendation": ReportGenerator._generate_recommendation(conflict_free, parsers),
            "complexity_comparison": {
                parser_type: {
                    "conflicts": result.get("conflict_count", result.get("summary", {}).get("conflicts", 0)),
                    "table_size": result.get("summary", {}).get("total_table_entries") or result.get("summary", {}).get("filled_cells", 0),
                    "states": result.get("summary", {}).get("states", 0)
                }
                for parser_type, result in parsers.items()
            }
        }
    
    @staticmethod
    def _generate_recommendation(conflict_free: Dict, parsers: Dict) -> str:
        """Generate human-readable recommendation."""
        working = [p for p, works in conflict_free.items() if works]
        
        if not working:
            return "Grammar is not suitable for any of the tested parsing methods. Consider rewriting the grammar."
        
        if "LL(1)" in working:
            return "Grammar is LL(1). Use predictive top-down parsing for simplicity and efficiency."
        elif "SLR(1)" in working:
            return "Grammar is SLR(1). Use SLR parser for efficient bottom-up parsing with minimal states."
        elif "LALR(1)" in working:
            return "Grammar is LALR(1). Use LALR parser (like YACC) for powerful parsing with moderate state count."
        elif "CLR(1)" in working:
            return "Grammar is CLR(1). Use canonical LR parser for maximum parsing power (may have many states)."
        else:
            return "No suitable parser found for this grammar."
    
    @staticmethod
    def parse_result_report(parse_result, parser_type: str) -> Dict:
        """
        Generate report for parsing result.
        
        Args:
            parse_result: Parse result object (LRParseResult or similar)
            parser_type: Type of parser used
        
        Returns:
            Dictionary with parsing results
        """
        return {
            "parser_type": parser_type,
            "accepted": parse_result.accepted,
            "steps_count": len(parse_result.steps),
            "steps": [
                {
                    "step": i + 1,
                    "stack": getattr(step, 'stack', str(step)),
                    "input": getattr(step, 'input_remaining', ''),
                    "action": getattr(step, 'action', str(step))
                }
                for i, step in enumerate(parse_result.steps)
            ]
        }
