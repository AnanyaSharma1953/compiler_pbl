# Unified Parsing Framework - Architecture & API Documentation

## Overview

This is a complete refactoring of the LR Parser project into a **unified parsing framework** that supports both **top-down (LL)** and **bottom-up (LR)** parsing strategies with comprehensive conflict detection and grammar analysis.

## Architecture

### Core Modules

```
parser/
├── grammar.py                    # Grammar representation (unchanged)
├── first_follow.py              # FIRST/FOLLOW computation (unchanged)
├── lr_items.py                  # LR item generation (unchanged)
├── dfa_builder.py               # DFA construction (unchanged)
├── parsing_table.py             # LR table builder (unchanged)
├── shift_reduce.py              # LR parsing simulation (unchanged)
├── transformations.py           # [NEW] Grammar transformations
├── ll1_parser.py                # [NEW] LL(1) parser implementation
├── lr_parser.py                 # [NEW] Unified LR parser classes
├── conflict_detector.py         # [NEW] Unified conflict detection
├── report_generator.py          # [NEW] Structured report generation
└── parser_comparator.py         # [NEW] Grammar comparison across all parsers
```

---

## Module Details

### 1. `transformations.py` - Grammar Transformations

**Purpose:** Transform grammars for top-down parsing by eliminating left recursion and left factoring.

**Key Classes:**
- `GrammarTransformer` - Main transformation engine
- `TransformationResult` - Result dataclass

**Key Methods:**
```python
transformer = GrammarTransformer(grammar)
result = transformer.transform_for_ll1()

# Result contains:
# - transformed_grammar: Grammar after all transformations
# - transformations_applied: List of transformation descriptions
# - left_recursion_removed: Boolean
# - left_factored: Boolean
# - new_nonterminals: Set of newly created symbols
```

**Algorithms Implemented:**
1. **Direct Left Recursion Elimination**
   - Transform: `A → A α | β` → `A → β A' | A' → α A' | ε`
   
2. **Indirect Left Recursion Elimination**
   - Aho/Ullman algorithm for indirect recursion
   
3. **Left Factoring**
   - Transform: `A → α β₁ | α β₂` → `A → α A' | A' → β₁ | β₂`

---

### 2. `ll1_parser.py` - LL(1) Predictive Parser

**Purpose:** Implement top-down predictive parsing with conflict detection.

**Key Classes:**
- `LL1Parser` - Main LL(1) parser
- `LL1Conflict` - Conflict representation
- `LL1ParseStep` - Parsing trace step

**Key Methods:**
```python
ll1_parser = LL1Parser(transformed_grammar)

# Check if grammar is LL(1)
if ll1_parser.is_ll1:
    # Parse input
    steps, accepted = ll1_parser.parse("id + id")
    
    # Get summary
    summary = ll1_parser.get_table_summary()
```

**Parsing Table Construction:**
- Uses FIRST+ sets: `FIRST+(A → α) = FIRST(α) ∪ (FOLLOW(A) if ε ∈ FIRST(α))`
- Detects multiple productions for same (nonterminal, terminal) pair
- Returns clear conflict information

---

### 3. `lr_parser.py` - Unified LR Parsers

**Purpose:** Class-based architecture for SLR, CLR, and LALR parsers.

**Key Classes:**
- `LRParser` - Abstract base class
- `SLRParser` - Simple LR(1)
- `CLRParser` - Canonical LR(1)
- `LALRParser` - Look-Ahead LR(1)

**Factory Function:**
```python
from parser.lr_parser import create_parser

parser = create_parser(grammar, "SLR")   # or "CLR", "LALR"
summary = parser.get_summary()
result = parser.parse("id + id")
```

**Parser Comparison:**
```
SLR:    Uses LR(0) items + FOLLOW sets for reduces
        Smallest state count, most conflicts
        
LALR:   Merges LR(1) cores with same LR(0) items
        Medium state count, balanced conflicts
        Standard choice (YACC, Bison)
        
CLR:    Full LR(1) with individual lookahead
        Most states, fewest conflicts
        Most powerful but expensive
```

---

### 4. `conflict_detector.py` - Unified Conflict Detection

**Purpose:** Detect and report conflicts for both LL(1) and LR parsers.

**Key Classes:**
- `ConflictDetector` - Static methods for conflict analysis
- `ConflictReport` - Structured conflict report

**Key Methods:**
```python
from parser.conflict_detector import ConflictDetector

# For LL(1)
ll1_report = ConflictDetector.analyze_ll1_conflicts(ll1_parser)

# For LR
lr_report = ConflictDetector.analyze_lr_conflicts(slr_parser)

# Generate comparison
summary = ConflictDetector.generate_conflict_summary([ll1_report, lr_report])
```

**Conflict Types Detected:**
- **LL(1)**: Multiple productions for same (nonterminal, terminal)
- **Shift-Reduce**: Parser can shift or reduce
- **Reduce-Reduce**: Parser can use multiple reductions
- **Ambiguity**: Reduce-reduce in CLR indicates potential ambiguity

---

### 5. `report_generator.py` - Structured Report Generation

**Purpose:** Generate formatted, structured reports for all parser types.

**Key Class:**
- `ReportGenerator` - Static report generation methods

**Key Methods:**
```python
from parser.report_generator import ReportGenerator

# Individual reports
grammar_report = ReportGenerator.grammar_summary(grammar)
first_follow_report = ReportGenerator.first_follow_report(first_sets, follow_sets)
ll1_report = ReportGenerator.ll1_report(ll1_parser)
lr_report = ReportGenerator.lr_report(slr_parser)

# Comprehensive comparison
comparison = ReportGenerator.comparison_report(
    grammar, ll1_result, slr_result, clr_result, lalr_result
)
```

**Report Structure:**
- Grammar statistics
- FIRST/FOLLOW sets
- Parsing table information
- Conflict details
- Parser recommendations

---

### 6. `parser_comparator.py` - Grammar Comparison

**Purpose:** Evaluate grammar across all parser types and provide recommendations.

**Key Class:**
- `ParserComparator` - Main comparison engine

**Key Methods:**
```python
from parser.parser_comparator import ParserComparator

comparator = ParserComparator(grammar)
results = comparator.compare_all(transform_for_ll1=True)

# Results structure:
# {
#     "transformations": {...},
#     "LL(1)": {...},
#     "SLR(1)": {...},
#     "CLR(1)": {...},
#     "LALR(1)": {...},
#     "comparison": {
#         "conflict_free_parsers": [...],
#         "best_parser": "LALR(1)",
#         "recommendation": "..."
#     }
# }
```

---

## Usage Examples

### Example 1: Full Parsing Pipeline

```python
from parser.grammar import Grammar
from parser.parser_comparator import ParserComparator
from parser.report_generator import ReportGenerator

# Parse grammar
grammar_text = """
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
"""
grammar = Grammar.from_text(grammar_text)

# Compare all parsers
comparator = ParserComparator(grammar)
results = comparator.compare_all(transform_for_ll1=True)

# Get best parser
best_parser_type = results["comparison"]["best_parser"]
print(f"Best parser: {best_parser_type}")
print(f"Recommendation: {results['comparison']['recommendation']}")

# Parse input
best_parser = comparator.get_parser(best_parser_type)
parse_result = best_parser.parse("id + id * id")
print(f"Accepted: {parse_result.accepted}")
```

### Example 2: LL(1) Parser with Transformations

```python
from parser.transformations import GrammarTransformer
from parser.ll1_parser import LL1Parser

# Transform grammar
transformer = GrammarTransformer(grammar)
transform_result = transformer.transform_for_ll1()

if transform_result.left_recursion_removed:
    print("Left recursion eliminated")
    print(f"New nonterminals: {transform_result.new_nonterminals}")

# Build LL(1) parser
ll1 = LL1Parser(transform_result.transformed_grammar)

if ll1.is_ll1:
    steps, accepted = ll1.parse("id + id")
    print(f"Parse steps: {len(steps)}")
else:
    print(f"Grammar has {len(ll1.conflicts)} conflicts")
    for conflict in ll1.conflicts:
        print(f"  {conflict.nonterminal}, {conflict.terminal}")
```

### Example 3: Detailed Conflict Analysis

```python
from parser.lr_parser import SLRParser
from parser.conflict_detector import ConflictDetector

slr = SLRParser(grammar)
report = ConflictDetector.analyze_lr_conflicts(slr)

print(f"Parser: {report.parser_type}")
print(f"Conflicts: {report.conflict_count}")
for conflict in report.conflicts:
    print(f"  {conflict}")
```

---

## Data Flow Diagram

```
Grammar Input
    ↓
Grammar.from_text()
    ↓
ParserComparator.compare_all()
    ├─→ GrammarTransformer.transform_for_ll1()
    │   ├─→ eliminate_indirect_left_recursion()
    │   └─→ apply_left_factoring()
    │
    ├─→ LL1Parser(transformed_grammar)
    │   └─→ ConflictDetector.analyze_ll1_conflicts()
    │
    ├─→ SLRParser(original_grammar)
    │   └─→ ConflictDetector.analyze_lr_conflicts()
    │
    ├─→ CLRParser(original_grammar)
    │   └─→ ConflictDetector.analyze_lr_conflicts()
    │
    └─→ LALRParser(original_grammar)
        └─→ ConflictDetector.analyze_lr_conflicts()
    
ReportGenerator generates structured output
```

---

## Key Design Decisions

1. **No Global State**: All functionality in classes or static methods
2. **Structured Data**: All results returned as dictionaries, not printed
3. **Separation of Concerns**: Logic separate from UI/reporting
4. **Clear Conflict Information**: Conflicts include location, type, productions involved
5. **Flexible Transformations**: Optional application for LL(1) only
6. **Recommendation Engine**: Automatic suggestion of best parser type

---

## Integration with UI

The framework is designed to be UI-agnostic. The new `app.py` should:

1. **Accept user input**: Grammar text and parsing mode (LL1/SLR/CLR/LALR)
2. **Use comparator**: `ParserComparator.compare_all()`
3. **Display results**: Use `report_generator` output for UI
4. **Parse input**: Use selected parser's `parse()` method
5. **Show conflicts**: Display from `conflict_detector` output

---

## Testing

All new modules are tested and working:
- ✅ Grammar transformation (left recursion, left factoring)
- ✅ LL(1) parser construction
- ✅ LR parser classes (SLR, CLR, LALR)
- ✅ Conflict detection
- ✅ Report generation
- ✅ Grammar comparison

Example test:
```python
grammar = Grammar.from_text("""
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
""")

comparator = ParserComparator(grammar)
results = comparator.compare_all()

# All results generated successfully
assert "LL(1)" in results
assert "SLR(1)" in results
assert "comparison" in results
```

---

## Next Steps

1. **Update app.py** to support both LL(1) and LR modes
2. **Add UI sections** for:
   - Grammar transformations display
   - LL(1) vs LR selection
   - Conflict visualization
   - Recommendation display
3. **Visualization updates** for LL(1) parsing table
4. **Step-by-step** trace for both LL(1) and LR parsing

