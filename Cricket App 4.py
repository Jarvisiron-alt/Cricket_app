import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from contextlib import contextmanager
from copy import deepcopy

PRIMARY_COLOR = "#2563eb"       
SECONDARY_COLOR = "#111827"      
ACCENT_COLOR = "#f97316"         

CARD_BACKGROUND = "#ffffff"
BACKGROUND_GRADIENT = "linear-gradient(135deg, #f5f7ff 0%, #ffffff 100%)"

SUBTLE_TEXT = "#4b5563"         
FONT_FAMILY = "'Inter', 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, sans-serif"


st.set_page_config(
    page_title="CricStream Tournament",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Combined CSS styling
st.markdown(
    f"""
    <style>
    :root {{
        --primary: {PRIMARY_COLOR};
        --secondary: {SECONDARY_COLOR};
        --accent: {ACCENT_COLOR};
        --muted: {SUBTLE_TEXT};
        --card-bg: {CARD_BACKGROUND};
    }}

    .main {{
        background: {BACKGROUND_GRADIENT};
    }}

    .main .block-container {{
        padding-top: 0.75rem;
        padding-bottom: 0.75rem;
        font-family: {FONT_FAMILY};
        color: var(--secondary);
        min-height: 100vh;
    }}

    body, .main, .block-container {{
        font-family: {FONT_FAMILY};
        color: var(--secondary);
    }}

    h1, h2, h3, h4, h5, h6 {{
        font-family: {FONT_FAMILY};
        color: var(--secondary);
        font-weight: 700;
    }}

    .top-metrics div[data-testid="stMetric"] {{
        background: linear-gradient(135deg, rgba(15,98,254,0.12), rgba(15,98,254,0.05));
        border-radius: 16px;
        padding: 22px 20px;
        border: 1px solid rgba(15, 98, 254, 0.12);
        box-shadow: 0 16px 32px rgba(15, 98, 254, 0.08);
        text-align: left;
    }}

    .top-metrics div[data-testid="stMetric"] label {{
        color: var(--muted) !important;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }}

    .top-metrics div[data-testid="stMetricValue"] {{
        color: var(--secondary) !important;
        font-size: 2rem;
        font-weight: 700;
    }}

    .top-metrics div[data-testid="stMetricDelta"] {{
        color: var(--accent) !important;
    }}

    div.stButton > button {{
        width: 100%;
        height: 48px;
        border-radius: 14px;
        font-size: 0.95rem;
        font-weight: 600;
        border: none;
        background: var(--secondary);
        color: #ffffff;
        box-shadow: 0 10px 20px rgba(31, 41, 55, 0.25);
        transition: all 0.2s ease-in-out;
    }}

    div.stButton > button:hover {{
        background: var(--primary);
        box-shadow: 0 16px 32px rgba(15, 98, 254, 0.20);
        transform: translateY(-2px);
    }}

    .live-pill {{
        color: #fff;
        background: linear-gradient(135deg, #ff4b4b, #ff8a65);
        border-radius: 999px;
        padding: 4px 14px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        animation: pulse 2s infinite;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }}

    .live-pill::before {{
        content: '';
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #fff;
    }}

    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.6; }}
    }}

    .score-card {{
        background: var(--card-bg);
        border-radius: 20px;
        padding: 20px 22px;
        border: 1px solid rgba(15, 98, 254, 0.12);
        box-shadow: 0 24px 40px rgba(15, 98, 254, 0.12);
        margin-bottom: 18px;
    }}

    .score-card__header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 18px;
    }}

    .score-card__title {{
        font-size: 1.35rem;
        font-weight: 700;
        color: var(--secondary);
    }}

    .score-card__teams {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
        gap: 16px;
        margin-bottom: 12px;
    }}

    .score-card__team {{
        background: rgba(15, 98, 254, 0.06);
        border-radius: 16px;
        padding: 16px 18px;
        display: flex;
        flex-direction: column;
        gap: 6px;
    }}

    .score-card__team-name {{
        font-size: 1rem;
        font-weight: 600;
        color: var(--secondary);
    }}

    .score-card__score {{
        font-size: 1.85rem;
        font-weight: 800;
        color: var(--primary);
        letter-spacing: 0.02em;
    }}

    .score-card__meta {{
        font-size: 0.9rem;
        color: var(--muted);
    }}

    .batsman-pill {{
        background: rgba(31, 41, 55, 0.06);
        padding: 10px 12px;
        border-radius: 14px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.95rem;
        color: var(--secondary);
    }}

    .batsman-pill strong {{
        font-weight: 700;
    }}

    .big-score {{
        font-size: 3rem;
        font-weight: 800;
        color: var(--primary);
        letter-spacing: 0.02em;
    }}

    .page-flex {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1rem;
        align-items: start;
    }}

    .summary-card {{
        background: var(--card-bg);
        border-radius: 18px;
        padding: 18px 20px;
        border: 1px solid rgba(15, 98, 254, 0.08);
        box-shadow: 0 18px 28px rgba(15, 98, 254, 0.08);
    }}

    .control-panel {{
        background: rgba(15, 98, 254, 0.04);
        border-radius: 18px;
        padding: 18px 20px;
        border: 1px solid rgba(15, 98, 254, 0.08);
        box-shadow: 0 12px 18px rgba(15, 98, 254, 0.06);
    }}

    .compact-section {{
        margin-bottom: 0.75rem;
    }}

    .compact-section:last-child {{
        margin-bottom: 0;
    }}

    [data-testid="stDataFrame"] table {{
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(0,0,0,0.05);
    }}

    [data-testid="stDataFrame"] tbody tr:hover {{
        background: rgba(15, 98, 254, 0.08) !important;
    }}

    [data-testid="stSidebar"] {{
        background: #ffffff;
    }}

    [data-testid="stSidebar"] > div:first-child {{
        background: linear-gradient(180deg, rgba(15, 98, 254, 0.12), transparent);
        border-right: 1px solid rgba(15, 98, 254, 0.12);
    }}

    .notification-banner {{
        margin-bottom: 1rem;
    }}

    .notification-card {{
        display: flex;
        gap: 14px;
        align-items: center;
        background: rgba(15, 98, 254, 0.08);
        border-left: 5px solid var(--primary);
        border-radius: 16px;
        padding: 14px 18px;
        margin-bottom: 0.75rem;
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--secondary);
        box-shadow: 0 20px 32px rgba(15, 98, 254, 0.12);
    }}

    .notification-card.success {{
        background: rgba(16, 185, 129, 0.12);
        border-left-color: rgba(16, 185, 129, 0.8);
    }}

    .notification-card.alert {{
        background: rgba(248, 113, 113, 0.18);
        border-left-color: rgba(248, 113, 113, 0.9);
    }}

    .notification-icon {{
        font-size: 1.5rem;
        line-height: 1;
    }}

    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# 2. DATABASE MANAGEMENT (OPTIMIZED)
# ==========================================
DB_PATH = 'tournament.db'

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize all database tables with migration support"""
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # Teams Table
        c.execute('''CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT UNIQUE, 
            short_name TEXT
        )''')
        
        # Players Table - Create or migrate
        c.execute('''CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT,
            team_name TEXT,
            UNIQUE(player_name, team_name)
        )''')
        
        # Check if new columns exist, if not add them
        c.execute("PRAGMA table_info(players)")
        columns = [col[1] for col in c.fetchall()]
        
        if 'runs' not in columns:
            c.execute("ALTER TABLE players ADD COLUMN runs INTEGER DEFAULT 0")
        if 'balls' not in columns:
            c.execute("ALTER TABLE players ADD COLUMN balls INTEGER DEFAULT 0")
        if 'fours' not in columns:
            c.execute("ALTER TABLE players ADD COLUMN fours INTEGER DEFAULT 0")
        if 'sixes' not in columns:
            c.execute("ALTER TABLE players ADD COLUMN sixes INTEGER DEFAULT 0")
        if 'out_status' not in columns:
            c.execute("ALTER TABLE players ADD COLUMN out_status TEXT DEFAULT 'Not Out'")
        
        # Matches Table
        c.execute('''CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_a TEXT,
            team_b TEXT,
            status TEXT DEFAULT 'Scheduled',
            team_a_runs INTEGER DEFAULT 0,
            team_a_wickets INTEGER DEFAULT 0,
            team_a_overs REAL DEFAULT 0.0,
            team_b_runs INTEGER DEFAULT 0,
            team_b_wickets INTEGER DEFAULT 0,
            team_b_overs REAL DEFAULT 0.0,
            batting_team TEXT,
            target INTEGER DEFAULT 0,
            winner TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        c.execute("PRAGMA table_info(matches)")
        match_columns = [col[1] for col in c.fetchall()]
        if 'first_innings_team' not in match_columns:
            c.execute("ALTER TABLE matches ADD COLUMN first_innings_team TEXT")
        if 'first_innings_runs' not in match_columns:
            c.execute("ALTER TABLE matches ADD COLUMN first_innings_runs INTEGER DEFAULT 0")
        if 'created_at' not in match_columns:
            c.execute("ALTER TABLE matches ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        if 'current_bowler_name' not in match_columns:
            c.execute("ALTER TABLE matches ADD COLUMN current_bowler_name TEXT")
        if 'current_bowler_runs' not in match_columns:
            c.execute("ALTER TABLE matches ADD COLUMN current_bowler_runs INTEGER DEFAULT 0")
        if 'current_bowler_wickets' not in match_columns:
            c.execute("ALTER TABLE matches ADD COLUMN current_bowler_wickets INTEGER DEFAULT 0")
        
        conn.commit()

def run_query(query, params=()):
    """Execute a query without returning results"""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute(query, params)
        conn.commit()


def reset_team_player_stats(team_name):
    """Reset player scorecard stats for a team."""
    run_query(
        """
        UPDATE players
        SET runs = 0, balls = 0, fours = 0, sixes = 0, out_status = 'Not Out'
        WHERE team_name = ?
        """,
        (team_name,),
    )


def reset_match_state(match_id, batting_team):
    """Clear match scoreboard and first-innings metadata."""
    run_query(
        """
        UPDATE matches
        SET team_a_runs = 0,
            team_a_wickets = 0,
            team_a_overs = 0.0,
            team_b_runs = 0,
            team_b_wickets = 0,
            team_b_overs = 0.0,
            batting_team = ?,
            target = 0,
            winner = NULL,
            first_innings_team = NULL,
            first_innings_runs = 0,
            current_bowler_name = NULL,
            current_bowler_runs = 0,
            current_bowler_wickets = 0
        WHERE id = ?
        """,
        (batting_team, match_id),
    )

@st.cache_data(ttl=2)
def get_data(query, params=()):
    """Fetch data with caching"""
    with get_db_connection() as conn:
        df = pd.read_sql(query, conn, params=params)
    return df
# ADD THIS NEW FUNCTION (no caching for live data)
def get_live_data(query, params=()):
    """Fetch live data WITHOUT caching - always fresh"""
    with get_db_connection() as conn:
        df = pd.read_sql(query, conn, params=params)
    return df


def get_match_number_map():
    """Map actual match IDs to sequential match numbers starting at 1."""
    order_df = get_data(
        "SELECT id FROM matches ORDER BY COALESCE(created_at, CURRENT_TIMESTAMP), id"
    )
    return {
        int(row.id): idx + 1
        for idx, row in enumerate(order_df.itertuples())
    }


def compute_team_extras(team_name, team_runs):
    """Calculate extras for a team (total runs minus batter contributions)."""
    if not team_name:
        return 0
    totals_df = get_live_data(
        "SELECT SUM(runs) AS total_runs FROM players WHERE team_name = ?",
        (team_name,),
    )
    if totals_df.empty:
        return safe_numeric_conversion(team_runs)
    player_runs = totals_df.iloc[0].get("total_runs")
    team_total = safe_numeric_conversion(team_runs)
    batter_total = safe_numeric_conversion(player_runs)
    return max(0, team_total - batter_total)

# Initialize DB on load
init_db()

# ==========================================
# 3. HELPER FUNCTIONS (OPTIMIZED)
# ==========================================
def safe_numeric_conversion(value, default=0, dtype=int):
    """Safely convert database values to numeric types"""
    try:
        return dtype(value)
    except (ValueError, TypeError):
        return dtype(default)


def format_overs(raw_overs):
    """Format overs stored as float-like values into conventional notation."""
    try:
        overs = float(raw_overs)
    except (TypeError, ValueError):
        return "0.0"

    over_int = int(overs)
    balls = int(round((overs - over_int) * 10))
    balls = max(0, min(5, balls))
    return f"{over_int}.{balls}"


def calculate_run_rate(runs, overs):
    """Compute run rate while avoiding division by zero."""
    try:
        runs_val = int(runs)
        overs_val = float(overs)
    except (TypeError, ValueError):
        return "—"

    over_int = int(overs_val)
    balls = int(round((overs_val - over_int) * 10))
    total_balls = over_int * 6 + balls
    if total_balls <= 0:
        return "—"
    run_rate = runs_val / (total_balls / 6)
    return f"{run_rate:.2f}"


def get_scalar(query, params=(), default=0):
    """Fetch a single scalar value from the database using cached reads."""
    df = get_data(query, params)
    if df.empty:
        return default
    value = df.iloc[0, 0]
    return value if value is not None else default

def calculate_new_overs(current_overs, is_extra):
    """Calculate updated overs count"""
    if is_extra:
        return current_overs
    
    over_int = int(current_overs)
    balls = round((current_overs - over_int) * 10)
    balls += 1
    
    return float(over_int + 1) if balls == 6 else over_int + (balls / 10.0)

def add_score(match_id, runs, is_wicket, is_extra, batting_team):
    """Add score to match with optimized logic"""
    # Fetch fresh match data
    match_data = get_data("SELECT * FROM matches WHERE id = ?", (match_id,)).iloc[0]
    
    # Determine prefix
    prefix = "team_a" if batting_team == match_data['team_a'] else "team_b"
    
    # Safe conversions
    current_runs = safe_numeric_conversion(match_data[f'{prefix}_runs'])
    current_wickets = safe_numeric_conversion(match_data[f'{prefix}_wickets'])
    current_overs = safe_numeric_conversion(match_data[f'{prefix}_overs'], dtype=float)
    
    # Calculate updates
    new_runs = current_runs + runs
    new_wickets = current_wickets + (1 if is_wicket else 0)
    new_overs = calculate_new_overs(current_overs, is_extra)
    
    # Update database
    query = f"""
        UPDATE matches 
        SET {prefix}_runs = ?, {prefix}_wickets = ?, {prefix}_overs = ? 
        WHERE id = ?
    """
    run_query(query, (new_runs, new_wickets, new_overs, match_id))

def update_player_stats(player_name, team_name, runs, is_wicket, is_extra):
    """Update individual player statistics"""
    # Fetch current stats
    player_data = get_data(
        "SELECT * FROM players WHERE player_name = ? AND team_name = ?",
        (player_name, team_name)
    )
    
    if player_data.empty:
        return
    
    player = player_data.iloc[0]
    
    # Calculate updates
    new_runs = safe_numeric_conversion(player['runs']) + runs
    new_balls = safe_numeric_conversion(player['balls']) + (0 if is_extra else 1)
    new_fours = safe_numeric_conversion(player['fours']) + (1 if runs == 4 else 0)
    new_sixes = safe_numeric_conversion(player['sixes']) + (1 if runs == 6 else 0)
    new_status = "Out" if is_wicket else player['out_status']
    
    # Update
    run_query("""
        UPDATE players 
        SET runs = ?, balls = ?, fours = ?, sixes = ?, out_status = ?
        WHERE player_name = ? AND team_name = ?
    """, (new_runs, new_balls, new_fours, new_sixes, new_status, player_name, team_name))


def render_live_match_card(match, match_number):
    """Present a live match with rich visuals"""
    team_a_rr = calculate_run_rate(match["team_a_runs"], match["team_a_overs"])
    team_b_rr = calculate_run_rate(match["team_b_runs"], match["team_b_overs"])
    team_a_extras = compute_team_extras(match["team_a"], match["team_a_runs"])
    team_b_extras = compute_team_extras(match["team_b"], match["team_b_runs"])
    target_val = safe_numeric_conversion(match.get("target"), default=0)
    batting_side = match.get("batting_team")
    innings_hint = "First innings in progress"
    if target_val > 0 and batting_side:
        prefix = "team_a" if batting_side == match["team_a"] else "team_b"
        current_runs = safe_numeric_conversion(match.get(f"{prefix}_runs"))
        runs_required = max(0, target_val - current_runs)
        first_innings_team = match.get("first_innings_team") or "First Innings"
        first_innings_total = safe_numeric_conversion(match.get("first_innings_runs"), default=0)
        innings_hint = f"Target: {target_val} (1st inns {first_innings_total} by {first_innings_team}) • Need {runs_required}"
    elif target_val > 0:
        innings_hint = f"Target: {target_val}"

    current_bowler_name = match.get("current_bowler_name")
    current_bowler_runs = safe_numeric_conversion(match.get("current_bowler_runs"))
    current_bowler_wickets = safe_numeric_conversion(match.get("current_bowler_wickets"))
    if current_bowler_name:
        bowler_line = f"{current_bowler_name} — {current_bowler_runs} runs • {current_bowler_wickets} wkts"
    else:
        bowler_line = "Awaiting selection"

    st.markdown(
        f"""
        <div class="score-card">
            <div class="score-card__header">
                <div>
                    <div class="score-card__title">{match['team_a']} vs {match['team_b']}</div>
                    <div class="score-card__meta">Match #{match_number} • {match['status']}</div>
                </div>
                <span class="live-pill">LIVE</span>
            </div>
            <div class="score-card__teams">
                <div class="score-card__team">
                    <span class="score-card__team-name">{match['team_a']}</span>
                    <span class="score-card__score">{match['team_a_runs']}/{match['team_a_wickets']}</span>
                    <span class="score-card__meta">Overs: {format_overs(match['team_a_overs'])} • RR {team_a_rr}</span>
                    <span class="score-card__meta">Extras: {team_a_extras}</span>
                </div>
                <div class="score-card__team">
                    <span class="score-card__team-name">{match['team_b']}</span>
                    <span class="score-card__score">{match['team_b_runs']}/{match['team_b_wickets']}</span>
                    <span class="score-card__meta">Overs: {format_overs(match['team_b_overs'])} • RR {team_b_rr}</span>
                    <span class="score-card__meta">Extras: {team_b_extras}</span>
                </div>
            </div>
            <div class="score-card__meta">
                Batting now: <strong>{match['batting_team'] or '—'}</strong> • {innings_hint}
            </div>
            <div class="score-card__meta">
                Current Bowler: <strong>{bowler_line}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    batting_team = match.get("batting_team")
    if batting_team:
        player_stats = get_live_data(
            """
                SELECT player_name, runs, balls, fours, sixes, out_status
                FROM players
                WHERE team_name = ? AND out_status = 'Not Out'
                ORDER BY runs DESC, balls ASC
            """,
            (batting_team,),
        )
        if not player_stats.empty:
            st.markdown("**🧍 Current Batters**")
            top_players = player_stats.head(2)
            batter_cols = st.columns(len(top_players))
            for (idx, (_, p_row)) in enumerate(top_players.iterrows()):
                with batter_cols[idx]:
                    st.markdown(
                        f"""
                        <div class="batsman-pill">
                            <strong>{p_row['player_name']}</strong>
                            <span>{p_row['runs']} ({p_row['balls']}) • 4s {p_row['fours']} • 6s {p_row['sixes']}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            st.caption("Waiting for the first partnership to start.")

# ==========================================
# 4. PAGE: PUBLIC DASHBOARD
# ==========================================
def render_dashboard():
    st.title("🏏 Tournament Dashboard")
    st.caption("Live pulse of the tournament with fresh data every refresh.")

    # Snapshot metrics
    st.markdown('<div class="top-metrics">', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        live_count = int(get_scalar("SELECT COUNT(*) FROM matches WHERE status = 'Live'"))
        st.metric("Live Matches", live_count)
    with m2:
        team_count = int(get_scalar("SELECT COUNT(*) FROM teams"))
        st.metric("Teams Registered", team_count)
    with m3:
        player_count = int(get_scalar("SELECT COUNT(*) FROM players"))
        st.metric("Players Active", player_count)
    with m4:
        completed_count = int(get_scalar("SELECT COUNT(*) FROM matches WHERE status = 'Completed'"))
        st.metric("Matches Completed", completed_count)
    st.markdown('</div>', unsafe_allow_html=True)

    _, refresh_col = st.columns([3, 1])
    with refresh_col:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    match_numbers = get_match_number_map()

    live_tab, results_tab, schedule_tab = st.tabs([
        "Live Matches",
        "Recent Results",
        "Upcoming Schedule",
    ])

    with live_tab:
        live_matches = get_live_data("SELECT * FROM matches WHERE status = 'Live'")
        if live_matches.empty:
            st.info("No matches are currently live.")
        else:
            live_matches = live_matches.sort_values(by=["id"])
            live_options = {
                f"Match #{match_numbers.get(int(row['id']), row['id'])} — {row['team_a']} vs {row['team_b']}": int(row["id"])
                for _, row in live_matches.iterrows()
            }
            live_label = st.selectbox(
                "Select live match",
                list(live_options.keys()),
                key="dashboard_live_select"
            )
            selected_live_id = live_options[live_label]
            live_row = live_matches[live_matches["id"] == selected_live_id].iloc[0]
            match_no = match_numbers.get(int(live_row["id"]), live_row["id"])
            render_live_match_card(live_row, match_no)

    with results_tab:
        completed = get_data(
            "SELECT * FROM matches WHERE status = 'Completed' ORDER BY COALESCE(created_at, CURRENT_TIMESTAMP) DESC, id DESC LIMIT 5"
        )
        if completed.empty:
            st.caption("Play a few matches to populate recent results.")
        else:
            completed = completed.reset_index(drop=True)
            result_options = {
                f"Match #{match_numbers.get(int(row['id']), row['id'])} — {row['team_a']} vs {row['team_b']}": int(row["id"])
                for _, row in completed.iterrows()
            }
            result_label = st.selectbox(
                "Select completed match",
                list(result_options.keys()),
                key="dashboard_result_select"
            )
            selected_result_id = result_options[result_label]
            result_row = completed[completed["id"] == selected_result_id].iloc[0]
            match_no = match_numbers.get(int(result_row["id"]), result_row["id"])
            st.markdown(
                f"""
                <div class="score-card" style="box-shadow: 0 14px 24px rgba(16,185,129,0.12); border-left: 6px solid rgba(16,185,129,0.8);">
                    <div class="score-card__title">Match #{match_no} — {result_row['team_a']} vs {result_row['team_b']}</div>
                    <div class="score-card__meta">
                        {result_row['team_a_runs']}/{result_row['team_a_wickets']} ({format_overs(result_row['team_a_overs'])} ov) •
                        {result_row['team_b_runs']}/{result_row['team_b_wickets']} ({format_overs(result_row['team_b_overs'])} ov)
                    </div>
                    <div class="score-card__meta">Winner: <strong>{result_row['winner'] or '—'}</strong></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with schedule_tab:
        scheduled = get_data("SELECT team_a, team_b, status FROM matches WHERE status = 'Scheduled'")
        if scheduled.empty:
            st.info("No upcoming matches scheduled.")
        else:
            schedule_view = scheduled.rename(columns={"team_a": "Team A", "team_b": "Team B", "status": "Status"})
            table_height = min(len(schedule_view) * 34 + 60, 260)
            st.dataframe(
                schedule_view,
                use_container_width=True,
                hide_index=True,
                height=table_height,
            )


def render_scorer():
    st.title("📝 Official Scorer Console — Cricket Sync")


    if "notifications" not in st.session_state:
        st.session_state.notifications = []
    if "active_notifications" not in st.session_state:
        st.session_state.active_notifications = []
    if "active_match_id" not in st.session_state:
        st.session_state.active_match_id = None
    if "log" not in st.session_state:
        st.session_state.log = []
    if "history" not in st.session_state:
        st.session_state.history = []
    if "match_strikers" not in st.session_state:
        st.session_state.match_strikers = {}  # keyed by match_id -> {"striker": name, "non_striker": name, "striker_team": team}
    if "match_bowlers" not in st.session_state:
        st.session_state.match_bowlers = {}
    if "pending_bowler" not in st.session_state:
        st.session_state.pending_bowler = {}
    if "match_innings_complete" not in st.session_state:
        st.session_state.match_innings_complete = {}
    if "match_bowling_figures" not in st.session_state:
        st.session_state.match_bowling_figures = {}
    if "run_out_dialog" not in st.session_state:
        st.session_state.run_out_dialog = {}
    if "no_ball_dialog" not in st.session_state:
        st.session_state.no_ball_dialog = {}
    if "wicket_dialog" not in st.session_state:
        st.session_state.wicket_dialog = {}
    if "wicket_nbo_dialog" not in st.session_state:
        st.session_state.wicket_nbo_dialog = {}

    now_ts = datetime.now().timestamp()
    if st.session_state.notifications:
        for note in st.session_state.notifications:
            note_entry = {
                "message": note.get("message", ""),
                "icon": note.get("icon", "ℹ️"),
                "expiry": now_ts + note.get("duration", 10),
                "level": note.get("level", "info"),
            }
            st.session_state.active_notifications.append(note_entry)
        st.session_state.notifications = []

    st.session_state.active_notifications = [
        note for note in st.session_state.active_notifications
        if note.get("expiry", 0) > now_ts
    ]

    if st.session_state.active_notifications:
        cards_html = []
        for note in st.session_state.active_notifications:
            icon = note.get("icon", "ℹ️")
            message_html = note.get("message", "").replace("\n", "<br>")
            level = note.get("level", "info")
            extra_class = "success" if level == "success" else "alert" if level == "alert" else ""
            cards_html.append(
                f"<div class='notification-card {extra_class}'>"
                f"<span class='notification-icon'>{icon}</span>"
                f"<div>{message_html}</div>"
                "</div>"
            )
        st.markdown(
            "<div class='notification-banner'>" + "".join(cards_html) + "</div>",
            unsafe_allow_html=True,
        )

    # -----------------------------
    # Helpers: safe conversions
    # -----------------------------
    def safe_int(x):
        try:
            return int(x)
        except Exception:
            return 0

    def safe_float(x):
        try:
            return float(x)
        except Exception:
            return 0.0

    def queue_notification(message, icon="ℹ️", level="info", duration=10):
        st.session_state.notifications.append({
            "message": message,
            "icon": icon,
            "level": level,
            "duration": duration,
        })

    def clear_no_ball_state(match_id):
        st.session_state.no_ball_dialog.pop(match_id, None)
        for suffix in (
            f"no_ball_hit_{match_id}",
            f"no_ball_outcome_{match_id}",
            f"no_ball_running_runs_{match_id}",
            f"no_ball_custom_runs_{match_id}",
            f"no_ball_credit_mode_{match_id}",
        ):
            st.session_state.pop(suffix, None)

    def clear_wicket_state(match_id):
        st.session_state.wicket_dialog.pop(match_id, None)
        st.session_state.wicket_nbo_dialog.pop(match_id, None)
        for suffix in (
            f"wicket_type_{match_id}",
            f"nbo_runs_{match_id}",
            f"nbo_out_choice_{match_id}",
            f"wicket_nbo_runs_{match_id}",
        ):
            st.session_state.pop(suffix, None)

    # -----------------------------
    # DB helpers for player & match updates
    # -----------------------------
    def update_player_stats(player_name, team_name, runs_scored, is_wicket, is_extra, credit_batsman=True, dismissal_code=None):
        """Increment player stats in DB.
        credit_batsman=False => do not add runs to batsman (used for neutral run credits).
        is_extra=True => does not increment ball count (wide/no-ball)."""
        if not player_name:
            return

        # Determine increments
        ball_inc = 0 if is_extra else 1
        four_inc = 1 if credit_batsman and runs_scored == 4 else 0
        six_inc = 1 if credit_batsman and runs_scored == 6 else 0
        runs_inc = runs_scored if credit_batsman else 0

        params = []
        set_clauses = []
        if runs_inc:
            set_clauses.append("runs = runs + ?"); params.append(runs_inc)
        if ball_inc:
            set_clauses.append("balls = balls + ?"); params.append(ball_inc)
        if four_inc:
            set_clauses.append("fours = fours + ?"); params.append(four_inc)
        if six_inc:
            set_clauses.append("sixes = sixes + ?"); params.append(six_inc)

        if set_clauses:
            query = f"UPDATE players SET {', '.join(set_clauses)} WHERE player_name = ? AND team_name = ?"
            params.extend([player_name, team_name])
            run_query(query, tuple(params))

        if is_wicket:
            status_text = "Out"
            if dismissal_code:
                status_text = f"Out ({dismissal_code})"
            run_query(
                "UPDATE players SET out_status = ? WHERE player_name = ? AND team_name = ?",
                (status_text, player_name, team_name),
            )

    def get_match_prefix(team_name, match_row):
        return "team_a" if team_name == match_row["team_a"] else "team_b"

    def update_bowling_figures(match_id, fielding_team, bowler_name, runs_scored, is_wicket, is_extra, credit_batsman):
        """Track bowling stats per match for current innings."""
        if not bowler_name:
            return
        figures = st.session_state.match_bowling_figures.setdefault(match_id, {})
        entry = figures.setdefault(
            bowler_name,
            {"team": fielding_team, "runs": 0, "balls": 0, "wickets": 0},
        )
        runs_conceded = runs_scored
        if not credit_batsman and not is_extra:
            runs_conceded = 0
        entry["runs"] += runs_conceded
        if not is_extra:
            entry["balls"] += 1
        if is_wicket:
            entry["wickets"] += 1

        current_bowler = st.session_state.match_bowlers.get(match_id)
        if current_bowler == bowler_name:
            run_query(
                "UPDATE matches SET current_bowler_runs = ?, current_bowler_wickets = ? WHERE id = ?",
                (entry["runs"], entry["wickets"], match_id),
            )

    DISMISSAL_META = {
        "Bowled": ("Bowled", "B"),
        "Catch Out": ("Catch Out", "C"),
        "Run Out": ("Run Out", "R"),
        "No Ball Run Out": ("No Ball Run Out", "NBO"),
    }

    def resolve_dismissal_meta(dismissal_type, is_wicket):
        if dismissal_type in DISMISSAL_META:
            return DISMISSAL_META[dismissal_type]
        if dismissal_type:
            return dismissal_type, None
        if is_wicket:
            return "Wicket", None
        return None, None

    # -----------------------------
    # Snapshot / Undo
    # -----------------------------
    def snapshot_state(match_id, batting_team, action_text):
        """Save snapshot for undo (match + two players)"""
        match_row = get_live_data("SELECT * FROM matches WHERE id = ?", (match_id,)).iloc[0]
        prefix = get_match_prefix(batting_team, match_row)
        snap = {
            "match_id": match_id,
            "action": action_text,
            "log": list(st.session_state.log),
            "match_runs": safe_int(match_row[f"{prefix}_runs"]),
            "match_wickets": safe_int(match_row[f"{prefix}_wickets"]),
            "match_overs": safe_float(match_row[f"{prefix}_overs"]),
            "striker": st.session_state.match_strikers.get(match_id, {}).get("striker"),
            "non_striker": st.session_state.match_strikers.get(match_id, {}).get("non_striker"),
            "batting_team": batting_team,
            "current_bowler": st.session_state.match_bowlers.get(match_id),
            "pending_bowler": st.session_state.pending_bowler.get(match_id, False),
            "innings_complete": st.session_state.match_innings_complete.get(match_id, False),
        }
        snap["bowling_figures"] = deepcopy(st.session_state.match_bowling_figures.get(match_id, {}))
        for p in ("striker", "non_striker"):
            pname = snap.get(p)
            if pname:
                df = get_live_data(
                    "SELECT runs, balls, fours, sixes, out_status FROM players WHERE player_name = ? AND team_name = ?",
                    (pname, batting_team)
                )
                snap[f"{p}_stats"] = df.iloc[0].to_dict() if not df.empty else None
            else:
                snap[f"{p}_stats"] = None
        st.session_state.history.append(snap)

    def restore_snapshot():
        if not st.session_state.history:
            st.warning("Nothing to undo")
            return
        last = st.session_state.history.pop()
        match_id = last["match_id"]
        batting_team_snap = last.get("batting_team")
        match_row = get_live_data("SELECT * FROM matches WHERE id = ?", (match_id,)).iloc[0]
        prefix = get_match_prefix(batting_team_snap, match_row) if batting_team_snap else "team_a"
        run_query(f"UPDATE matches SET {prefix}_runs=?, {prefix}_wickets=?, {prefix}_overs=? WHERE id=?",
                  (last["match_runs"], last["match_wickets"], last["match_overs"], match_id))

        # restore players with team_name constraint
        for p in ("striker", "non_striker"):
            pname = last.get(p)
            pst = last.get(f"{p}_stats")
            if pname and pst:
                run_query("""
                    UPDATE players SET runs=?, balls=?, fours=?, sixes=?, out_status=? 
                    WHERE player_name=? AND team_name=?
                """, (safe_int(pst.get("runs", 0)), safe_int(pst.get("balls", 0)),
                      safe_int(pst.get("fours", 0)), safe_int(pst.get("sixes", 0)),
                      pst.get("out_status", "Not Out"), pname, batting_team_snap))
        st.session_state.log = last["log"]
        # restore striker/non-striker in session if snapshot had them
        if match_id not in st.session_state.match_strikers:
            st.session_state.match_strikers[match_id] = {"striker": None, "non_striker": None, "striker_team": last.get("batting_team")}
        st.session_state.match_strikers[match_id]["striker"] = last.get("striker")
        st.session_state.match_strikers[match_id]["non_striker"] = last.get("non_striker")

        if "match_bowling_figures" not in st.session_state:
            st.session_state.match_bowling_figures = {}
        st.session_state.match_bowling_figures[match_id] = last.get("bowling_figures", {})

        if "match_bowlers" not in st.session_state:
            st.session_state.match_bowlers = {}
        st.session_state.match_bowlers[match_id] = last.get("current_bowler")

        if "pending_bowler" not in st.session_state:
            st.session_state.pending_bowler = {}
        st.session_state.pending_bowler[match_id] = bool(last.get("pending_bowler", False))

        if "match_innings_complete" not in st.session_state:
            st.session_state.match_innings_complete = {}
        st.session_state.match_innings_complete[match_id] = bool(last.get("innings_complete", False))

        # Clear any open modals related to this match when undoing
        st.session_state.run_out_dialog.pop(match_id, None)
        st.session_state.no_ball_dialog.pop(match_id, None)
        st.session_state.wicket_dialog.pop(match_id, None)
        st.session_state.wicket_nbo_dialog.pop(match_id, None)

        st.success(f"Undone: {last['action']}")

    # -----------------------------
    # Core: apply delivery (updates match + player)
    # -----------------------------
    def apply_delivery(match_id, batting_team, striker_name, non_striker_name, runs_scored, is_wicket, is_extra, credit_batsman=True, dismissed_player=None, dismissal_type=None, batsman_runs=None):
        """Handles ball-by-ball update including overs, strike rotation and player updates."""
        display_label, dismissal_code = resolve_dismissal_meta(dismissal_type, is_wicket)

        parts = [f"{striker_name or 'Team'} → {runs_scored}"]
        if is_wicket:
            parts.append("W")
        if is_extra:
            parts.append("(extra)")
        if display_label:
            parts.append(f"[{display_label}]")
        action_text = " ".join(parts)

        dismissed_name = dismissed_player or (striker_name if is_wicket else None)
        striker_dismissed = bool(is_wicket and striker_name and dismissed_name == striker_name)
        snapshot_state(match_id, batting_team, action_text)

        st.session_state.setdefault("match_bowlers", {})
        st.session_state.setdefault("pending_bowler", {})

        credited_runs = 0
        if batsman_runs is not None:
            credited_runs = max(0, batsman_runs)
        elif credit_batsman and not is_extra:
            credited_runs = runs_scored

        if striker_name and credit_batsman:
            should_record = not is_extra or credited_runs > 0 or (is_wicket and striker_dismissed)
            if should_record:
                update_player_stats(
                    striker_name,
                    batting_team,
                    credited_runs,
                    is_wicket and striker_dismissed,
                    is_extra,
                    credit_batsman=True,
                    dismissal_code=dismissal_code if striker_dismissed else None,
                )
        elif striker_name and not credit_batsman and not is_extra:
            # ball counts but striker receives no additional runs
            update_player_stats(striker_name, batting_team, 0, False, False, credit_batsman=False)
            run_query("UPDATE players SET balls = balls + 1 WHERE player_name = ? AND team_name = ?", (striker_name, batting_team))
        # extras (wide/no-ball): do not credit batsman or balls (handled above)

        # Update match scoreboard
        row = get_data("SELECT * FROM matches WHERE id = ?", (match_id,)).iloc[0]
        prefix = get_match_prefix(batting_team, row)
        current_runs = safe_int(row[f"{prefix}_runs"])
        current_wickets = safe_int(row[f"{prefix}_wickets"])
        current_overs = safe_float(row[f"{prefix}_overs"])
        target_score = safe_int(row.get("target", 0))
        first_innings_team = row.get("first_innings_team")
        fielding_team = row["team_b"] if batting_team == row["team_a"] else row["team_a"]

        new_runs = current_runs + runs_scored
        new_wickets = current_wickets + (1 if is_wicket else 0)

        new_overs = current_overs
        over_completed = False
        balls_after = None
        # ball counting for legal deliveries (not wides/no-balls)
        if not is_extra:
            over_int = int(current_overs)
            balls_before = int(round((current_overs - over_int) * 10))
            balls_after = balls_before + 1
            if balls_after == 6:
                new_overs = float(over_int + 1)
                over_completed = True
            else:
                new_overs = over_int + (balls_after / 10.0)

        run_query(f"UPDATE matches SET {prefix}_runs=?, {prefix}_wickets=?, {prefix}_overs=? WHERE id=?",
                  (new_runs, new_wickets, new_overs, match_id))

        current_bowler = st.session_state.match_bowlers.get(match_id)
        update_bowling_figures(
            match_id,
            fielding_team,
            current_bowler,
            runs_scored,
            is_wicket,
            is_extra,
            credit_batsman,
        )

        # strike rotation: on odd runs for legal deliveries OR at end of over
        rotate = False
        if not is_extra:
            if credit_batsman and (runs_scored % 2 == 1):
                rotate = True
            if balls_after == 6:
                rotate = True  # end of over rotation

        # apply rotation if needed
        if rotate and match_id in st.session_state.match_strikers:
            s = st.session_state.match_strikers[match_id]["striker"]
            ns = st.session_state.match_strikers[match_id]["non_striker"]
            st.session_state.match_strikers[match_id]["striker"], st.session_state.match_strikers[match_id]["non_striker"] = ns, s

        match_completed = False
        innings_completed = False

        # handle wicket: mark out and bring next batsman (only if wicket on legal delivery)
        if is_wicket:
            label = display_label or "Wicket"
            if dismissed_name:
                latest_stats = get_live_data(
                    "SELECT runs, balls FROM players WHERE player_name = ? AND team_name = ?",
                    (dismissed_name, batting_team)
                )
                if not latest_stats.empty:
                    runs_final = safe_int(latest_stats.iloc[0]["runs"])
                    balls_final = safe_int(latest_stats.iloc[0]["balls"])
                    strike_rate = (runs_final / balls_final * 100) if balls_final else 0
                    queue_notification(
                        f"<strong>{label}!</strong> {dismissed_name} departs for {runs_final} ({balls_final}) • SR {strike_rate:.1f}",
                        icon="⚠️",
                        level="alert",
                    )
                else:
                    queue_notification(
                        f"<strong>{label}!</strong> {dismissed_name} is out.",
                        icon="⚠️",
                        level="alert",
                    )
                status_text = "Out"
                if dismissal_code:
                    status_text = f"Out ({dismissal_code})"
                run_query(
                    "UPDATE players SET out_status = ? WHERE player_name = ? AND team_name = ?",
                    (status_text, dismissed_name, batting_team),
                )

            striker_roles = st.session_state.match_strikers.get(match_id)
            dismissed_role = None
            if striker_roles:
                if dismissed_name == striker_roles.get("striker"):
                    dismissed_role = "striker"
                    striker_roles["striker"] = None
                elif dismissed_name == striker_roles.get("non_striker"):
                    dismissed_role = "non_striker"
                    striker_roles["non_striker"] = None

            bench_df = get_live_data(
                "SELECT player_name FROM players WHERE team_name = ? AND out_status NOT LIKE 'Out%'",
                (batting_team,),
            )
            bench = bench_df["player_name"].tolist() if not bench_df.empty else []

            if striker_roles:
                role_for_replacement = dismissed_role or "striker"
                if role_for_replacement == "non_striker":
                    current_striker = striker_roles.get("striker")
                    candidates = [p for p in bench if p != current_striker]
                    if candidates:
                        striker_roles["non_striker"] = candidates[0]
                    else:
                        striker_roles["non_striker"] = None
                else:
                    current_non = striker_roles.get("non_striker")
                    candidates = [p for p in bench if p != current_non]
                    if candidates:
                        striker_roles["striker"] = candidates[0]
                    else:
                        striker_roles["striker"] = None

        if target_score and new_runs >= target_score:
            queue_notification(
                f"<strong>{batting_team}</strong> chase down the target of {target_score}!",
                icon="🏆",
                level="success",
            )
            run_query("UPDATE matches SET status='Completed', winner=? WHERE id=?", (batting_team, match_id))
            st.session_state.pending_bowler[match_id] = False
            st.session_state.match_bowlers[match_id] = None
            run_query(
                "UPDATE matches SET current_bowler_name = NULL, current_bowler_runs = 0, current_bowler_wickets = 0 WHERE id = ?",
                (match_id,),
            )
            match_completed = True

        if over_completed and not match_completed:
            formatted_over = format_overs(new_overs)
            st.session_state.match_bowlers[match_id] = None
            st.session_state.pending_bowler[match_id] = True
            run_query(
                "UPDATE matches SET current_bowler_name = NULL, current_bowler_runs = 0, current_bowler_wickets = 0 WHERE id = ?",
                (match_id,),
            )
            queue_notification(
                f"Over complete! {batting_team} {new_runs}/{new_wickets} after {formatted_over} overs. Assign a new bowler.",
                icon="✅",
                level="info",
            )

        if not match_completed:
            remaining_batters = get_live_data(
                "SELECT player_name FROM players WHERE team_name = ? AND out_status NOT LIKE 'Out%'",
                (batting_team,)
            )
            if len(remaining_batters) <= 1:
                stranded_name = None
                if not remaining_batters.empty:
                    stranded_name = remaining_batters.iloc[0]["player_name"]

                if target_score <= 0:
                    innings_completed = True
                    first_total = new_runs
                    chasing_team = row["team_b"] if batting_team == row["team_a"] else row["team_a"]
                    target_runs = first_total + 1 if first_total >= 0 else 0
                    run_query(
                        """
                        UPDATE matches
                        SET batting_team = ?,
                            target = ?,
                            first_innings_team = ?,
                            first_innings_runs = ?,
                            status = 'Live'
                        WHERE id = ?
                        """,
                        (chasing_team, target_runs, batting_team, first_total, match_id),
                    )
                    st.session_state.match_strikers.pop(match_id, None)
                    st.session_state.match_bowlers[match_id] = None
                    st.session_state.pending_bowler[match_id] = True
                    run_query(
                        "UPDATE matches SET current_bowler_name = NULL, current_bowler_runs = 0, current_bowler_wickets = 0 WHERE id = ?",
                        (match_id,),
                    )
                    st.session_state.match_innings_complete[match_id] = False
                    st.session_state.match_bowling_figures[match_id] = {}
                    queue_notification(
                        f"End of innings! {batting_team} are all out for {first_total}. {chasing_team} need {target_runs} to win.",
                        icon="🎯",
                        level="info",
                    )
                    st.session_state.log.append(action_text)
                    st.cache_data.clear()
                    return

                innings_completed = True
                st.session_state.match_innings_complete[match_id] = True
                st.session_state.pending_bowler[match_id] = False
                st.session_state.match_bowlers[match_id] = None
                run_query(
                    "UPDATE matches SET current_bowler_name = NULL, current_bowler_runs = 0, current_bowler_wickets = 0 WHERE id = ?",
                    (match_id,),
                )
                if match_id in st.session_state.match_strikers:
                    st.session_state.match_strikers[match_id]["striker"] = None
                    st.session_state.match_strikers[match_id]["non_striker"] = stranded_name
                queue_notification(
                    f"<strong>{batting_team}</strong> innings complete — no batting partner remaining.",
                    icon="🛑",
                    level="info",
                )
                if target_score and new_runs < target_score:
                    defending_team = first_innings_team or (row["team_a"] if batting_team == row["team_b"] else row["team_a"])
                    run_query("UPDATE matches SET status='Completed', winner=? WHERE id=?", (defending_team, match_id))
                    queue_notification(
                        f"<strong>{defending_team}</strong> win — {batting_team} are bowled out.",
                        icon="🏆",
                        level="success",
                    )
                    match_completed = True

        # append commentary
        st.session_state.log.append(action_text)
        # ✅ ADD THIS LINE - Clear cache before rerun
        st.cache_data.clear()

        if match_completed or innings_completed:
            return

    # -----------------------------
    # Fetch live matches & select match (top part)
    # -----------------------------
    matches = get_data("SELECT * FROM matches WHERE status = 'Live'")
    if matches.empty:
        st.warning("No LIVE matches found. Ask Admin to start a match.")
        return

    match_numbers = get_match_number_map()
    match_options = {
        f"Match #{match_numbers.get(int(r['id']), r['id'])}: {r['team_a']} vs {r['team_b']}": r['id']
        for _, r in matches.iterrows()
    }
    selected_label = st.selectbox("Select Match", list(match_options.keys()))
    match_id = match_options[selected_label]

    if st.session_state.active_match_id != match_id:
        st.session_state.active_match_id = match_id
        st.session_state.log = []
        st.session_state.history = []
        st.session_state.notifications = []
        st.session_state.active_notifications = []
        st.session_state.match_strikers = {}
        st.session_state.match_bowlers = {}
        st.session_state.pending_bowler = {}
        st.session_state.match_innings_complete = {}
        st.session_state.match_bowling_figures = {}
        st.session_state.run_out_dialog = {}
        st.session_state.no_ball_dialog = {}
        st.session_state.wicket_dialog = {}
        st.session_state.wicket_nbo_dialog = {}

    match_row = get_live_data("SELECT * FROM matches WHERE id = ?", (match_id,)).iloc[0]
    batting_team = match_row["batting_team"]
    prefix = get_match_prefix(batting_team, match_row)
    fielding_team = match_row["team_b"] if batting_team == match_row["team_a"] else match_row["team_a"]

    stored_bowler = match_row.get("current_bowler_name")
    st.session_state.match_bowlers[match_id] = stored_bowler
    if match_id not in st.session_state.match_innings_complete:
        st.session_state.match_innings_complete[match_id] = False
    if match_id not in st.session_state.pending_bowler or not st.session_state.match_innings_complete[match_id]:
        st.session_state.pending_bowler[match_id] = stored_bowler is None
    if match_id not in st.session_state.match_bowling_figures:
        st.session_state.match_bowling_figures[match_id] = {}

    # -----------------------------
    # Ensure striker/non-striker set in session (initialize from players if not present)
    # -----------------------------
    if match_id not in st.session_state.match_strikers:
        p_df = get_live_data("SELECT player_name FROM players WHERE team_name = ? AND out_status NOT LIKE 'Out%'", (batting_team,))
        p_list = p_df["player_name"].tolist() if not p_df.empty else []
        # Instead of default first two players, allow user to select starting striker and non-striker
        if len(p_list) > 1:
            striker = st.selectbox("Select starting Striker", p_list, key=f"start_striker_{match_id}")
            non_striker_options = [p for p in p_list if p != striker]
            non_striker = st.selectbox("Select starting Non-Striker", non_striker_options, key=f"start_non_striker_{match_id}")
        elif len(p_list) == 1:
            striker = p_list[0]
            non_striker = None
        else:
            striker = None
            non_striker = None
        st.session_state.match_strikers[match_id] = {"striker": striker, "non_striker": non_striker, "striker_team": batting_team}
    striker = st.session_state.match_strikers[match_id]["striker"]
    non_striker = st.session_state.match_strikers[match_id]["non_striker"]

    # -----------------------------
    # SCOREBOARD + CONTROLS LAYOUT
    # -----------------------------
    pending_bowler = st.session_state.pending_bowler.get(match_id, False)
    allow_scoring = (
        not pending_bowler
        and bool(st.session_state.match_bowlers.get(match_id))
        and not st.session_state.match_innings_complete.get(match_id, False)
    )

    def batter_snapshot(player_name):
        if not player_name:
            return "—", "Awaiting partner"
        snapshot_df = get_live_data(
            "SELECT runs, balls, fours, sixes FROM players WHERE player_name = ? AND team_name = ?",
            (player_name, batting_team)
        )
        if snapshot_df.empty:
            return player_name, "Yet to bat"
        stats = snapshot_df.iloc[0]
        runs_val = safe_int(stats["runs"])
        balls_val = safe_int(stats["balls"])
        fours_val = safe_int(stats["fours"])
        sixes_val = safe_int(stats["sixes"])
        return (
            player_name,
            f"{runs_val} ({balls_val}) · 4s:{fours_val} · 6s:{sixes_val}",
        )

    batting_card = pd.DataFrame()
    if batting_team:
        batting_card = get_live_data(
            "SELECT player_name, runs, balls, fours, sixes, out_status FROM players WHERE team_name = ?",
            (batting_team,)
        )

    summary_col, control_col = st.columns([1.25, 1])

    with summary_col:
        runs_val = safe_int(match_row[f"{prefix}_runs"])
        wickets_val = safe_int(match_row[f"{prefix}_wickets"])
        overs_display = format_overs(match_row[f"{prefix}_overs"])
        run_rate_display = calculate_run_rate(match_row[f"{prefix}_runs"], match_row[f"{prefix}_overs"])
        bowler_display = st.session_state.match_bowlers.get(match_id) or "Awaiting selection"
        striker_name, striker_line = batter_snapshot(striker)
        non_name, non_line = batter_snapshot(non_striker)

        def add_active_marker(label, active_name):
            if not active_name or not label or label == "—":
                return label
            return label if label.endswith("*") else f"{label}*"

        striker_display = add_active_marker(striker_name, striker)
        non_display = add_active_marker(non_name, non_striker)

        sum_batter_runs = safe_int(batting_card["runs"].sum()) if not batting_card.empty else 0
        extras_val = max(0, runs_val - sum_batter_runs)

        summary_html = f"""
        <div class="summary-card compact-section">
            <div style="display:flex; justify-content:space-between; align-items:center; gap:1rem;">
                <div>
                    <div style="font-size:0.75rem; letter-spacing:0.08em; text-transform:uppercase; color: var(--muted);">Batting</div>
                    <div style="font-size:1.1rem; font-weight:600;">{batting_team or '—'}</div>
                </div>
                <div style="text-align:right;">
                    <div class="big-score">{runs_val}/{wickets_val}</div>
                    <div style="font-size:0.85rem; color: var(--muted);">Overs {overs_display}</div>
                </div>
            </div>
            <div style="display:grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap:0.5rem; margin-top:0.75rem;">
                <div class="batsman-pill"><strong>{striker_display}</strong><span>{striker_line}</span></div>
                <div class="batsman-pill"><strong>{non_display}</strong><span>{non_line}</span></div>
            </div>
            <div style="margin-top:0.75rem; background: rgba(15, 98, 254, 0.06); border-radius: 12px; padding: 0.6rem 0.75rem; display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:0.85rem; font-weight:600; color: var(--secondary);">Extras</span>
                <span style="font-size:0.95rem; font-weight:700; color: var(--primary);">{extras_val}</span>
            </div>
            <div style="margin-top:0.35rem; font-size:0.75rem; color: var(--muted); text-align:right;">Includes wides and no-balls</div>
            <div style="margin-top:0.75rem; display:flex; justify-content:space-between; font-size:0.85rem; color: var(--muted);">
                <span>Bowler: {bowler_display}</span>
                <span>Run Rate: {run_rate_display}</span>
            </div>
        </div>
        """
        st.markdown(summary_html, unsafe_allow_html=True)

        if st.session_state.match_innings_complete.get(match_id):
            st.markdown(
                "<div class='notification-card alert compact-section'><span class='notification-icon'>⏸️</span><div>Innings closed. Start the next innings or end the match to continue scoring.</div></div>",
                unsafe_allow_html=True,
            )

        target_val = safe_int(match_row.get("target", 0))
        if target_val:
            first_innings_team = match_row.get("first_innings_team") or "First Innings"
            runs_so_far = safe_int(match_row[f"{prefix}_runs"])
            runs_required = max(0, target_val - runs_so_far)
            first_innings_total = safe_int(match_row.get("first_innings_runs", 0))
            target_html = (
                f"<div class='notification-card success compact-section' style='margin-top:0;'>"
                f"<span class='notification-icon'>🎯</span>"
                f"<div><strong>Target:</strong> {target_val} runs (1st inns: {first_innings_total}) set by {first_innings_team}."
                f"<br><strong>Runs needed:</strong> {runs_required}</div>"
                "</div>"
            )
            st.markdown(target_html, unsafe_allow_html=True)

        bowling_figures = st.session_state.match_bowling_figures.get(match_id, {})
        bat_col, bowl_col = st.columns(2)

        with bat_col:
            st.markdown("**Batting Card**")
            if batting_card.empty:
                st.info("No players available for batting team.")
            else:
                display_card = batting_card.copy()
                display_card["strike_rate"] = display_card.apply(
                    lambda row: round((row["runs"] / row["balls"]) * 100, 1) if row["balls"] else 0.0,
                    axis=1,
                )
                active_batters = {p for p in (striker, non_striker) if p}
                if active_batters:
                    display_card["player_name"] = display_card["player_name"].map(
                        lambda name: f"{name}*" if name in active_batters and not str(name).endswith("*") else name
                    )
                display_card = display_card.rename(
                    columns={
                        "player_name": "Player",
                        "runs": "Runs",
                        "balls": "Balls",
                        "fours": "4s",
                        "sixes": "6s",
                        "out_status": "Status",
                        "strike_rate": "SR",
                    }
                )
                display_card = display_card[["Player", "Runs", "Balls", "4s", "6s", "SR", "Status"]]
                display_card["SR"] = display_card["SR"].map(
                    lambda val: f"{float(val):.1f}" if val is not None and not pd.isna(val) else "0.0"
                )
                table_height = min(len(display_card) * 32 + 52, 280)
                st.dataframe(
                    display_card,
                    use_container_width=True,
                    hide_index=True,
                    height=table_height,
                )

        with bowl_col:
            st.markdown(f"**Bowling Card — {fielding_team}**")
            if not bowling_figures:
                st.info("No bowling figures recorded yet.")
            else:
                bowl_rows = []
                for bowler_name, stats in bowling_figures.items():
                    balls_bowled = safe_int(stats.get("balls", 0))
                    overs_text = f"{balls_bowled // 6}.{balls_bowled % 6}"
                    runs_conceded = safe_int(stats.get("runs", 0))
                    wickets_taken = safe_int(stats.get("wickets", 0))
                    economy = (runs_conceded / (balls_bowled / 6)) if balls_bowled else 0.0
                    bowl_rows.append({
                        "Bowler": bowler_name,
                        "Overs": overs_text,
                        "Runs": runs_conceded,
                        "Wkts": wickets_taken,
                        "Econ": economy,
                        "_balls": balls_bowled,
                    })
                bowl_df = pd.DataFrame(bowl_rows)
                bowl_df = bowl_df.sort_values(
                    by=["Wkts", "Runs", "_balls"],
                    ascending=[False, True, True],
                ).reset_index(drop=True)
                bowl_df["Econ"] = bowl_df["Econ"].map(
                    lambda val: f"{float(val):.2f}" if val is not None and not pd.isna(val) else "0.00"
                )
                bowl_df = bowl_df.drop(columns=["_balls"])
                bowl_table_height = min(len(bowl_df) * 32 + 52, 280)
                st.dataframe(
                    bowl_df,
                    use_container_width=True,
                    hide_index=True,
                    height=bowl_table_height,
                )

    with control_col:
        st.markdown("### Match Controls")
        current_over_val = safe_float(match_row[f"{prefix}_overs"])
        current_bowler = st.session_state.match_bowlers.get(match_id)

        if pending_bowler:
            prompt_text = "Over complete. Please choose the next bowler."
            if current_over_val == 0.0:
                prompt_text = "Select the opening bowler to start the innings."
            st.warning(prompt_text)
            bowlers_df = get_data("SELECT player_name FROM players WHERE team_name = ?", (fielding_team,))
            bowlers = bowlers_df["player_name"].tolist() if not bowlers_df.empty else []
            if not bowlers:
                st.info(f"No player list available for {fielding_team}. Add players in the Admin panel.")
            else:
                default_index = 0
                if current_bowler and current_bowler in bowlers:
                    default_index = bowlers.index(current_bowler)
                bowler_choice = st.selectbox(
                    "Select Bowler",
                    bowlers,
                    index=min(default_index, len(bowlers) - 1),
                    key=f"bowler_select_{match_id}"
                )
                if st.button("Confirm Bowler", key=f"confirm_bowler_{match_id}", help="Lock in this bowler for the over"):
                    st.session_state.match_bowlers[match_id] = bowler_choice
                    st.session_state.pending_bowler[match_id] = False
                    run_query(
                        "UPDATE matches SET current_bowler_name = ?, current_bowler_runs = 0, current_bowler_wickets = 0 WHERE id = ?",
                        (bowler_choice, match_id),
                    )
                    queue_notification(
                        f"<strong>{bowler_choice}</strong> to bowl the next over for {fielding_team}.",
                        icon="🎯",
                        level="success",
                    )
                    st.rerun()
        else:
            if current_bowler:
                st.info(f"Current bowler: {current_bowler}")
                if st.button("Change Bowler", key=f"change_bowler_{match_id}", help="Switch to a different bowler"):
                    st.session_state.pending_bowler[match_id] = True
                    st.session_state.match_bowlers[match_id] = None
                    run_query(
                        "UPDATE matches SET current_bowler_name = NULL, current_bowler_runs = 0, current_bowler_wickets = 0 WHERE id = ?",
                        (match_id,),
                    )
                    queue_notification(
                        "Bowling change requested. Select the new bowler before continuing.",
                        icon="🔄",
                        level="info",
                    )
                    st.rerun()
            else:
                st.warning("Assign a bowler to begin scoring.")

        st.markdown("#### Ball-by-ball Controls")
        st.markdown(
            """
            <style>
            .ball-control div.stButton>button {
                background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%) !important;
                color: #ffffff !important;
                border: 1px solid rgba(255, 255, 255, 0.35) !important;
                border-radius: 18px !important;
                font-weight: 600 !important;
                font-size: 0.98rem !important;
                letter-spacing: 0.03em !important;
                padding: 0.8rem 0.4rem !important;
                min-height: 58px !important;
                box-shadow: 0 16px 32px rgba(37, 99, 235, 0.3) !important;
                transition: transform 0.18s ease-in-out, box-shadow 0.18s ease-in-out, filter 0.18s ease-in-out !important;
                text-transform: uppercase !important;
                position: relative;
                overflow: hidden;
            }
            .ball-control div.stButton>button:hover {
                filter: brightness(1.1);
                box-shadow: 0 26px 40px rgba(37, 99, 235, 0.42);
                transform: translateY(-4px);
            }
            .ball-control div.stButton>button::after {
                content: "";
                position: absolute;
                inset: 0;
                background: linear-gradient(135deg, rgba(255,255,255,0.18), rgba(255,255,255,0));
                opacity: 0.3;
                transition: opacity 0.18s ease-in-out;
            }
            .ball-control div.stButton>button:hover::after {
                opacity: 0.55;
            }
            .ball-control div.stButton>button:focus-visible {
                outline: none !important;
                box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.9), 0 0 0 7px rgba(37, 99, 235, 0.55) !important;
            }
            .ball-control div.stButton {
                margin-bottom: 0.55rem;
            }
            .ball-control {
                padding: 0.4rem 0.2rem 0.5rem;
            }
            .ball-control .stColumn {
                display: flex;
                justify-content: center;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        def do_delivery(runs=0, wicket=False, extra=False, credit_batsman=True, dismissed_player=None, dismissal_type=None, batsman_runs=None):
            if st.session_state.match_innings_complete.get(match_id, False):
                queue_notification(
                    "Innings already completed. Swap sides or end the match before logging more deliveries.",
                    icon="🚫",
                    level="alert",
                )
                st.warning("This innings has finished. No further deliveries can be recorded.")
                return
            if st.session_state.pending_bowler.get(match_id, False) or not st.session_state.match_bowlers.get(match_id):
                queue_notification(
                    "Select a bowler before recording deliveries.",
                    icon="⛔",
                    level="alert",
                )
                st.warning("Assign a bowler to enable scoring controls.")
                return
            apply_delivery(
                match_id,
                batting_team,
                st.session_state.match_strikers[match_id]["striker"],
                st.session_state.match_strikers[match_id]["non_striker"],
                runs,
                wicket,
                extra,
                credit_batsman,
                dismissed_player=dismissed_player,
                dismissal_type=dismissal_type,
                batsman_runs=batsman_runs,
            )
            st.rerun()

        def open_no_ball_dialog():
            st.session_state.no_ball_dialog[match_id] = True

        def open_wicket_dialog():
            st.session_state.wicket_dialog[match_id] = True

        def undo_last_delivery():
            restore_snapshot()
            st.rerun()

        button_rows = [
            [
                {
                    "label": "Dot Ball •",
                    "callback": lambda: do_delivery(0, False, False, True),
                    "help": "Dot ball – no runs scored",
                    "respect_lock": True,
                },
                {
                    "label": "1 Run",
                    "callback": lambda: do_delivery(1, False, False, True),
                    "help": "Add 1 run to striker",
                    "respect_lock": True,
                },
                {
                    "label": "2 Runs",
                    "callback": lambda: do_delivery(2, False, False, True),
                    "help": "Add 2 runs to striker",
                    "respect_lock": True,
                },
                {
                    "label": "3 Runs",
                    "callback": lambda: do_delivery(3, False, False, True),
                    "help": "Add 3 runs to striker",
                    "respect_lock": True,
                },
                {
                    "label": "Four 4️⃣",
                    "callback": lambda: do_delivery(4, False, False, True),
                    "help": "Record a boundary four",
                    "respect_lock": True,
                },
            ],
            [
                {
                    "label": "Six 6️⃣",
                    "callback": lambda: do_delivery(6, False, False, True),
                    "help": "Record a six",
                    "respect_lock": True,
                },
                {
                    "label": "Wide +1",
                    "callback": lambda: do_delivery(1, False, True, False),
                    "help": "Add a wide – 1 extra run",
                    "respect_lock": True,
                },
                {
                    "label": "No Ball ⚡",
                    "callback": open_no_ball_dialog,
                    "help": "Open quick no-ball options",
                    "respect_lock": True,
                },
                {
                    "label": "Wicket ❌",
                    "callback": open_wicket_dialog,
                    "help": "Log a wicket dismissal",
                    "respect_lock": True,
                },
                {
                    "label": "Undo ↩️",
                    "callback": undo_last_delivery,
                    "help": "Restore the previous delivery",
                    "respect_lock": False,
                },
            ],
        ]

        st.markdown('<div class="ball-control">', unsafe_allow_html=True)
        for row in button_rows:
            columns = st.columns(len(row))
            for col, spec in zip(columns, row):
                disabled = (not allow_scoring) if spec.get("respect_lock", True) else False
                if col.button(spec["label"], disabled=disabled, help=spec["help"]):
                    spec["callback"]()
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.no_ball_dialog.get(match_id):
            no_ball_container = st.container()
            with no_ball_container:
                st.markdown("### No Ball Outcome")
                st.caption("Pick a quick result or use the custom panel for edge cases.")

                quick_options = [
                    ("Missed • 1 extra", 0, False, "miss"),
                    ("Hit +1", 1, True, "plus1"),
                    ("Hit +2", 2, True, "plus2"),
                    ("Boundary 4", 4, True, "four"),
                    ("Six 6️⃣", 6, True, "six"),
                ]

                quick_cols = st.columns(3)
                for idx, (label, bat_runs, credit_flag, key_suffix) in enumerate(quick_options):
                    target_col = quick_cols[idx % len(quick_cols)]
                    if target_col.button(label, key=f"nb_quick_{key_suffix}_{match_id}", help=label):
                        clear_no_ball_state(match_id)
                        total_runs = 1 + bat_runs
                        do_delivery(
                            total_runs,
                            False,
                            True,
                            credit_flag,
                            dismissal_type="No Ball",
                            batsman_runs=bat_runs if credit_flag else 0,
                        )

                st.markdown("---")
                st.markdown("**Custom combination**")
                custom_cols = st.columns(2)
                custom_runs = int(
                    custom_cols[0].number_input(
                        "Runs completed",
                        min_value=0,
                        max_value=10,
                        step=1,
                        key=f"no_ball_custom_runs_{match_id}",
                    )
                )
                credit_choice = custom_cols[1].radio(
                    "Credit to",
                    ["Extras", "Batsman"],
                    index=1,
                    key=f"no_ball_credit_mode_{match_id}",
                    horizontal=True,
                )

                custom_cols_action = st.columns([1, 1, 1])
                with custom_cols_action[0]:
                    if st.button("Apply", key=f"apply_no_ball_custom_{match_id}", help="Use the custom no-ball values"):
                        credit_flag = credit_choice == "Batsman"
                        clear_no_ball_state(match_id)
                        total_runs = 1 + custom_runs
                        do_delivery(
                            total_runs,
                            False,
                            True,
                            credit_flag,
                            dismissal_type="No Ball",
                            batsman_runs=custom_runs if credit_flag else 0,
                        )
                with custom_cols_action[1]:
                    if st.button("Reset", key=f"reset_no_ball_custom_{match_id}", help="Reset custom no-ball inputs"):
                        st.session_state[f"no_ball_custom_runs_{match_id}"] = 0
                        st.session_state[f"no_ball_credit_mode_{match_id}"] = "Batsman"
                        st.rerun()
                with custom_cols_action[2]:
                    if st.button("Close", key=f"close_no_ball_{match_id}", help="Dismiss the no-ball panel"):
                        clear_no_ball_state(match_id)
                        st.rerun()

        if st.session_state.wicket_dialog.get(match_id):
            wicket_container = st.container()
            with wicket_container:
                st.markdown("### Wicket Type")
                st.caption("Quick actions log the dismissal immediately.")

                striker_state = st.session_state.match_strikers.get(match_id, {})
                striker_name_now = striker_state.get("striker")
                non_striker_name_now = striker_state.get("non_striker")
                active_batter_available = bool(striker_name_now or non_striker_name_now)

                wicket_cols = st.columns(4)
                if wicket_cols[0].button(
                    "Bowled (B)",
                    key=f"wicket_bowled_{match_id}",
                    disabled=not striker_name_now,
                    help="Bowled dismissal for the striker",
                ):
                    if striker_name_now:
                        clear_wicket_state(match_id)
                        do_delivery(0, True, False, True, dismissal_type="Bowled")

                if wicket_cols[1].button(
                    "Catch out (C)",
                    key=f"wicket_catch_{match_id}",
                    disabled=not striker_name_now,
                    help="Caught dismissal for the striker",
                ):
                    if striker_name_now:
                        clear_wicket_state(match_id)
                        do_delivery(0, True, False, True, dismissal_type="Catch Out")

                if wicket_cols[2].button(
                    "Run out (R)",
                    key=f"wicket_run_out_{match_id}",
                    disabled=not active_batter_available,
                    help="Open run-out selection",
                ):
                    clear_wicket_state(match_id)
                    st.session_state.run_out_dialog[match_id] = True

                if wicket_cols[3].button(
                    "No ball out (NBO)",
                    key=f"wicket_nbo_{match_id}",
                    disabled=not striker_name_now,
                    help="No-ball run-out workflow",
                ):
                    st.session_state.wicket_nbo_dialog[match_id] = True

                if not striker_name_now:
                    st.info("Assign the on-strike batter before logging bowled or caught dismissals.")

                close_cols = st.columns([1, 3])
                if close_cols[0].button("Close", key=f"close_wicket_{match_id}", help="Hide wicket options"):
                    clear_wicket_state(match_id)
                    st.rerun()

                if st.session_state.wicket_nbo_dialog.get(match_id):
                    st.markdown("---")
                    st.markdown("**No ball run out**")
                    st.caption("Enter completed runs (excluding the no ball) then choose the dismissed batter.")
                    nbo_runs_val = int(
                        st.number_input(
                            "Runs completed",
                            min_value=0,
                            max_value=10,
                            step=1,
                            key=f"wicket_nbo_runs_{match_id}",
                        )
                    )
                    nbo_cols = st.columns(3)
                    has_option = False
                    if striker_name_now:
                        has_option = True
                        if nbo_cols[0].button(
                            f"{striker_name_now} (striker)",
                            key=f"wicket_nbo_striker_{match_id}",
                            help="Dismiss the striker",
                        ):
                            clear_wicket_state(match_id)
                            do_delivery(
                                1 + nbo_runs_val,
                                True,
                                True,
                                True,
                                dismissed_player=striker_name_now,
                                dismissal_type="No Ball Run Out",
                                batsman_runs=nbo_runs_val,
                            )
                    if non_striker_name_now:
                        has_option = True
                        if nbo_cols[1].button(
                            f"{non_striker_name_now} (non-striker)",
                            key=f"wicket_nbo_non_{match_id}",
                            help="Dismiss the non-striker",
                        ):
                            clear_wicket_state(match_id)
                            do_delivery(
                                1 + nbo_runs_val,
                                True,
                                True,
                                True,
                                dismissed_player=non_striker_name_now,
                                dismissal_type="No Ball Run Out",
                                batsman_runs=nbo_runs_val,
                            )
                    if nbo_cols[2].button("Cancel", key=f"cancel_nbo_panel_{match_id}", help="Close the NBO panel"):
                        st.session_state.wicket_nbo_dialog.pop(match_id, None)
                        st.session_state.pop(f"wicket_nbo_runs_{match_id}", None)
                        st.rerun()
                    if not has_option:
                        st.warning("No active batters available to dismiss.")

        if st.session_state.run_out_dialog.get(match_id):
            dialog_container = st.container()
            with dialog_container:
                st.markdown("### Run Out Dismissal")
                st.caption("Tap the batter who was dismissed.")
                strikers_state = st.session_state.match_strikers.get(match_id, {})
                striker_option = strikers_state.get("striker")
                non_striker_option = strikers_state.get("non_striker")

                options = []
                if striker_option:
                    options.append((f"{striker_option} (striker)", striker_option, "striker"))
                if non_striker_option:
                    options.append((f"{non_striker_option} (non-striker)", non_striker_option, "non"))

                if options:
                    run_out_cols = st.columns(len(options))
                    for idx, (label, player_name, suffix) in enumerate(options):
                        if run_out_cols[idx].button(label, key=f"run_out_pick_{suffix}_{match_id}", help=f"Dismiss {player_name}"):
                            st.session_state.run_out_dialog.pop(match_id, None)
                            do_delivery(
                                0,
                                True,
                                False,
                                True,
                                dismissed_player=player_name,
                                dismissal_type="Run Out",
                            )
                    if st.button("Cancel", key=f"cancel_run_out_{match_id}", help="Close run-out options"):
                        st.session_state.run_out_dialog.pop(match_id, None)
                        st.rerun()
                else:
                    st.info("No active batters available to dismiss.")
                    if st.button("Close", key=f"close_run_out_{match_id}", help="Dismiss the run-out dialog"):
                        st.session_state.run_out_dialog.pop(match_id, None)
                        st.rerun()

        with st.expander("Manage Batters", expanded=st.session_state.match_strikers[match_id]["striker"] is None):
            if st.session_state.match_strikers[match_id]["striker"] is None:
                st.warning("Set the next striker to continue scoring.")

            bench_df_all = get_live_data(
                "SELECT player_name FROM players WHERE team_name = ? AND out_status NOT LIKE 'Out%'",
                (batting_team,)
            )
            bench_all = bench_df_all["player_name"].tolist() if not bench_df_all.empty else []

            if bench_all:
                current_striker = st.session_state.match_strikers[match_id]["striker"]
                striker_index = bench_all.index(current_striker) if current_striker in bench_all else 0
                new_striker = st.selectbox(
                    "Assign Striker",
                    bench_all,
                    index=striker_index,
                    key=f"assign_striker_{match_id}"
                )
                if st.button("Set Striker", key=f"set_striker_direct_{match_id}"):
                    st.session_state.match_strikers[match_id]["striker"] = new_striker
                    st.rerun()

                current_non = st.session_state.match_strikers[match_id]["non_striker"]
                ns_index = bench_all.index(current_non) if current_non in bench_all else 0
                new_non = st.selectbox(
                    "Assign Non-Striker",
                    bench_all,
                    index=ns_index,
                    key=f"assign_non_striker_{match_id}"
                )
                if st.button("Set Non-Striker", key=f"set_non_striker_direct_{match_id}"):
                    current_striker_now = st.session_state.match_strikers[match_id]["striker"]
                    current_non_now = st.session_state.match_strikers[match_id]["non_striker"]
                    if new_non == current_striker_now and current_non_now:
                        st.session_state.match_strikers[match_id]["striker"] = current_non_now
                        st.session_state.match_strikers[match_id]["non_striker"] = current_striker_now
                    else:
                        st.session_state.match_strikers[match_id]["non_striker"] = new_non
                    st.rerun()
            else:
                st.info("No available batters to assign.")

        st.markdown("### Match Actions")
        action_cols = st.columns([1.5, 1])

        with action_cols[0]:
            st.markdown("**Bat First Selector**")
            bat_first_options = [match_row["team_a"], match_row["team_b"]]
            current_choice_index = bat_first_options.index(batting_team) if batting_team in bat_first_options else 0
            selected_bat_first = st.selectbox(
                "Choose batting team",
                bat_first_options,
                index=current_choice_index,
                key=f"bat_first_choice_{match_id}"
            )

            innings_started = any([
                safe_int(match_row["team_a_runs"]) > 0,
                safe_int(match_row["team_b_runs"]) > 0,
                safe_int(match_row["team_a_wickets"]) > 0,
                safe_int(match_row["team_b_wickets"]) > 0,
                safe_float(match_row["team_a_overs"]) > 0.0,
                safe_float(match_row["team_b_overs"]) > 0.0,
            ])

            if st.button("Set Bat First", key=f"set_bat_first_btn_{match_id}", disabled=innings_started):
                if selected_bat_first != batting_team:
                    reset_match_state(match_id, selected_bat_first)
                    st.session_state.match_strikers.pop(match_id, None)
                    st.session_state.match_bowlers[match_id] = None
                    st.session_state.pending_bowler[match_id] = True
                    st.session_state.match_innings_complete[match_id] = False
                    st.session_state.match_bowling_figures.pop(match_id, None)
                    queue_notification(
                        f"{selected_bat_first} will bat first.",
                        icon="🟢",
                        level="info",
                    )
                    st.cache_data.clear()
                    st.rerun()

            if innings_started:
                st.caption("Batting order locked because the innings has already started.")

        with action_cols[1]:
            st.markdown("**Close Match**")
            if st.button("🏁 End Match", use_container_width=True):
                target_val = safe_int(match_row.get("target", 0))
                if target_val and batting_team:
                    chasing_total = safe_int(match_row[f"{prefix}_runs"])
                    if chasing_total >= target_val:
                        winner = batting_team
                    else:
                        winner = match_row["team_a"] if batting_team == match_row["team_b"] else match_row["team_b"]
                else:
                    a = safe_int(match_row["team_a_runs"])
                    b = safe_int(match_row["team_b_runs"])
                    winner = match_row["team_a"] if a > b else match_row["team_b"] if b > a else "Draw"
                run_query("UPDATE matches SET status='Completed', winner=? WHERE id=?", (winner, match_id))
                queue_notification(
                    f"Match completed. <strong>{winner}</strong> declared winner.",
                    icon="🏁",
                    level="success",
                )
                st.session_state.pending_bowler[match_id] = False
                st.session_state.match_bowlers[match_id] = None
                run_query(
                    "UPDATE matches SET current_bowler_name = NULL, current_bowler_runs = 0, current_bowler_wickets = 0 WHERE id = ?",
                    (match_id,),
                )
                st.session_state.match_innings_complete[match_id] = False
                st.session_state.match_bowling_figures.pop(match_id, None)
                st.cache_data.clear()
                st.balloons()
                st.rerun()

# ==========================================
# 6. PAGE: ADMIN PANEL (OPTIMIZED)
# ==========================================
def render_admin():
    st.title("🛠️ Admin Control Panel")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Teams", "Matches", "Players", "Database", "History"])
    
    # TAB 1: MANAGE TEAMS
    with tab1:
        st.subheader("Add New Team")
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            new_team = st.text_input("Team Name", key="new_team")
        with col2:
            short_name = st.text_input("Short Code", key="short_name")
        with col3:
            if st.button("➕ Create", use_container_width=True):
                if new_team and short_name:
                    try:
                        run_query(
                            "INSERT INTO teams (name, short_name) VALUES (?, ?)",
                            (new_team, short_name)
                        )
                        st.success(f"Team {new_team} added!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Fill all fields!")
        
        st.subheader("Existing Teams")
        teams_df = get_data("SELECT id, name, short_name FROM teams")
        if not teams_df.empty:
            st.dataframe(teams_df, use_container_width=True, hide_index=True)
        else:
            st.info("No teams created yet.")

    # TAB 2: MANAGE MATCHES
    with tab2:
        st.subheader("Create New Match")
        teams = get_data("SELECT name FROM teams")
        
        if not teams.empty:
            team_list = teams['name'].tolist()
            
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                t1 = st.selectbox("Team A", team_list, key="t1")
            with col2:
                t2 = st.selectbox("Team B", team_list, index=min(1, len(team_list)-1), key="t2")
            with col3:
                if st.button("📅 Schedule", use_container_width=True):
                    if t1 == t2:
                        st.error("Teams must be different!")
                    else:
                        run_query("""
                            INSERT INTO matches (team_a, team_b, status, batting_team) 
                            VALUES (?, ?, 'Scheduled', ?)
                        """, (t1, t2, t1))
                        reset_team_player_stats(t1)
                        reset_team_player_stats(t2)
                        st.success("Match Scheduled!")
                        st.cache_data.clear()
                        st.rerun()
            
            st.divider()
            st.subheader("Manage Active Matches")
            matches = get_data("SELECT * FROM matches WHERE status != 'Completed' ORDER BY id DESC")
            match_numbers = get_match_number_map()
            
            if not matches.empty:
                for _, match in matches.iterrows():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        status_emoji = "🔴" if match['status'] == 'Live' else "⏳"
                        match_no = match_numbers.get(int(match['id']), match['id'])
                        st.write(f"{status_emoji} **Match {match_no}**: {match['team_a']} vs {match['team_b']}")
                    with col2:
                        if match['status'] == 'Scheduled':
                            if st.button(f"▶️ Go Live", key=f"live_{match['id']}", use_container_width=True):
                                reset_team_player_stats(match['team_a'])
                                reset_team_player_stats(match['team_b'])
                                reset_match_state(match['id'], match['team_a'])
                                run_query("UPDATE matches SET status = 'Live' WHERE id = ?", (match['id'],))
                                if 'match_strikers' in st.session_state:
                                    st.session_state.match_strikers.pop(match['id'], None)
                                if 'match_bowlers' in st.session_state:
                                    st.session_state.match_bowlers.pop(match['id'], None)
                                if 'pending_bowler' in st.session_state:
                                    st.session_state.pending_bowler.pop(match['id'], None)
                                if 'match_innings_complete' in st.session_state:
                                    st.session_state.match_innings_complete.pop(match['id'], None)
                                if 'match_bowling_figures' in st.session_state:
                                    st.session_state.match_bowling_figures.pop(match['id'], None)
                                st.success("Match is now LIVE!")
                                st.cache_data.clear()
                                st.rerun()
            else:
                st.info("No active matches.")
        else:
            st.warning("Create teams first.")

    # TAB 3: MANAGE PLAYERS
    with tab3:
        st.subheader("Add Player to Team")
        team_df = get_data("SELECT name FROM teams")
        
        if not team_df.empty:
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                selected_team = st.selectbox("Select Team", team_df['name'].tolist(), key="player_team")
            with col2:
                player_name = st.text_input("Player Name", key="player_name")
            with col3:
                if st.button("➕ Add", use_container_width=True):
                    if player_name:
                        try:
                            run_query(
                                "INSERT INTO players (player_name, team_name) VALUES (?, ?)",
                                (player_name, selected_team)
                            )
                            st.success(f"{player_name} added to {selected_team}")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.error("Enter player name!")
            
            st.divider()
            st.subheader("Players by Team")
            for team in team_df['name']:
                with st.expander(f"🏏 {team}"):
                    players = get_data(
                        "SELECT player_name, runs, balls, fours, sixes, out_status FROM players WHERE team_name = ?",
                        (team,)
                    )
                    if players.empty:
                        st.write("No players added yet.")
                    else:
                        st.dataframe(players, use_container_width=True, hide_index=True)
        else:
            st.warning("Create teams first.")

    # TAB 4: DATABASE TOOLS
    with tab4:
        st.subheader("Database Management")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Reset Database", use_container_width=True):
                run_query("DELETE FROM matches")
                run_query("DELETE FROM teams")
                run_query("DELETE FROM players")
                st.cache_data.clear()
                st.warning("Database Reset Complete!")
                st.rerun()
        
        with col2:
            if st.button("📦 Load Demo Data", use_container_width=True):
                # Clear existing
                run_query("DELETE FROM teams")
                run_query("DELETE FROM players")
                run_query("DELETE FROM matches")
                
                # Add teams
                teams = [
                    ('Mumbai Indians', 'MI'),
                    ('Chennai Super Kings', 'CSK'),
                    ('Royal Challengers', 'RCB')
                ]
                for team, short in teams:
                    run_query("INSERT INTO teams (name, short_name) VALUES (?, ?)", (team, short))
                
                # Add players
                mi_players = ['Rohit Sharma', 'Ishan Kishan', 'Suryakumar Yadav']
                csk_players = ['MS Dhoni', 'Ruturaj Gaikwad', 'Ravindra Jadeja']
                
                for player in mi_players:
                    run_query("INSERT INTO players (player_name, team_name) VALUES (?, ?)", 
                             (player, 'Mumbai Indians'))
                for player in csk_players:
                    run_query("INSERT INTO players (player_name, team_name) VALUES (?, ?)", 
                             (player, 'Chennai Super Kings'))
                
                # Add demo match
                run_query("""
                    INSERT INTO matches (team_a, team_b, status, team_a_runs, team_a_wickets, 
                                        team_a_overs, batting_team)
                    VALUES ('Mumbai Indians', 'Chennai Super Kings', 'Live', 145, 3, 15.2, 
                           'Mumbai Indians')
                """)
                
                st.cache_data.clear()
                st.success("Demo Data Loaded!")
                st.rerun()

    # TAB 5: MATCH HISTORY
    with tab5:
        st.subheader("Match History")
        history_df = get_data(
            """
            SELECT id, status, team_a, team_a_runs, team_a_wickets, team_a_overs,
                   team_b, team_b_runs, team_b_wickets, team_b_overs, target, winner, created_at
            FROM matches
            ORDER BY id DESC
            """
        )
        if history_df.empty:
            st.info("No matches recorded yet.")
        else:
            display_history = history_df.rename(
                columns={
                    "id": "Match ID",
                    "team_a": "Team A",
                    "team_a_runs": "A Runs",
                    "team_a_wickets": "A Wkts",
                    "team_a_overs": "A Overs",
                    "team_b": "Team B",
                    "team_b_runs": "B Runs",
                    "team_b_wickets": "B Wkts",
                    "team_b_overs": "B Overs",
                    "target": "Target",
                    "winner": "Winner",
                    "status": "Status",
                    "created_at": "Created",
                }
            )
            st.dataframe(display_history, use_container_width=True, hide_index=True)

# ==========================================
# 7. AUTHENTICATION & ROUTING
# ==========================================
def login_screen():
    """Handle user login"""
    st.sidebar.title("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login", use_container_width=True):
        credentials = {
            "admin": ("admin123", "admin"),
            "scorer": ("score123", "scorer")
        }
        
        if username in credentials and password == credentials[username][0]:
            st.session_state['user_role'] = credentials[username][1]
            st.sidebar.success(f"{username.title()} Logged In!")
            st.rerun()
        else:
            st.sidebar.error("Invalid Credentials!")

def main():
    """Main application router"""
    st.sidebar.title("🏏 CricStream")
    
    # Initialize user role
    if 'user_role' not in st.session_state:
        st.session_state['user_role'] = 'guest'

    # Define menu options based on role
    menu_options = {
        'guest': ["Dashboard", "Login"],
        'scorer': ["Dashboard", "Scorer Panel", "Logout"],
        'admin': ["Dashboard", "Admin Panel", "Scorer Panel", "Logout"]
    }
    
    options = menu_options.get(st.session_state['user_role'], ["Dashboard", "Login"])
    choice = st.sidebar.radio("Navigation", options)

    # Route to appropriate page
    if choice == "Dashboard":
        render_dashboard()
    
    elif choice == "Login":
        st.title("🔐 Staff Login")
        st.info("**Demo Credentials:**\n\n**Admin:** admin / admin123\n\n**Scorer:** scorer / score123")
        login_screen()
    
    elif choice == "Admin Panel":
        if st.session_state['user_role'] == 'admin':
            render_admin()
        else:
            st.error("⛔ Access Denied")
    
    elif choice == "Scorer Panel":
        if st.session_state['user_role'] in ['admin', 'scorer']:
            render_scorer()
        else:
            st.error("⛔ Access Denied")
    
    elif choice == "Logout":
        st.session_state['user_role'] = 'guest'
        st.cache_data.clear()
        st.rerun()

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("© CricStream 2025 • v2.0")

if __name__ == '__main__':
    main()