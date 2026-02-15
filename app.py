import streamlit as st
import pandas as pd

from parser.grammar import Grammar
from parser.first_follow import compute_first_sets, compute_follow_sets
from parser.parsing_table import build_slr_table, build_clr_table, build_lalr_table
from parser.shift_reduce import parse_input
from visualizer.dfa_graph import build_dfa_graph


# =========================================================
# LL1 IMPLEMENTATION WITH CONFLICT CHECK
# =========================================================

def first_of_string(symbols, first_sets):

    result = set()

    if not symbols:
        result.add("ε")
        return result

    for sym in symbols:

        if sym not in first_sets:
            result.add(sym)
            return result

        result |= (first_sets[sym] - {"ε"})

        if "ε" not in first_sets[sym]:
            return result

    result.add("ε")
    return result


def build_ll1_table(grammar, first_sets, follow_sets):

    table = {}
    conflict = False

    for nt in grammar.get_nonterminals():
        table[nt] = {}

    for prod in grammar.productions:

        A = prod.lhs
        alpha = prod.rhs

        first_alpha = first_of_string(alpha, first_sets)

        for t in first_alpha - {"ε"}:
            if t in table[A]:
                conflict = True
            table[A][t] = alpha

        if "ε" in first_alpha:
            for f in follow_sets[A]:
                if f in table[A]:
                    conflict = True
                table[A][f] = alpha

    return table, conflict


class LL1Step:
    def __init__(self, stack, input_remaining, action):
        self.stack = stack
        self.input_remaining = input_remaining
        self.action = action


def parse_ll1(grammar, parsing_table, input_string):

    stack = ["$", grammar.start_symbol]
    tokens = input_string.split() + ["$"]

    steps = []
    i = 0

    while stack:

        stack_str = " ".join(stack)
        remaining = " ".join(tokens[i:])

        top = stack.pop()
        cur = tokens[i]

        if top == cur:
            steps.append(LL1Step(stack_str, remaining, "match"))
            i += 1

        elif top in grammar.get_nonterminals():

            if cur not in parsing_table[top]:
                steps.append(LL1Step(stack_str, remaining, "error"))
                return steps, False

            rhs = parsing_table[top][cur]
            steps.append(LL1Step(stack_str, remaining, f"{top} → {' '.join(rhs)}"))

            for sym in reversed(rhs):
                if sym != "ε":
                    stack.append(sym)

        else:
            steps.append(LL1Step(stack_str, remaining, "error"))
            return steps, False

        if top == "$" and cur == "$":
            break

    return steps, True


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(page_title="Parser Visualizer", layout="wide")
st.title("🚀 Parser Visualizer")


# =========================================================
# SESSION STATE
# =========================================================

def reset():
    st.session_state.table = None
    st.session_state.grammar = None
    st.session_state.first = None
    st.session_state.follow = None
    st.session_state.steps = None
    st.session_state.accepted = None


if "table" not in st.session_state:
    reset()


# =========================================================
# HELPERS
# =========================================================

def make_set_table(data, grammar, name):
    rows = []
    nts = set(grammar.get_nonterminals())

    for nt, vals in sorted(data.items()):
        if nt in nts:
            rows.append([nt, ", ".join(sorted(vals))])

    return pd.DataFrame(rows, columns=["NonTerminal", name])


def make_lr_table(table, grammar):

    terminals = sorted([t for t in grammar.get_terminals() if t != "$"]) + ["$"]
    nonterminals = sorted(grammar.get_nonterminals())

    rows = []

    for s in range(len(table.states)):
        row = {"State": f"I{s}"}

        for t in terminals:
            val = ""
            if s in table.action and t in table.action[s]:
                a, v = table.action[s][t]
                if a == "shift":
                    val = f"s{v}"
                elif a == "reduce":
                    val = f"r{v}"
                elif a == "accept":
                    val = "acc"
            row[t] = str(val)

        for nt in nonterminals:
            val = ""
            if s in table.goto and nt in table.goto[s]:
                val = table.goto[s][nt]
            row[nt] = str(val)

        rows.append(row)

    return pd.DataFrame(rows)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.header("Configuration")

    mode = st.radio(
        "Parsing Type",
        ["Top Down (LL1)", "Bottom Up (LR)"],
        on_change=reset
    )

    if mode == "Bottom Up (LR)":
        parser_type = st.selectbox(
            "LR Variant",
            ["SLR(1)", "LALR(1)", "CLR(1)"],
            on_change=reset
        )

    grammar_text = st.text_area("Grammar", height=180, on_change=reset)

    input_string = st.text_input(
        "Input String (space separated)",
        on_change=lambda: st.session_state.update({"steps": None})
    )

    build_btn = st.button("🔨 Build & Parse", use_container_width=True)


# =========================================================
# BUILD
# =========================================================

if build_btn and grammar_text.strip():

    grammar = Grammar.from_text(grammar_text)

    first = compute_first_sets(grammar)
    follow = compute_follow_sets(grammar)

    st.session_state.grammar = grammar
    st.session_state.first = first
    st.session_state.follow = follow

    # -----------------------------------------------------
    # Bottom Up (LR)
    # -----------------------------------------------------
    if mode == "Bottom Up (LR)":

        if parser_type == "SLR(1)":
            table = build_slr_table(grammar)
        elif parser_type == "CLR(1)":
            table = build_clr_table(grammar)
        else:
            table = build_lalr_table(grammar)

        # 🔥 CONFLICT CHECK
        # 🔥 CONFLICT CHECK
        if not table.is_conflict_free:
            st.error(f"❌ Given grammar is NOT {parser_type}")
            
            # Optional: Show detailed conflicts
            for c in table.conflicts:
                st.write(
                    f"State I{c.state}, Symbol '{c.symbol}': "
                    f"{c.existing_action}  vs  {c.new_action}"
                )
            
            st.stop()

        st.session_state.table = table

        steps, accepted, _ = parse_input(grammar, table, input_string)
        st.session_state.steps = steps
        st.session_state.accepted = accepted

    # -----------------------------------------------------
    # Top Down (LL1)
    # -----------------------------------------------------
    else:

        ll1_table, conflict = build_ll1_table(grammar, first, follow)

        if conflict:
            st.error("❌ Given grammar is NOT LL(1)")
            st.stop()

        steps, accepted = parse_ll1(grammar, ll1_table, input_string)

        st.session_state.table = None
        st.session_state.steps = steps
        st.session_state.accepted = accepted


# =========================================================
# DISPLAY
# =========================================================

if st.session_state.grammar:

    grammar = st.session_state.grammar
    first = st.session_state.first
    follow = st.session_state.follow
    steps = st.session_state.steps

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["FIRST/FOLLOW", "LR States", "Parsing Table", "DFA", "Parsing Trace"]
    )

    with tab1:
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("FIRST")
            st.dataframe(make_set_table(first, grammar, "FIRST"), use_container_width=True)

        with c2:
            st.subheader("FOLLOW")
            st.dataframe(make_set_table(follow, grammar, "FOLLOW"), use_container_width=True)

    if st.session_state.table:

        table = st.session_state.table

        with tab2:
            for i, state in enumerate(table.states):
                with st.expander(f"I{i}"):
                    for item in state:

                        if item.prod_index < len(grammar.productions):
                            prod = grammar.productions[item.prod_index]
                            lhs = prod.lhs
                            rhs = list(prod.rhs)
                        else:
                            lhs = grammar.start_symbol + "'"
                            rhs = [grammar.start_symbol]

                        dot_pos = min(item.dot, len(rhs))
                        rhs_with_dot = rhs[:dot_pos] + ["•"] + rhs[dot_pos:]

                        st.write(f"{lhs} → {' '.join(rhs_with_dot)}")

        with tab3:
            df = make_lr_table(table, grammar)
            st.dataframe(df, use_container_width=True)

        with tab4:
            graph = build_dfa_graph(table.states, table.transitions)
            st.graphviz_chart(graph)

    else:
        with tab2:
            st.info("Only for Bottom-Up parsers")
        with tab3:
            st.info("Only for Bottom-Up parsers")
        with tab4:
            st.info("Only for Bottom-Up parsers")

    with tab5:

        if steps:
            rows = []
            for i, step in enumerate(steps):
                rows.append([str(i + 1), step.stack, step.input_remaining, step.action])

            df = pd.DataFrame(rows, columns=["Step", "Stack", "Input", "Action"])
            st.dataframe(df, use_container_width=True)

            if st.session_state.accepted:
                st.success("✅ ACCEPTED")
            else:
                st.error("❌ REJECTED")

        else:
            st.info("Run parser to see trace")
