"""
Top-Down grammar validation utilities.

Provides structured validation for:
1. Left recursion (direct and indirect)
2. FIRST/FIRST conflicts
3. FIRST/FOLLOW conflicts
4. Left factoring requirements
5. LL(1) table conflicts
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

from parser.first_follow import compute_first_sets, compute_follow_sets, first_of_sequence
from parser.grammar import EPSILON, Grammar, Production
from parser.ll1_parser import LL1Parser


@dataclass
class ValidationIssue:
    code: str
    message: str
    details: str
    severity: str = "error"


@dataclass
class TopDownValidationReport:
    grammar: Grammar
    first_sets: Dict[str, Set[str]]
    follow_sets: Dict[str, Set[str]]
    issues: List[ValidationIssue] = field(default_factory=list)
    ll1_conflicts: List[dict] = field(default_factory=list)

    has_left_recursion: bool = False
    has_first_first_conflict: bool = False
    has_first_follow_conflict: bool = False
    needs_left_factoring: bool = False
    is_ll1: bool = False

    def is_valid_for_ll1(self) -> bool:
        return self.is_ll1 and not self.has_left_recursion and not self.needs_left_factoring

    def is_valid_for_recursive_descent(self) -> bool:
        return not self.has_left_recursion

    def as_dict(self) -> dict:
        return {
            "is_ll1": self.is_ll1,
            "valid_for_ll1": self.is_valid_for_ll1(),
            "valid_for_recursive_descent": self.is_valid_for_recursive_descent(),
            "has_left_recursion": self.has_left_recursion,
            "has_first_first_conflict": self.has_first_first_conflict,
            "has_first_follow_conflict": self.has_first_follow_conflict,
            "needs_left_factoring": self.needs_left_factoring,
            "issue_count": len(self.issues),
            "issues": [
                {
                    "code": issue.code,
                    "message": issue.message,
                    "details": issue.details,
                    "severity": issue.severity,
                }
                for issue in self.issues
            ],
            "ll1_conflicts": self.ll1_conflicts,
        }


class TopDownGrammarValidator:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.first_sets = compute_first_sets(grammar)
        self.follow_sets = compute_follow_sets(grammar)

    def validate(self) -> TopDownValidationReport:
        report = TopDownValidationReport(
            grammar=self.grammar,
            first_sets=self.first_sets,
            follow_sets=self.follow_sets,
        )

        self._detect_left_recursion(report)
        self._detect_first_first_conflicts(report)
        self._detect_first_follow_conflicts(report)
        self._detect_left_factoring(report)
        self._detect_ll1_conflicts(report)

        return report

    def _group_by_lhs(self) -> Dict[str, List[Production]]:
        grouped: Dict[str, List[Production]] = {}
        for production in self.grammar.productions:
            grouped.setdefault(production.lhs, []).append(production)
        return grouped

    def _detect_left_recursion(self, report: TopDownValidationReport) -> None:
        grouped = self._group_by_lhs()
        nullable = {
            symbol
            for symbol in self.grammar.get_nonterminals()
            if EPSILON in self.first_sets.get(symbol, set())
        }

        adjacency: Dict[str, Set[str]] = {nt: set() for nt in self.grammar.get_nonterminals()}

        for lhs, productions in grouped.items():
            for production in productions:
                for symbol in production.rhs:
                    if symbol in self.grammar.get_nonterminals():
                        adjacency[lhs].add(symbol)
                        if symbol in nullable:
                            continue
                    break

        for nonterminal in sorted(self.grammar.get_nonterminals()):
            path = self._find_cycle_path(nonterminal, adjacency)
            if path:
                report.has_left_recursion = True
                cycle_text = " -> ".join(path)
                direct = len(path) == 2 and path[0] == path[1]
                message = "Left recursion detected"
                details = (
                    f"Direct left recursion in {nonterminal}: {cycle_text}"
                    if direct
                    else f"Indirect left recursion involving {nonterminal}: {cycle_text}"
                )
                report.issues.append(
                    ValidationIssue(
                        code="LEFT_RECURSION",
                        message=message,
                        details=details,
                    )
                )

    def _find_cycle_path(self, start: str, adjacency: Dict[str, Set[str]]) -> List[str] | None:
        visited: Set[str] = set()

        def dfs(node: str, path: List[str]) -> List[str] | None:
            if node in visited:
                return None
            visited.add(node)

            for next_node in adjacency.get(node, set()):
                if next_node == start:
                    return path + [next_node]
                if next_node not in path:
                    found = dfs(next_node, path + [next_node])
                    if found:
                        return found
            return None

        return dfs(start, [start])

    def _detect_first_first_conflicts(self, report: TopDownValidationReport) -> None:
        grouped = self._group_by_lhs()
        for lhs, productions in grouped.items():
            production_firsts = [first_of_sequence(prod.rhs, self.first_sets) for prod in productions]

            for i in range(len(productions)):
                for j in range(i + 1, len(productions)):
                    overlap = (production_firsts[i] - {EPSILON}) & (production_firsts[j] - {EPSILON})
                    if overlap:
                        report.has_first_first_conflict = True
                        report.issues.append(
                            ValidationIssue(
                                code="FIRST_FIRST_CONFLICT",
                                message="FIRST/FIRST conflict detected",
                                details=(
                                    f"{lhs}: {productions[i]} and {productions[j]} overlap on "
                                    f"{sorted(overlap)}"
                                ),
                            )
                        )

    def _detect_first_follow_conflicts(self, report: TopDownValidationReport) -> None:
        grouped = self._group_by_lhs()

        for lhs, productions in grouped.items():
            follow_lhs = self.follow_sets.get(lhs, set())
            production_firsts = [first_of_sequence(prod.rhs, self.first_sets) for prod in productions]

            nullable_indices = [idx for idx, first_set in enumerate(production_firsts) if EPSILON in first_set]

            if len(nullable_indices) > 1:
                report.has_first_follow_conflict = True
                report.issues.append(
                    ValidationIssue(
                        code="FIRST_FOLLOW_CONFLICT",
                        message="FIRST/FOLLOW conflict detected",
                        details=f"{lhs} has multiple ε-producing alternatives, all map to FOLLOW({lhs})={sorted(follow_lhs)}",
                    )
                )

            for nullable_idx in nullable_indices:
                nullable_prod = productions[nullable_idx]
                for idx, first_set in enumerate(production_firsts):
                    if idx == nullable_idx:
                        continue
                    overlap = (first_set - {EPSILON}) & follow_lhs
                    if overlap:
                        report.has_first_follow_conflict = True
                        report.issues.append(
                            ValidationIssue(
                                code="FIRST_FOLLOW_CONFLICT",
                                message="FIRST/FOLLOW conflict detected",
                                details=(
                                    f"{nullable_prod} conflicts with {productions[idx]} for {lhs} on "
                                    f"{sorted(overlap)}"
                                ),
                            )
                        )

    def _detect_left_factoring(self, report: TopDownValidationReport) -> None:
        grouped = self._group_by_lhs()

        for lhs, productions in grouped.items():
            seen_prefixes: Set[Tuple[str, ...]] = set()
            for i in range(len(productions)):
                for j in range(i + 1, len(productions)):
                    prefix = self._longest_common_prefix(productions[i].rhs, productions[j].rhs)
                    if prefix:
                        if prefix in seen_prefixes:
                            continue
                        seen_prefixes.add(prefix)
                        report.needs_left_factoring = True
                        report.issues.append(
                            ValidationIssue(
                                code="LEFT_FACTORING_REQUIRED",
                                message="Grammar requires left factoring",
                                details=(
                                    f"{lhs} has common prefix '{' '.join(prefix)}' in "
                                    f"{productions[i]} and {productions[j]}"
                                ),
                            )
                        )

    def _longest_common_prefix(self, rhs1: Tuple[str, ...], rhs2: Tuple[str, ...]) -> Tuple[str, ...]:
        common: List[str] = []
        for symbol1, symbol2 in zip(rhs1, rhs2):
            if symbol1 != symbol2:
                break
            common.append(symbol1)
        return tuple(common)

    def _detect_ll1_conflicts(self, report: TopDownValidationReport) -> None:
        ll1_parser = LL1Parser(self.grammar)
        report.is_ll1 = ll1_parser.is_ll1

        if not ll1_parser.is_ll1:
            for conflict in ll1_parser.conflicts:
                report.ll1_conflicts.append(
                    {
                        "nonterminal": conflict.nonterminal,
                        "terminal": conflict.terminal,
                        "production1": str(conflict.production1),
                        "production2": str(conflict.production2),
                        "type": conflict.conflict_type,
                    }
                )

            report.issues.append(
                ValidationIssue(
                    code="LL1_CONFLICT",
                    message="Grammar is not LL(1)",
                    details=f"Parsing table has {len(ll1_parser.conflicts)} conflicting entries",
                )
            )
