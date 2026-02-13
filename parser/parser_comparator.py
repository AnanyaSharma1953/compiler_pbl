"""
Parser Comparison Module

Compares grammar across all parser types (LL1, SLR, CLR, LALR).
Provides unified interface for evaluating grammar suitability.
"""

from typing import Dict, Optional
from parser.grammar import Grammar
from parser.transformations import GrammarTransformer
from parser.ll1_parser import LL1Parser
from parser.lr_parser import SLRParser, CLRParser, LALRParser
from parser.conflict_detector import ConflictDetector
from parser.report_generator import ReportGenerator


class ParserComparator:
    """
    Compares grammar across multiple parser types.
    
    Evaluates which parsing strategies work for a given grammar
    and provides recommendations.
    """
    
    def __init__(self, grammar: Grammar):
        """
        Initialize comparator with a grammar.
        
        Args:
            grammar: Context-free grammar to analyze
        """
        self.original_grammar = grammar
        self.transformation_result = None
        self.ll1_parser = None
        self.slr_parser = None
        self.clr_parser = None
        self.lalr_parser = None
        self.reports = {}
    
    def compare_all(self, transform_for_ll1: bool = True) -> Dict:
        """
        Compare grammar across all parser types.
        
        Args:
            transform_for_ll1: Whether to apply transformations for LL(1)
        
        Returns:
            Comprehensive comparison report
        """
        results = {}
        
        # Step 1: Try LL(1) parsing
        ll1_grammar = self.original_grammar
        if transform_for_ll1:
            # Apply transformations
            transformer = GrammarTransformer(self.original_grammar)
            self.transformation_result = transformer.transform_for_ll1()
            ll1_grammar = self.transformation_result.transformed_grammar
            results["transformations"] = ReportGenerator.transformation_report(
                self.transformation_result
            )
        
        # Build LL(1) parser
        try:
            self.ll1_parser = LL1Parser(ll1_grammar)
            ll1_report = ReportGenerator.ll1_report(self.ll1_parser, include_table=False)
            ll1_conflicts = ConflictDetector.analyze_ll1_conflicts(self.ll1_parser)
            results["LL(1)"] = {
                **ll1_report,
                "conflict_analysis": ll1_conflicts.__dict__,
                "grammar_used": "transformed" if transform_for_ll1 else "original"
            }
        except Exception as e:
            results["LL(1)"] = {
                "error": str(e),
                "is_ll1": False,
                "conflict_count": float('inf')
            }
        
        # Step 2: Build LR parsers (use original grammar)
        # SLR
        try:
            self.slr_parser = SLRParser(self.original_grammar)
            slr_report = ReportGenerator.lr_report(self.slr_parser, include_tables=False)
            slr_conflicts = ConflictDetector.analyze_lr_conflicts(self.slr_parser)
            results["SLR(1)"] = {
                **slr_report,
                "conflict_analysis": slr_conflicts.__dict__
            }
        except Exception as e:
            results["SLR(1)"] = {
                "error": str(e),
                "is_conflict_free": False,
                "conflict_count": float('inf')
            }
        
        # CLR
        try:
            self.clr_parser = CLRParser(self.original_grammar)
            clr_report = ReportGenerator.lr_report(self.clr_parser, include_tables=False)
            clr_conflicts = ConflictDetector.analyze_lr_conflicts(self.clr_parser)
            results["CLR(1)"] = {
                **clr_report,
                "conflict_analysis": clr_conflicts.__dict__
            }
        except Exception as e:
            results["CLR(1)"] = {
                "error": str(e),
                "is_conflict_free": False,
                "conflict_count": float('inf')
            }
        
        # LALR
        try:
            self.lalr_parser = LALRParser(self.original_grammar)
            lalr_report = ReportGenerator.lr_report(self.lalr_parser, include_tables=False)
            lalr_conflicts = ConflictDetector.analyze_lr_conflicts(self.lalr_parser)
            results["LALR(1)"] = {
                **lalr_report,
                "conflict_analysis": lalr_conflicts.__dict__
            }
        except Exception as e:
            results["LALR(1)"] = {
                "error": str(e),
                "is_conflict_free": False,
                "conflict_count": float('inf')
            }
        
        # Step 3: Generate comparison report
        comparison = self._generate_comparison_summary(results)
        results["comparison"] = comparison
        
        self.reports = results
        return results
    
    def _generate_comparison_summary(self, results: Dict) -> Dict:
        """Generate summary comparing all parsers."""
        summary = {
            "parsers_tested": len([k for k in results.keys() if k != "transformations"]),
            "conflict_free_parsers": [],
            "parsers_with_conflicts": [],
            "parser_comparison": {}
        }
        
        for parser_type in ["LL(1)", "SLR(1)", "CLR(1)", "LALR(1)"]:
            if parser_type not in results:
                continue
            
            result = results[parser_type]
            is_conflict_free = result.get("is_ll1", result.get("is_conflict_free", False))
            conflicts = result.get("conflict_count", result.get("summary", {}).get("conflicts", 0))
            
            parser_info = {
                "conflict_free": is_conflict_free,
                "conflicts": conflicts if conflicts != float('inf') else "N/A",
                "status": "✅ Works" if is_conflict_free else "❌ Has Conflicts"
            }
            
            # Add size metrics
            if "summary" in result:
                summary_data = result["summary"]
                if "states" in summary_data:
                    parser_info["states"] = summary_data["states"]
                if "total_table_entries" in summary_data:
                    parser_info["table_entries"] = summary_data["total_table_entries"]
                elif "filled_cells" in summary_data:
                    parser_info["table_entries"] = summary_data["filled_cells"]
            
            summary["parser_comparison"][parser_type] = parser_info
            
            if is_conflict_free:
                summary["conflict_free_parsers"].append(parser_type)
            else:
                summary["parsers_with_conflicts"].append(parser_type)
        
        # Best recommendation
        summary["best_parser"] = self._get_best_parser(summary["conflict_free_parsers"])
        summary["recommendation"] = self._generate_recommendation(summary)
        
        return summary
    
    def _get_best_parser(self, conflict_free: list) -> Optional[str]:
        """Determine best parser from conflict-free options."""
        # Preference order: LL(1) > SLR > LALR > CLR
        # (LL1 is simplest, CLR has most states)
        preference = ["LL(1)", "SLR(1)", "LALR(1)", "CLR(1)"]
        
        for parser in preference:
            if parser in conflict_free:
                return parser
        
        return None
    
    def _generate_recommendation(self, summary: Dict) -> str:
        """Generate human-readable recommendation."""
        best = summary["best_parser"]
        
        if best is None:
            return ("❌ Grammar is not suitable for any tested parser. "
                   "Consider rewriting the grammar to eliminate ambiguity and conflicts.")
        
        recommendations = {
            "LL(1)": ("✅ Use LL(1) predictive parser. "
                     "Grammar is suitable for top-down parsing (simplest and most efficient)."),
            "SLR(1)": ("✅ Use SLR(1) parser. "
                      "Grammar works with Simple LR parsing (good balance of power and efficiency)."),
            "LALR(1)": ("✅ Use LALR(1) parser. "
                       "Grammar requires LALR parsing (standard choice, used by YACC/Bison)."),
            "CLR(1)": ("✅ Use CLR(1) parser. "
                      "Grammar needs canonical LR parsing (most powerful but more states).")
        }
        
        recommendation = recommendations.get(best, "")
        
        # Add note about alternatives
        all_working = summary["conflict_free_parsers"]
        if len(all_working) > 1:
            others = [p for p in all_working if p != best]
            recommendation += f" (Also works: {', '.join(others)})"
        
        return recommendation
    
    def get_parser(self, parser_type: str):
        """
        Get specific parser instance.
        
        Args:
            parser_type: One of "LL(1)", "SLR(1)", "CLR(1)", "LALR(1)"
        
        Returns:
            Parser instance or None if not built
        """
        parser_map = {
            "LL(1)": self.ll1_parser,
            "SLR(1)": self.slr_parser,
            "CLR(1)": self.clr_parser,
            "LALR(1)": self.lalr_parser
        }
        return parser_map.get(parser_type)
