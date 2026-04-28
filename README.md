# Unified Parsing Framework & Compiler Design Laboratory

### A comprehensive, educational parsing system with interactive visualization, supporting both top-down and bottom-up parsing algorithms.

---

## 📌 Project Overview

This project is a **comprehensive parsing framework** that teaches and demonstrates how real compilers parse code. It implements a complete suite of parsing algorithms—from simple recursive descent to powerful LALR(1)—all with interactive visualization, conflict detection, and educational insights.

**What it does:**

- Parses context-free grammars in a unified framework
- Supports **6 different parsing strategies** (LL(1), Recursive Descent, SLR(1), CLR(1), LALR(1))
- Automatically transforms grammars to work with specific parsers
- Detects and explains conflicts in grammars
- Visualizes parsing steps and construction with parse trees
- Compares parser capabilities and recommends the best one for your grammar

**What makes it special:**

- ✅ All algorithms implemented from scratch—no external parsing libraries
- ✅ Interactive Streamlit UI with beautiful dark-mode visualization
- ✅ Educational focus: Learn how parsers actually work, step-by-step
- ✅ Unified framework: Compare multiple parsing strategies on the same grammar
- ✅ Production-ready code architecture with clear separation of concerns

---

## 🎯 Learning Objectives

This framework helps you understand:

- **How compilers parse code** at the algorithmic level
- **Top-down parsing**: Recursive descent and LL(1) predictive parsing
- **Bottom-up parsing**: Shift-reduce and LR algorithms (SLR, CLR, LALR)
- **Grammar transformations**: Making grammars parseable by different strategies
- **Conflict resolution**: Understanding ambiguities in grammars
- **Automatic table generation**: From grammar to ACTION/GOTO tables
- **Parser comparison**: How different algorithms trade-off power vs. simplicity

---

## ✨ Core Features

### Parsing Algorithms (6 Total)

**Top-Down Parsers:**

- ✅ **LL(1) Predictive Parser**: Efficient, predictable parsing
- ✅ **Recursive Descent Parser**: Manual backtracking-based parsing

**Bottom-Up Parsers:**

- ✅ **SLR(1)** (Simple LR): Fast, limited power
- ✅ **CLR(1)** (Canonical LR): Most powerful, fewer conflicts
- ✅ **LALR(1)** (Look-Ahead LR): Balanced—power and table size
- ✅ **LR(0)**: Simplest form, used as foundation

### Grammar Analysis & Transformation

- ✅ FIRST and FOLLOW set computation
- ✅ **Automatic left recursion elimination** (direct & indirect)
- ✅ **Automatic left factoring** for LL(1) compatibility
- ✅ Grammar validation for specific parser types
- ✅ Production ordering and optimization

### Parser Construction (All Automatic)

- ✅ LR item set generation (closure & goto functions)
- ✅ Canonical collection of parser states
- ✅ DFA state diagram visualization (Graphviz)
- ✅ ACTION & GOTO parsing table generation
- ✅ Conflict detection and analysis
- ✅ Step-by-step state transitions

### Parsing & Visualization

- ✅ Step-by-step shift-reduce simulation
- ✅ Parse tree visualization
- ✅ Stack and input trace during parsing
- ✅ Visual DFA state diagrams with transitions
- ✅ Detailed parsing tables (Pandas DataFrames)

### Advanced Features

- ✅ **Unified conflict detection**: Identify shift-reduce and reduce-reduce conflicts
- ✅ **Parser comparison**: Test grammar on multiple parsers
- ✅ **Smart recommendations**: Which parser to use for your grammar
- ✅ **Structured reporting**: Export grammar analysis as structured data
- ✅ **Interactive UI**: Browser-based exploration with Streamlit

---

## 🧠 Algorithms Implemented (From Scratch)

### Grammar Foundation

**FIRST & FOLLOW Sets** (`parser/first_follow.py`)

- Computes terminal symbols that can appear first and after non-terminals
- Handles epsilon productions automatically
- Fixed-point iteration with cycle detection

### Grammar Transformations

**Left Recursion Elimination** (`parser/transformations.py`)

- Direct recursion (A → A α | β)
- Indirect recursion (complex dependencies)
- Aho-Ullman algorithm
- Preserves language while enabling predictive parsing

**Left Factoring**

- Removes common prefixes in productions
- Enables LL(1) compatibility
- Automatic transformation with rollback

### Top-Down Parsing

**LL(1) Prediction** (`parser/ll1_parser.py`)

- Builds prediction matrix from FIRST+ sets
- Single-pass table-driven parsing
- Conflict detection (FIRST-FIRST, FIRST-FOLLOW)

**Recursive Descent** (`parser/recursive_descent.py`)

- Mutually recursive functions as parser methods
- Optional backtracking mode for error recovery
- Manual steering of parsing flow

### Bottom-Up Parsing

**LR Item Generation** (`parser/lr_items.py`)

- LR(0) items with dot notation
- LR(1) items with lookahead symbols
- Closure computation: Add items for non-terminals after dots
- GOTO computation: Item set transitions

**DFA State Builder** (`parser/dfa_builder.py`)

- Canonical collection of LR states
- Breadth-first state space exploration
- Transition table generation

**Shift-Reduce Parsing** (`parser/shift_reduce.py`)

- Stack-based parsing simulation
- ACTION/GOTO table lookup
- Conflict handling and error reporting

**Parser Types** (`parser/lr_parser.py`)

- **SLR(1)**: Uses FOLLOW sets for reduce actions
- **CLR(1)**: Uses lookahead in items for reduce actions
- **LALR(1)**: Merges CLR states for compact tables

### Conflict Analysis

**Conflict Detection** (`parser/conflict_detector.py`)

- Shift-Reduce conflicts: When grammar is ambiguous
- Reduce-Reduce conflicts: Multiple possible reductions
- FIRST-FIRST conflicts: Multiple productions for same input
- Grammar ambiguity assessment

---

## 🏗️ Architecture & Tech Stack

| Component           | Technology                            |
| ------------------- | ------------------------------------- |
| **Language**        | Python 3.10+                          |
| **UI Framework**    | Streamlit (interactive web interface) |
| **Visualization**   | Graphviz (DFA, parse trees)           |
| **Data Processing** | Pandas (parsing tables)               |
| **Structure**       | Object-oriented, modular design       |
| **Algorithms**      | All implemented from scratch          |
| **Deployment**      | Web-based + CLI ready                 |

### Architecture Overview

```
┌──────────────────────────────────────────────────┐
│          Streamlit Interactive UI (app.py)       │
└──────────────────┬───────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    ▼              ▼              ▼
┌─────────┐  ┌──────────┐  ┌────────────┐
│ Grammar │  │ Analysis │  │ Parsing    │
│ Layer   │  │ Layer    │  │ Layer      │
└────┬────┘  └────┬─────┘  └─────┬──────┘
     │            │              │
     ▼            ▼              ▼
  grammar.py  first_follow.py  shift_reduce.py
             transformations.py  lr_parser.py
             ll1_parser.py       conflict_detector.py

     ▼            ▼              ▼
  ┌────────────────────────────────────┐
  │    Visualization Layer             │
  │  (dfa_graph.py, parse_tree.py)    │
  └────────────────────────────────────┘
```

---

## 📂 Project Structure

```
compiler_pbl/
│
├── app.py                          # Streamlit UI application
│
├── parser/                         # Core parsing algorithms
│   ├── __init__.py
│   ├── grammar.py                 # Grammar parsing & representation
│   ├── first_follow.py            # FIRST/FOLLOW computation
│   ├── lr_items.py                # LR items (LR(0) & LR(1))
│   ├── dfa_builder.py             # DFA construction
│   ├── parsing_table.py           # SLR/CLR/LALR table generation
│   └── shift_reduce.py            # Shift-reduce parsing simulator
│
├── visualizer/                     # Visualization modules
│   ├── __init__.py
│   ├── dfa_graph.py               # DFA visualization (Graphviz)
│   └── parse_tree.py              # Parse tree visualization
│
├── examples/                       # Sample grammars
│   └── sample_grammar.txt
│
├── .streamlit/                     # Streamlit configuration
│   └── config.toml
│
├── requirements.txt                # Python dependencies
├── README.md                       # This file
└── screenshots/                    # Project screenshots
```

---

## ⚙️ Installation & Quick Start

### Prerequisites

- **Python 3.10+** (or 3.8+)
- **Graphviz** system package (for visualization)
- **pip** (Python package manager)

### Setup (5 minutes)

**1. Clone/Navigate to the project:**

```bash
cd ~/Desktop/compiler_pbl
```

**2. Create and activate virtual environment:**

```bash
# Create venv
python3 -m venv .venv

# Activate (macOS/Linux)
source .venv/bin/activate

# Or on Windows:
# .venv\Scripts\activate
```

**3. Install dependencies:**

```bash
pip install -r requirements.txt
```

**4. Install Graphviz system package** (required for visualizations):

```bash
# macOS (with Homebrew)
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz

# Windows (with Chocolatey)
choco install graphviz

# Or download from: https://graphviz.org/download/
```

**5. Launch the application:**

```bash
streamlit run app.py
```

✅ Open your browser to **http://localhost:8501**

---

## 🚀 Quick Usage Guide

### Basic Workflow

**Step 1: Input Your Grammar**

Write a context-free grammar using the format:

```
NonTerminal -> production1 | production2
```

Example (Expression Grammar):

```
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
```

**Step 2: Choose Parser Type**

Select which parsing strategy to use:

- **LL(1)**: Top-down, fast, limited power
- **Recursive Descent**: Manual parsing, good for learning
- **SLR(1)**: Shift-reduce, simple, adequate for many grammars
- **CLR(1)**: Most powerful LR parser, handles most grammars
- **LALR(1)**: Balanced (recommended), used in most real compilers

**Step 3: Analyze & Visualize**

The framework automatically:

- Transforms grammar if needed (eliminates left recursion, etc.)
- Computes FIRST/FOLLOW sets
- Builds parser states and DFA
- Generates parsing table
- Detects conflicts and provides recommendations

**Step 4: Test & Debug**

Enter tokens to parse:

```
id + id * id
```

See:

- ✅ Step-by-step trace
- ✅ Stack evolution
- ✅ Parse tree
- ✅ Action decisions (shift/reduce)

### Programmatic Usage (Python API)

```python
from parser.grammar import Grammar
from parser.parser_comparator import ParserComparator

# 1. Parse grammar
grammar = Grammar.from_text("""
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
""")

# 2. Compare all parsers
comparator = ParserComparator(grammar)
results = comparator.compare_all()

# 3. Check results
for parser_name, result in results.items():
    print(f"{parser_name}: {'✅' if result.success else '❌'}")
    if result.conflicts:
        print(f"  Conflicts: {result.conflicts}")

# 4. Use best parser
best_parser = comparator.get_recommended_parser()
if best_parser.parse("id + id * id").accepted:
    print("✅ Input accepted!")
```

---

## 📚 Example Grammars

### Simple Expression Grammar

```
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
```

**Type:** Ambiguous, needs precedence handling  
**Best Parser:** CLR(1) or LALR(1) with conflict resolution

### Simple Assignment Grammar (LL(1) Compatible)

```
S -> V = E ;
V -> id
E -> E + V | V
```

**Type:** Unambiguous  
**Best Parser:** LL(1) after transformation

### Boolean Expression

```
E -> E | E | E & E | ! E | ( E ) | true | false
```

**Type:** Highly ambiguous  
**Best Parser:** CLR(1) with careful conflict handling

---

## 📊 What You'll See

The interactive UI displays comprehensive information:

### Analysis Phase

- **Grammar Summary**: Productions, terminals, non-terminals
- **FIRST/FOLLOW Sets**: Terminal symbols analysis
- **Grammar Transformations**: Left recursion elimination report
- **Conflict Detection**: Any ambiguities identified

### Construction Phase

- **LR States**: Item sets for each parser state
- **State Transitions**: Which symbols cause which transitions
- **DFA Diagram**: Visual state machine (Graphviz)
- **Parsing Tables**: ACTION and GOTO entries (Pandas DataFrames)

### Parsing Phase

- **Parsing Trace**: Step-by-step stack operations
- **Parse Tree**: Visual representation of derivation
- **Decision Log**: Each shift/reduce decision explained
- **Result**: Accept or reject with explanation

---

## 🎓 Educational Value

### For Students Learning Compiler Design

- Visualize algorithms taught in theory
- Understand real compiler internals
- Practice building parsers
- See why certain transformations are needed
- Learn trade-offs between parser types

### For Teaching/Research

- Interactive demonstration tool
- Helps explain complex concepts
- Student assignment framework
- Research into grammar transformations
- Algorithm comparison platform

### Key Insights Gained

1. **Predictive vs. Shift-Reduce**: See fundamental differences
2. **Conflicts**: Understand when/why they occur
3. **Grammar Design**: Why certain features require specific parsers
4. **Transformations**: Why left recursion elimination is necessary
5. **Table Generation**: How compilers automate parser construction

---

## � Project Structure & Module Guide

```
compiler_pbl/
├── app.py                              # Main Streamlit web interface
├── requirements.txt                    # Python dependencies
├── parser/                             # Core parsing module
│   ├── grammar.py                      # Grammar representation & parsing
│   ├── first_follow.py                 # FIRST/FOLLOW set computation
│   ├── transformations.py              # Left recursion, left factoring
│   ├── lr_items.py                     # LR(0) and LR(1) item classes
│   ├── dfa_builder.py                  # DFA state construction
│   ├── ll1_parser.py                   # LL(1) predictive parser
│   ├── recursive_descent.py            # Recursive descent parser
│   ├── lr_parser.py                    # LR parsers (SLR, CLR, LALR)
│   ├── parsing_table.py                # ACTION/GOTO table generation
│   ├── shift_reduce.py                 # LR parsing simulation
│   ├── conflict_detector.py            # Conflict detection & analysis
│   ├── parser_comparator.py            # Compare multiple parsers
│   ├── report_generator.py             # Structured report generation
│   ├── top_down_validator.py           # LL(1) grammar validation
│   └── __init__.py                     # Module initialization
├── visualizer/                         # Visualization module
│   ├── dfa_graph.py                    # DFA visualization (Graphviz)
│   ├── parse_tree.py                   # Parse tree visualization
│   └── __init__.py                     # Module initialization
├── examples/                           # Sample grammars
│   └── sample_grammar.txt              # Example input file
└── screenshots/                        # Documentation screenshots
```

### Module Dependencies

```
grammar.py (base)
    ├── first_follow.py
    ├── transformations.py
    └── lr_items.py
        └── dfa_builder.py
            ├── parsing_table.py
            └── shift_reduce.py

ll1_parser.py
    └─ transformations.py

recursive_descent.py
    └─ transformations.py

lr_parser.py (abstract base)
    ├── SLRParser
    ├── CLRParser
    └── LALRParser

conflict_detector.py
    ├── ll1_parser.py
    └── lr_parser.py

parser_comparator.py
    ├── ll1_parser.py
    ├── recursive_descent.py
    ├── lr_parser.py
    └── conflict_detector.py

visualizer/
    ├── dfa_graph.py (uses dfa_builder.py)
    └── parse_tree.py (uses shift_reduce.py)
```

---

## � Use Cases & Applications

### Academic

- **Compiler Design Course**: Interactive demonstrations
- **Formal Languages & Automata**: Parsing visualization
- **Algorithm Courses**: Study of parsing algorithms
- **Student Projects**: Framework for parser construction

### Professional

- **Parser Debugging**: Test grammar behavior
- **Conflict Analysis**: Understand grammar ambiguities
- **Algorithm Research**: Compare parser implementations
- **Educational Content**: Create tutorials/documentation

### Real-World Scenarios

- Designing domain-specific languages (DSLs)
- Building configuration file parsers
- Creating query language parsers
- Understanding existing compiler internals

---

## 🐛 Troubleshooting

### Environment Issues

**"ModuleNotFoundError: No module named..."**

```bash
# Ensure virtual environment is activated
source .venv/bin/activate
# Reinstall requirements
pip install -r requirements.txt
```

**"Port 8501 already in use"**

```bash
# Use different port
streamlit run app.py --server.port 8502
```

**"graphviz module not found"**

```bash
# Install Graphviz and Python bindings
pip install graphviz
# Then install system package as well (see Installation section)
```

### Parsing Issues

**"Grammar doesn't accept valid input"**

- Check for left recursion (use transformations)
- Verify grammar is unambiguous or conflicts are acceptable
- Try automatic grammar transformation for LL(1)

**"Too many conflicts detected"**

- Grammar may be inherently ambiguous
- Try CLR(1) instead of SLR(1)
- Consider LALR(1) for practical use

**"Transformation failed"**

- Grammar may not be transformable for desired parser type
- Try different parser type
- Consider rewriting grammar manually

---

## 🚀 Advanced Features

### Comparing Parser Types

Use [parser_comparator.py](parser/parser_comparator.py) to analyze your grammar:

```python
from parser.parser_comparator import ParserComparator
from parser.grammar import Grammar

grammar = Grammar.from_text("E -> E + T | T | 'id'")
comparator = ParserComparator(grammar)

# Compare all parsers
results = comparator.compare_all()

# Get recommendation
best = comparator.get_recommended_parser()
print(f"Best parser: {best.name}")
```

### Grammar Transformation

Automatically transform grammars for LL(1) parsing:

```python
from parser.transformations import GrammarTransformer

transformer = GrammarTransformer(grammar)
result = transformer.transform_for_ll1()

print(f"Original: {result.original_grammar}")
print(f"Transformed: {result.transformed_grammar}")
print(f"Transformations applied: {result.transformations}")
```

### Detailed Analysis

Generate comprehensive reports:

```python
from parser.report_generator import ReportGenerator

generator = ReportGenerator(grammar)
report = generator.generate_analysis_report()

# Access structured data
print(report.grammar_summary)
print(report.first_sets)
print(report.follow_sets)
print(report.conflicts)
```

---

## �📄 License

This project is for educational purposes only.

---

## 👨‍💻 Author

Created as a compiler design project for educational purposes.

---

## 📖 References

- Dragon Book (Compilers: Principles, Techniques, and Tools)
- Principles of Compiler Design
- LR Parsing Theory
- YACC & Bison documentation

---

## ✉️ Support

For issues or questions, please refer to the code comments and docstrings which provide detailed explanations of all algorithms.

---

**Happy Parsing! 🎉**
