"""
Streamlit UI for the LR Parser Visualizer.

Provides interactive interface for building and testing LR parsers.
"""

import pandas as pd
import streamlit as st

from parser.grammar import Grammar
from parser.first_follow import compute_first_sets, compute_follow_sets
from parser.parsing_table import build_clr_table, build_lalr_table, build_slr_table
from parser.shift_reduce import parse_input
from visualizer.dfa_graph import build_dfa_graph

# Page configuration
st.set_page_config(page_title="LR Parser Visualizer", layout="wide")

st.title("🚀 LR Parser Visualizer")
st.markdown("Build and visualize SLR(1), CLR(1), and LALR(1) parsers from context-free grammars.")

# Session state initialization
if "parser_built" not in st.session_state:
    st.session_state.parser_built = False
if "table" not in st.session_state:
    st.session_state.table = None
if "grammar" not in st.session_state:
    st.session_state.grammar = None
if "first_sets" not in st.session_state:
    st.session_state.first_sets = None
if "follow_sets" not in st.session_state:
    st.session_state.follow_sets = None
if "parse_steps" not in st.session_state:
    st.session_state.parse_steps = None
if "parse_accepted" not in st.session_state:
    st.session_state.parse_accepted = None


def reset_parser_state() -> None:
    """Reset parser and parsing results when grammar or parser type changes."""
    st.session_state.parser_built = False
    st.session_state.table = None
    st.session_state.grammar = None
    st.session_state.first_sets = None
    st.session_state.follow_sets = None
    st.session_state.parse_steps = None
    st.session_state.parse_accepted = None


def build_parser(grammar_text: str, parser_type: str) -> None:
    """Build parsing table and store results in session state."""
    grammar = Grammar.from_text(grammar_text)
    if parser_type == "SLR(1)":
        table = build_slr_table(grammar)
    elif parser_type == "CLR(1)":
        table = build_clr_table(grammar)
    else:
        table = build_lalr_table(grammar)

    st.session_state.table = table
    st.session_state.grammar = grammar
    st.session_state.first_sets = compute_first_sets(grammar)
    st.session_state.follow_sets = compute_follow_sets(grammar)
    st.session_state.parser_built = table.is_conflict_free
    st.session_state.parse_steps = None
    st.session_state.parse_accepted = None


def parse_with_table(input_string: str) -> None:
    """Parse input using existing parsing table and store results."""
    grammar = st.session_state.grammar
    table = st.session_state.table
    steps, accepted, _ = parse_input(grammar, table, input_string)
    st.session_state.parse_steps = steps
    st.session_state.parse_accepted = accepted


# Sidebar for configuration
with st.sidebar:
    st.header("Parser Configuration")
    
    grammar_text = st.text_area(
        "Grammar Input (CFG)",
        value=st.session_state.get("grammar_text", ""),
        height=200,
        help="Format: LHS -> RHS1 | RHS2 | ... (one rule per line)\nExample:\nE -> E + T | T\nT -> T * F | F\nF -> ( E ) | id",
        key="grammar_text",
        on_change=reset_parser_state,
    )

    parser_type = st.selectbox(
        "Select Parser Type",
        ["SLR(1)", "LALR(1)", "CLR(1)"],
        help="SLR: Simple, fewer states. LALR: Balanced. CLR: Most powerful.",
        key="parser_type",
        on_change=reset_parser_state,
    )

    st.divider()

    if st.button("🔨 Build Parser", type="primary", use_container_width=True):
        try:
            build_parser(grammar_text, parser_type)
        except ValueError as e:
            st.error(f"❌ Grammar Error: {str(e)}")
            reset_parser_state()
        except Exception as e:
            st.error(f"❌ Unexpected Error: {str(e)}")
            reset_parser_state()

main_left, main_right = st.columns([3, 2])

with main_left:
    if st.session_state.table is None:
        st.info("Build a parser to view results.")
    else:
        table = st.session_state.table
        grammar = st.session_state.grammar
        first_sets = st.session_state.first_sets
        follow_sets = st.session_state.follow_sets

        if table.is_conflict_free:
            st.success(f"✅ Grammar is valid for {parser_type}")
        else:
            st.error(f"❌ Grammar is NOT {parser_type} due to conflicts.")

        # Show conflicts if any
        if table.conflicts:
            st.warning(f"⚠️ {len(table.conflicts)} Conflict(s) detected:")
            conflict_df = pd.DataFrame([
                {
                    "State": f"I{c.state}",
                    "Symbol": c.symbol,
                    "Existing Action": str(c.existing_action),
                    "New Action": str(c.new_action),
                }
                for c in table.conflicts
            ])
            st.dataframe(conflict_df, width='stretch')

        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(
            ["FIRST/FOLLOW", "LR States", "Parsing Table", "DFA Graph"]
        )

        # Tab 1: FIRST and FOLLOW sets
        with tab1:
            col_f, col_fo = st.columns(2)

            with col_f:
                st.subheader("FIRST Sets")
                # Filter to only show non-terminals, sorted alphabetically
                nonterminals = grammar.get_nonterminals()
                first_nonterminals = {nt: first_sets[nt] for nt in sorted(nonterminals) if nt in first_sets}
                first_df = pd.DataFrame({
                    "Non-Terminal": list(first_nonterminals.keys()),
                    "FIRST": [", ".join(sorted(first_nonterminals[s])) for s in first_nonterminals.keys()]
                })
                st.dataframe(first_df, width='stretch')

            with col_fo:
                st.subheader("FOLLOW Sets")
                # Sort alphabetically by non-terminal name
                follow_sorted = {nt: follow_sets[nt] for nt in sorted(follow_sets.keys())}
                follow_df = pd.DataFrame({
                    "Non-Terminal": list(follow_sorted.keys()),
                    "FOLLOW": [", ".join(sorted(follow_sorted[s])) for s in follow_sorted.keys()]
                })
                st.dataframe(follow_df, width='stretch')

        # Tab 2: LR States
        with tab2:
            st.subheader(f"LR States ({len(table.states)} total)")
            
            augmented_grammar = grammar.augment()
            
            # Display each state as an expandable panel
            for state_id in range(len(table.states)):
                state = table.states[state_id]
                
                with st.expander(f"**I{state_id}** ({len(state)} items)", expanded=(state_id == 0)):
                    for item in sorted(state, key=lambda x: (x.prod_index, x.dot)):
                        prod = augmented_grammar.productions[item.prod_index]
                        lhs = prod.lhs
                        rhs = prod.rhs
                        
                        # Build item string with highlighted dot
                        before = " ".join(rhs[:item.dot]) if item.dot > 0 else ""
                        after = " ".join(rhs[item.dot:]) if item.dot < len(rhs) else ""
                        
                        # Format with bold dot for visibility
                        if before and after:
                            item_str = f"{lhs} → {before} **•** {after}"
                        elif before:
                            item_str = f"{lhs} → {before} **•**"
                        elif after:
                            item_str = f"{lhs} → **•** {after}"
                        else:
                            item_str = f"{lhs} → **•**"
                        
                        # Add lookahead for CLR/LALR items
                        if hasattr(item, "lookahead"):
                            item_str += f" &nbsp;&nbsp;**[** {item.lookahead} **]**"
                        
                        st.markdown(f"- {item_str}")
                    
                    # Show empty state message if no items (shouldn't happen)
                    if len(state) == 0:
                        st.info("Empty state")

        # Tab 3: Parsing Table
        with tab3:
            st.subheader("LR Parsing Table (Matrix Format)")
            
            # Collect all symbols for columns
            terminals = grammar.get_terminals()
            nonterminals = grammar.get_nonterminals()
            
            # Sort terminals: alphabetically, but $ at the end
            terminals_sorted = sorted([t for t in terminals if t != "$"]) + (["$"] if "$" in terminals else [])
            nonterminals_sorted = sorted(nonterminals)
            
            # Build matrix
            num_states = len(table.states)
            matrix_data = {}
            matrix_data["State"] = [f"I{i}" for i in range(num_states)]
            
            # Collect conflicts for highlighting
            conflict_cells = set()
            for conflict in table.conflicts:
                conflict_cells.add((conflict.state, conflict.symbol))
            
            # ACTION columns (terminals)
            for terminal in terminals_sorted:
                column = []
                for state_id in range(num_states):
                    cell_value = ""
                    if state_id in table.action and terminal in table.action[state_id]:
                        action_type, action_value = table.action[state_id][terminal]
                        if action_type == "shift":
                            cell_value = f"s{action_value}"
                        elif action_type == "reduce":
                            cell_value = f"r{action_value}"
                        elif action_type == "accept":
                            cell_value = "acc"
                        
                        # Mark conflicts
                        if (state_id, terminal) in conflict_cells:
                            cell_value = f"⚠️ {cell_value}"
                    column.append(cell_value)
                matrix_data[terminal] = column
            
            # GOTO columns (non-terminals)
            for nonterminal in nonterminals_sorted:
                column = []
                for state_id in range(num_states):
                    cell_value = ""
                    if state_id in table.goto and nonterminal in table.goto[state_id]:
                        next_state = table.goto[state_id][nonterminal]
                        cell_value = str(next_state)
                    column.append(cell_value)
                matrix_data[nonterminal] = column
            
            # Create DataFrame
            matrix_df = pd.DataFrame(matrix_data)
            
            # Display with styling
            st.write("**ACTION** (terminals) | **GOTO** (non-terminals)")
            st.write(f"Terminals: {', '.join(terminals_sorted)}")
            st.write(f"Non-terminals: {', '.join(nonterminals_sorted)}")
            
            # Apply styling function
            def highlight_conflicts(val):
                if isinstance(val, str) and val.startswith("⚠️"):
                    return "background-color: #ffcccc; font-weight: bold;"
                return ""
            
            styled_df = matrix_df.style.map(highlight_conflicts)
            st.dataframe(styled_df, width='stretch', height=400)

        # Tab 4: DFA Graph
        with tab4:
            st.subheader("LR Deterministic Finite Automaton")
            dfa_graph = build_dfa_graph(table.states, table.transitions)
            st.graphviz_chart(dfa_graph)

with main_right:
    st.subheader("⚙️ Parse Input")
    
    if st.session_state.table is None:
        st.info("💡 Build a parser first to enable parsing.")
    elif not st.session_state.parser_built:
        st.error("❌ Grammar has conflicts. Parsing is disabled.")
    
    input_string = st.text_input(
        "Input String (space-separated tokens)",
        "id + id * id",
        help="Example: 'id + id * id' or '( id )'",
        key="parse_input_text",
        disabled=st.session_state.table is None or not st.session_state.parser_built,
        on_change=lambda: (
            st.session_state.__setattr__("parse_steps", None),
            st.session_state.__setattr__("parse_accepted", None),
        ),
    )

    parse_disabled = st.session_state.table is None or not st.session_state.parser_built
    
    if st.button("▶️ Parse", type="secondary", disabled=parse_disabled, use_container_width=True):
        parse_with_table(input_string)

    if st.session_state.parse_steps is not None:
        steps = st.session_state.parse_steps
        accepted = st.session_state.parse_accepted

        if accepted:
            st.success("✅ ACCEPTED")
        else:
            st.error("❌ REJECTED")

        st.write("**Shift-Reduce Trace**")
        trace_data = []
        for i, step in enumerate(steps):
            trace_data.append({
                "Step": i + 1,
                "Stack": step.stack,
                "Input": step.input_remaining,
                "Action": step.action,
            })
        trace_df = pd.DataFrame(trace_data)
        st.dataframe(trace_df, width='stretch')

# Footer
st.divider()
st.caption("Educational LR parser visualizer implementing SLR(1), CLR(1), and LALR(1) algorithms from scratch.")

