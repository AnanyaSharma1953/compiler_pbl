"""Test script for unified parsing framework"""

print('Testing new modules...')
from parser.transformations import GrammarTransformer
from parser.ll1_parser import LL1Parser
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
print('\n🎉 ALL TESTS PASSED!')
