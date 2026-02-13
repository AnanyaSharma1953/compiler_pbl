# LR Parser Visualizer and Generator

### (SLR / CLR / LALR Bottom-Up Parser Simulator)

---

## 📌 Project Overview

This project is a **Visual LR Parser Generator** that automatically constructs a **bottom-up parser** from a context-free grammar and demonstrates how **LR parsing works step-by-step**.

The system takes a grammar as input and:

- Computes FIRST and FOLLOW sets
- Constructs LR item sets (closure and goto)
- Builds DFA of states
- Generates ACTION and GOTO parsing tables
- Performs shift–reduce parsing
- Visually shows parsing steps and parse tree

It acts as a **mini version of YACC/Bison** with visualization and is designed for educational and compiler design learning purposes.

**Key Feature:** All algorithms are implemented from scratch without external parsing libraries.

---

## 🎯 Objectives

- Understand Bottom-Up Parsing
- Implement LR algorithms from scratch
- Visualize parser construction
- Simulate real compiler behavior
- Provide interactive learning for students

---

## ✨ Features

✅ Grammar input from user
✅ FIRST and FOLLOW computation
✅ LR(0) item generation
✅ Closure and GOTO functions
✅ Canonical collection of LR states
✅ DFA state diagram visualization
✅ ACTION & GOTO parsing table generation
✅ Step-by-step Shift–Reduce parsing
✅ Parse tree visualization
✅ Conflict detection (Shift/Reduce, Reduce/Reduce)
✅ Support for:

- SLR(1)
- CLR(1)
- LALR(1)

---

## 🧠 Algorithms Implemented

### 1. FIRST & FOLLOW

Computes terminals that can appear first and follow a non-terminal.

### 2. Closure

Adds all possible productions when a dot is before a non-terminal.

### 3. GOTO

Transitions between states using grammar symbols.

### 4. Canonical Collection

Creates complete LR item sets.

### 5. Parsing Table Construction

Builds:

- ACTION table (Shift/Reduce/Accept)
- GOTO table (State transitions)

### 6. Shift–Reduce Parser

Simulates:

- Stack operations
- Input reading
- Reductions
- Acceptance or rejection

---

## 🏗️ Tech Stack

| Component       | Technology   |
| --------------- | ------------ |
| Language        | Python 3     |
| UI              | Streamlit    |
| Visualization   | Graphviz     |
| Tables          | Pandas       |
| Version Control | Git & GitHub |

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

## ⚙️ Installation & Setup

### Step 1 – Clone/Navigate to repository

```bash
cd ~/Desktop/compiler_pbl
```

### Step 2 – Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3 – Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 – Run application

```bash
streamlit run app.py
```

Open browser at: **http://localhost:8501**

---

## 🧪 Sample Grammar

```
E → E + T
E → T
T → T * F
T → F
F → ( E )
F → id
```

### Sample Input

```
id + id * id
```

The system will show:

- Stack state at each step
- Input remaining to parse
- Action taken (Shift/Reduce)
- Final result (Accept/Reject)
- Parse tree visualization

---

## 📊 Output Screens

The tool displays:

- ✅ FIRST/FOLLOW sets
- ✅ LR states with items
- ✅ DFA diagram
- ✅ Parsing table (ACTION & GOTO)
- ✅ Parsing trace table
- ✅ Parse tree

---

## 🚀 Usage Guide

### 1. **Input Grammar**

Write grammar rules using the format:

```
NonTerminal -> production1 | production2 | production3
```

Examples:

```
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
```

### 2. **Select Parser Type**

- **SLR(1)**: Fastest, uses FOLLOW sets, less powerful
- **CLR(1)**: Full LR power, more states, most powerful
- **LALR(1)**: Balanced between SLR and CLR (recommended for most cases)

### 3. **Build Parser**

Click "Build Parser" to:

- Parse the grammar
- Compute FIRST/FOLLOW sets
- Build LR DFA
- Generate parsing tables

### 4. **View Visualizations**

Explore multiple tabs:

- **FIRST/FOLLOW**: Terminal sets
- **LR States**: Detailed item sets
- **Parsing Table**: ACTION and GOTO entries
- **DFA Graph**: State machine diagram

### 5. **Test Input**

- Enter space-separated tokens
- Click "Parse Input"
- View step-by-step trace
- See final parse tree

---

## 🎓 Learning Outcomes

After exploring this project, you will understand:

- How FIRST and FOLLOW sets work
- LR item construction and closure
- State machine (DFA) construction for parsing
- ACTION and GOTO table generation
- Differences between SLR, CLR, and LALR
- Shift-Reduce parsing mechanics
- Parse tree construction
- How real parser generators like YACC/Bison work

---

## 🚀 Future Improvements

- Grammar file upload support
- Export parsing table to CSV/JSON
- Syntax tree animation
- Error recovery strategies
- Code generation phase
- Grammar transformation tools
- Web deployment

---

## 📚 Applications

- Compiler design learning
- Educational visualization tool
- Parser debugging and testing
- Academic projects
- Understanding YACC/Bison internals
- CS course teaching assistant

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'X'"

Make sure you're using the virtual environment:

```bash
source .venv/bin/activate
```

### "Port 8501 already in use"

Kill the existing Streamlit process or use a different port:

```bash
streamlit run app.py --server.port 8502
```

### "graphviz not installed"

Install Graphviz system package:

```bash
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz

# Windows (with Chocolatey)
choco install graphviz
```

---

## 📝 Module Documentation

### `parser/grammar.py`

- Parses CFG from text format
- Stores productions in structured format
- Identifies terminals and non-terminals
- Augments grammar with S' -> S

### `parser/first_follow.py`

- Computes FIRST sets using fixed-point iteration
- Computes FOLLOW sets with proper epsilon handling
- Provides helper methods for set queries

### `parser/lr_items.py`

- Defines LR0Item and LR1Item classes
- Implements closure() for both LR(0) and LR(1)
- Implements goto() function

### `parser/dfa_builder.py`

- Builds canonical collection of LR states
- Maintains state transitions
- Supports both LR(0) and LR(1) construction

### `parser/parsing_table.py`

- Generates ACTION and GOTO tables
- Implements SLR(1), CLR(1), LALR(1) builders
- Detects and reports shift/reduce conflicts

### `parser/shift_reduce.py`

- Simulates stack-based LR parsing
- Records all parsing steps
- Builds parse tree during parsing

### `visualizer/dfa_graph.py`

- Renders DFA using Graphviz
- Shows state transitions clearly

### `visualizer/parse_tree.py`

- Defines parse tree Node class
- Renders parse tree using Graphviz

### `app.py`

- Streamlit UI with interactive interface
- Displays all visualizations
- Allows real-time testing and debugging

---

## 📄 License

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
