import streamlit as st
import pandas as pd
import time

from parser.grammar import Grammar
from parser.first_follow import compute_first_sets, compute_follow_sets
from parser.parsing_table import build_slr_table, build_clr_table, build_lalr_table
from parser.shift_reduce import parse_input
from visualizer.dfa_graph import build_dfa_graph


# =========================================================
# CUSTOM CSS STYLING - DARK MODE COSY THEME
# =========================================================

def load_custom_css():
    st.markdown("""
        <style>
        /* ===== DARK MODE COSY COLOR PALETTE ===== */
        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-tertiary: #334155;
            --bg-card: #1e293b;
            --text-primary: #f1f5f9;
            --text-secondary: #cbd5e1;
            --accent-warm: #f59e0b;
            --accent-purple: #a78bfa;
            --accent-blue: #60a5fa;
            --accent-green: #34d399;
            --accent-red: #f87171;
            --shadow-glow: rgba(168, 139, 250, 0.2);
        }
        
        /* ===== MAIN APP BACKGROUND ===== */
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        }
        
        /* ===== HIDE STREAMLIT BRANDING ===== */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* ===== MAIN HEADER - COSY GRADIENT ===== */
        .main-header {
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
            padding: 2.5rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow: 0 20px 40px rgba(168, 139, 250, 0.3);
            animation: fadeIn 0.8s ease-in;
            border: 1px solid rgba(168, 139, 250, 0.2);
        }
        
        .main-header h1 {
            color: white;
            font-size: 3rem;
            font-weight: 800;
            margin: 0;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
            letter-spacing: -1px;
        }
        
        .main-header p {
            color: rgba(255,255,255,0.95);
            font-size: 1.2rem;
            margin-top: 0.8rem;
            font-weight: 400;
        }
        
        /* ===== CARD STYLING - DARK COSY ===== */
        .custom-card {
            background: var(--bg-card);
            border-radius: 16px;
            padding: 1.8rem;
            box-shadow: 0 8px 24px rgba(0,0,0,0.4);
            margin-bottom: 1.5rem;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid rgba(148, 163, 184, 0.1);
        }
        
        .custom-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 32px rgba(168, 139, 250, 0.3);
            border-color: rgba(168, 139, 250, 0.3);
        }
        
        /* ===== METRIC CARDS - WARM GLOW ===== */
        .metric-card {
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            border-radius: 16px;
            padding: 2rem;
            color: white;
            text-align: center;
            box-shadow: 0 8px 24px rgba(168, 139, 250, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            transform: scale(1.05);
            box-shadow: 0 12px 32px rgba(168, 139, 250, 0.6);
        }
        
        .metric-value {
            font-size: 2.8rem;
            font-weight: 800;
            margin: 0.5rem 0;
            text-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.95;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-weight: 600;
        }
        
        /* ===== SIDEBAR - DARK COSY ===== */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
            border-right: 1px solid rgba(148, 163, 184, 0.1);
        }
        
        [data-testid="stSidebar"] .stMarkdown {
            color: var(--text-primary);
        }
        
        /* ===== BUTTONS - GLOWING STYLE ===== */
        .stButton>button {
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.85rem 2.5rem;
            font-weight: 700;
            font-size: 1rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 16px rgba(168, 139, 250, 0.4);
            letter-spacing: 0.5px;
        }
        
        .stButton>button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(168, 139, 250, 0.6);
            background: linear-gradient(135deg, #7c3aed 0%, #c026d3 100%);
        }
        
        .stButton>button:active {
            transform: translateY(-1px);
        }
        
        /* ===== TABS - DARK MODE ===== */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: var(--bg-secondary);
            border-radius: 12px;
            padding: 0.6rem;
            box-shadow: inset 0 2px 8px rgba(0,0,0,0.3);
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px;
            padding: 0.85rem 1.8rem;
            font-weight: 600;
            transition: all 0.3s ease;
            color: var(--text-secondary);
            background: transparent;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(168, 139, 250, 0.1);
            color: var(--text-primary);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            color: white !important;
            box-shadow: 0 4px 12px rgba(168, 139, 250, 0.4);
        }
        
        /* ===== TEXT INPUTS - DARK COSY ===== */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            background: var(--bg-secondary);
            color: var(--text-primary);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 10px;
            padding: 0.75rem;
            transition: all 0.3s ease;
        }
        
        .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
            border-color: var(--accent-purple);
            box-shadow: 0 0 0 3px rgba(168, 139, 250, 0.2);
            background: var(--bg-tertiary);
        }
        
        /* ===== SELECT BOX - DARK MODE ===== */
        .stSelectbox>div>div {
            background: var(--bg-secondary);
            border-radius: 10px;
            border: 1px solid rgba(148, 163, 184, 0.2);
        }
        
        /* ===== EXPANDER - COSY DARK ===== */
        .streamlit-expanderHeader {
            background-color: var(--bg-secondary);
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s ease;
            color: var(--text-primary);
            border: 1px solid rgba(148, 163, 184, 0.1);
        }
        
        .streamlit-expanderHeader:hover {
            background-color: var(--bg-tertiary);
            border-color: rgba(168, 139, 250, 0.3);
            box-shadow: 0 4px 12px rgba(168, 139, 250, 0.2);
        }
        
        /* ===== TABLES - DARK MODE ===== */
        .dataframe {
            background: var(--bg-secondary);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 16px rgba(0,0,0,0.3);
        }
        
        .dataframe thead tr th {
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            color: white;
            font-weight: 700;
            padding: 1rem;
            border: none;
        }
        
        .dataframe tbody tr {
            background: var(--bg-card);
            border-bottom: 1px solid rgba(148, 163, 184, 0.1);
            transition: all 0.2s ease;
        }
        
        .dataframe tbody tr:hover {
            background: var(--bg-tertiary);
        }
        
        .dataframe tbody tr td {
            color: var(--text-secondary);
            padding: 0.85rem;
            border: none;
        }
        
        /* ===== ANIMATIONS ===== */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-30px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        @keyframes glow {
            0%, 100% { box-shadow: 0 0 20px rgba(168, 139, 250, 0.4); }
            50% { box-shadow: 0 0 30px rgba(168, 139, 250, 0.7); }
        }
        
        .animate-slide {
            animation: slideIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        /* ===== STATUS BADGES ===== */
        .status-badge {
            display: inline-block;
            padding: 0.6rem 1.4rem;
            border-radius: 24px;
            font-weight: 700;
            font-size: 1rem;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        
        .status-success {
            background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
            color: white;
            animation: glow 2s infinite;
        }
        
        .status-error {
            background: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
            color: white;
        }
        
        /* ===== GRAMMAR EXAMPLES - DARK COSY ===== */
        .grammar-example {
            background: var(--bg-secondary);
            border-left: 4px solid var(--accent-purple);
            padding: 1.2rem;
            margin: 0.8rem 0;
            border-radius: 8px;
            font-family: 'Fira Code', 'Courier New', monospace;
            color: var(--text-primary);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        
        /* ===== INFO BOXES ===== */
        .info-box {
            background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
            color: white;
            padding: 1.2rem;
            border-radius: 12px;
            margin: 1.2rem 0;
            box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* ===== LOADING SPINNER - GLOWING ===== */
        .loader {
            border: 4px solid rgba(148, 163, 184, 0.2);
            border-top: 4px solid var(--accent-purple);
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s cubic-bezier(0.4, 0, 0.2, 1) infinite;
            margin: 2rem auto;
            box-shadow: 0 0 20px rgba(168, 139, 250, 0.4);
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* ===== TEXT COLORS ===== */
        .stMarkdown, .stText, p, span, li {
            color: var(--text-primary);
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-primary) !important;
        }
        
        /* ===== CODE BLOCKS - DARK ===== */
        code {
            background: var(--bg-secondary);
            color: var(--accent-warm);
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-family: 'Fira Code', monospace;
        }
        
        pre {
            background: var(--bg-secondary);
            border-radius: 10px;
            padding: 1rem;
            border: 1px solid rgba(148, 163, 184, 0.2);
        }
        
        /* ===== SCROLLBAR - DARK MODE ===== */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--bg-primary);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--bg-tertiary);
            border-radius: 5px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--accent-purple);
        }
        </style>
    """, unsafe_allow_html=True)


# =========================================================
# EXAMPLE GRAMMARS
# =========================================================

EXAMPLE_GRAMMARS = {
    "Select an example...": "",
    "Arithmetic Expression": """E -> E + T | T
T -> T * F | F
F -> ( E ) | id""",
    "Simple Assignment": """S -> id = E
E -> E + T | T
T -> id | num""",
    "If-Else Statement": """S -> if E then S | if E then S else S | id
E -> id | num""",
    "Balanced Parentheses": """S -> ( S ) | S S | ε""",
    "List Structure": """L -> [ E ]
E -> E , T | T
T -> id | num"""
}

EXAMPLE_INPUTS = {
    "Arithmetic Expression": "id + id * id",
    "Simple Assignment": "id = id + num",
    "If-Else Statement": "if id then id else id",
    "Balanced Parentheses": "( ) ( )",
    "List Structure": "[ id , num , id ]"
}


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

st.set_page_config(
    page_title="Parser Visualizer | Compiler Design Tool",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_custom_css()

# Hero Header
st.markdown("""
    <div class="main-header">
        <h1>🚀 Parser Visualizer</h1>
        <p>Interactive LR & LL(1) Parser Generator with Real-Time Visualization</p>
    </div>
""", unsafe_allow_html=True)


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
    """
    Create a table displaying FIRST or FOLLOW sets for non-terminals only.
    
    Args:
        data: Dictionary mapping symbols to their sets
        grammar: Grammar object
        name: "FIRST" or "FOLLOW" - used as column header
    
    Returns:
        DataFrame with non-terminals and their sets
    """
    rows = []
    nonterminals = grammar.get_nonterminals()
    
    # Sort non-terminals alphabetically for consistent display
    sorted_nonterminals = sorted(nonterminals)
    
    # Only display non-terminals (filter out terminals)
    for nt in sorted_nonterminals:
        if nt in data:
            # Format set as { a, b, c }
            vals = sorted(data[nt])
            formatted_set = "{ " + ", ".join(vals) + " }"
            rows.append([nt, formatted_set])
    
    return pd.DataFrame(rows, columns=["Non-Terminal", name])


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
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")
    
    # Parser mode selection
    st.markdown("#### 🎯 Parsing Mode")
    mode = st.radio(
        "Select Parser Type",
        ["🔻 Bottom-Up (LR)", "🔺 Top-Down (LL1)"],
        on_change=reset,
        label_visibility="collapsed"
    )
    
    # Extract actual mode
    if "Bottom-Up" in mode:
        mode = "Bottom Up (LR)"
    else:
        mode = "Top Down (LL1)"
    
    st.markdown("---")
    
    # LR variant selection
    if mode == "Bottom Up (LR)":
        st.markdown("#### 🔧 LR Parser Variant")
        parser_type = st.selectbox(
            "Choose LR Type",
            ["SLR(1)", "LALR(1)", "CLR(1)"],
            on_change=reset,
            help="""
            **SLR(1)**: Simple LR - Fastest, uses FOLLOW sets
            **LALR(1)**: Look-Ahead LR - Balanced power & states
            **CLR(1)**: Canonical LR - Most powerful, more states
            """
        )
        
        # Info about selected parser
        parser_info = {
            "SLR(1)": "⚡ Fast | Less powerful | Uses FOLLOW sets",
            "LALR(1)": "⚖️ Balanced | Recommended | Optimal states",
            "CLR(1)": "💪 Powerful | More states | Full LR power"
        }
        st.info(parser_info[parser_type])
    
    st.markdown("---")
    
    # Example grammar selector
    st.markdown("#### 📚 Grammar Templates")
    selected_example = st.selectbox(
        "Load Example",
        list(EXAMPLE_GRAMMARS.keys()),
        on_change=reset
    )
    
    # Initialize grammar text
    if selected_example != "Select an example...":
        default_grammar = EXAMPLE_GRAMMARS[selected_example]
        default_input = EXAMPLE_INPUTS.get(selected_example, "")
    else:
        default_grammar = st.session_state.get("grammar_text", "")
        default_input = st.session_state.get("input_text", "")
    
    st.markdown("---")
    st.markdown("#### ✍️ Grammar Input")
    
    grammar_text = st.text_area(
        "Enter Grammar Rules",
        value=default_grammar,
        height=200,
        on_change=reset,
        placeholder="Example:\nE -> E + T | T\nT -> T * F | F\nF -> ( E ) | id",
        help="Use format: NonTerminal -> production1 | production2"
    )
    
    # Store in session state
    st.session_state["grammar_text"] = grammar_text
    
    st.markdown("---")
    st.markdown("#### 🎮 Test Input")
    
    input_string = st.text_input(
        "Input String (space-separated tokens)",
        value=default_input,
        on_change=lambda: st.session_state.update({"steps": None}),
        placeholder="id + id * id",
        help="Enter tokens separated by spaces"
    )
    
    # Store in session state
    st.session_state["input_text"] = input_string
    
    st.markdown("---")
    
    # Build button with icon
    build_btn = st.button(
        "🚀 Build & Parse",
        use_container_width=True,
        type="primary"
    )
    
    # Quick info section
    with st.expander("ℹ️ Quick Help"):
        st.markdown("""
        **Grammar Format:**
        - Use `->` for productions
        - Use `|` for alternatives
        - Terminals: lowercase or symbols
        - Non-terminals: UPPERCASE
        
        **Example:**
        ```
        E -> E + T | T
        T -> id | num
        ```
        """)
    
    # Stats section
    if st.session_state.get("grammar"):
        st.markdown("---")
        st.markdown("#### 📊 Grammar Stats")
        grammar = st.session_state.grammar
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Productions", len(grammar.productions))
        with col2:
            st.metric("Non-Terminals", len(grammar.get_nonterminals()))


# =========================================================
# BUILD
# =========================================================

if build_btn and grammar_text.strip():
    
    # Show loading animation
    with st.spinner("🔧 Parsing grammar..."):
        time.sleep(0.3)
        try:
            grammar = Grammar.from_text(grammar_text)
        except Exception as e:
            st.error(f"❌ **Grammar Parse Error:** {str(e)}")
            st.stop()
    
    # Show progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("Computing FIRST sets...")
    progress_bar.progress(20)
    first = compute_first_sets(grammar)
    
    status_text.text("Computing FOLLOW sets...")
    progress_bar.progress(40)
    follow = compute_follow_sets(grammar)
    
    st.session_state.grammar = grammar
    st.session_state.first = first
    st.session_state.follow = follow
    
    # -----------------------------------------------------
    # Bottom Up (LR)
    # -----------------------------------------------------
    if mode == "Bottom Up (LR)":
        
        status_text.text(f"Building {parser_type} parser...")
        progress_bar.progress(60)
        
        try:
            if parser_type == "SLR(1)":
                table = build_slr_table(grammar)
            elif parser_type == "CLR(1)":
                table = build_clr_table(grammar)
            else:
                table = build_lalr_table(grammar)
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ **Parser Build Error:** {str(e)}")
            st.stop()
        
        progress_bar.progress(80)
        
        # 🔥 CONFLICT CHECK
        if not table.is_conflict_free:
            progress_bar.empty()
            status_text.empty()
            
            st.error(f"### ❌ Grammar Conflict Detected")
            st.warning(f"**The given grammar is NOT {parser_type} parseable.**")
            
            # Show conflicts in expandable section
            with st.expander("🔍 View Conflict Details"):
                for c in table.conflicts:
                    st.code(
                        f"State I{c.state}, Symbol '{c.symbol}':\n"
                        f"  Conflict: {c.existing_action} ↔ {c.new_action}",
                        language="text"
                    )
            
            st.info("💡 **Tip:** Try modifying the grammar or using a different parser type (CLR is most powerful).")
            st.stop()
        
        st.session_state.table = table
        
        status_text.text("Parsing input string...")
        progress_bar.progress(90)
        
        if input_string.strip():
            steps, accepted, _ = parse_input(grammar, table, input_string)
            st.session_state.steps = steps
            st.session_state.accepted = accepted
        
        progress_bar.progress(100)
        status_text.text("✅ Complete!")
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        # Success message
        st.success(f"✨ **{parser_type} Parser Built Successfully!**")
    
    # -----------------------------------------------------
    # Top Down (LL1)
    # -----------------------------------------------------
    else:
        
        status_text.text("Building LL(1) parsing table...")
        progress_bar.progress(60)
        
        ll1_table, conflict = build_ll1_table(grammar, first, follow)
        
        progress_bar.progress(80)
        
        if conflict:
            progress_bar.empty()
            status_text.empty()
            
            st.error("### ❌ Grammar Conflict Detected")
            st.warning("**The given grammar is NOT LL(1) parseable.**")
            st.info("💡 **Tip:** LL(1) grammars cannot have left recursion or common prefixes. Try left-factoring or eliminating left recursion.")
            st.stop()
        
        status_text.text("Parsing input string...")
        progress_bar.progress(90)
        
        if input_string.strip():
            steps, accepted = parse_ll1(grammar, ll1_table, input_string)
            st.session_state.steps = steps
            st.session_state.accepted = accepted
        
        st.session_state.table = None
        
        progress_bar.progress(100)
        status_text.text("✅ Complete!")
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        # Success message
        st.success("✨ **LL(1) Parser Built Successfully!**")

elif build_btn:
    st.warning("⚠️ Please enter a grammar first!")


# =========================================================
# DISPLAY
# =========================================================

if st.session_state.grammar:

    grammar = st.session_state.grammar
    first = st.session_state.first
    follow = st.session_state.follow
    steps = st.session_state.steps
    
    st.markdown("---")
    
    # Display grammar info in cards
    st.markdown("### 📋 Grammar Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Productions</div>
                <div class="metric-value">{len(grammar.productions)}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Non-Terminals</div>
                <div class="metric-value">{len(grammar.get_nonterminals())}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Terminals</div>
                <div class="metric-value">{len([t for t in grammar.get_terminals() if t != '$'])}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Start Symbol</div>
                <div class="metric-value" style="font-size: 2rem;">{grammar.start_symbol}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Show grammar productions
    with st.expander("🔍 View Grammar Productions", expanded=False):
        for i, prod in enumerate(grammar.productions, 1):
            st.code(f"{i}. {prod.lhs} → {' '.join(prod.rhs)}", language="text")
    
    st.markdown("---")
    
    # Modern tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 FIRST & FOLLOW",
        "🔢 LR States",
        "📑 Parsing Table",
        "🗺️ DFA Graph",
        "▶️ Parsing Trace"
    ])

    # TAB 1: FIRST/FOLLOW
    with tab1:
        st.markdown("### 📊 FIRST & FOLLOW Sets")
        st.markdown("These sets are fundamental for parsing decisions.")
        
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🔷 FIRST Sets")
            st.markdown("Terminals that can appear first in derivations")
            df_first = make_set_table(first, grammar, "FIRST")
            st.dataframe(
                df_first,
                use_container_width=True,
                height=min(400, len(df_first) * 35 + 38)
            )

        with col2:
            st.markdown("#### 🔶 FOLLOW Sets")
            st.markdown("Terminals that can appear after a non-terminal")
            df_follow = make_set_table(follow, grammar, "FOLLOW")
            st.dataframe(
                df_follow,
                use_container_width=True,
                height=min(400, len(df_follow) * 35 + 38)
            )

    # TAB 2: LR STATES
    with tab2:
        if st.session_state.table:
            table = st.session_state.table
            
            st.markdown("### 🔢 LR Item Sets (Canonical Collection)")
            st.markdown(f"**Total States:** {len(table.states)}")
            
            # Search box for states
            search_state = st.number_input(
                "Jump to State:",
                min_value=0,
                max_value=len(table.states)-1,
                value=0,
                step=1
            )
            
            for i, state in enumerate(table.states):
                # Highlight searched state
                expanded = (i == search_state)
                
                with st.expander(f"**State I{i}** ({len(state)} items)", expanded=expanded):
                    items_text = []
                    
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

                        items_text.append(f"{lhs} → {' '.join(rhs_with_dot)}")
                    
                    st.code("\n".join(items_text), language="text")
        else:
            st.info("🔸 **LR States are only available for Bottom-Up (LR) parsers**")
            st.markdown("""
            LR parsers use a state machine to track parsing progress.
            Each state represents a set of items showing possible positions in productions.
            
            Switch to Bottom-Up mode to see LR states.
            """)

    # TAB 3: PARSING TABLE
    with tab3:
        if st.session_state.table:
            table = st.session_state.table
            
            st.markdown("### 📑 ACTION & GOTO Parsing Table")
            
            df = make_lr_table(table, grammar)
            
            # Add explanation
            with st.expander("ℹ️ How to Read This Table"):
                st.markdown("""
                **ACTION Columns** (Terminals):
                - `sN` = Shift and go to state N
                - `rN` = Reduce by production N
                - `acc` = Accept (parsing complete)
                - Empty = Error
                
                **GOTO Columns** (Non-terminals):
                - `N` = Go to state N after reduction
                - Empty = Not applicable
                """)
            
            st.dataframe(
                df,
                use_container_width=True,
                height=min(600, len(df) * 35 + 38)
            )
            
            # Download button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Table as CSV",
                data=csv,
                file_name="parsing_table.csv",
                mime="text/csv"
            )
        else:
            st.info("🔸 **Parsing Table is only available for Bottom-Up (LR) parsers**")
            st.markdown("""
            The parsing table guides the shift-reduce parser's decisions.
            It consists of ACTION and GOTO functions.
            
            Switch to Bottom-Up mode to see the parsing table.
            """)

    # TAB 4: DFA GRAPH
    with tab4:
        if st.session_state.table:
            table = st.session_state.table
            
            st.markdown("### 🗺️ DFA State Diagram")
            st.markdown(f"Visualizing transitions between {len(table.states)} states")
            
            with st.spinner("Generating DFA graph..."):
                try:
                    graph = build_dfa_graph(table.states, table.transitions)
                    st.graphviz_chart(graph, use_container_width=True)
                except Exception as e:
                    st.error(f"Error generating graph: {str(e)}")
                    st.info("💡 Make sure Graphviz is installed on your system")
            
            with st.expander("ℹ️ Understanding the DFA"):
                st.markdown("""
                **Nodes**: Each node represents an LR state (set of items)
                
                **Edges**: Transitions between states on grammar symbols
                - Edge label shows the symbol that triggers the transition
                
                **Purpose**: Shows the complete state machine used by the parser
                to make shift/reduce decisions.
                """)
        else:
            st.info("🔸 **DFA Graph is only available for Bottom-Up (LR) parsers**")
            st.markdown("""
            The DFA (Deterministic Finite Automaton) represents the state machine
            that drives LR parsing.
            
            Switch to Bottom-Up mode to see the DFA visualization.
            """)

    # TAB 5: PARSING TRACE
    with tab5:
        st.markdown("### ▶️ Step-by-Step Parsing Trace")
        
        if steps:
            # Parse result badge
            if st.session_state.accepted:
                st.markdown("""
                    <div style="text-align: center; margin: 2rem 0;">
                        <span class="status-badge status-success">
                            ✅ INPUT ACCEPTED
                        </span>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style="text-align: center; margin: 2rem 0;">
                        <span class="status-badge status-error">
                            ❌ INPUT REJECTED
                        </span>
                    </div>
                """, unsafe_allow_html=True)
            
            # Build trace dataframe
            rows = []
            for i, step in enumerate(steps):
                rows.append({
                    "Step": i + 1,
                    "Stack": step.stack,
                    "Input": step.input_remaining,
                    "Action": step.action
                })

            df_trace = pd.DataFrame(rows)
            
            # Display with custom styling
            st.dataframe(
                df_trace,
                use_container_width=True,
                height=min(500, len(df_trace) * 35 + 38)
            )
            
            st.markdown(f"**Total Steps:** {len(steps)}")
            
            # Download trace
            csv = df_trace.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Trace as CSV",
                data=csv,
                file_name="parsing_trace.csv",
                mime="text/csv"
            )
            
            # Explanation
            with st.expander("ℹ️ Understanding the Trace"):
                st.markdown("""
                **Stack**: Shows the parser's stack contents at each step
                
                **Input**: Remaining input to be parsed
                
                **Action**: What the parser does:
                - `Shift`: Push input symbol onto stack
                - `Reduce N`: Apply production rule N
                - `Match`: Symbol matches (for LL1)
                - `Accept`: Parsing complete successfully
                - `Error`: Parsing failed
                """)
        else:
            st.info("💡 **Enter an input string and click 'Build & Parse' to see the trace**")
            st.markdown("""
            The parsing trace shows how the parser processes your input step-by-step.
            
            Each row shows:
            - Current stack contents
            - Remaining input
            - Action taken by the parser
            """)

else:
    # Welcome screen when no grammar is loaded
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; padding: 3rem;">
            <h2>👈 Get Started</h2>
            <p style="font-size: 1.2rem; color: #64748b;">
                Enter a grammar in the sidebar and click <strong>"Build & Parse"</strong> to begin
            </p>
            <br>
            <p style="font-size: 1rem; color: #94a3b8;">
                Or select an example grammar from the dropdown to try it out!
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights
    st.markdown("### ✨ Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="custom-card">
                <h4>🔻 Bottom-Up Parsing</h4>
                <p>Support for SLR(1), LALR(1), and CLR(1) parsers with complete state machine visualization</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="custom-card">
                <h4>🔺 Top-Down Parsing</h4>
                <p>LL(1) parser with automatic conflict detection and detailed parsing traces</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="custom-card">
                <h4>📊 Rich Visualizations</h4>
                <p>Interactive DFA graphs, parsing tables, and step-by-step trace analysis</p>
            </div>
        """, unsafe_allow_html=True)


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")
st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #64748b;">
        <p style="font-size: 0.9rem;">
            Built with ❤️ for Compiler Design Education
        </p>
        <p style="font-size: 0.8rem; margin-top: 0.5rem;">
            🚀 Parser Visualizer | Educational Tool for LR & LL(1) Parsing
        </p>
    </div>
""", unsafe_allow_html=True)
