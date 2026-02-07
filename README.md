# LR Parser Visualizer and Generator

### (SLR / CLR / LALR Bottom-Up Parser Simulator)

---

## 📌 Project Overview

This project is a **Visual LR Parser Generator** that automatically constructs a **bottom-up parser** from a context-free grammar and demonstrates how **LR parsing works step-by-step**.

The system takes a grammar as input and:

* Computes FIRST and FOLLOW sets
* Constructs LR item sets (closure and goto)
* Builds DFA of states
* Generates ACTION and GOTO parsing tables
* Performs shift–reduce parsing
* Visually shows parsing steps and parse tree

It acts as a **mini version of YACC/Bison** with visualization and is designed for educational and compiler design learning purposes.

---

## 🎯 Objectives

* Understand Bottom-Up Parsing
* Implement LR algorithms from scratch
* Visualize parser construction
* Simulate real compiler behavior
* Provide interactive learning for students

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

* SLR(1)
* CLR(1)
* LALR(1)

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

* ACTION table (Shift/Reduce/Accept)
* GOTO table (State transitions)

### 6. Shift–Reduce Parser

Simulates:

* Stack operations
* Input reading
* Reductions
* Acceptance or rejection

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
lr-parser-visualizer/
│
├── app.py
│
├── parser/
│   ├── grammar.py
│   ├── first_follow.py
│   ├── lr_items.py
│   ├── dfa_builder.py
│   ├── parsing_table.py
│   ├── shift_reduce.py
│
├── visualizer/
│   ├── dfa_graph.py
│   ├── parse_tree.py
│
├── examples/
│   ├── sample_grammar.txt
│
├── requirements.txt
├── README.md
└── screenshots/
```

---

## ⚙️ Installation & Setup

### Step 1 – Clone repository

```
git clone https://github.com/your-username/lr-parser-visualizer.git
cd lr-parser-visualizer
```

### Step 2 – Install dependencies

```
pip install -r requirements.txt
```

### Step 3 – Run application

```
streamlit run app.py
```

Open browser at:

```
http://localhost:8501
```

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

* Stack
* Input
* Action (Shift/Reduce)
* Final result

---

## 📊 Output Screens

The tool displays:

* FIRST/FOLLOW sets
* LR states
* DFA diagram
* Parsing table
* Parsing trace table
* Parse tree

(Add screenshots inside the `screenshots/` folder)

---

## 🎓 Learning Outcomes

After completing this project, you will understand:

* Bottom-up parsing techniques
* Working of LR parsers
* Construction of DFA for parsing
* Compiler front-end concepts
* Real parser generators like YACC/Bison

---

## 🚀 Future Improvements

* Grammar file upload support
* Export parsing table to CSV
* Syntax tree animation
* Error recovery strategies
* Code generation phase
* Web deployment

---

## 📚 Applications

* Compiler design learning
* Educational visualization tool
* Parser debugging
* Academic projects
* Understanding YACC/Bison internals

---

## 📄 License

This project is for educational purposes only.
