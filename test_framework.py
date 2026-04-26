"""Test script for unified parsing framework"""

print('Testing new modules...')
from parser.transformations import GrammarTransformer
from parser.ll1_parser import LL1Parser
from parser.recursive_descent import RecursiveDescentParser
from parser.top_down_validator import TopDownGrammarValidator
from parser.lr_parser import SLRParser, CLRParser, LALRParser
from parser.conflict_detector import ConflictDetector
from parser.report_generator import ReportGenerator
from parser.parser_comparator import ParserComparator
print('✅ All new modules imported successfully!\n')

# Quick functional test
from parser.grammar import Grammar

print('Testing with simple grammar...')
grammar_text = '''E -> E + T | T
T -> T * F | F
F -> ( E ) | id'''

grammar = Grammar.from_text(grammar_text)
print(f'✅ Grammar parsed: {len(grammar.productions)} productions')

# Test LR parsers
slr = SLRParser(grammar)
print(f'✅ SLR parser built: {slr.get_parser_type()}, conflict_free={slr.is_conflict_free}')

# Test comparator
comparator = ParserComparator(grammar)
results = comparator.compare_all(transform_for_ll1=True)
print(f'✅ Comparison complete: tested {len([k for k in results if k != "comparison" and k != "transformations"])} parsers')
print(f'   Working parsers: {results["comparison"]["conflict_free_parsers"]}')

# Test recursive descent on transformed grammar
transformer = GrammarTransformer(grammar)
transformed = transformer.transform_for_ll1()
rd = RecursiveDescentParser(transformed.transformed_grammar)
_, rd_ok_valid, _ = rd.parse('id + id * id')
_, rd_ok_invalid, _ = rd.parse('id + + id')
assert rd_ok_valid is True and rd_ok_invalid is False
print('✅ Recursive Descent parser validated on transformed grammar')

# Verify LL(1) conflict reporting on a common-prefix grammar
prefix_grammar = Grammar.from_text('''S -> a A | a B
A -> b
B -> c''')
prefix_ll1 = LL1Parser(prefix_grammar)
assert prefix_ll1.is_ll1 is False
assert len(prefix_ll1.conflicts) > 0
prefix_transformed = GrammarTransformer(prefix_grammar).transform_for_ll1()
assert LL1Parser(prefix_transformed.transformed_grammar).is_ll1 is True
print('✅ LL(1) conflict detection validated on common-prefix grammar')

# Validate top-down diagnostics report
prefix_report = TopDownGrammarValidator(prefix_grammar).validate()
assert prefix_report.is_ll1 is False
assert prefix_report.has_first_first_conflict is True
assert prefix_report.needs_left_factoring is True
assert prefix_report.has_left_recursion is False
print('✅ Top-Down grammar validation diagnostics verified')

# Validate recursive descent mode control
rd_backtracking = RecursiveDescentParser(prefix_grammar, mode='backtracking')
_, rd_backtrack_ok1, _ = rd_backtracking.parse('a b')
_, rd_backtrack_ok2, _ = rd_backtracking.parse('a c')
_, rd_backtrack_bad, _ = rd_backtracking.parse('a d')
assert rd_backtrack_ok1 is True and rd_backtrack_ok2 is True and rd_backtrack_bad is False

ll1_grammar = Grammar.from_text('''S -> a A
A -> b''')
rd_predictive = RecursiveDescentParser(ll1_grammar, mode='predictive')
_, rd_predict_ok, _ = rd_predictive.parse('a b')
_, rd_predict_bad, _ = rd_predictive.parse('a c')
assert rd_predict_ok is True and rd_predict_bad is False
print('✅ Recursive Descent predictive/backtracking modes verified')

print('\n🎉 ALL TESTS PASSED!')
