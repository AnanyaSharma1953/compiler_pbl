"""
Unified Conflict Detector

Detects and reports conflicts for both LL(1) and LR parsers.
Provides structured conflict information for clear reporting.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from parser.grammar import Grammar, Production


@dataclass
class ConflictReport:
    """Unified conflict report for any parser type."""
    parser_type: str
    has_conflicts: bool
    conflict_count: int
    conflicts: List[Dict]
    is_ambiguous: bool = False
    ambiguity_reason: Optional[str] = None


class ConflictDetector:
    """Detects and analyzes conflicts in parsing tables."""
    
    @staticmethod
    def analyze_ll1_conflicts(ll1_parser) -> ConflictReport:
        """
        Analyze LL(1) parser conflicts.
        
        Args:
            ll1_parser: LL1Parser instance
        
        Returns: ConflictReport with LL(1) conflict details
        """
        conflicts_data = []
        
        for conflict in ll1_parser.conflicts:
            conflicts_data.append({
                "type": "LL(1) Multiple Productions",
                "location": f"table[{conflict.nonterminal}, {conflict.terminal}]",
                "nonterminal": conflict.nonterminal,
                "terminal": conflict.terminal,
                "production1": f"{conflict.production1.lhs} → {' '.join(conflict.production1.rhs)}",
                "production2": f"{conflict.production2.lhs} → {' '.join(conflict.production2.rhs)}",
                "description": f"Multiple productions for ({conflict.nonterminal}, {conflict.terminal})",
                "severity": "error"
            })
        
        has_conflicts = len(ll1_parser.conflicts) > 0
        
        return ConflictReport(
            parser_type="LL(1)",
            has_conflicts=has_conflicts,
            conflict_count=len(ll1_parser.conflicts),
            conflicts=conflicts_data,
            is_ambiguous=False,  # LL(1) conflicts don't necessarily mean ambiguity
            ambiguity_reason=None
        )
    
    @staticmethod
    def analyze_lr_conflicts(lr_parser) -> ConflictReport:
        """
        Analyze LR parser conflicts.
        
        Args:
            lr_parser: LRParser instance (SLR/CLR/LALR)
        
        Returns: ConflictReport with LR conflict details
        """
        conflicts_data = []
        reduce_reduce_count = 0
        
        for conflict in lr_parser.conflicts:
            conflict_desc = {
                "type": conflict.conflict_type.replace("_", "-").title(),
                "location": f"state {conflict.state}, symbol '{conflict.symbol}'",
                "state": conflict.state,
                "symbol": conflict.symbol,
                "conflict_type": conflict.conflict_type,
                "existing_action": conflict.existing_action,
                "new_action": conflict.new_action,
                "severity": "error"
            }
            
            if conflict.conflict_type == "shift_reduce":
                conflict_desc["description"] = (
                    f"Shift-Reduce conflict at state {conflict.state} on symbol '{conflict.symbol}'. "
                    f"Parser cannot decide whether to shift or reduce."
                )
            elif conflict.conflict_type == "reduce_reduce":
                conflict_desc["description"] = (
                    f"Reduce-Reduce conflict at state {conflict.state} on symbol '{conflict.symbol}'. "
                    f"Parser cannot decide which production to use for reduction."
                )
                reduce_reduce_count += 1
            else:
                conflict_desc["description"] = f"Conflict at state {conflict.state} on '{conflict.symbol}'"
            
            conflicts_data.append(conflict_desc)
        
        has_conflicts = len(lr_parser.conflicts) > 0
        
        # Reduce-reduce conflicts in CLR strongly indicate ambiguity
        is_ambiguous = reduce_reduce_count > 0 and lr_parser.get_parser_type() == "CLR(1)"
        ambiguity_reason = None
        if is_ambiguous:
            ambiguity_reason = (
                f"Grammar has {reduce_reduce_count} reduce-reduce conflict(s) in CLR parser. "
                "This typically indicates the grammar is ambiguous."
            )
        
        return ConflictReport(
            parser_type=lr_parser.get_parser_type(),
            has_conflicts=has_conflicts,
            conflict_count=len(lr_parser.conflicts),
            conflicts=conflicts_data,
            is_ambiguous=is_ambiguous,
            ambiguity_reason=ambiguity_reason
        )
    
    @staticmethod
    def generate_conflict_summary(reports: List[ConflictReport]) -> Dict:
        """
        Generate summary comparing conflicts across multiple parsers.
        
        Args:
            reports: List of ConflictReport objects
        
        Returns: Dictionary with comparison summary
        """
        summary = {
            "total_parsers": len(reports),
            "conflict_free_count": sum(1 for r in reports if not r.has_conflicts),
            "parsers_with_conflicts": sum(1 for r in reports if r.has_conflicts),
            "by_parser": {}
        }
        
        for report in reports:
            summary["by_parser"][report.parser_type] = {
                "has_conflicts": report.has_conflicts,
                "conflict_count": report.conflict_count,
                "is_ambiguous": report.is_ambiguous
            }
        
        return summary
    
    @staticmethod
    def format_conflict_for_display(conflict: Dict) -> str:
        """
        Format a single conflict for human-readable display.
        
        Args:
            conflict: Conflict dictionary
        
        Returns: Formatted string
        """
        lines = []
        lines.append(f"⚠️ {conflict['type']} at {conflict['location']}")
        lines.append(f"   {conflict['description']}")
        
        if 'production1' in conflict:
            lines.append(f"   Production 1: {conflict['production1']}")
            lines.append(f"   Production 2: {conflict['production2']}")
        
        if 'existing_action' in conflict:
            lines.append(f"   Existing: {conflict['existing_action']}")
            lines.append(f"   New: {conflict['new_action']}")
        
        return "\n".join(lines)
