"""
Recursive Descent Parser

Supports two modes:
1. predictive: deterministic (no backtracking), for LL(1) grammars
2. backtracking: tries alternatives with controlled pointer restore
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from parser.first_follow import compute_first_sets, compute_follow_sets, first_of_sequence
from parser.grammar import EPSILON, Grammar, Production
from visualizer.parse_tree import Node


@dataclass
class RecursiveDescentStep:
    """Represents one trace step during recursive descent parsing."""
    stack: str
    input_remaining: str
    action: str


@dataclass
class RecursiveDescentError:
    """Structured recursive descent parse error."""
    message: str
    position: int
    token: Optional[str] = None
    nonterminal: Optional[str] = None
    expected: Optional[str] = None


class RecursiveDescentParser:
    """Recursive descent parser with predictive and backtracking modes."""

    def __init__(self, grammar: Grammar, mode: str = "backtracking"):
        self.grammar = grammar
        self.mode = mode
        self.last_error: Optional[RecursiveDescentError] = None

        self.first_sets: Dict[str, Set[str]] = compute_first_sets(grammar)
        self.follow_sets: Dict[str, Set[str]] = compute_follow_sets(grammar)

        if mode not in {"predictive", "backtracking"}:
            raise ValueError("mode must be 'predictive' or 'backtracking'")

    def parse(self, input_string: str) -> Tuple[List[RecursiveDescentStep], bool, Optional[Node]]:
        """
        Parse input string and return (steps, accepted, parse_tree_root).

        Input must be space-separated tokens.
        """
        self.last_error = None
        tokens = input_string.split() if input_string.strip() else []
        steps: List[RecursiveDescentStep] = []

        if self.mode == "predictive":
            node, next_pos = self._parse_nonterminal_predictive(
                self.grammar.start_symbol,
                tokens,
                0,
                [],
                set(),
                steps,
            )
        else:
            node, next_pos = self._parse_nonterminal_backtracking(
                self.grammar.start_symbol,
                tokens,
                0,
                [],
                set(),
                steps,
            )

        accepted = node is not None and next_pos == len(tokens)
        if not accepted and self.last_error is None:
            token = tokens[next_pos] if next_pos < len(tokens) else "$"
            self.last_error = RecursiveDescentError(
                message=f"Unexpected token at position {next_pos}",
                position=next_pos,
                token=token,
            )
            steps.append(
                RecursiveDescentStep(
                    stack=self.grammar.start_symbol,
                    input_remaining=" ".join(tokens[next_pos:]) if next_pos < len(tokens) else "",
                    action=f"Error: Unexpected token at position {next_pos} ('{token}')",
                )
            )

        return steps, accepted, node if accepted else None

    def _record_error(
        self,
        message: str,
        position: int,
        token: Optional[str] = None,
        nonterminal: Optional[str] = None,
        expected: Optional[str] = None,
    ) -> None:
        self.last_error = RecursiveDescentError(
            message=message,
            position=position,
            token=token,
            nonterminal=nonterminal,
            expected=expected,
        )

    def _parse_nonterminal_predictive(
        self,
        nonterminal: str,
        tokens: List[str],
        pos: int,
        call_stack: List[str],
        active_calls: Set[Tuple[str, int]],
        steps: List[RecursiveDescentStep],
    ) -> Tuple[Optional[Node], int]:
        state = (nonterminal, pos)
        stack_view = " > ".join(call_stack + [nonterminal])
        input_remaining = " ".join(tokens[pos:]) if pos < len(tokens) else ""

        if state in active_calls:
            token = tokens[pos] if pos < len(tokens) else "$"
            self._record_error(
                message="Left recursion detected",
                position=pos,
                token=token,
                nonterminal=nonterminal,
            )
            steps.append(
                RecursiveDescentStep(
                    stack=stack_view,
                    input_remaining=input_remaining,
                    action=f"Error: Left recursion detected at {nonterminal}",
                )
            )
            return None, pos

        active_calls.add(state)

        lookahead = tokens[pos] if pos < len(tokens) else "$"
        production = self._select_predictive_production(nonterminal, lookahead)
        if production is None:
            self._record_error(
                message=f"No matching production found for {nonterminal}",
                position=pos,
                token=lookahead,
                nonterminal=nonterminal,
            )
            steps.append(
                RecursiveDescentStep(
                    stack=stack_view,
                    input_remaining=input_remaining,
                    action=f"Error: No matching production found for {nonterminal} with lookahead '{lookahead}'",
                )
            )
            active_calls.remove(state)
            return None, pos

        steps.append(
            RecursiveDescentStep(
                stack=stack_view,
                input_remaining=input_remaining,
                action=f"Predict {production.lhs} -> {' '.join(production.rhs) if production.rhs else 'ε'}",
            )
        )

        children: List[Node] = []
        current_pos = pos

        for symbol in production.rhs:
            if symbol in self.grammar.nonterminals:
                child_node, new_pos = self._parse_nonterminal_predictive(
                    symbol,
                    tokens,
                    current_pos,
                    call_stack + [nonterminal],
                    active_calls,
                    steps,
                )
                if child_node is None:
                    active_calls.remove(state)
                    return None, pos
                children.append(child_node)
                current_pos = new_pos
            else:
                current_token = tokens[current_pos] if current_pos < len(tokens) else "$"
                if current_pos < len(tokens) and current_token == symbol:
                    steps.append(
                        RecursiveDescentStep(
                            stack=stack_view,
                            input_remaining=" ".join(tokens[current_pos:]),
                            action=f"Match terminal '{symbol}'",
                        )
                    )
                    children.append(Node(symbol))
                    current_pos += 1
                else:
                    self._record_error(
                        message=f"Unexpected token at position {current_pos}",
                        position=current_pos,
                        token=current_token,
                        nonterminal=nonterminal,
                        expected=symbol,
                    )
                    steps.append(
                        RecursiveDescentStep(
                            stack=stack_view,
                            input_remaining=" ".join(tokens[current_pos:]) if current_pos < len(tokens) else "",
                            action=(
                                f"Error: Unexpected token at position {current_pos} "
                                f"(expected '{symbol}', got '{current_token}')"
                            ),
                        )
                    )
                    active_calls.remove(state)
                    return None, pos

        if len(production.rhs) == 0:
            children.append(Node("ε"))

        node = Node(nonterminal, children)
        steps.append(
            RecursiveDescentStep(
                stack=stack_view,
                input_remaining=" ".join(tokens[current_pos:]) if current_pos < len(tokens) else "",
                action=f"Apply {production.lhs} -> {' '.join(production.rhs) if production.rhs else 'ε'}",
            )
        )

        active_calls.remove(state)
        return node, current_pos

    def _parse_nonterminal_backtracking(
        self,
        nonterminal: str,
        tokens: List[str],
        pos: int,
        call_stack: List[str],
        active_calls: Set[Tuple[str, int]],
        steps: List[RecursiveDescentStep],
    ) -> Tuple[Optional[Node], int]:
        state = (nonterminal, pos)
        stack_view = " > ".join(call_stack + [nonterminal])
        input_remaining = " ".join(tokens[pos:]) if pos < len(tokens) else ""

        if state in active_calls:
            token = tokens[pos] if pos < len(tokens) else "$"
            self._record_error(
                message="Left recursion detected",
                position=pos,
                token=token,
                nonterminal=nonterminal,
            )
            steps.append(
                RecursiveDescentStep(
                    stack=stack_view,
                    input_remaining=input_remaining,
                    action=f"Error: Left recursion detected at {nonterminal}",
                )
            )
            return None, pos

        active_calls.add(state)

        for prod_idx in self.grammar.prod_by_lhs.get(nonterminal, []):
            prod = self.grammar.productions[prod_idx]
            saved_pos = pos
            steps.append(
                RecursiveDescentStep(
                    stack=stack_view,
                    input_remaining=input_remaining,
                    action=f"Try {prod.lhs} -> {' '.join(prod.rhs) if prod.rhs else 'ε'}",
                )
            )

            children: List[Node] = []
            current_pos = saved_pos
            failed = False

            for symbol in prod.rhs:
                if symbol in self.grammar.nonterminals:
                    child_node, new_pos = self._parse_nonterminal_backtracking(
                        symbol,
                        tokens,
                        current_pos,
                        call_stack + [nonterminal],
                        active_calls,
                        steps,
                    )
                    if child_node is None:
                        failed = True
                        break
                    children.append(child_node)
                    current_pos = new_pos
                else:
                    current_token = tokens[current_pos] if current_pos < len(tokens) else "<EOF>"
                    if current_pos < len(tokens) and current_token == symbol:
                        steps.append(
                            RecursiveDescentStep(
                                stack=stack_view,
                                input_remaining=" ".join(tokens[current_pos:]),
                                action=f"Match terminal '{symbol}'",
                            )
                        )
                        children.append(Node(symbol))
                        current_pos += 1
                    else:
                        failed = True
                        self._record_error(
                            message=f"Unexpected token at position {current_pos}",
                            position=current_pos,
                            token=current_token,
                            nonterminal=nonterminal,
                            expected=symbol,
                        )
                        steps.append(
                            RecursiveDescentStep(
                                stack=stack_view,
                                input_remaining=" ".join(tokens[current_pos:]) if current_pos < len(tokens) else "",
                                action=(
                                    f"Error: Unexpected token at position {current_pos} "
                                    f"(expected '{symbol}', got '{current_token}')"
                                ),
                            )
                        )
                        break

            if not failed:
                if len(prod.rhs) == 0:
                    children.append(Node("ε"))

                node = Node(nonterminal, children)
                steps.append(
                    RecursiveDescentStep(
                        stack=stack_view,
                        input_remaining=" ".join(tokens[current_pos:]) if current_pos < len(tokens) else "",
                        action=f"Apply {prod.lhs} -> {' '.join(prod.rhs) if prod.rhs else 'ε'}",
                    )
                )
                active_calls.remove(state)
                return node, current_pos

            steps.append(
                RecursiveDescentStep(
                    stack=stack_view,
                    input_remaining=input_remaining,
                    action=f"Backtrack from {prod.lhs} production (restore input pointer to {saved_pos})",
                )
            )

        active_calls.remove(state)
        token = tokens[pos] if pos < len(tokens) else "$"
        self._record_error(
            message=f"No matching production found for {nonterminal}",
            position=pos,
            token=token,
            nonterminal=nonterminal,
        )
        return None, pos

    def _select_predictive_production(self, nonterminal: str, lookahead: str) -> Optional[Production]:
        for prod_idx in self.grammar.prod_by_lhs.get(nonterminal, []):
            production = self.grammar.productions[prod_idx]
            first_plus = self._first_plus(production)
            if lookahead in first_plus:
                return production
        return None

    def _first_plus(self, production: Production) -> Set[str]:
        rhs_first = first_of_sequence(production.rhs, self.first_sets)
        result = set(rhs_first - {EPSILON})
        if EPSILON in rhs_first:
            result.update(self.follow_sets.get(production.lhs, set()))
        return result
