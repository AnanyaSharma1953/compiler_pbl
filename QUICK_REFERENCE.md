# Unified Parsing Framework - Quick Reference Guide

## 🎯 One-Minute Overview

Your project now supports:

- **LL(1)**: Top-down predictive parsing with automatic left recursion elimination
- **SLR(1)**: Simple bottom-up parsing
- **CLR(1)**: Canonical LR parsing (most powerful)
- **LALR(1)**: Balanced LR parsing (most practical)

All with automatic conflict detection, comparison, and intelligent recommendations.

---

## 📦 What's Included

### 6 New Production Modules

```
transformations.py      - Grammar transformation (left recursion, left factoring)
ll1_parser.py          - LL(1) predictive parser
lr_parser.py           - Unified LR parsers (SLR, CLR, LALR classes)
conflict_detector.py   - Unified conflict detection
report_generator.py    - Structured report generation
parser_comparator.py   - Grammar comparison & recommendation
```

### All Preserved

```
grammar.py             - Grammar representation ✓ Unchanged
first_follow.py        - FIRST/FOLLOW computation ✓ Unchanged
lr_items.py            - LR item generation ✓ Unchanged
dfa_builder.py         - DFA construction ✓ Unchanged
parsing_table.py       - Parsing table builder ✓ Unchanged
shift_reduce.py        - LR parsing simulation ✓ Unchanged
```

---

## ⚡ Quick Start

### Most Common: Compare All Parsers

```python
from parser.parser_comparator import ParserComparator
from parser.grammar import Grammar

# 1. Parse grammar
grammar = Grammar.from_text("""
E -> E + T | T
T -> id
""")

# 2. Compare all parsers
comparator = ParserComparator(grammar)
results = comparator.compare_all()

# 3. See recommendations
print(results["comparison"]["best_parser"])
print(results["comparison"]["recommendation"])

# 4. Get working parsers
print(results["comparison"]["conflict_free_parsers"])

# 5. Parse input with best parser
best_parser_type = results["comparison"]["best_parser"]
best_parser = comparator.get_parser(best_parser_type)
parse_result = best_parser.parse("id + id")
print(f"Accepted: {parse_result.accepted}")
```

---

## 🔨 Core Classes & Methods

### ParserComparator (Main Entry Point)

```python
from parser.parser_comparator import ParserComparator

comparator = ParserComparator(grammar)
results = comparator.compare_all(transform_for_ll1=True)

# Access specific parsers
ll1_parser = comparator.get_parser("LL(1)")
slr_parser = comparator.get_parser("SLR(1)")
clr_parser = comparator.get_parser("CLR(1)")
lalr_parser = comparator.get_parser("LALR(1)")
```

### Individual Parsers

```python
from parser.lr_parser import SLRParser, CLRParser, LALRParser, create_parser
from parser.ll1_parser import LL1Parser
from parser.transformations import GrammarTransformer

# LR Parsers
slr = SLRParser(grammar)
clr = CLRParser(grammar)
lalr = LALRParser(grammar)

# Or factory function
parser = create_parser(grammar, "LALR")

# LL(1) with transformation
transformer = GrammarTransformer(grammar)
result = transformer.transform_for_ll1()
ll1 = LL1Parser(result.transformed_grammar)
```

### Parser Common Interface

```python
# All parsers have same interface
parser.get_parser_type()      # "SLR(1)", "LL(1)", etc.
parser.get_summary()          # Dict with stats
parser.parse(input_string)    # Parse result
parser.is_conflict_free       # Boolean
parser.conflicts              # List of conflicts
```

### Conflict Detection

```python
from parser.conflict_detector import ConflictDetector

# For LL(1)
ll1_report = ConflictDetector.analyze_ll1_conflicts(ll1_parser)

# For LR
lr_report = ConflictDetector.analyze_lr_conflicts(slr_parser)

# Summary
summary = ConflictDetector.generate_conflict_summary([ll1_report, lr_report])
```

### Report Generation

```python
from parser.report_generator import ReportGenerator

# Various reports
grammar_summary = ReportGenerator.grammar_summary(grammar)
first_follow = ReportGenerator.first_follow_report(first_sets, follow_sets)
ll1_report = ReportGenerator.ll1_report(ll1_parser)
lr_report = ReportGenerator.lr_report(slr_parser)

# Comprehensive comparison
comparison = ReportGenerator.comparison_report(
    grammar, ll1_result, slr_result, clr_result, lalr_result
)
```

### Grammar Transformations

```python
from parser.transformations import GrammarTransformer

transformer = GrammarTransformer(grammar)
result = transformer.transform_for_ll1()

# Result contains:
result.transformed_grammar       # Transformed grammar
result.transformations_applied   # List of applied transformations
result.left_recursion_removed    # Boolean
result.left_factored             # Boolean
result.new_nonterminals          # Set of new symbols created
```

---

## 🎯 Common Scenarios

### Scenario 1: Auto-select Best Parser

```python
comparator = ParserComparator(grammar)
results = comparator.compare_all()
best_parser = comparator.get_parser(results["comparison"]["best_parser"])
parse_result = best_parser.parse(input_string)
```

### Scenario 2: Try LL(1)

```python
transformer = GrammarTransformer(grammar)
result = transformer.transform_for_ll1()
ll1 = LL1Parser(result.transformed_grammar)

if ll1.is_ll1:
    steps, accepted = ll1.parse(input_string)
else:
    print(f"Grammar is not LL(1). Conflicts: {len(ll1.conflicts)}")
```

### Scenario 3: Compare Specific Parsers

```python
slr = SLRParser(grammar)
clr = CLRParser(grammar)
lalr = LALRParser(grammar)

print(f"SLR states: {len(slr.states)}")
print(f"CLR states: {len(clr.states)}")
print(f"LALR states: {len(lalr.states)}")
print(f"SLR conflicts: {len(slr.conflicts)}")
```

### Scenario 4: Detailed Conflict Report

```python
slr = SLRParser(grammar)
report = ConflictDetector.analyze_lr_conflicts(slr)

print(f"Parser: {report.parser_type}")
print(f"Conflicts: {report.conflict_count}")
for conflict in report.conflicts:
    print(ConflictDetector.format_conflict_for_display(conflict))
```

---

## 📊 Results Structure

### Comparator Results

```python
results = {
    "transformations": {                    # If LL(1) chosen
        "left_recursion_removed": bool,
        "left_factored": bool,
        # ... transformation details
    },
    "LL(1)": {
        "is_ll1": bool,
        "conflict_count": int,
        "summary": {...}
    },
    "SLR(1)": {
        "is_conflict_free": bool,
        "summary": {"states": int, "transitions": int, ...}
    },
    "CLR(1)": {...},
    "LALR(1)": {...},
    "comparison": {
        "conflict_free_parsers": ["SLR(1)", "LALR(1)"],
        "best_parser": "LALR(1)",
        "recommendation": "Use LALR(1) parser..."
    }
}
```

### Parser Summary

```python
parser.get_summary()
# Returns:
{
    "parser_type": "SLR(1)",
    "is_conflict_free": true,
    "states": 12,
    "transitions": 25,
    "conflicts": 0,
    "conflict_details": [],
    "terminals": 4,
    "nonterminals": 3,
    "action_entries": 48,
    "goto_entries": 9,
    "total_table_entries": 57
}
```

---

## 🎓 Parsing Algorithms at a Glance

### LL(1) - Top-Down Predictive

- **Strategy**: Start from root, expand using parsing table
- **Table Entry**: Production to use for (nonterminal, terminal)
- **Conflicts**: Multiple productions for same (NT, T)
- **Grammar Requirement**: No left recursion, unique first symbols
- **Transformations**: Eliminate left recursion and left factor

### SLR - Simple LR

- **Strategy**: Shift-reduce with FOLLOW sets
- **Table**: LR(0) items + FOLLOW sets for reduce decisions
- **States**: Fewest among LR parsers
- **Conflicts**: Most likely among LR parsers
- **Use**: When simple parsing needed

### CLR - Canonical LR

- **Strategy**: Shift-reduce with per-state lookahead
- **Table**: Full LR(1) items with individual lookaheads
- **States**: Most among LR parsers
- **Conflicts**: Fewest conflicts, most powerful
- **Use**: When maximum parsing power needed

### LALR - Look-Ahead LR

- **Strategy**: Merge CLR states with same core
- **Table**: Between SLR and CLR in power
- **States**: Between SLR and CLR
- **Conflicts**: Balanced
- **Use**: Standard choice (YACC, Bison)

---

## ⚠️ Common Issues & Solutions

### "Grammar is not LL(1)"

**Cause**: Multiple productions for same (nonterminal, terminal)
**Solution**: Use LR parser (SLR, CLR, or LALR) instead

### "SLR has conflicts but CLR doesn't"

**Cause**: SLR uses only FOLLOW sets; CLR has more precise lookahead
**Solution**: Use CLR or LALR

### "Left recursion detected in LL(1)"

**Expected**: Transformations automatically handle it
**Check**: `transformation_result.left_recursion_removed`

---

## 📈 Performance Notes

- **LL(1)**: Fastest parsing, limited grammar class
- **SLR**: Fast, fewer states, possible conflicts
- **LALR**: Good balance, standard choice
- **CLR**: Most powerful, most states, slowest table construction

---

## 🚀 Next: Integrating with UI

All new modules are **UI-agnostic** - they return structured data only.

For app.py:

1. Use `ParserComparator` for comparison
2. Get results as dictionaries
3. Display using any UI framework
4. Pass user selections to parsers
5. Show parse results using same interface

Example UI integration:

```python
# In app.py
from parser.parser_comparator import ParserComparator

# User enters grammar
grammar_text = st.text_area("Enter grammar:")
grammar = Grammar.from_text(grammar_text)

# Compare all parsers
comparator = ParserComparator(grammar)
results = comparator.compare_all()

# Show comparison results
st.write(results["comparison"]["recommendation"])

# Let user choose or auto-select
parser = comparator.get_parser(results["comparison"]["best_parser"])

# Parse input
input_str = st.text_input("Enter input:")
result = parser.parse(input_str)
st.write(f"Accepted: {result.accepted}")
```

---

## 📚 Files Reference

- `UNIFIED_FRAMEWORK_DOCUMENTATION.md` - Complete detailed documentation
- `FRAMEWORK_IMPLEMENTATION_SUMMARY.md` - Implementation overview
- `test_framework.py` - Working example/test
- `parser/transformations.py` - Grammar transformations
- `parser/ll1_parser.py` - LL(1) implementation
- `parser/lr_parser.py` - LR parsers (SLR, CLR, LALR)
- `parser/conflict_detector.py` - Conflict detection
- `parser/report_generator.py` - Report generation
- `parser/parser_comparator.py` - Grammar comparison

---

**✅ Framework ready to use!**
