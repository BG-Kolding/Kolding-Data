import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from mplsoccer import VerticalPitch
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Crossing Analysis", layout="wide", page_icon="⚽")

st.markdown("""
<style>
    .main { background-color: #fbf9f4; }
    .block-container { padding-top: 1.5rem; }
    h1, h2, h3 { color: #4a2e19; }

    [data-testid="stMetric"] {
        background: #fbf9f4;
        border: 1px solid #4a2e19;
        border-radius: 10px;
        padding: 12px 16px;
    }
    [data-testid="stMetricLabel"] p {
        color: #4a2e19 !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] {
        color: #4a2e19 !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }

    section[data-testid="stSidebar"] { background-color: #fbf9f4; }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div { color: #4a2e19 !important; }
    .stMultiSelect [data-baseweb="tag"] { background: #b5cae3 !important; }

    thead tr th { background: #4a2e19 !important; color: #fbf9f4 !important; text-align: center !important; }
    tbody tr:nth-child(even) td { background: #ede8df !important; }
    tbody tr:nth-child(odd)  td { background: #fbf9f4 !important; }
    tbody td { color: #4a2e19 !important; text-align: center !important; }
    .stCaption, small { color: #7a6050 !important; }

    .zone-table thead tr th { background: #4a2e19 !important; color: #fbf9f4 !important; }
    .zone-table tbody td { color: #4a2e19 !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("https://raw.githubusercontent.com/BG-Kolding/Kolding-Data/refs/heads/main/Crossing_Analysis_df.csv")
    df.columns = df.columns.str.strip().str.lstrip('\ufeff')
    return df

df = load_data()
df['Date'] = pd.to_datetime(df['Date'])

ZONE_COLS   = ['EarlyCrossRight','EarlyCrossLeft','GoldenZoneRight','GoldenZoneLeft','ChipZoneRight','ChipZoneLeft']
POST_COLS   = ['NearPost','Center','FarPost']
ZONE_LABELS = {c: c.replace('Cross','Cross ').replace('Zone',' Zone') for c in ZONE_COLS}

# Zone groupings (combine L+R)
ZONE_GROUPS = {
    'Early Cross':  ['EarlyCrossRight', 'EarlyCrossLeft'],
    'Golden Zone':  ['GoldenZoneRight', 'GoldenZoneLeft'],
    'Chip Zone':    ['ChipZoneRight',   'ChipZoneLeft'],
}

CROSS_COL   = 'Cross'
CUTBACK_COL = 'Cutback'

COL_GOAL    = '#ee5454'
COL_XG      = '#f6ba00'
COL_FC      = '#4c94f6'
COL_NOTHING = 'silver'

# ── Sidebar ───────────────────────────────────────────────────────────────────
#st.sidebar.markdown("## ⚽ Crossing Analysis")
#st.sidebar.markdown("---")

teams = sorted(df['Team'].unique())

st.sidebar.markdown("### Team / Role")
selected_team = st.sidebar.selectbox("Select Team", ["All Teams"] + teams, 10)
role = st.sidebar.radio("View as", ["Crosses Made", "Crosses Conceded"])

st.sidebar.markdown("---")
st.sidebar.markdown("### Action Type")
show_crosses  = st.sidebar.checkbox("Crosses",  value=True)
show_cutbacks = st.sidebar.checkbox("Cutbacks", value=True)

if show_crosses and show_cutbacks:
    type_event = 'Crosses & Cutbacks'
elif show_crosses:
    type_event = 'Crosses'
elif show_cutbacks:
    type_event = 'Cutbacks'
else:
    type_event = 'Actions'

st.sidebar.markdown("---")
st.sidebar.markdown("### Zone Filter")
selected_zones = st.sidebar.multiselect("Zones (blank = all)", options=ZONE_COLS,
                                        format_func=lambda x: ZONE_LABELS[x])

st.sidebar.markdown("### Post Area Filter")
selected_posts = st.sidebar.multiselect("Post Areas (blank = all)", options=POST_COLS)

st.sidebar.markdown("---")
st.sidebar.markdown("### Date Range")
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()
date_from = st.sidebar.date_input("From", value=min_date, min_value=min_date, max_value=max_date)
date_to   = st.sidebar.date_input("To",   value=max_date, min_value=min_date, max_value=max_date)
if date_from > date_to:
    st.sidebar.error("'From' date must be before 'To' date.")
    date_from, date_to = min_date, max_date
st.sidebar.caption(f"{(pd.Timestamp(date_to) - pd.Timestamp(date_from)).days + 1} days selected")

# ── Filter helpers ────────────────────────────────────────────────────────────
def apply_filters(df_in, team=None, role_col=None):
    filt = df_in.copy()
    # Date filter — global
    filt = filt[(filt['Date'] >= pd.Timestamp(date_from)) & (filt['Date'] <= pd.Timestamp(date_to))]
    mask = pd.Series(False, index=filt.index)
    if show_crosses:  mask |= (filt[CROSS_COL]   == 1)
    if show_cutbacks: mask |= (filt[CUTBACK_COL] == 1)
    filt = filt[mask]
    if selected_zones:
        filt = filt[filt[selected_zones].any(axis=1)]
    if selected_posts:
        filt = filt[filt[selected_posts].any(axis=1)]
    if team and team != "All Teams" and role_col:
        filt = filt[filt[role_col] == team]
    return filt

filt_league = apply_filters(df)
role_col    = 'Team' if role == "Crosses Made" else 'Opponent'
team_filt   = apply_filters(df, team=selected_team, role_col=role_col)

def assign_color(row):
    if row['Goal_within_5_seconds'] == 1:   return COL_GOAL
    elif row['xG_within_5_seconds'] > 0:    return COL_XG
    elif row['outcome'] == 1:               return COL_FC
    else:                                   return COL_NOTHING

# ── Header + metrics ──────────────────────────────────────────────────────────
header_team = selected_team if selected_team != "All Teams" else "All Teams"
role_str    = "Made" if role == "Crosses Made" else "Conceded"
st.markdown(f"## {header_team} — {type_event} {role_str}")

n     = len(team_filt)
goals = int(team_filt['Goal_within_5_seconds'].sum()) if n else 0
xg    = team_filt['xG_within_5_seconds'].sum() if n else 0.0
fc    = int(team_filt['outcome'].sum()) if n else 0
eff   = int(((team_filt['outcome'] == 1) | (team_filt['xG_within_5_seconds'] > 0)).sum()) if n else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Actions",     f"{n}")
c2.metric("First Contact",     f"{fc}  ({fc/n*100:.0f}%)" if n else "0")
c3.metric("xG Generated",      f"{xg:.2f}")
c4.metric("Goals (within 5s)", f"{goals}")
c5.metric("Effective Rate",    f"{eff/n*100:.0f}%" if n else "0%")

st.markdown("---")

# ── Pitch visualisation ───────────────────────────────────────────────────────
if n == 0:
    st.warning("No actions match the current filters.")
else:
    team_filt = team_filt.copy()
    team_filt['_color'] = team_filt.apply(assign_color, axis=1)

    pitch = VerticalPitch(pitch_type='opta', pitch_color='#fbf9f4',
                          line_color='#4A2E19', line_zorder=1, half=True)
    fig, axs = pitch.grid(endnote_height=0.045, endnote_space=0,
                          figheight=12, title_height=0.045, title_space=0,
                          axis=False, grid_height=0.86)
    fig.set_facecolor('#fbf9f4')

    for color, group in team_filt.groupby('_color', sort=False):
        pitch.lines(group['x'].values, group['y'].values,
                    group['endX'].values, group['endY'].values,
                    comet=True, alpha=0.45, lw=3,
                    color=color, ax=axs['pitch'])
        pitch.scatter(group['endX'].values, group['endY'].values,
                      ec='k', lw=0.5, s=35, c=color, zorder=3, ax=axs['pitch'])

    axs['title'].text(0.5, -0.4,
        f"{header_team} {type_event} {role_str} ({n})\n\n{date_from} - {date_to}",
        ha='center', va='bottom', fontsize=20, fontweight='bold',
        color='#4A2E19', transform=axs['title'].transAxes)

    n_goal = goals
    n_xg   = int((team_filt['xG_within_5_seconds'] > 0).sum()) - n_goal
    n_fc   = int(((team_filt['outcome'] == 1) & (team_filt['xG_within_5_seconds'] == 0)).sum())
    n_sil  = int(((team_filt['outcome'] == 0) & (team_filt['xG_within_5_seconds'] == 0)).sum())

    legend_patches = [
        mpatches.Patch(color=COL_GOAL,    label=f'Goal within 5s ({n_goal})'),
        mpatches.Patch(color=COL_XG,      label=f'Shot within 5s ({n_xg})'),
        mpatches.Patch(color=COL_FC,      label=f'1st contact, no shot ({n_fc})'),
        mpatches.Patch(color=COL_NOTHING, label=f'Incomplete ({n_sil})'),
    ]
    axs['endnote'].legend(handles=legend_patches, loc='center', ncol=4,
                          fontsize=13, frameon=False, labelcolor='#4A2E19')
    axs['endnote'].axis('off')

    # ── Top 3 deliverers per side, annotated in bottom corners of pitch ─────────
    # opta coords: y > 50 = left side, y < 50 = right side
    def top_deliverers(df_side, top_n=3):
        if df_side.empty or 'playerName' not in df_side.columns:
            return []
        counts = df_side['playerName'].value_counts()
        return [(name, cnt) for name, cnt in counts.head(top_n).items()]

    left_df   = team_filt[team_filt['y'] >  50]
    right_df  = team_filt[team_filt['y'] <= 50]
    left_top  = top_deliverers(left_df)
    right_top = top_deliverers(right_df)

    def shorten(name):
        parts = name.strip().split()
        return f"{parts[0][0]}. {' '.join(parts[1:])}" if len(parts) > 1 else name

    def build_label(players, side_label):
        if not players:
            return ''
        lines = [f"{side_label}"]
        for i, (name, cnt) in enumerate(players, 1):
            lines.append(f"{shorten(name)} ({cnt})")
        return "\n".join(lines)

    left_label  = build_label(left_top,  f'{len(left_df)} TOTAL')
    right_label = build_label(right_top, f'{len(right_df)} TOTAL')

    text_kw = dict(fontsize=12, color='#4A2E19', va='bottom',
                   fontfamily='monospace',
                   bbox=dict(boxstyle='round,pad=0.4', fc='#fbf9f4',
                             ec='#4A2E19', alpha=0.80, lw=0.9))

    ax_pitch = axs['pitch']
    # In vertical half-pitch (opta): bottom of visible area is around x=50,
    # y=0 is right touchline, y=100 is left touchline
    if left_label:
        ax_pitch.text(97, 51, left_label, ha='left',  **text_kw)
    if right_label:
        ax_pitch.text(3,  51, right_label, ha='right', **text_kw)

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# ── Zone × Post breakdown table ───────────────────────────────────────────────
st.markdown("---")
st.markdown("## 🗺️ Zone × Post Breakdown")

# Determine which team column to use for zone breakdown (respects Made/Conceded)
zp_role_col = 'Team' if role == "Crosses Made" else 'Opponent'

if selected_team != "All Teams":
    st.caption(
        f"Showing **{header_team}** ({role_str.lower()}) vs league average. "
        f"Date range and team role applied. "
        f"Rank = {header_team}'s position among all teams for that metric (1 = best)."
    )
else:
    st.caption("No team selected — showing league-wide totals for the selected date range. Select a team in the sidebar to see their stats and rankings.")

# Build base dataset: all crosses+cutbacks, date-filtered, no other filters
zone_base_mask = (df[CROSS_COL] == 1) | (df[CUTBACK_COL] == 1)
zone_base = df[zone_base_mask].copy()
zone_base = zone_base[(zone_base['Date'] >= pd.Timestamp(date_from)) & (zone_base['Date'] <= pd.Timestamp(date_to))]

zone_order   = ['Early Cross', 'Golden Zone', 'Chip Zone']
post_order   = ['NearPost', 'Center', 'FarPost']
post_display = {'NearPost': 'Near Post', 'Center': 'Center', 'FarPost': 'Far Post'}

def get_zone_group(row):
    for group_name, cols in ZONE_GROUPS.items():
        if any(row.get(c, 0) == 1 for c in cols):
            return group_name
    return None

def get_post(row):
    for p in POST_COLS:
        if row.get(p, 0) == 1:
            return p
    return None

zone_base['_zone_group'] = zone_base.apply(get_zone_group, axis=1)
zone_base['_post']       = zone_base.apply(get_post, axis=1)
zp = zone_base.dropna(subset=['_zone_group', '_post']).copy()

# ── Build per-team stats for every (team, zone, post) combination ─────────────
def zp_stats_for(subset, zone_total_n):
    cnt    = len(subset)
    xg_sum = subset['xG_within_5_seconds'].sum()
    gls    = int(subset['Goal_within_5_seconds'].sum())
    fc     = int(subset['outcome'].sum())
    eff    = int(((subset['outcome'] == 1) | (subset['xG_within_5_seconds'] > 0)).sum())
    return {
        'Crosses':    cnt,
        '% of Zone':  round(cnt / zone_total_n * 100, 1) if zone_total_n else 0.0,
        'xG':         round(xg_sum, 2),
        'Goals':      gls,
        'FC %':       round(fc / cnt * 100, 1) if cnt else 0.0,
        'Eff %':      round(eff / cnt * 100, 1) if cnt else 0.0,
        'xG / Cross': round(xg_sum / cnt, 3) if cnt else 0.0,
    }

all_teams_list = sorted(zp[zp_role_col].unique())
n_teams = len(all_teams_list)

# Rank metrics: higher = better for xG, Goals, FC%, Eff%, xG/Cross
# For % of Zone: not ranked (it's a distribution choice, not a quality metric)
RANK_METRICS = ['xG', 'Goals', 'FC %', 'Eff %', 'xG / Cross']

for zone in zone_order:
    zp_zone = zp[zp['_zone_group'] == zone]

    # League totals for this zone (for the header count)
    league_zone_n = len(zp_zone)

    # Build per-team rows for ranking
    per_team_rows = []
    for team in all_teams_list:
        team_zone = zp_zone[zp_zone[zp_role_col] == team]
        team_zone_n = len(team_zone)
        for post in post_order:
            grp = team_zone[team_zone['_post'] == post]
            s   = zp_stats_for(grp, team_zone_n)
            s['_team'] = team
            s['_post'] = post
            per_team_rows.append(s)

    per_team_df = pd.DataFrame(per_team_rows)

    # Compute ranks per (post) for each ranked metric — rank descending (1=best)
    rank_df = per_team_df.copy()
    for post in post_order:
        post_mask = rank_df['_post'] == post
        for metric in RANK_METRICS:
            col_rank = f'_rank_{metric}_{post}'
            vals = rank_df.loc[post_mask, metric]
            rank_df.loc[post_mask, col_rank] = vals.rank(ascending=False, method='min').astype(int)

    # ── League totals row (for the table) ─────────────────────────────────────
    league_rows = []
    for post in post_order:
        grp = zp_zone[zp_zone['_post'] == post]
        s   = zp_stats_for(grp, league_zone_n)
        s['Post Area'] = post_display[post]
        league_rows.append(s)
    league_zone_df = pd.DataFrame(league_rows)
    league_zone_total = league_zone_df['Crosses'].sum()

    st.markdown(
        f"#### {zone}"
        f"  <span style='color:#7a6050; font-size:0.85rem; font-weight:400'>"
        f"(league: {league_zone_total} crosses)</span>",
        unsafe_allow_html=True
    )

    if selected_team == "All Teams":
        # ── No team selected: show plain league table ──────────────────────────
        display_df = league_zone_df[['Post Area','Crosses','% of Zone','xG','Goals','FC %','Eff %','xG / Cross']].copy()
        styled = (display_df.style
                  .format({'% of Zone': '{:.1f}%', 'xG': '{:.2f}',
                           'FC %': '{:.1f}%', 'Eff %': '{:.1f}%', 'xG / Cross': '{:.3f}'})
                  .background_gradient(subset=['% of Zone'], cmap='YlOrBr', vmin=0, vmax=60)
                  .background_gradient(subset=['xG / Cross'], cmap='YlGn',  vmin=0, vmax=0.12)
                  .set_properties(**{'text-align': 'center'}))
        st.dataframe(styled, use_container_width=True, hide_index=True)

    else:
        # ── Team selected: show team stats + rank vs league avg ────────────────
        team_zone_rows = rank_df[rank_df['_team'] == selected_team].copy()
        team_zone_n_total = team_zone_rows['Crosses'].sum()

        display_rows = []
        for post in post_order:
            team_row = team_zone_rows[team_zone_rows['_post'] == post]
            league_row = league_zone_df[league_zone_df['Post Area'] == post_display[post]]

            if team_row.empty:
                t_crosses = 0
                t_pct, t_xg, t_goals = 0.0, 0.0, 0
                t_fc, t_eff, t_xgpc = 0.0, 0.0, 0.0
            else:
                r = team_row.iloc[0]
                t_crosses = int(r['Crosses'])
                t_pct     = float(r['% of Zone'])
                t_xg      = float(r['xG'])
                t_goals   = int(r['Goals'])
                t_fc      = float(r['FC %'])
                t_eff     = float(r['Eff %'])
                t_xgpc    = float(r['xG / Cross'])

            l = league_row.iloc[0] if not league_row.empty else {}

            def rank_str(metric, post_key):
                col = f'_rank_{metric}_{post_key}'
                if team_row.empty or col not in rank_df.columns:
                    return '—'
                val = team_zone_rows[team_zone_rows['_post'] == post_key][col]
                if val.empty:
                    return '—'
                return f"{int(val.iloc[0])}/{n_teams}"

            display_rows.append({
                'Post Area':          post_display[post],
                'Crosses':            t_crosses,
                '% of Zone':          t_pct,
                'Lg % of Zone':       float(l.get('% of Zone', 0)),
                'xG':                 t_xg,
                'xG Rank':            rank_str('xG', post),
                'Goals':              t_goals,
                'Goals Rank':         rank_str('Goals', post),
                'FC %':               t_fc,
                'FC % Rank':          rank_str('FC %', post),
                'Eff %':              t_eff,
                'Eff % Rank':         rank_str('Eff %', post),
                'xG / Cross':         t_xgpc,
                'xG/Cross Rank':      rank_str('xG / Cross', post),
            })

        display_df = pd.DataFrame(display_rows)
        team_total_n_label = team_zone_n_total

        st.markdown(
            f"<span style='color:#7a6050; font-size:0.82rem'>"
            f"{header_team}: {team_total_n_label} crosses from this zone  |  "
            f"Lg = league average  |  Rank out of {n_teams} teams</span>",
            unsafe_allow_html=True
        )

        # Colour rank cells: green if top third, amber if mid, red if bottom third
        top_cut    = n_teams // 3
        bottom_cut = n_teams - n_teams // 3

        def colour_rank_cell(val):
            if not isinstance(val, str) or '/' not in val:
                return ''
            rank_num = int(val.split('/')[0])
            if rank_num <= top_cut:
                return 'background-color: #d4edda; color: #155724; font-weight:600'
            elif rank_num >= bottom_cut:
                return 'background-color: #f8d7da; color: #721c24; font-weight:600'
            else:
                return 'background-color: #fff3cd; color: #856404; font-weight:600'

        rank_cols = ['xG Rank', 'Goals Rank', 'FC % Rank', 'Eff % Rank', 'xG/Cross Rank']

        styled = (display_df.style
                  .format({
                      '% of Zone':     '{:.1f}%',
                      'Lg % of Zone':  '{:.1f}%',
                      'xG':            '{:.2f}',
                      'FC %':          '{:.1f}%',
                      'Eff %':         '{:.1f}%',
                      'xG / Cross':    '{:.3f}',
                  })
                  .applymap(colour_rank_cell, subset=rank_cols)
                  .background_gradient(subset=['% of Zone'],  cmap='YlOrBr', vmin=0, vmax=70)
                  .background_gradient(subset=['xG / Cross'], cmap='YlGn',   vmin=0, vmax=0.12)
                  .set_properties(**{'text-align': 'center'}))
        st.dataframe(styled, use_container_width=True, hide_index=True)

# ── League-wide rankings ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 📊 League-Wide Rankings")
st.caption("Zone / Post / Action-type / Date filters applied. Team filter does NOT affect rankings.")

def team_stats(grp):
    n   = len(grp)
    gls = int(grp['Goal_within_5_seconds'].sum())
    xg  = grp['xG_within_5_seconds'].sum()
    fc  = int(grp['outcome'].sum())
    eff = int(((grp['outcome'] == 1) | (grp['xG_within_5_seconds'] > 0)).sum())
    return pd.Series({
        'Crosses': '%i' %n,
        'xG': round(xg, 2),
        'Goals (5s)': '%i' %gls,
        'First Contact': int(fc),
        'FC %': round(fc / n * 100, 1) if n else 0,
        'Effective': '%i' %eff,
        'Eff %': round(eff / n * 100, 1) if n else 0,
        'xG / Cross': round(xg / n, 3) if n else 0,
    })

tab1, tab2 = st.tabs(["Crosses Made", "Crosses Conceded"])

for tab, grp_col, sort_ in [(tab1, 'Team', False), (tab2, 'Opponent', True)]:
    with tab:
        stats = filt_league.groupby(grp_col).apply(team_stats).reset_index()
        stats.rename(columns={grp_col: 'Team'}, inplace=True)
        stats = stats.sort_values('xG / Cross', ascending=sort_).reset_index(drop=True)
        stats.index += 1

        def highlight_team(row):
            if selected_team != "All Teams" and row['Team'] == selected_team:
                return ['background-color: #d4e8f7; font-weight: bold; color: #4a2e19'] * len(row)
            return [''] * len(row)

        styled = (stats.style
                  .apply(highlight_team, axis=1)
                  .format({'xG': '{:.2f}', 'FC %': '{:.1f}%',
                           'Eff %': '{:.1f}%', 'xG / Cross': '{:.3f}'}))
        st.dataframe(styled, use_container_width=True, height=520)
