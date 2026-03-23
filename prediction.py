import io
import os
import re
import json
import hashlib
import time
from collections import deque, defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import zipfile
from matplotlib.backends.backend_pdf import PdfPages


# =========================================================
# OPTIONAL: GOOGLE DRIVE SUPPORT FOR COLAB
# =========================================================
USE_GOOGLE_DRIVE = True
GOOGLE_DRIVE_BASE_FOLDER = "DailyTradeBias"   # map inside MyDrive
COLAB_LOCAL_BASE = "/content"

def running_in_colab() -> bool:
    try:
        import google.colab  # type: ignore
        return True
    except Exception:
        return False

def setup_output_base_dir() -> Path:
    """
    Choose a writable output base directory.
    Priority:
    1) Google Drive (if in Colab and USE_GOOGLE_DRIVE=True)
    2) Colab local runtime (/content)
    3) Script directory (normal local Python execution)
    """
    if running_in_colab():
        if USE_GOOGLE_DRIVE:
            try:
                from google.colab import drive  # type: ignore
                drive.mount("/content/drive", force_remount=False)
                base = Path("/content/drive/MyDrive") / GOOGLE_DRIVE_BASE_FOLDER
                base.mkdir(parents=True, exist_ok=True)
                print(f"[INFO] Using Google Drive output folder: {base}")
                return base
            except Exception as e:
                print(f"[WARN] Could not mount/use Google Drive: {e}")
                base = Path(COLAB_LOCAL_BASE)
                base.mkdir(parents=True, exist_ok=True)
                print(f"[INFO] Falling back to Colab local storage: {base}")
                return base
        else:
            base = Path(COLAB_LOCAL_BASE)
            base.mkdir(parents=True, exist_ok=True)
            print(f"[INFO] Using Colab local storage: {base}")
            return base

    # normal local / desktop / server execution
    try:
        base = Path(__file__).resolve().parent
    except NameError:
        # __file__ may not exist in notebook-like environments
        base = Path.cwd()

    base.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Using local output folder: {base}")
    return base


# =========================================================
# CONFIG
# =========================================================

API_KEY = os.environ.get("TWELVEDATA_API_KEY", "").strip()

if not API_KEY:
    raise RuntimeError(
        "No API key found. Set TWELVEDATA_API_KEY as an environment variable in Colab before running this script."
    )

def with_key(url: str) -> str:
    if "apikey=" in url:
        return re.sub(r"apikey=[^&]+", f"apikey={API_KEY}", url)
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}apikey={API_KEY}"

# =========================================================
# CURATED FX UNIVERSE
# =========================================================

LAYER_1 = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD",
    "AUDUSD", "NZDUSD", "EURJPY", "GBPJPY", "AUDJPY",
    "NZDJPY", "EURGBP", "GBPCHF", "EURCHF", "CADJPY",
]

LAYER_2 = [
    "AUDNZD", "EURNZD", "EURAUD", "GBPAUD", "GBPNZD",
    "EURCAD", "GBPCAD", "AUDCAD", "NZDCAD", "CADCHF",
    "AUDCHF", "NZDCHF",
]

LAYER_3 = [
    "USDMXN", "USDZAR",
]


PAIR_MAP = {
    "EURUSD": "EUR/USD",
    "GBPUSD": "GBP/USD",
    "USDJPY": "USD/JPY",
    "USDCHF": "USD/CHF",
    "USDCAD": "USD/CAD",
    "AUDUSD": "AUD/USD",
    "NZDUSD": "NZD/USD",
    "EURJPY": "EUR/JPY",
    "GBPJPY": "GBP/JPY",
    "AUDJPY": "AUD/JPY",
    "NZDJPY": "NZD/JPY",
    "EURGBP": "EUR/GBP",
    "GBPCHF": "GBP/CHF",
    "EURCHF": "EUR/CHF",
    "CADJPY": "CAD/JPY",
    "AUDNZD": "AUD/NZD",
    "EURNZD": "EUR/NZD",
    "EURAUD": "EUR/AUD",
    "GBPAUD": "GBP/AUD",
    "GBPNZD": "GBP/NZD",
    "EURCAD": "EUR/CAD",
    "GBPCAD": "GBP/CAD",
    "AUDCAD": "AUD/CAD",
    "NZDCAD": "NZD/CAD",
    "CADCHF": "CAD/CHF",
    "AUDCHF": "AUD/CHF",
    "NZDCHF": "NZD/CHF",
    "USDMXN": "USD/MXN",
    "USDZAR": "USD/ZAR",
}

TIMEZONE = "America/New_York"

H1_OUTPUTSIZE = 220
D1_OUTPUTSIZE = 90
W1_OUTPUTSIZE = 100

DATE_STR = datetime.now().strftime("%Y-%m-%d")

# =========================================================
# CALIBRATION BACKTEST CONFIG
# =========================================================
# Pair baskets chosen to allow quick A/B calibration runs without editing the rest of the script.
# set1 keeps the original v5.21 basket.
# set2 is a complementary cross-heavy basket.
BACKTEST_SYMBOLS_SET1 = ["EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "USDCAD", "USDCHF", "EURJPY", "AUDNZD"]
BACKTEST_SYMBOLS_SET2 = ["EURGBP", "GBPJPY", "EURCHF", "CADJPY", "EURAUD", "GBPCAD", "AUDCHF", "NZDCAD"]
BACKTEST_SYMBOLS_SWITCH = "both"   # choose: "set1", "set2", "both"

def resolve_backtest_symbols(symbol_switch: str):
    mode = str(symbol_switch or "set1").strip().lower()
    if mode == "set1":
        return BACKTEST_SYMBOLS_SET1[:], "set1"
    if mode == "set2":
        return BACKTEST_SYMBOLS_SET2[:], "set2"
    if mode == "both":
        seen = set()
        merged = []
        for sym in BACKTEST_SYMBOLS_SET1 + BACKTEST_SYMBOLS_SET2:
            if sym not in seen:
                seen.add(sym)
                merged.append(sym)
        return merged, "bothsets"
    raise ValueError(f"Unknown BACKTEST_SYMBOLS_SWITCH: {symbol_switch}. Use 'set1', 'set2', or 'both'.")

BACKTEST_SYMBOLS, BACKTEST_SYMBOLS_LABEL = resolve_backtest_symbols(BACKTEST_SYMBOLS_SWITCH)
BACKTEST_SNAPSHOT_DAYS = 5          # number of snapshot days to generate
FORWARD_VERIFY_HOURS = 24           # primary forward evaluation window after each snapshot
ALT_FORWARD_VERIFY_HOURS = 48       # secondary calibration diagnostic horizon
THIRD_FORWARD_VERIFY_HOURS = 72     # tertiary calibration diagnostic horizon
BACKTEST_END_DATE = None            # e.g. "2026-03-07"; None = latest available date in fetched H1 data
BACKTEST_H1_OUTPUTSIZE = 700
BACKTEST_D1_OUTPUTSIZE = 160
BACKTEST_W1_OUTPUTSIZE = 130
EXPORT_DAILY_ZIPS = True
EXPORT_BATCH_ZIP = True
PRODUCTION_MODE = True

SYMBOLS = BACKTEST_SYMBOLS[:]

BASE_DIR = setup_output_base_dir()
OUTDIR = BASE_DIR / f"{DATE_STR}_FX_BACKTEST_CALIBRATION_BATCH_{len(SYMBOLS)}PAIRS_20D_{BACKTEST_SYMBOLS_LABEL}"
OUTDIR.mkdir(parents=True, exist_ok=True)

LATEST_DIR = BASE_DIR / "daily_outputs" / "latest"
LATEST_DIR.mkdir(parents=True, exist_ok=True)

if not OUTDIR.exists():
    raise RuntimeError(f"Failed to create output directory: {OUTDIR}")
if not OUTDIR.is_dir():
    raise RuntimeError(f"Output path exists but is not a directory: {OUTDIR}")
if not LATEST_DIR.exists():
    raise RuntimeError(f"Failed to create latest output directory: {LATEST_DIR}")
if not LATEST_DIR.is_dir():
    raise RuntimeError(f"Latest output path exists but is not a directory: {LATEST_DIR}")

PDFfilename = f"{DATE_STR}_FX_BACKTEST_CALIBRATION_PACK_{BACKTEST_SYMBOLS_LABEL}.pdf"

BULL_COLOR = "green"
BEAR_COLOR = "red"

OTE_LOW = 0.62
OTE_HIGH = 0.79

MAX_ENTRY_ZONES_TO_PLOT = 2

REQUIRE_OTE = True
REQUIRE_AT_LEAST_ONE_OF = {"FVG", "OB"}

H1_PLOT_BARS = 140
D1_PLOT_BARS = 60
W1_PLOT_BARS = 80

FVG_LOOKBACK_BARS = 180
OB_LOOKBACK_BARS = 180
GAP_LOOKBACK_BARS = 180

SWING_LEN = 3
DISPLACEMENT_K = 1.5
BOS_LOOKBACK = 30
ATR_LEN = 14
GAP_ATR_MULT = 0.20

DEALING_RANGE_LOOKBACK_D1 = 40
LIQUIDITY_LOOKBACK_H1 = 30
DISPLACEMENT_LOOKAHEAD = 4
ZONE_TOUCH_TOL_FRAC = 0.15
USE_SMT_BONUS = True

MONTHLY_PIVOT_MIN_BARS = 40
STRUCTURAL_TREND_BARS_D1 = 20
STRUCTURAL_TREND_BARS_W1 = 12
RECENT_SWING_CONTEXT = 20
LIQUIDITY_MAJOR_LOOKBACK = 60
REJECTION_CLOSEBACK_FRAC = 0.20
BOTH_SIDES_LOOKBACK = 12
EVENT_RECENCY_LOOKBACK = 8

SCRIPT_VERSION = "v5.51-backtest-calibration-and-prediction-8pairs-20days-mastertable"
CHANGE_LOG = [
    "v5.51 github-latest export patch: added stable daily_outputs/latest exports with unsuffixed json/csv/txt prediction files plus Today_Predictions.zip for GitHub + ChatGPT reading.",
    "v5.4.1 prediction export release: added a separate contemporaneous-only today-prediction ranking for all symbols, exported setup-quality grades and readable factor breakdowns, and added integrity reporting that explicitly excludes verifier/outcome fields from prediction scoring.",
    "v5.3 symbol-set switch + safe naming release: built on v5.21, added BACKTEST_SYMBOLS_SET2 plus a set1/set2/both switch, pushed the selected set label into output directories and key filenames to avoid overwrite collisions, and expanded manifest metadata so each batch clearly records which symbol basket was used.",
    "v5.21 shadow recovery patch: preserved the v5.1 primary shortlist logic, added a safe fallback shadow-watchlist path for strong near-miss rows, exported shadow reason/order diagnostics, and kept blocked/gate-pass/relval rows out of the primary shortlist.",
    "v5.1 guarded binding-admission rebuild: preserved the strong v4.9 primary shortlist, turned blocked leakage into a hard impossibility, quarantined gate-passed and relval exception cases into a non-primary shadow watchlist, and exported comparative/lane/admission diagnostics for every row.",
    "v4.9 comparative-admission selector rebuild: replaced mostly row-wise veto scoring with hard admission classes, batch-relative dominance ranking, stronger gate-pass and relval blocks, explicit override logic, and exportable lane/admission diagnostics.",
    "v4.8 counter-bias selector rebuild: replaced mostly-linear radical scoring with veto-first scoring, hard anti-leak penalties for legacy gate-pass + relative-value archetypes, explicit relval cap, guaranteed survivor-lane admission, and new export diagnostics for vetoes and admission lanes.",
    "v4.2b calibrated-confidence selector patch: added legacy vs calibrated confidence exports, promoted confidence into shortlist ranking via Selection_Score and Final_Rank_Score, reduced dependence on clean-looking confluence, and aligned batch exports with the v4.2b review prompt.",
    "v4.2 auditability patch: selector diagnostics promoted into calibration_master_table, added selector_audit_table exports, and expanded manifest reporting so shortlist logic can be verified directly from the batch outputs.",
    "v4.1 kill-switch selector release: shifted shortlist construction toward fragility kills and idea-family deduplication, reduced dependence on tournament ranking, and selected from robust survivors rather than forcing archetype exposure.",
    "v4.0 simplified-selector release: kept the newer realism engine, removed forced continuation exposure, reduced pool scoring complexity, and separated ranking more cleanly from allocator constraints.",
    "v3.9 variable-pruning release: simplified selector to a smaller driver set, demoted confidence and descriptive nuance fields to diagnostic-only, reduced tournament pools, and shifted crowding control more into allocator logic.",
    "v3.8.1 continuation-selection repair: added within-continuation quality scoring, elite continuation gating, stronger crowded-USD continuation suppression, and reordered shortlist slots to favor diversified/execution winners before continuation exposure.",
    "v3.8 tournament allocator redesign: moved shortlist construction from one global ranking into pool-based finalists, added robustness scoring, mandatory challenger representation, anti-adjacency crowding control, and exported tournament diagnostics.",
    "v3.7.1 shortlist repair: confidence weight muted to zero for calibration ranking, D-tier no longer auto-kills calibration rows, and diversification strengthened with explicit continuation-cap handling.",
    "v3.7 shortlist allocator redesign: slot-based core/flex/challenger shortlist, near-muted confidence weight, stronger continuation vs relative-value continuation split, and harder anti-crowding allocator rules.",
    "v3.6 shortlist allocator patch: added soft-gate shortlist admission, differentiated soft-fail penalties, reduced confidence weight, split continuation vs relative-value continuation ranking, and strengthened theme/USD diversification caps.",
    "Added preset-based execution/payoff profiles (mild/medium/wide) for SL/TP calibration.",
    "Added batch/day manifest reporting for preset and payoff multipliers.",
    "Fixed zip export order bug by exporting only after all outputs are written.",
    "Removed embedded fallback API key; runtime now requires env configuration.",
    "Upgraded W1/D1 bias from last-candle-only to structural multi-factor bias.",
    "Added daily/weekly/monthly pivot regime, zone fit, stretch, and conflict fields.",
    "Expanded liquidity into side, external/internal, major/minor, rejection, both-sides, and follow-through fields.",
    "Added confidence and data-quality fields to reduce false precision.",
    "Improved shortlist ranking with confidence and pivot-context adjustments.",
    "Added manifest and changelog exports for traceability.",
    "Backtest calibration mode: multi-day snapshot generation with forward verifier outcomes.",
    "v2.3 calibration patch: fixed verifier side handling, hard-gated D-tier rows, tightened reactive/conflict shortlist logic, and activated stronger overlap penalties.",
    "v2.3.1 verifier patch: infer side from execution levels when needed and create fallback execution plans when no entry zone is found.",
    "v2.3.2 calibration patch: propagated shortlist overlap penalties back into the master dataset and made execution targets/entries more realistic for 24h forward verification.",
    "v2.3.3 calibration patch: tightened entry proximity, reduced reactive ranking privilege, strengthened same-theme overlap penalties, and added batch validation diagnostics.",
    "v3.0 redesign: separated measurement from decision logic, added hard gates, execution-quality scoring, A-book/B-book separation, and portfolio allocator shortlist construction.",
    "v3.1 calibration patch: added ATR-distance gating, dual structural/calibration entries, separate live vs calibration gates, 24h and 48h verifier outputs, shortlist count synchronization, and batch validation reporting.",
    "v3.2 verifier patch: fixed missing secondary-horizon population/export, expanded forward verifier summaries to include all horizons, added 72h verifier outputs, and cleaned duplicated manifest keys.",
    "v3.3 execution calibration patch: added configurable SL/TP distance multipliers, RR metrics per trade, and batch-level R/weighted-R validation reporting across 24h/48h/72h.",
    "v3.4 calibration patch: made forward verifier horizons trading-hours aware so weekend market closures no longer compress 24h/48h/72h windows, tightened high-confidence labeling, and reduced reversal-after-sweep ranking privilege unless evidence is strong.",
    "v4.7 radical score rebuild: replaced additive confluence-first selection with kill-switch filtering, survivability/asymmetry/calibration-utility scoring, false-positive risk taxes, and a direct draft-board shortlist allocator with minimal pool dependence.",
]


CALIBRATION_MASTER_COLUMNS = [
    "Snapshot_Date", "Instrument", "Layer", "Cluster_Tags",
    "W1_Bias", "D1_Bias", "Alignment", "Price_Side_vs_D1_Range",
    "Liquidity_Condition", "Sweep_Quality", "Liquidity_Side", "Liquidity_Tier",
    "Liquidity_Reference_Type", "Rejection_Quality", "Follow_Through",
    "Both_Sides_Taken_Recently", "Displacement_Quality", "MSS_BOS",
    "Array_Quality", "Session_Quality", "RS_RW_Alignment", "SMT_Hint",
    "Pivot_Regime", "Pivot_Zone_Fit", "Pivot_Confluence", "Pivot_Conflict",
    "Pivot_Stretch", "Technical_Score_0_4", "Legacy_Confidence_Score", "Legacy_Confidence_Band", "Confidence_Score", "Confidence_Band",
    "Technical_Quality_Score_10", "Execution_Realism_Score_10", "Calibrated_Confidence_Score_10", "Context_Quality_Score_10", "Trigger_Quality_Score_10", "Conflict_Penalty_Score_10", "Balance_Score_10", "Opportunity_Score_10", "Kill_Switch_Score_10", "False_Positive_Risk_Score_10", "Archetype_Tax_Score_10", "Survivability_Score_10", "Asymmetry_Score_10", "Calibration_Utility_Score_10", "Radical_Confidence_Score_10", "Comparative_Edge_Score_10", "Comparator_Floor_Score_10", "Dominance_Score_10", "Admission_Class", "Override_Reason", "Selection_Score", "Final_Rank_Score",
    "Data_Quality", "Entry_Label", "Preferred_Side", "Best_Entry", "SL", "TP1", "TP2",
    "Current_Price", "ATR_H1", "Structural_Entry", "Calibration_Entry", "Entry_Distance_ATR", "RR_TP1", "RR_TP2", "Setup_Archetype", "Decision_Book", "Live_Gate_Passed", "Calibration_Gate_Passed", "Gate_Passed", "Gate_Fail_Reasons",
    "Decision_Setup_Quality", "Decision_Execution_Quality", "Decision_Portfolio_Fit", "Decision_Rank_Score",
    "Base_Ranking_Score", "Overlap_Penalty", "Ranking_Score", "In_Top_Shortlist",
    "Selector_Profile", "Continuation_Subquality", "Fragility_Reason", "Idea_Family",
    "Tournament_Pool", "Tournament_Pool_Display", "Tournament_Pool_Eligible",
    "Tournament_Finalist_Flag", "Local_Pool_Score", "Survivor_Score",
    "Shortlist_Slot_Name", "Shortlist_Slot_Order", "Selection_Lane", "Primary_Shortlist_Flag", "Primary_Override_Flag", "Shadow_Watchlist_Flag", "Shadow_Watchlist_Reason", "Shadow_Watchlist_Order", "Shortlist_Eligibility", "Admission_Binding_Status", "Veto_Flag", "Veto_Reasons", "Leakage_Penalty_Score",
    "Crowding_Block_Reason", "Selection_Passed_Over_For_Diversity",
    "Verifier_Triggered", "Verifier_TP1_Hit", "Verifier_TP2_Hit", "Verifier_SL_Hit",
    "Verifier_First_Event", "Verifier_Outcome_Label", "Verifier_MFE", "Verifier_MAE", "Verifier_R_Multiple", "Verifier_Weighted_Return_R", "Verifier_Window_Bars", "Verifier_Window_Calendar_Hours", "Verifier_Window_Weekend_Gap_Hours",
    "Verifier48_Triggered", "Verifier48_TP1_Hit", "Verifier48_TP2_Hit", "Verifier48_SL_Hit", "Verifier48_First_Event", "Verifier48_Outcome_Label", "Verifier48_MFE", "Verifier48_MAE", "Verifier48_R_Multiple", "Verifier48_Weighted_Return_R", "Verifier48_Window_Bars", "Verifier48_Window_Calendar_Hours", "Verifier48_Window_Weekend_Gap_Hours",
    "Verifier72_Triggered", "Verifier72_TP1_Hit", "Verifier72_TP2_Hit", "Verifier72_SL_Hit", "Verifier72_First_Event", "Verifier72_Outcome_Label", "Verifier72_MFE", "Verifier72_MAE", "Verifier72_R_Multiple", "Verifier72_Weighted_Return_R", "Verifier72_Window_Bars", "Verifier72_Window_Calendar_Hours", "Verifier72_Window_Weekend_Gap_Hours"
]

DIAGNOSTIC_ONLY_FIELDS = [
    "Array_Quality", "Session_Quality", "RS_RW_Alignment", "SMT_Hint", "Pivot_Confluence", "Pivot_Stretch",
    "Legacy_Confidence_Score", "Legacy_Confidence_Band", "Liquidity_Label", "Liquidity_Descriptor"
]

SELECTOR_AUDIT_COLUMNS = [
    "Snapshot_Date", "Instrument", "Setup_Archetype", "Decision_Book",
    "Selector_Profile", "In_Top_Shortlist", "Gate_Passed", "Gate_Fail_Reasons",
    "Decision_Setup_Quality", "Decision_Execution_Quality", "Entry_Distance_ATR",
    "Continuation_Subquality", "Fragility_Reason", "Idea_Family",
    "Tournament_Pool", "Tournament_Pool_Display", "Tournament_Pool_Eligible",
    "Tournament_Finalist_Flag", "Local_Pool_Score", "Survivor_Score",
    "Shortlist_Slot_Name", "Shortlist_Slot_Order", "Selection_Lane", "Primary_Shortlist_Flag", "Primary_Override_Flag", "Shadow_Watchlist_Flag", "Shadow_Watchlist_Reason", "Shadow_Watchlist_Order", "Shortlist_Eligibility", "Admission_Binding_Status",
    "Legacy_Confidence_Score", "Legacy_Confidence_Band", "Confidence_Score", "Confidence_Band",
    "Technical_Quality_Score_10", "Execution_Realism_Score_10", "Calibrated_Confidence_Score_10",
    "Context_Quality_Score_10", "Trigger_Quality_Score_10", "Conflict_Penalty_Score_10", "Balance_Score_10", "Opportunity_Score_10",
    "Kill_Switch_Score_10", "False_Positive_Risk_Score_10", "Archetype_Tax_Score_10", "Survivability_Score_10", "Asymmetry_Score_10", "Calibration_Utility_Score_10", "Radical_Confidence_Score_10",
    "Selection_Score", "Final_Rank_Score", "Overlap_Penalty", "Ranking_Score", "Decision_Rank_Score",
    "Crowding_Block_Reason", "Selection_Passed_Over_For_Diversity",
    "Verifier_R_Multiple", "Verifier_Weighted_Return_R",
    "Verifier48_R_Multiple", "Verifier48_Weighted_Return_R",
    "Verifier72_R_Multiple", "Verifier72_Weighted_Return_R",
]

TOP_SHORTLIST_N = 6
MAX_SAME_BASE_OR_QUOTE_IN_SHORTLIST = 2
MAX_SAME_CLUSTER_IN_SHORTLIST = 2
MAX_BBOOK_IN_SHORTLIST = 2
MAX_THEME_IN_SHORTLIST = 1
MAX_USD_BASKET_IN_SHORTLIST = 2
MAX_CONTINUATION_IN_SHORTLIST = 3
V36_MAX_SOFT_ROWS_IN_SHORTLIST = 2

# v3.8 tournament allocator knobs
V37_CONFIDENCE_WEIGHT = 0.00
V37_SETUP_WEIGHT = 0.55
V37_EXECUTION_WEIGHT = 1.05
V37_CORE_SLOT_RATIO = 0.50
V37_FLEX_SLOT_RATIO = 0.35
V37_CHALLENGER_SLOT_RATIO = 0.15
V37_CHALLENGER_BONUS_DIVERSIFIED = 0.15
V37_CHALLENGER_BONUS_RELVAL = 0.10
V37_CHALLENGER_BONUS_LOW_CONF = 0.05
V37_CHALLENGER_PENALTY_CROWDED_CONTINUATION = -0.15

V38_LOCAL_SETUP_WEIGHT = 0.50
V38_LOCAL_EXECUTION_WEIGHT = 1.10
V38_FINALISTS_PER_POOL = 2
V38_POOL_TOP_EXECUTION_COUNT = 2
V38_POOL_TOP_CONTINUATION_COUNT = 2
V38_POOL_TOP_RELVAL_COUNT = 2
V38_POOL_TOP_DIVERSIFIED_COUNT = 2
V38_POOL_TOP_CHALLENGER_COUNT = 2
V38_NO_ADJACENT_SAME_THEME = True
V38_REQUIRE_MANDATORY_CHALLENGER = True
V38_CONTINUATION_POOL_MIN_LOCAL_SCORE = 3.05
V38_CONTINUATION_MIN_SUBQUALITY = 0.10
V38_CONTINUATION_MIN_EXECUTION_QUALITY = 1.55
V38_CONTINUATION_MIN_SETUP_QUALITY = 1.55
V38_CONTINUATION_USD_SOFT_CAP = 1
V38_CONTINUATION_CROWDED_USD_EXTRA_PENALTY = 0.45
V38_CONTINUATION_THEME_REPEAT_EXTRA_PENALTY = 0.30
V38_MANDATORY_SLOT_SEQUENCE = ("relval_or_diversified", "execution", "best_remaining", "best_remaining", "challenger", "continuation")

# v3.9 reduced-selector knobs
V39_SETUP_WEIGHT = 0.85
V39_EXECUTION_WEIGHT = 1.15
V39_RELVAL_BONUS = 0.10
V39_CONT_SUBQ_HIGH = 0.20
V39_CONT_SUBQ_LOW = -0.20
V39_ENTRY_DIST_BONUS_TIGHT = 0.10
V39_ENTRY_DIST_BONUS_GOOD = 0.05
V39_ENTRY_DIST_PENALTY_FAR = -0.15
V39_POOL_TOP_CONTINUATION_COUNT = 2
V39_POOL_TOP_RELVAL_COUNT = 2
V39_POOL_TOP_DIVERSIFIED_COUNT = 2
V39_POOL_TOP_CHALLENGER_COUNT = 2
V39_SIMPLIFIED_SLOT_SEQUENCE = ("relval", "diversified", "challenger", "continuation", "best_remaining", "best_remaining")

# v4.0 simplified-selector knobs
V40_SETUP_WEIGHT = 0.80
V40_EXECUTION_WEIGHT = 1.20
V40_ENTRY_DIST_BONUS_TIGHT = 0.10
V40_ENTRY_DIST_BONUS_GOOD = 0.05
V40_ENTRY_DIST_PENALTY_FAR = -0.12
V40_RELVAL_POOL_BONUS = 0.08
V40_DIVERSIFIED_POOL_BONUS = 0.08
V40_CHALLENGER_POOL_BONUS = 0.05
V40_CONTINUATION_POOL_BONUS = 0.00
V40_REQUIRE_ELITE_CONTINUATION = True
V40_CONTINUATION_MIN_SUBQUALITY = 0.15
V40_CONTINUATION_MIN_EXECUTION_QUALITY = 1.60
V40_CONTINUATION_MIN_SETUP_QUALITY = 1.55
V40_POOL_TOP_CONTINUATION_COUNT = 2
V40_POOL_TOP_RELVAL_COUNT = 2
V40_POOL_TOP_DIVERSIFIED_COUNT = 2
V40_POOL_TOP_CHALLENGER_COUNT = 2
V40_SIMPLIFIED_SLOT_SEQUENCE = ("relval", "diversified", "challenger", "best_remaining", "best_remaining", "best_remaining")
V41_SETUP_WEIGHT = 0.75
V41_EXECUTION_WEIGHT = 1.25
V41_ENTRY_DIST_BONUS_TIGHT = 0.08
V41_ENTRY_DIST_BONUS_GOOD = 0.04
V41_ENTRY_DIST_PENALTY_FAR = -0.10
V41_RELVAL_BONUS = 0.10
V41_CONT_SUBQ_GOOD = 0.12
V41_CONT_SUBQ_BAD = -0.15
V41_POOL_TOP_RELVAL_COUNT = 2
V41_POOL_TOP_DIVERSIFIED_COUNT = 2
V41_POOL_TOP_CHALLENGER_COUNT = 2
V41_POOL_TOP_OVERALL_COUNT = 8
V41_SIMPLIFIED_SLOT_SEQUENCE = ("relval", "diversified", "challenger", "best_remaining", "best_remaining", "best_remaining")
V41_CONTINUATION_SUBQUALITY_FLOOR = 0.00
V41_FAMILY_MAX_PER_SIDE = 1



TRIGGER_PROXIMITY_ZONE_FRACTION = 0.12
TRIGGER_PROXIMITY_FALLBACK_VOL = 0.10
TP2_REALISM_RISK_CAP = 1.45
TP2_REALISM_VOL_CAP = 0.70
CALIBRATION_A_BOOK_MAX_ENTRY_ATR = 1.5
CALIBRATION_B_BOOK_MAX_ENTRY_ATR = 2.0
CALIBRATION_ZONE_FRACTION = 0.05
CALIBRATION_FALLBACK_VOL = 0.04

# =========================================================
# EXECUTION / PAYOFF CALIBRATION KNOBS
# =========================================================
EXECUTION_PAYOFF_PRESET = "medium"  # choose: "mild", "medium", "wide"
EXECUTION_PAYOFF_PRESETS = {
    "mild": {
        "sl": 1.10,
        "tp1": 1.20,
        "tp2": 1.40,
        "tp1_partial_exit_fraction": 0.50,
    },
    "medium": {
        "sl": 1.25,
        "tp1": 1.35,
        "tp2": 1.60,
        "tp1_partial_exit_fraction": 0.50,
    },
    "wide": {
        "sl": 1.45,
        "tp1": 1.60,
        "tp2": 1.95,
        "tp1_partial_exit_fraction": 0.50,
    },
}
if EXECUTION_PAYOFF_PRESET not in EXECUTION_PAYOFF_PRESETS:
    raise ValueError(f"Unknown EXECUTION_PAYOFF_PRESET: {EXECUTION_PAYOFF_PRESET}")
_EXECUTION_PAYOFF_CFG = EXECUTION_PAYOFF_PRESETS[EXECUTION_PAYOFF_PRESET]
SL_DISTANCE_MULTIPLIER = float(_EXECUTION_PAYOFF_CFG["sl"])
TP1_DISTANCE_MULTIPLIER = float(_EXECUTION_PAYOFF_CFG["tp1"])
TP2_DISTANCE_MULTIPLIER = float(_EXECUTION_PAYOFF_CFG["tp2"])
TP1_PARTIAL_EXIT_FRACTION = float(_EXECUTION_PAYOFF_CFG["tp1_partial_exit_fraction"])

VERIFIER_HORIZON_MODE = "trading_hours"  # choose: "calendar_hours" or "trading_hours"
HIGH_CONFIDENCE_MIN_SCORE = 0.72
MEDIUM_CONFIDENCE_MIN_SCORE = 0.56
LEGACY_HIGH_CONFIDENCE_MIN_SCORE = 0.88
LEGACY_MEDIUM_CONFIDENCE_MIN_SCORE = 0.64
V42B_SELECTION_SETUP_WEIGHT = 0.45
V42B_SELECTION_CONFIDENCE_WEIGHT = 0.40
V42B_SELECTION_EXECUTION_WEIGHT = 0.15
V42B_CONFIDENCE_BONUS_HIGH = 0.35
V42B_CONFIDENCE_BONUS_MEDIUM = 0.10
V42B_CONFIDENCE_BONUS_LOW = -0.25
V46_CONTEXT_WEIGHT = 0.24
V46_TRIGGER_WEIGHT = 0.26
V46_EXECUTION_WEIGHT = 0.22
V46_BALANCE_WEIGHT = 0.18
V46_OPPORTUNITY_WEIGHT = 0.10
V46_HARMONIC_WEIGHT = 0.30
V46_CONFLICT_PENALTY_WEIGHT = 0.70
V46_GATE_PASSED_PENALTY = 0.15
V46_SOFT_REBOUND_BONUS = 0.55
V46_RELVAL_PENALTY = 0.30
V46_CONTINUATION_BONUS = 0.18
V46_HARD_REJECT_SCORE_PENALTY = 1.80

V47_KILL_WEIGHT = 0.78
V47_FALSE_POSITIVE_WEIGHT = 0.62
V47_ARCHETYPE_TAX_WEIGHT = 0.34
V47_SOFT_FAIL_BONUS = 0.85
V47_GATE_PASS_TAX = 0.55
V47_HARD_REJECT_FLOOR_PENALTY = 2.60
V47_DIRECT_DRAFT_TOP_N = 12
V49_RELVAL_MAX_IN_SHORTLIST = 1
V49_MIN_ANTI_GATE_SLOTS = 2
V49_MIN_UTILITY_SLOTS = 2
V49_MAX_GATEPASS_SLOTS = 2
V49_KILL_SWITCH_BLOCK = 7.8
V49_FALSE_POSITIVE_BLOCK = 7.0
V49_GATEPASS_REQUIRE_ASYM = 7.8
V49_GATEPASS_REQUIRE_UTIL = 7.8
V49_GATEPASS_REQUIRE_TRIGGER = 6.8
V49_RELVAL_OVERRIDE_ASYM = 8.7
V49_RELVAL_OVERRIDE_UTIL = 8.8
V49_RELVAL_OVERRIDE_TRIGGER = 7.2
V49_RELVAL_OVERRIDE_FP_MAX = 3.6
V49_COMPARATIVE_WEIGHT = 0.62
V49_ROW_QUALITY_WEIGHT = 0.38
V49_OVERRIDE_BONUS = 0.60
V49_BLOCK_FLOOR_PENALTY = 4.25

V50_PRIMARY_SHORTLIST_N = TOP_SHORTLIST_N
V50_SHADOW_WATCHLIST_N = 2
V50_GATEPASS_PROOF_UTIL = 8.9
V50_GATEPASS_PROOF_ASYM = 8.8
V50_GATEPASS_PROOF_TRIGGER = 7.6
V50_GATEPASS_PROOF_DOM = 8.4
V50_RELVAL_PROOF_UTIL = 9.0
V50_RELVAL_PROOF_ASYM = 8.9
V50_RELVAL_PROOF_TRIGGER = 7.6
V50_RELVAL_PROOF_DOM = 8.5
V50_FALSE_POSITIVE_BLOCK = 6.8
V50_KILL_BLOCK = 7.6
V50_PRIMARY_MIN_ANTI_GATE = 2
V50_PRIMARY_MIN_UTILITY = 2
V50_PRIMARY_MIN_BEST_REMAINING = 2
V50_QUARANTINE_TAX = 2.4
V50_BLOCK_FLOOR_PENALTY = 6.5
V50_PRIMARY_PREFERRED_BONUS = 0.30
V50_PRIMARY_ELIGIBLE_BONUS = 0.10
V50_COMPARATIVE_WEIGHT = 0.58
V50_ROW_QUALITY_WEIGHT = 0.42
V521_SHADOW_WATCHLIST_N = V50_SHADOW_WATCHLIST_N
V521_SHADOW_MIN_UTIL = 6.4
V521_SHADOW_MIN_ASYM = 6.0
V521_SHADOW_MIN_DOM = 6.0
V521_SHADOW_MIN_TRIGGER = 5.8
V521_SHADOW_FP_MAX = 6.0
V521_SHADOW_FALLBACK_BONUS = 0.18
REVERSAL_ARCHETYPE_RANK_PENALTY = 0.22
CONTINUATION_ARCHETYPE_RANK_BONUS = 0.00
RELATIVE_VALUE_CONTINUATION_RANK_BONUS = 0.08
CONTINUATION_ARCHETYPE_RANK_PENALTY = 0.10
CONFIDENCE_RANK_WEIGHT = 0.22
BBOOK_RANK_PENALTY = 0.08
CALIBRATION_SOFT_FAIL_RANK_PENALTY = 0.18
CALIBRATION_SOFT_FAIL_REASONS = {"weak_impulse", "d_tier", "stacked_conflict"}
CALIBRATION_HARD_REJECT_REASONS = {"status_not_ok", "poor_data", "no_side", "entry_too_far_calibration", "full_conflict", "strong_pivot_conflict", "weak_execution"}
MIN_REVERSAL_REJECTION_FOR_PRIORITY = "strong rejection"

# =========================================================
# TODAY PREDICTION CONFIG (v5.4.1)
# =========================================================
ENABLE_TODAY_PREDICTION = True
PREDICTION_TOP_N = 8
PREDICTION_SCORE_VERSION = "v5.5_prediction_quality_v2"
TODAY_PREDICTIONS_ZIP_NAME = "Today_Predictions.zip"
TODAY_PREDICTIONS_PROMPT_NAME = "MASTERPROMPT_Top10_Prediction_Auditor_v6 (1).txt"
PREDICTION_FORBIDDEN_FIELDS = [
    "Verifier_Triggered", "Verifier_TP1_Hit", "Verifier_TP2_Hit", "Verifier_SL_Hit",
    "Verifier_First_Event", "Verifier_Outcome_Label", "Verifier_MFE", "Verifier_MAE",
    "Verifier_R_Multiple", "Verifier_Weighted_Return_R",
    "Verifier48_Triggered", "Verifier48_TP1_Hit", "Verifier48_TP2_Hit", "Verifier48_SL_Hit",
    "Verifier48_First_Event", "Verifier48_Outcome_Label", "Verifier48_MFE", "Verifier48_MAE",
    "Verifier48_R_Multiple", "Verifier48_Weighted_Return_R",
    "Verifier72_Triggered", "Verifier72_TP1_Hit", "Verifier72_TP2_Hit", "Verifier72_SL_Hit",
    "Verifier72_First_Event", "Verifier72_Outcome_Label", "Verifier72_MFE", "Verifier72_MAE",
    "Verifier72_R_Multiple", "Verifier72_Weighted_Return_R",
]
PREDICTION_INPUT_FIELDS = [
    "Instrument", "Preferred_Side", "Setup_Archetype", "Decision_Book", "W1_Bias", "D1_Bias", "Alignment",
    "Price_Side_vs_D1_Range", "Liquidity_Condition", "Sweep_Quality", "Liquidity_Side", "Liquidity_Tier",
    "Liquidity_Reference_Type", "Rejection_Quality", "Follow_Through", "Both_Sides_Taken_Recently",
    "Displacement_Quality", "MSS_BOS", "Pivot_Regime", "Pivot_Zone_Fit", "Pivot_Conflict", "Pivot_Stretch",
    "Data_Quality", "Confidence_Score", "Confidence_Band", "Technical_Quality_Score_10",
    "Execution_Realism_Score_10", "Calibrated_Confidence_Score_10", "Context_Quality_Score_10",
    "Trigger_Quality_Score_10", "Conflict_Penalty_Score_10", "Balance_Score_10", "Opportunity_Score_10",
    "Kill_Switch_Score_10", "False_Positive_Risk_Score_10", "Archetype_Tax_Score_10",
    "Survivability_Score_10", "Asymmetry_Score_10", "Calibration_Utility_Score_10",
    "Comparative_Edge_Score_10", "Comparator_Floor_Score_10", "Dominance_Score_10",
    "Selection_Score", "Final_Rank_Score", "Admission_Class", "Override_Reason",
    "Shortlist_Eligibility", "Admission_Binding_Status", "Selection_Lane", "Primary_Shortlist_Flag",
    "Shadow_Watchlist_Flag", "Gate_Passed", "Gate_Fail_Reasons", "Veto_Flag", "Veto_Reasons",
    "Current_Price", "Best_Entry", "SL", "TP1", "TP2", "RR_TP1", "RR_TP2", "Entry_Distance_ATR",
]

CALLS_PER_MIN = 8
WINDOW_SECONDS = 60.0
SAFETY_SECONDS = 3.0

def build_url(pair: str, interval: str, outputsize: int) -> str:
    return (
        "https://api.twelvedata.com/time_series"
        f"?symbol={pair}"
        f"&interval={interval}"
        f"&outputsize={outputsize}"
        f"&timezone={TIMEZONE}"
        "&format=CSV"
    )

H1_URLS = {sym: build_url(PAIR_MAP[sym], "1h", H1_OUTPUTSIZE) for sym in SYMBOLS}
D1_URLS = {sym: build_url(PAIR_MAP[sym], "1day", D1_OUTPUTSIZE) for sym in SYMBOLS}
W1_URLS = {sym: build_url(PAIR_MAP[sym], "1week", W1_OUTPUTSIZE) for sym in SYMBOLS}

# =========================================================
# RATE LIMIT
# =========================================================
request_timestamps = deque(maxlen=CALLS_PER_MIN)

# =========================================================
# PROGRESS + ETA
# =========================================================
TOTAL_CALLS = 0
CALLS_DONE = 0
START_TS = time.time()

def _fmt_secs(s: float) -> str:
    s = max(0, int(s))
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h{m:02d}m{s:02d}s"
    return f"{m}m{s:02d}s"

def print_progress(prefix: str = ""):
    global CALLS_DONE
    if TOTAL_CALLS <= 0:
        return
    elapsed = time.time() - START_TS
    rate = CALLS_DONE / elapsed if elapsed > 0 else 0.0
    remaining = (TOTAL_CALLS - CALLS_DONE) / rate if rate > 0 else float("inf")
    eta_str = _fmt_secs(remaining) if remaining != float("inf") else "?"
    print(f"{prefix}Progress: {CALLS_DONE}/{TOTAL_CALLS} calls | elapsed {_fmt_secs(elapsed)} | ETA {eta_str}")

def rate_limit_wait():
    if len(request_timestamps) < CALLS_PER_MIN:
        return
    now = time.time()
    oldest = request_timestamps[0]
    elapsed = now - oldest
    if elapsed < WINDOW_SECONDS:
        sleep_for = (WINDOW_SECONDS - elapsed) + SAFETY_SECONDS
        print(f"[RATE LIMIT] Sleeping {sleep_for:.1f}s to respect {CALLS_PER_MIN}/min ...")
        time.sleep(sleep_for)

def limited_get_with_retry(url: str, timeout: int = 30, max_retries: int = 5) -> requests.Response:
    global CALLS_DONE
    last_err = None
    backoff = 2.0

    for attempt in range(1, max_retries + 1):
        try:
            rate_limit_wait()
            resp = requests.get(with_key(url), timeout=timeout)
            request_timestamps.append(time.time())
            CALLS_DONE += 1
            print_progress()

            if resp.status_code == 200:
                return resp

            if resp.status_code == 429 or 500 <= resp.status_code < 600:
                retry_after = resp.headers.get("Retry-After")
                if retry_after:
                    try:
                        wait_s = float(retry_after)
                    except ValueError:
                        wait_s = backoff
                else:
                    wait_s = backoff
                print(f"[RETRY] HTTP {resp.status_code} attempt {attempt}/{max_retries}. Sleeping {wait_s:.1f}s...")
                time.sleep(wait_s)
                backoff = min(backoff * 2.0, 60.0)
                last_err = RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
                continue

            resp.raise_for_status()
            return resp

        except (requests.Timeout, requests.ConnectionError) as e:
            last_err = e
            print(f"[RETRY] Network/timeout attempt {attempt}/{max_retries}. Sleeping {backoff:.1f}s...")
            time.sleep(backoff)
            backoff = min(backoff * 2.0, 60.0)

        except Exception as e:
            last_err = e
            break

    raise RuntimeError(f"Request failed after {max_retries} attempts. Last error: {last_err}")

# =========================================================
# DATA FETCH
# =========================================================
def fetch_csv(url: str) -> pd.DataFrame:
    r = limited_get_with_retry(url, timeout=30, max_retries=5)
    r.raise_for_status()
    txt = r.text.strip()

    if txt.startswith("{") and "error" in txt.lower():
        raise RuntimeError(f"TwelveData error:\n{txt}")

    df = pd.read_csv(io.StringIO(txt), sep=None, engine="python")
    df.columns = [c.strip().lower() for c in df.columns]

    df = ensure_datetime_column(df)
    for col in ["open", "high", "low", "close"]:
        if col not in df.columns:
            raise RuntimeError(f"Missing required column '{col}' in: {df.columns}")
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if "volume" in df.columns:
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")

    df = df.dropna(subset=["open", "high", "low", "close"]).sort_values("datetime").reset_index(drop=True)
    return df

# =========================================================
# HELPERS
# =========================================================
def round_price(sym: str, value: float):
    if value is None or pd.isna(value):
        return None
    if sym.endswith("JPY"):
        return round(float(value), 3)
    if sym in {"USDMXN", "USDZAR"}:
        return round(float(value), 4)
    return round(float(value), 4)


def ensure_datetime_column(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    if "datetime" in x.columns:
        x["datetime"] = pd.to_datetime(x["datetime"], errors="coerce")
    else:
        candidate_cols = [
            "date", "time", "timestamp", "time_close", "date_time", "datetime_utc"
        ]
        found = next((c for c in candidate_cols if c in x.columns), None)
        if found is not None:
            x["datetime"] = pd.to_datetime(x[found], errors="coerce")
        elif isinstance(x.index, pd.DatetimeIndex):
            x = x.reset_index()
            first_col = x.columns[0]
            x["datetime"] = pd.to_datetime(x[first_col], errors="coerce")
            if first_col != "datetime":
                x = x.drop(columns=[first_col])
        else:
            try:
                inferred = pd.to_datetime(x.index, errors="coerce")
                if pd.Series(inferred).notna().any():
                    x = x.reset_index(drop=True)
                    x["datetime"] = inferred
                else:
                    raise KeyError("datetime")
            except Exception as e:
                raise KeyError("datetime") from e
    if "datetime" not in x.columns:
        raise KeyError("datetime")
    x = x.dropna(subset=["datetime"]).copy()
    return x


def last_timestamp_from_df(df: pd.DataFrame):
    x = ensure_datetime_column(df)
    if len(x) == 0:
        return None
    return pd.Timestamp(x["datetime"].iloc[-1])

def last_completed(df: pd.DataFrame) -> pd.DataFrame:
    if len(df) < 3:
        return df.copy()
    return df.iloc[:-1].reset_index(drop=True)

def instrument_layer(sym: str) -> str:
    if sym in LAYER_1:
        return "Layer 1 — Core execution universe"
    if sym in LAYER_2:
        return "Layer 2 — Relative-value crosses"
    if sym in LAYER_3:
        return "Layer 3 — Selective EM block"
    return "Unknown"

def pair_currencies(sym: str):
    return sym[:3], sym[3:]

# =========================================================
# BIAS
# =========================================================
def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()

def _structure_state(df: pd.DataFrame, trend_bars: int) -> dict:
    x = last_completed(df).copy().reset_index(drop=True)
    if len(x) < max(12, trend_bars + 2):
        return {
            "trend": "NEUTRAL",
            "ema_fast": None,
            "ema_slow": None,
            "close_pos": 0.5,
            "hh_hl": False,
            "ll_lh": False,
            "range_hi": float(x["high"].max()) if len(x) else None,
            "range_lo": float(x["low"].min()) if len(x) else None,
        }

    x["ema_fast"] = _ema(x["close"], 5)
    x["ema_slow"] = _ema(x["close"], 13)
    recent = x.tail(trend_bars).reset_index(drop=True)
    hi = float(recent["high"].max())
    lo = float(recent["low"].min())
    last = recent.iloc[-1]
    prev = recent.iloc[-2]
    rng = max(hi - lo, 1e-9)
    close_pos = (float(last["close"]) - lo) / rng

    hh_hl = float(last["high"]) >= float(recent["high"].tail(5).max()) and float(last["low"]) >= float(prev["low"])
    ll_lh = float(last["low"]) <= float(recent["low"].tail(5).min()) and float(last["high"]) <= float(prev["high"])

    bull_votes = 0
    bear_votes = 0
    if float(last["close"]) > float(last["open"]):
        bull_votes += 1
    elif float(last["close"]) < float(last["open"]):
        bear_votes += 1
    if float(last["ema_fast"]) > float(last["ema_slow"]):
        bull_votes += 1
    elif float(last["ema_fast"]) < float(last["ema_slow"]):
        bear_votes += 1
    if close_pos >= 0.60:
        bull_votes += 1
    elif close_pos <= 0.40:
        bear_votes += 1
    if hh_hl:
        bull_votes += 1
    if ll_lh:
        bear_votes += 1

    if bull_votes >= bear_votes + 2:
        trend = "BULLISH"
    elif bear_votes >= bull_votes + 2:
        trend = "BEARISH"
    else:
        trend = "NEUTRAL"

    return {
        "trend": trend,
        "ema_fast": float(last["ema_fast"]),
        "ema_slow": float(last["ema_slow"]),
        "close_pos": round(float(close_pos), 4),
        "hh_hl": bool(hh_hl),
        "ll_lh": bool(ll_lh),
        "range_hi": hi,
        "range_lo": lo,
    }

def bias_from_last_closed_bar(df: pd.DataFrame) -> dict:
    x = last_completed(df)
    row = x.iloc[-1]
    hi = float(row["high"])
    lo = float(row["low"])
    eq = (hi + lo) / 2.0
    rng = hi - lo
    if row["close"] > row["open"]:
        bias = "BULLISH"
    elif row["close"] < row["open"]:
        bias = "BEARISH"
    else:
        bias = "NEUTRAL"
    return {
        "bias": bias,
        "hi": hi,
        "lo": lo,
        "eq": eq,
        "range": rng,
        "date": (row["datetime"].date() if "datetime" in row.index else (x.index[-1].date() if isinstance(x.index, pd.DatetimeIndex) else None)),
        "open": float(row["open"]),
        "close": float(row["close"]),
    }

def daily_bias_from_last_closed_d1(d1: pd.DataFrame) -> dict:
    info = bias_from_last_closed_bar(d1)
    structure = _structure_state(d1, STRUCTURAL_TREND_BARS_D1)
    final_bias = structure["trend"] if structure["trend"] != "NEUTRAL" else info["bias"]
    return {
        "bias": final_bias,
        "bias_bar": info["bias"],
        "bias_structure": structure["trend"],
        "struct_close_pos": structure["close_pos"],
        "pdh": info["hi"],
        "pdl": info["lo"],
        "eq": info["eq"],
        "range": info["range"],
        "pd_date": info["date"],
        "pd_open": info["open"],
        "pd_close": info["close"],
    }

def weekly_bias_from_last_closed_w1(w1: pd.DataFrame) -> dict:
    info = bias_from_last_closed_bar(w1)
    structure = _structure_state(w1, STRUCTURAL_TREND_BARS_W1)
    final_bias = structure["trend"] if structure["trend"] != "NEUTRAL" else info["bias"]
    return {
        "bias": final_bias,
        "bias_bar": info["bias"],
        "bias_structure": structure["trend"],
        "struct_close_pos": structure["close_pos"],
        "pwh": info["hi"],
        "pwl": info["lo"],
        "weq": info["eq"],
        "range": info["range"],
        "pw_date": info["date"],
        "pw_open": info["open"],
        "pw_close": info["close"],
    }

# =========================================================
# TA HELPERS
# =========================================================
def atr(df: pd.DataFrame, length: int = 14) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            (df["high"] - df["low"]).abs(),
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.rolling(length).mean()

def _find_swings(df: pd.DataFrame, swing_len: int = 3):
    n = len(df)
    sh = np.zeros(n, dtype=bool)
    sl = np.zeros(n, dtype=bool)
    for i in range(swing_len, n - swing_len):
        window_high = df.loc[i - swing_len : i + swing_len, "high"]
        window_low = df.loc[i - swing_len : i + swing_len, "low"]
        if df.loc[i, "high"] == window_high.max():
            sh[i] = True
        if df.loc[i, "low"] == window_low.min():
            sl[i] = True
    return sh, sl

def _overlap(a_lo, a_hi, b_lo, b_hi):
    lo = max(a_lo, b_lo)
    hi = min(a_hi, b_hi)
    if hi > lo:
        return lo, hi
    return None

# =========================================================
# ACTIVE DEALING RANGE
# =========================================================
def active_dealing_range(df: pd.DataFrame, lookback: int = DEALING_RANGE_LOOKBACK_D1) -> dict:
    x = last_completed(df).copy().tail(lookback).reset_index(drop=True)
    if len(x) < 10:
        hi = float(x["high"].max())
        lo = float(x["low"].min())
        eq = (hi + lo) / 2.0
        return {"hi": hi, "lo": lo, "eq": eq, "range": hi - lo, "is_clear": hi > lo}

    sh, sl = _find_swings(x, SWING_LEN)
    swing_highs = [i for i, f in enumerate(sh) if f]
    swing_lows = [i for i, f in enumerate(sl) if f]

    if not swing_highs or not swing_lows:
        hi = float(x["high"].max())
        lo = float(x["low"].min())
    else:
        last_hi = swing_highs[-1]
        last_lo = swing_lows[-1]
        start = min(last_hi, last_lo)
        hi = float(x.loc[start:, "high"].max())
        lo = float(x.loc[start:, "low"].min())

    eq = (hi + lo) / 2.0
    return {"hi": hi, "lo": lo, "eq": eq, "range": hi - lo, "is_clear": hi > lo}

def price_side_vs_range(price: float, dealing: dict) -> str:
    if not dealing["is_clear"] or dealing["range"] <= 0:
        return "unclear"
    if price > dealing["eq"]:
        return "premium"
    if price < dealing["eq"]:
        return "discount"
    return "at EQ"

# =========================================================
# LIQUIDITY / SWEEP / REJECTION
# =========================================================
def detect_recent_liquidity_event(h1: pd.DataFrame, lookback: int = LIQUIDITY_LOOKBACK_H1) -> dict:
    df = last_completed(h1).copy().reset_index(drop=True)
    if len(df) < lookback + 10:
        return {
            "condition": "no clear liquidity reference",
            "sweep_quality": "no meaningful sweep",
            "side": "none",
            "idx": None,
            "ref": None,
            "liquidity_tier": "unclear",
            "reference_type": "none",
            "rejection_quality": "none",
            "follow_through": "none",
            "both_sides_taken_recently": False,
            "bars_since_event": None,
        }

    df["atr"] = atr(df, ATR_LEN)
    sh, sl = _find_swings(df, SWING_LEN)
    recent_idx = range(max(SWING_LEN + 1, len(df) - lookback), len(df) - 1)
    recent_both = {"buy-side": False, "sell-side": False}
    candidates = []

    for i in recent_idx:
        prior_highs = [k for k in range(max(0, i - LIQUIDITY_MAJOR_LOOKBACK), i) if sh[k]]
        prior_lows = [k for k in range(max(0, i - LIQUIDITY_MAJOR_LOOKBACK), i) if sl[k]]
        c = float(df.loc[i, "close"])
        o = float(df.loc[i, "open"])
        h = float(df.loc[i, "high"])
        l = float(df.loc[i, "low"])
        a = float(df.loc[i, "atr"]) if not pd.isna(df.loc[i, "atr"]) else max(h - l, 1e-9)
        body = abs(c - o)
        upper_wick = h - max(c, o)
        lower_wick = min(c, o) - l

        if prior_highs:
            ref_idx = prior_highs[-1]
            ref = float(df.loc[ref_idx, "high"])
            if h > ref:
                overshoot = h - ref
                recent_both["buy-side"] = True
                close_back_inside = c < ref
                rejection_score = upper_wick / max(a, 1e-9)
                rejection_quality = "strong rejection" if close_back_inside and rejection_score >= 0.35 else "moderate rejection" if close_back_inside or rejection_score >= 0.20 else "weak/no rejection"
                follow = df.loc[i + 1 : min(len(df) - 1, i + 3), "close"] if i + 1 < len(df) else pd.Series(dtype=float)
                follow_through = "clean follow-through" if len(follow) and float(follow.min()) < min(c, ref) else "limited follow-through"
                tier = "major" if len(prior_highs) >= 2 and ref_idx <= len(df) - 12 else "minor"
                sweep_quality = "sweep + close back inside range" if close_back_inside else "clean sweep only"
                candidates.append({
                    "condition": "external liquidity taken",
                    "sweep_quality": sweep_quality,
                    "side": "buy-side",
                    "idx": i,
                    "ref": ref,
                    "liquidity_tier": tier,
                    "reference_type": "swing high",
                    "rejection_quality": rejection_quality,
                    "follow_through": follow_through,
                    "overshoot_atr": round(overshoot / max(a, 1e-9), 3),
                })
        if prior_lows:
            ref_idx = prior_lows[-1]
            ref = float(df.loc[ref_idx, "low"])
            if l < ref:
                overshoot = ref - l
                recent_both["sell-side"] = True
                close_back_inside = c > ref
                rejection_score = lower_wick / max(a, 1e-9)
                rejection_quality = "strong rejection" if close_back_inside and rejection_score >= 0.35 else "moderate rejection" if close_back_inside or rejection_score >= 0.20 else "weak/no rejection"
                follow = df.loc[i + 1 : min(len(df) - 1, i + 3), "close"] if i + 1 < len(df) else pd.Series(dtype=float)
                follow_through = "clean follow-through" if len(follow) and float(follow.max()) > max(c, ref) else "limited follow-through"
                tier = "major" if len(prior_lows) >= 2 and ref_idx <= len(df) - 12 else "minor"
                sweep_quality = "sweep + close back inside range" if close_back_inside else "clean sweep only"
                candidates.append({
                    "condition": "external liquidity taken",
                    "sweep_quality": sweep_quality,
                    "side": "sell-side",
                    "idx": i,
                    "ref": ref,
                    "liquidity_tier": tier,
                    "reference_type": "swing low",
                    "rejection_quality": rejection_quality,
                    "follow_through": follow_through,
                    "overshoot_atr": round(overshoot / max(a, 1e-9), 3),
                })

    if not candidates:
        return {
            "condition": "internal liquidity only",
            "sweep_quality": "no meaningful sweep",
            "side": "none",
            "idx": None,
            "ref": None,
            "liquidity_tier": "none",
            "reference_type": "none",
            "rejection_quality": "none",
            "follow_through": "none",
            "both_sides_taken_recently": False,
            "bars_since_event": None,
        }

    best = sorted(candidates, key=lambda x: (x["idx"], x["liquidity_tier"] == "major", x["rejection_quality"] == "strong rejection"), reverse=True)[0]
    best["both_sides_taken_recently"] = recent_both["buy-side"] and recent_both["sell-side"]
    best["bars_since_event"] = len(df) - 1 - int(best["idx"])
    return best

# =========================================================
# DISPLACEMENT
# =========================================================
def detect_displacement(h1: pd.DataFrame, from_idx=None, lookahead: int = DISPLACEMENT_LOOKAHEAD) -> dict:
    df = last_completed(h1).copy().reset_index(drop=True)
    df["atr"] = atr(df, ATR_LEN)

    if len(df) < ATR_LEN + 5:
        return {"quality": "weak / no displacement", "dir": "none", "idx": None, "body_atr": None, "range_atr": None}

    if from_idx is None:
        from_idx = max(ATR_LEN + 2, len(df) - 5)

    end = min(len(df) - 1, from_idx + lookahead)
    best = {"quality": "weak / no displacement", "dir": "none", "idx": None, "body_atr": 0.0, "range_atr": 0.0}

    for i in range(from_idx, end + 1):
        a = df.loc[i, "atr"]
        if pd.isna(a) or a <= 0:
            continue

        body = abs(float(df.loc[i, "close"]) - float(df.loc[i, "open"]))
        rng = float(df.loc[i, "high"]) - float(df.loc[i, "low"])
        close_ = float(df.loc[i, "close"])
        open_ = float(df.loc[i, "open"])
        body_atr = body / float(a)
        range_atr = rng / float(a)

        if body_atr >= 1.2 and range_atr >= 1.5:
            return {
                "quality": "strong displacement",
                "dir": "bull" if close_ > open_ else "bear",
                "idx": i,
                "body_atr": round(body_atr, 3),
                "range_atr": round(range_atr, 3),
            }

        if body_atr >= 0.8 and range_atr >= 1.0:
            best = {
                "quality": "moderate displacement",
                "dir": "bull" if close_ > open_ else "bear",
                "idx": i,
                "body_atr": round(body_atr, 3),
                "range_atr": round(range_atr, 3),
            }

    return best

# =========================================================
# MSS / BOS
# =========================================================
def detect_mss_bos(h1: pd.DataFrame, event: dict) -> dict:
    df = last_completed(h1).copy().reset_index(drop=True)
    sh, sl = _find_swings(df, SWING_LEN)

    idx = event.get("idx")
    if idx is None:
        return {"status": "no clear shift", "dir": "none", "break_level": None, "confirmation_bars": 0}

    if event["side"] == "buy-side":
        lows = [k for k in range(max(0, idx - 10), idx) if sl[k]]
        if not lows:
            return {"status": "partial shift", "dir": "bear", "break_level": None, "confirmation_bars": 0}

        ref = float(df.loc[lows[-1], "low"])
        after = df.loc[idx + 1 : min(len(df) - 1, idx + 6), "close"]
        hit = [j for j, val in enumerate(after.tolist(), start=1) if float(val) < ref]
        if hit:
            return {"status": "clear MSS/BOS", "dir": "bear", "break_level": ref, "confirmation_bars": hit[0]}
        return {"status": "partial shift", "dir": "bear", "break_level": ref, "confirmation_bars": 0}

    if event["side"] == "sell-side":
        highs = [k for k in range(max(0, idx - 10), idx) if sh[k]]
        if not highs:
            return {"status": "partial shift", "dir": "bull", "break_level": None, "confirmation_bars": 0}

        ref = float(df.loc[highs[-1], "high"])
        after = df.loc[idx + 1 : min(len(df) - 1, idx + 6), "close"]
        hit = [j for j, val in enumerate(after.tolist(), start=1) if float(val) > ref]
        if hit:
            return {"status": "clear MSS/BOS", "dir": "bull", "break_level": ref, "confirmation_bars": hit[0]}
        return {"status": "partial shift", "dir": "bull", "break_level": ref, "confirmation_bars": 0}

    return {"status": "no clear shift", "dir": "none", "break_level": None, "confirmation_bars": 0}

# =========================================================
# ARRAY FRESHNESS
# =========================================================
def zone_freshness(df: pd.DataFrame, zone: dict, tolerance_frac: float = ZONE_TOUCH_TOL_FRAC) -> dict:
    lo, hi = zone["lo"], zone["hi"]
    mid = (lo + hi) / 2.0
    width = max(hi - lo, abs(mid) * 0.0001)
    tol = width * tolerance_frac
    created_idx = int(zone.get("created_idx", 0))

    touches = 0
    deep_mitigated = False

    for i in range(created_idx + 1, len(df)):
        lo_i = float(df.loc[i, "low"])
        hi_i = float(df.loc[i, "high"])

        touched = hi_i >= lo - tol and lo_i <= hi + tol
        if touched:
            touches += 1

        if zone["dir"] == "BEAR" and hi_i > hi + tol:
            deep_mitigated = True
        if zone["dir"] == "BULL" and lo_i < lo - tol:
            deep_mitigated = True

    return {"touches": touches, "deep_mitigated": deep_mitigated}

# =========================================================
# PIVOTS
# =========================================================
def _pivot_from_ohlc(high: float, low: float, close: float) -> dict:
    p = (high + low + close) / 3.0
    r1 = 2 * p - low
    s1 = 2 * p - high
    r2 = p + (high - low)
    s2 = p - (high - low)
    return {"pivot": float(p), "r1": float(r1), "s1": float(s1), "r2": float(r2), "s2": float(s2)}

def compute_pivot_pack(d1: pd.DataFrame, w1: pd.DataFrame) -> dict:
    d = last_completed(d1).copy().reset_index(drop=True)
    w = last_completed(w1).copy().reset_index(drop=True)
    if len(d) < 25 or len(w) < 3:
        return {
            "daily": None,
            "weekly": None,
            "monthly": None,
        }

    prev_d = d.iloc[-1]
    daily = _pivot_from_ohlc(float(prev_d["high"]), float(prev_d["low"]), float(prev_d["close"]))
    prev_w = w.iloc[-1]
    weekly = _pivot_from_ohlc(float(prev_w["high"]), float(prev_w["low"]), float(prev_w["close"]))

    monthly_df = ensure_datetime_column(d.copy())
    monthly_df["month"] = monthly_df["datetime"].dt.to_period("M")
    monthly_agg = monthly_df.groupby("month").agg(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last")).reset_index()
    monthly = None
    if len(monthly_agg) >= 2:
        target_idx = -2 if monthly_agg.iloc[-1]["month"] == pd.Timestamp(last_timestamp_from_df(d)).to_period("M") else -1
        prev_m = monthly_agg.iloc[target_idx]
        monthly = _pivot_from_ohlc(float(prev_m["high"]), float(prev_m["low"]), float(prev_m["close"]))

    return {"daily": daily, "weekly": weekly, "monthly": monthly}

def classify_pivot_context(price: float, pivots: dict, bias: str) -> dict:
    packs = [("daily", pivots.get("daily")), ("weekly", pivots.get("weekly")), ("monthly", pivots.get("monthly"))]
    regime_votes = []
    aligned = 0
    misaligned = 0
    confluence_count = 0
    stretch_notes = []
    fit = "unclear"

    for name, pack in packs:
        if not pack:
            continue
        p, r1, s1, r2, s2 = pack["pivot"], pack["r1"], pack["s1"], pack["r2"], pack["s2"]
        regime = "bullish above pivot" if price > p else "bearish below pivot" if price < p else "at pivot"
        regime_votes.append((name, regime))
        if bias == "BULLISH" and price <= p:
            misaligned += 1
        elif bias == "BEARISH" and price >= p:
            misaligned += 1
        elif bias in ("BULLISH", "BEARISH"):
            aligned += 1

        if bias == "BULLISH":
            if s1 <= price <= p:
                confluence_count += 1
                fit = "price in buy zone"
            elif price < s2 or price > r2:
                stretch_notes.append(name)
        elif bias == "BEARISH":
            if p <= price <= r1:
                confluence_count += 1
                fit = "price in sell zone"
            elif price > r2 or price < s2:
                stretch_notes.append(name)

    if confluence_count == 0 and fit == "unclear":
        if regime_votes:
            fit = "price at pivot" if any(r[1] == "at pivot" for r in regime_votes) else "price in neutral zone"
        else:
            fit = "unclear"

    if confluence_count >= 3:
        confluence = "daily + weekly + monthly aligned"
    elif confluence_count == 2:
        confluence = "daily + weekly aligned"
    elif confluence_count == 1:
        confluence = "daily only"
    else:
        confluence = "mixed confluence" if regime_votes else "no clear confluence"

    if misaligned >= 2:
        conflict = "strong pivot conflict"
    elif misaligned == 1:
        conflict = "mild pivot conflict"
    else:
        conflict = "no meaningful pivot conflict"

    if len(stretch_notes) >= 2:
        stretch = "heavily stretched"
    elif len(stretch_notes) == 1:
        stretch = "moderately stretched"
    else:
        stretch = "not stretched"

    return {
        "pivot_regime": " | ".join(f"{n}: {r}" for n, r in regime_votes) if regime_votes else "unclear",
        "pivot_zone_fit": fit,
        "pivot_confluence": confluence,
        "pivot_conflict": conflict,
        "pivot_stretch": stretch,
        "pivot_alignment_ratio": round(aligned / max(1, aligned + misaligned), 3),
    }

# =========================================================
# SESSION QUALITY
# =========================================================
def current_session_quality(h1: pd.DataFrame) -> str:
    ts = last_timestamp_from_df(last_completed(h1))
    hour = pd.Timestamp(ts).hour
    dow = pd.Timestamp(ts).dayofweek

    if dow == 0 and hour < 5:
        return "acceptable but not ideal"
    if dow == 4 and hour >= 12:
        return "acceptable but not ideal"
    if 2 <= hour <= 5 or 8 <= hour <= 11:
        return "valid session logic"
    if 0 <= hour <= 1 or 6 <= hour <= 7 or 12 <= hour <= 14:
        return "acceptable but not ideal"
    return "poor timing"

# =========================================================
# RELATIVE STRENGTH / WEAKNESS
# =========================================================
def compute_currency_strength(cache: dict, tf: str = "D1") -> dict:
    strength = defaultdict(list)

    for sym, data in cache.items():
        if data is None:
            continue
        h1, d1, w1 = data
        df = {"H1": h1, "D1": d1, "W1": w1}[tf]
        x = last_completed(df)

        if len(x) < 4:
            continue

        ret = float(x.iloc[-1]["close"] / x.iloc[-4]["close"] - 1.0)
        base, quote = pair_currencies(sym)

        strength[base].append(ret)
        strength[quote].append(-ret)

    all_ccy = sorted({c for s in SYMBOLS for c in pair_currencies(s)})
    out = {}
    for c in all_ccy:
        vals = strength.get(c, [])
        out[c] = float(np.mean(vals)) if vals else 0.0
    return out

def pair_rs_alignment(sym: str, d1_strength: dict, bias: str) -> str:
    base, quote = pair_currencies(sym)
    diff = d1_strength.get(base, 0.0) - d1_strength.get(quote, 0.0)

    if bias == "BULLISH":
        if diff > 0.001:
            return "clear alignment"
        if diff > -0.001:
            return "mixed"
        return "no clear alignment"

    if bias == "BEARISH":
        if diff < -0.001:
            return "clear alignment"
        if diff < 0.001:
            return "mixed"
        return "no clear alignment"

    return "mixed"

# =========================================================
# SMT BONUS
# =========================================================
def detect_smt_hint(sym: str, cache: dict) -> str:
    peers = {
        "EURUSD": "GBPUSD",
        "GBPUSD": "EURUSD",
        "AUDUSD": "NZDUSD",
        "NZDUSD": "AUDUSD",
        "EURJPY": "GBPJPY",
        "GBPJPY": "EURJPY",
        "AUDJPY": "NZDJPY",
        "NZDJPY": "AUDJPY",
        "AUDCHF": "NZDCHF",
        "NZDCHF": "AUDCHF",
        "AUDCAD": "NZDCAD",
        "NZDCAD": "AUDCAD",
        "EURAUD": "GBPAUD",
        "GBPAUD": "EURAUD",
        "EURNZD": "GBPNZD",
        "GBPNZD": "EURNZD",
    }
    peer = peers.get(sym)
    if not peer or cache.get(sym) is None or cache.get(peer) is None:
        return "none"

    df1 = last_completed(cache[sym][0]).reset_index(drop=True)
    df2 = last_completed(cache[peer][0]).reset_index(drop=True)
    if len(df1) < 5 or len(df2) < 5:
        return "none"

    hh1 = float(df1.iloc[-1]["high"]) > float(df1.iloc[-4:-1]["high"].max())
    hh2 = float(df2.iloc[-1]["high"]) > float(df2.iloc[-4:-1]["high"].max())
    ll1 = float(df1.iloc[-1]["low"]) < float(df1.iloc[-4:-1]["low"].min())
    ll2 = float(df2.iloc[-1]["low"]) < float(df2.iloc[-4:-1]["low"].min())

    if (hh1 ^ hh2) or (ll1 ^ ll2):
        return "clear SMT confirmation"
    return "none"

# =========================================================
# ICT ARRAYS + CONFLUENCE
# =========================================================
def detect_fvgs(h1: pd.DataFrame, lookback: int):
    zones = []
    df = last_completed(h1).copy().reset_index(drop=True)
    start = max(2, len(df) - lookback)

    for i in range(start, len(df)):
        hi_2 = df.loc[i - 2, "high"]
        lo_2 = df.loc[i - 2, "low"]
        hi_i = df.loc[i, "high"]
        lo_i = df.loc[i, "low"]

        if lo_i > hi_2:
            zones.append({
                "type": "FVG",
                "dir": "BULL",
                "lo": float(hi_2),
                "hi": float(lo_i),
                "created_idx": i,
            })

        if hi_i < lo_2:
            zones.append({
                "type": "FVG",
                "dir": "BEAR",
                "lo": float(hi_i),
                "hi": float(lo_2),
                "created_idx": i,
            })

    return [z for z in zones if z["hi"] > z["lo"]]

def detect_gaps(h1: pd.DataFrame, lookback: int, atr_mult: float = GAP_ATR_MULT):
    df = last_completed(h1).copy().reset_index(drop=True)
    df["atr"] = atr(df, ATR_LEN)
    zones = []
    start = max(1, len(df) - lookback)

    for i in range(start, len(df)):
        prev_close = float(df.loc[i - 1, "close"])
        cur_open = float(df.loc[i, "open"])
        a = df.loc[i, "atr"]
        if pd.isna(a) or a <= 0:
            continue

        thresh = float(a) * atr_mult
        diff = cur_open - prev_close
        if abs(diff) < thresh:
            continue

        if diff > 0:
            zones.append({
                "type": "GAP",
                "dir": "UP",
                "lo": prev_close,
                "hi": cur_open,
                "created_idx": i,
            })
        else:
            zones.append({
                "type": "GAP",
                "dir": "DOWN",
                "lo": cur_open,
                "hi": prev_close,
                "created_idx": i,
            })

    return [z for z in zones if z["hi"] > z["lo"]]

def detect_orderblocks(h1: pd.DataFrame, lookback: int):
    df = last_completed(h1).copy().reset_index(drop=True)
    n = len(df)
    if n < 60:
        return []

    df["body"] = (df["close"] - df["open"]).abs()
    sh, sl = _find_swings(df, SWING_LEN)
    zones = []
    start = max(2, n - lookback)

    for i in range(start, n):
        j0 = max(0, i - 50)
        med_body = float(df.loc[j0:i, "body"].median())
        if med_body <= 0:
            continue

        body_i = float(df.loc[i, "body"])
        if body_i < DISPLACEMENT_K * med_body:
            continue

        o_i = float(df.loc[i, "open"])
        c_i = float(df.loc[i, "close"])
        dir_i = "UP" if c_i > o_i else "DOWN" if c_i < o_i else "FLAT"
        if dir_i == "FLAT":
            continue

        lb0 = max(0, i - BOS_LOOKBACK)
        prior_sw_highs = [k for k in range(lb0, i) if sh[k]]
        prior_sw_lows = [k for k in range(lb0, i) if sl[k]]

        broke_up = False
        broke_down = False
        if prior_sw_highs:
            last_sh = prior_sw_highs[-1]
            if float(df.loc[i, "high"]) > float(df.loc[last_sh, "high"]):
                broke_up = True
        if prior_sw_lows:
            last_sl = prior_sw_lows[-1]
            if float(df.loc[i, "low"]) < float(df.loc[last_sl, "low"]):
                broke_down = True

        if dir_i == "UP" and not broke_up:
            continue
        if dir_i == "DOWN" and not broke_down:
            continue

        ob_idx = i - 1
        o_ob = float(df.loc[ob_idx, "open"])
        c_ob = float(df.loc[ob_idx, "close"])
        ob_dir = "DOWN" if c_ob < o_ob else "UP" if c_ob > o_ob else "FLAT"

        if dir_i == "UP" and ob_dir != "DOWN":
            continue
        if dir_i == "DOWN" and ob_dir != "UP":
            continue

        lo = min(o_ob, c_ob)
        hi = max(o_ob, c_ob)
        if hi <= lo:
            continue

        zones.append({
            "type": "OB",
            "dir": "BULL" if dir_i == "UP" else "BEAR",
            "lo": lo,
            "hi": hi,
            "created_idx": ob_idx,
        })

    return zones

def classify_array_quality(entry_zones: list) -> str:
    if not entry_zones:
        return "weak"

    z = entry_zones[0]
    arrays = set(z["arrays"])
    touches = z.get("touches", 99)
    deep = z.get("deep_mitigated", False)

    if deep or touches >= 3:
        return "weak"
    if len(arrays) >= 2 and touches <= 1:
        return "strong"
    if len(arrays) >= 1 and touches <= 2:
        return "good"
    return "average"

def ict_ote_zone_from_range(dealing: dict, bias: str):
    hi, lo, rng = dealing["hi"], dealing["lo"], dealing["range"]
    if rng <= 0:
        return None

    if bias == "BULLISH":
        z_hi = hi - OTE_LOW * rng
        z_lo = hi - OTE_HIGH * rng
        return (min(z_lo, z_hi), max(z_lo, z_hi))

    if bias == "BEARISH":
        z_lo = lo + OTE_LOW * rng
        z_hi = lo + OTE_HIGH * rng
        return (min(z_lo, z_hi), max(z_lo, z_hi))

    return None

def build_confluence_entry_zones(h1: pd.DataFrame, d_info: dict, dealing: dict):
    bias = d_info["bias"]
    if bias not in ("BULLISH", "BEARISH"):
        return []

    ote = ict_ote_zone_from_range(dealing, bias)
    if REQUIRE_OTE and not ote:
        return []

    eq = dealing["eq"]

    def side_ok(lo, hi):
        mid = (lo + hi) / 2.0
        return mid <= eq if bias == "BULLISH" else mid >= eq

    fvgs = detect_fvgs(h1, FVG_LOOKBACK_BARS)
    obs = detect_orderblocks(h1, OB_LOOKBACK_BARS)
    gaps = detect_gaps(h1, GAP_LOOKBACK_BARS, GAP_ATR_MULT)

    fvgs = [z for z in fvgs if ((bias == "BULLISH" and z["dir"] == "BULL") or (bias == "BEARISH" and z["dir"] == "BEAR"))]
    obs = [z for z in obs if ((bias == "BULLISH" and z["dir"] == "BULL") or (bias == "BEARISH" and z["dir"] == "BEAR"))]
    gaps = [z for z in gaps if ((bias == "BULLISH" and z["dir"] == "DOWN") or (bias == "BEARISH" and z["dir"] == "UP"))]

    fvgs = [z for z in fvgs if side_ok(z["lo"], z["hi"])]
    obs = [z for z in obs if side_ok(z["lo"], z["hi"])]
    gaps = [z for z in gaps if side_ok(z["lo"], z["hi"])]

    candidates = []

    def add_candidate(zone_lo, zone_hi, arrays_used, source_idx):
        ov = _overlap(zone_lo, zone_hi, ote[0], ote[1])
        if ov is None:
            return

        used_types = set(arrays_used)
        if not (used_types & REQUIRE_AT_LEAST_ONE_OF):
            return

        candidates.append({
            "lo": ov[0],
            "hi": ov[1],
            "arrays": sorted(list(used_types)),
            "created_idx": source_idx,
        })

    for f in fvgs:
        add_candidate(f["lo"], f["hi"], {"FVG"}, f["created_idx"])
    for o in obs:
        add_candidate(o["lo"], o["hi"], {"OB"}, o["created_idx"])

    for f in fvgs:
        for o in obs:
            ov1 = _overlap(f["lo"], f["hi"], o["lo"], o["hi"])
            if ov1 and side_ok(ov1[0], ov1[1]):
                add_candidate(ov1[0], ov1[1], {"FVG", "OB"}, max(f["created_idx"], o["created_idx"]))

    if gaps and candidates:
        enriched = []
        for c in candidates:
            hit = False
            for g in gaps:
                ov = _overlap(c["lo"], c["hi"], g["lo"], g["hi"])
                if ov:
                    new_c = dict(c)
                    new_c["lo"] = ov[0]
                    new_c["hi"] = ov[1]
                    new_c["arrays"] = sorted(list(set(c["arrays"]) | {"GAP"}))
                    new_c["created_idx"] = max(c["created_idx"], g["created_idx"])
                    enriched.append(new_c)
                    hit = True
            if not hit:
                enriched.append(c)
        candidates = enriched

    uniq = {}
    df = last_completed(h1).copy().reset_index(drop=True)

    for c in candidates:
        fresh = zone_freshness(df, {
            "lo": c["lo"],
            "hi": c["hi"],
            "dir": "BEAR" if bias == "BEARISH" else "BULL",
            "created_idx": c["created_idx"],
        })
        score = 1
        score += 1 if "FVG" in c["arrays"] else 0
        score += 1 if "OB" in c["arrays"] else 0
        score += 1 if "GAP" in c["arrays"] else 0
        score += 1 if fresh["touches"] <= 1 else 0
        score -= 1 if fresh["deep_mitigated"] else 0

        row = dict(c)
        row["touches"] = fresh["touches"]
        row["deep_mitigated"] = fresh["deep_mitigated"]
        row["score"] = score

        key = (round(row["lo"], 6), round(row["hi"], 6), tuple(row["arrays"]))
        if key not in uniq or row["score"] > uniq[key]["score"]:
            uniq[key] = row

    out = list(uniq.values())
    out.sort(key=lambda z: (-z["score"], z["touches"], (z["hi"] - z["lo"])))
    return out[:MAX_ENTRY_ZONES_TO_PLOT]

# =========================================================
# TECHNICAL SCORE PACKAGE
# =========================================================
def score_bias_clarity(w_bias: str, d_bias: str):
    if w_bias == d_bias and w_bias != "NEUTRAL":
        return 0.5, "aligned"
    if "NEUTRAL" in (w_bias, d_bias):
        return 0.1, "mild conflict"
    return 0.25, "full conflict"

def score_dealing_location(d_bias: str, side: str, dealing: dict) -> float:
    if not dealing["is_clear"] or dealing["range"] <= 0:
        return 0.0
    if d_bias == "BEARISH" and side == "premium":
        return 0.5
    if d_bias == "BULLISH" and side == "discount":
        return 0.5
    if side in ("premium", "discount"):
        return 0.25
    return 0.0

def score_liquidity(liq: dict) -> float:
    if liq["condition"] != "external liquidity taken":
        return 0.15 if liq["condition"] == "internal liquidity only" else 0.0
    score = 0.25
    if liq.get("liquidity_tier") == "major":
        score += 0.10
    if liq.get("sweep_quality") == "sweep + close back inside range":
        score += 0.10
    if liq.get("rejection_quality") == "strong rejection":
        score += 0.15
    elif liq.get("rejection_quality") == "moderate rejection":
        score += 0.05
    if liq.get("follow_through") == "clean follow-through":
        score += 0.05
    if liq.get("both_sides_taken_recently"):
        score -= 0.05
    return max(0.0, min(0.65, score))

def score_displacement(displacement: dict) -> float:
    if displacement["quality"] == "strong displacement":
        return 0.55
    if displacement["quality"] == "moderate displacement":
        return 0.30
    return 0.0

def score_mss(mss: dict) -> float:
    if mss["status"] == "clear MSS/BOS":
        return 0.55
    if mss["status"] == "partial shift":
        return 0.25
    return 0.0

def score_array_quality(array_quality: str) -> float:
    if array_quality == "strong":
        return 0.5
    if array_quality in ("good", "average"):
        return 0.25
    return 0.0

def score_session(session_quality: str) -> float:
    if session_quality == "valid session logic":
        return 0.45
    if session_quality == "acceptable but not ideal":
        return 0.20
    return 0.0

def score_rs(rs_alignment: str) -> float:
    if rs_alignment == "clear alignment":
        return 0.45
    if rs_alignment == "mixed":
        return 0.20
    return 0.0

def score_smt(smt_hint: str) -> float:
    if not USE_SMT_BONUS:
        return 0.0
    if smt_hint == "clear SMT confirmation":
        return 0.20
    return 0.0

def score_pivots(pivot_context: dict) -> float:
    score = 0.0
    if pivot_context["pivot_zone_fit"] in {"price in buy zone", "price in sell zone"}:
        score += 0.25
    if pivot_context["pivot_confluence"] == "daily + weekly + monthly aligned":
        score += 0.30
    elif pivot_context["pivot_confluence"] == "daily + weekly aligned":
        score += 0.20
    elif pivot_context["pivot_confluence"] == "daily only":
        score += 0.10
    if pivot_context["pivot_conflict"] == "strong pivot conflict":
        score -= 0.35
    elif pivot_context["pivot_conflict"] == "mild pivot conflict":
        score -= 0.15
    if pivot_context["pivot_stretch"] == "heavily stretched":
        score -= 0.25
    elif pivot_context["pivot_stretch"] == "moderately stretched":
        score -= 0.10
    return score

def entry_label_from_metrics(displacement: dict, mss: dict, array_quality: str, session_quality: str, pivot_context: dict, liq: dict) -> str:
    strong_disp = displacement["quality"] == "strong displacement"
    clear_mss = mss["status"] == "clear MSS/BOS"
    strong_array = array_quality == "strong"
    valid_session = session_quality == "valid session logic"
    good_pivot = pivot_context["pivot_conflict"] == "no meaningful pivot conflict" and pivot_context["pivot_stretch"] != "heavily stretched"
    meaningful_rejection = liq.get("rejection_quality") in {"strong rejection", "moderate rejection"}

    if strong_disp and clear_mss and strong_array and valid_session and good_pivot and meaningful_rejection:
        return "A-tier execution setup"
    if array_quality in ("strong", "good") and mss["status"] in ("clear MSS/BOS", "partial shift") and pivot_context["pivot_conflict"] != "strong pivot conflict":
        return "B-tier reactive setup"
    if array_quality in ("good", "average"):
        return "C-tier idea only"
    return "D-tier avoid"

def apply_penalties(score: float, displacement: dict, mss: dict, best_zone, session_quality: str, rs_alignment: str, pivot_context: dict, liq: dict) -> float:
    penalties = 0.0
    if displacement["quality"] == "weak / no displacement":
        penalties -= 0.5
    if mss["status"] == "no clear shift":
        penalties -= 0.45
    if best_zone and best_zone.get("deep_mitigated", False):
        penalties -= 0.5
    if session_quality == "poor timing":
        penalties -= 0.45
    elif session_quality == "acceptable but not ideal":
        penalties -= 0.20
    if rs_alignment == "no clear alignment":
        penalties -= 0.35
    elif rs_alignment == "mixed":
        penalties -= 0.15
    if pivot_context["pivot_conflict"] == "strong pivot conflict":
        penalties -= 0.35
    if pivot_context["pivot_stretch"] == "heavily stretched":
        penalties -= 0.25
    if liq.get("condition") == "external liquidity taken" and liq.get("rejection_quality") == "weak/no rejection":
        penalties -= 0.30
    return max(0.0, min(4.0, score + penalties))

def compute_legacy_confidence(data_quality: str, liq: dict, disp: dict, mss: dict, pivot_context: dict) -> dict:
    score = 0.50
    if data_quality == "good":
        score += 0.15
    if liq.get("condition") == "external liquidity taken":
        score += 0.10
    if liq.get("rejection_quality") == "strong rejection":
        score += 0.10
    if disp.get("quality") == "strong displacement":
        score += 0.10
    if mss.get("status") == "clear MSS/BOS":
        score += 0.10
    if pivot_context.get("pivot_conflict") == "strong pivot conflict":
        score -= 0.15
    if pivot_context.get("pivot_stretch") == "heavily stretched":
        score -= 0.10
    score = max(0.05, min(0.99, score))
    band = "high" if score >= LEGACY_HIGH_CONFIDENCE_MIN_SCORE else "medium" if score >= LEGACY_MEDIUM_CONFIDENCE_MIN_SCORE else "low"
    return {"score": round(score, 3), "band": band}


def compute_confidence(data_quality: str, liq: dict, disp: dict, mss: dict, pivot_context: dict) -> dict:
    legacy = compute_legacy_confidence(data_quality, liq, disp, mss, pivot_context)
    score10 = 5.0
    if data_quality == "good":
        score10 += 0.6
    elif data_quality == "poor":
        score10 -= 1.0
    if liq.get("condition") == "external liquidity taken":
        score10 += 0.4
    if liq.get("tier") == "major":
        score10 += 0.4
    if liq.get("rejection_quality") == "strong rejection":
        score10 += 0.9
    elif liq.get("rejection_quality") == "moderate rejection":
        score10 += 0.4
    else:
        score10 -= 0.5
    if disp.get("quality") == "strong displacement":
        score10 += 0.7
    elif disp.get("quality") == "moderate displacement":
        score10 += 0.3
    else:
        score10 -= 0.9
    if mss.get("status") == "clear MSS/BOS":
        score10 += 0.6
    elif mss.get("status") == "partial shift":
        score10 += 0.2
    else:
        score10 -= 0.5
    if pivot_context.get("pivot_conflict") == "strong pivot conflict":
        score10 -= 1.1
    elif pivot_context.get("pivot_conflict") == "minor pivot conflict":
        score10 -= 0.3
    if pivot_context.get("pivot_stretch") == "heavily stretched":
        score10 -= 0.8
    elif pivot_context.get("pivot_stretch") == "stretched":
        score10 -= 0.3
    if legacy["band"] == "high":
        score10 -= 0.5
    elif legacy["band"] == "medium":
        score10 += 0.2
    score10 = max(0.0, min(10.0, score10))
    score = round(score10 / 10.0, 3)
    band = "high" if score >= HIGH_CONFIDENCE_MIN_SCORE else "medium" if score >= MEDIUM_CONFIDENCE_MIN_SCORE else "low"
    return {
        "score": score,
        "band": band,
        "score_10": round(score10, 2),
        "legacy_score": legacy["score"],
        "legacy_band": legacy["band"],
    }

# =========================================================
# EXECUTION PLAN HELPERS
# =========================================================
def compute_rr_metrics(preferred_side: str, entry, sl, tp1, tp2) -> dict:
    try:
        entry = float(entry); sl = float(sl); tp1 = float(tp1); tp2 = float(tp2)
    except Exception:
        return {"risk": None, "rr_tp1": None, "rr_tp2": None}
    if not all(np.isfinite(v) for v in [entry, sl, tp1, tp2]):
        return {"risk": None, "rr_tp1": None, "rr_tp2": None}

    risk = abs(entry - sl)
    if risk <= 0:
        return {"risk": None, "rr_tp1": None, "rr_tp2": None}

    rr_tp1 = abs(tp1 - entry) / risk
    rr_tp2 = abs(tp2 - entry) / risk
    return {
        "risk": float(risk),
        "rr_tp1": round(float(rr_tp1), 4),
        "rr_tp2": round(float(rr_tp2), 4),
    }


def outcome_return_multiple(outcome_label: str, rr_tp1, rr_tp2, partial_fraction: float = TP1_PARTIAL_EXIT_FRACTION) -> dict:
    try:
        rr_tp1 = float(rr_tp1) if rr_tp1 is not None and np.isfinite(rr_tp1) else None
        rr_tp2 = float(rr_tp2) if rr_tp2 is not None and np.isfinite(rr_tp2) else None
    except Exception:
        rr_tp1 = None
        rr_tp2 = None

    outcome = str(outcome_label or "")
    realized = 0.0
    weighted = 0.0

    if outcome == "stopped":
        realized = -1.0
        weighted = -1.0
    elif outcome == "tp2_hit":
        realized = rr_tp2 if rr_tp2 is not None else 0.0
        if rr_tp1 is not None and rr_tp2 is not None:
            weighted = partial_fraction * rr_tp1 + (1.0 - partial_fraction) * rr_tp2
        else:
            weighted = realized
    elif outcome == "tp1_then_stop":
        realized = rr_tp1 if rr_tp1 is not None else 0.0
        weighted = (partial_fraction * rr_tp1) if rr_tp1 is not None else 0.0
    elif outcome == "tp1_only_open":
        realized = rr_tp1 if rr_tp1 is not None else 0.0
        weighted = (partial_fraction * rr_tp1) if rr_tp1 is not None else 0.0
    elif outcome in {"not_triggered", "triggered_no_resolution", "ambiguous_same_bar", "no_forward_data", "invalid_execution_values", "no_trade_plan"}:
        realized = 0.0
        weighted = 0.0

    return {
        "R_Multiple": round(float(realized), 4),
        "Weighted_Return_R": round(float(weighted), 4),
    }


def derive_execution_plan(sym: str, h1: pd.DataFrame, d_info: dict, w_info: dict, ict_pack: dict) -> dict:
    entry_zones = ict_pack["entry_zones"]
    bias = d_info["bias"]
    side = None
    entry = None
    sl = None
    tp1 = None
    tp2 = None
    execution_source = "zone"

    h1x = _ensure_dt_index(h1)
    current = float(h1x.iloc[-1]["close"]) if h1x is not None and not h1x.empty else None
    atr_h1 = None
    try:
        atr_series = atr(last_completed(h1), ATR_LEN)
        if len(atr_series.dropna()) > 0:
            atr_h1 = float(atr_series.dropna().iloc[-1])
    except Exception:
        atr_h1 = None
    daily_span = max(float(d_info["pdh"]) - float(d_info["pdl"]), abs(float(current or d_info["eq"])) * 0.001)
    vol = max(atr_h1 or 0.0, daily_span * 0.18, abs(float(current or d_info["eq"])) * 0.0008)

    def _finalize_levels(_side, _entry, _sl, structural_tp1, structural_tp2):
        base_risk = abs(_sl - _entry)
        base_risk = max(base_risk, vol * 0.35, abs(_entry) * 0.0005)
        risk = base_risk * SL_DISTANCE_MULTIPLIER
        if _side == "SHORT":
            _sl = _entry + risk
            tp1_floor = _entry - max(TP1_DISTANCE_MULTIPLIER * 0.9 * risk, TP1_DISTANCE_MULTIPLIER * 0.45 * vol)
            tp2_floor = _entry - max(TP2_DISTANCE_MULTIPLIER * TP2_REALISM_RISK_CAP * risk, TP2_DISTANCE_MULTIPLIER * TP2_REALISM_VOL_CAP * vol)
            _tp1 = max(float(structural_tp1), tp1_floor)
            _tp1 = min(_tp1, _entry - max(TP1_DISTANCE_MULTIPLIER * 0.35 * risk, TP1_DISTANCE_MULTIPLIER * 0.20 * vol))
            _tp2 = max(float(structural_tp2), tp2_floor)
            _tp2 = min(_tp2, _entry - max(TP2_DISTANCE_MULTIPLIER * 1.00 * risk, TP2_DISTANCE_MULTIPLIER * 0.50 * vol))
            if _tp2 >= _tp1:
                _tp2 = _tp1 - max(TP2_DISTANCE_MULTIPLIER * 0.55 * risk, TP2_DISTANCE_MULTIPLIER * 0.30 * vol)
        else:
            _sl = _entry - risk
            tp1_cap = _entry + max(TP1_DISTANCE_MULTIPLIER * 0.9 * risk, TP1_DISTANCE_MULTIPLIER * 0.45 * vol)
            tp2_cap = _entry + max(TP2_DISTANCE_MULTIPLIER * TP2_REALISM_RISK_CAP * risk, TP2_DISTANCE_MULTIPLIER * TP2_REALISM_VOL_CAP * vol)
            _tp1 = min(float(structural_tp1), tp1_cap)
            _tp1 = max(_tp1, _entry + max(TP1_DISTANCE_MULTIPLIER * 0.35 * risk, TP1_DISTANCE_MULTIPLIER * 0.20 * vol))
            _tp2 = min(float(structural_tp2), tp2_cap)
            _tp2 = max(_tp2, _entry + max(TP2_DISTANCE_MULTIPLIER * 1.00 * risk, TP2_DISTANCE_MULTIPLIER * 0.50 * vol))
            if _tp2 <= _tp1:
                _tp2 = _tp1 + max(TP2_DISTANCE_MULTIPLIER * 0.55 * risk, TP2_DISTANCE_MULTIPLIER * 0.30 * vol)
        return _entry, _sl, _tp1, _tp2

    if entry_zones and current is not None:
        z = entry_zones[0]
        lo = float(z["lo"])
        hi = float(z["hi"])
        zone_w = max(hi - lo, abs((lo + hi) / 2.0) * 0.0001)

        if bias == "BEARISH":
            side = "SHORT"
            entry = lo + TRIGGER_PROXIMITY_ZONE_FRACTION * zone_w
            if current >= lo and current <= hi:
                entry = min(max(current, lo), hi)
            sl = hi + 0.22 * zone_w
            structural_tp1 = min(float(d_info["eq"]), entry - max(0.40 * zone_w, 0.25 * vol))
            structural_tp2 = min(float(d_info["pdl"]), float(w_info["pwl"]))
            entry, sl, tp1, tp2 = _finalize_levels(side, entry, sl, structural_tp1, structural_tp2)
        elif bias == "BULLISH":
            side = "LONG"
            entry = hi - TRIGGER_PROXIMITY_ZONE_FRACTION * zone_w
            if current >= lo and current <= hi:
                entry = min(max(current, lo), hi)
            sl = lo - 0.22 * zone_w
            structural_tp1 = max(float(d_info["eq"]), entry + max(0.40 * zone_w, 0.25 * vol))
            structural_tp2 = max(float(d_info["pdh"]), float(w_info["pwh"]))
            entry, sl, tp1, tp2 = _finalize_levels(side, entry, sl, structural_tp1, structural_tp2)
    else:
        execution_source = "fallback"
        if current is not None and bias in {"BULLISH", "BEARISH"}:
            d_eq = float(d_info["eq"])
            if bias == "BEARISH":
                side = "SHORT"
                entry = current + TRIGGER_PROXIMITY_FALLBACK_VOL * vol
                entry = min(entry, max(d_eq, current + 0.35 * vol))
                entry = max(entry, current + 0.03 * vol)
                sl = entry + max(0.85 * vol, abs(entry) * 0.0008)
                structural_tp1 = min(d_eq, entry - max(0.70 * vol, abs(entry) * 0.0010))
                structural_tp2 = min(float(d_info["pdl"]), float(w_info["pwl"]), entry - max(1.10 * vol, abs(entry) * 0.0015))
                entry, sl, tp1, tp2 = _finalize_levels(side, entry, sl, structural_tp1, structural_tp2)
            elif bias == "BULLISH":
                side = "LONG"
                entry = current - TRIGGER_PROXIMITY_FALLBACK_VOL * vol
                entry = max(entry, min(d_eq, current - 0.35 * vol))
                entry = min(entry, current - 0.03 * vol)
                sl = entry - max(0.85 * vol, abs(entry) * 0.0008)
                structural_tp1 = max(d_eq, entry + max(0.70 * vol, abs(entry) * 0.0010))
                structural_tp2 = max(float(d_info["pdh"]), float(w_info["pwh"]), entry + max(1.10 * vol, abs(entry) * 0.0015))
                entry, sl, tp1, tp2 = _finalize_levels(side, entry, sl, structural_tp1, structural_tp2)

    if side is None or any(v is None for v in [entry, sl, tp1, tp2]):
        return {
            "preferred_side": None,
            "entry": None,
            "calibration_entry": None,
            "sl": None,
            "tp1": None,
            "tp2": None,
            "entry_text": "Entry/SL/TP levels not reliably readable",
            "execution_source": execution_source,
            "entry_distance_atr": None,
        }

    structural_entry = float(entry)
    calibration_entry = structural_entry
    atr_ref = max(float(atr_h1 or 0.0), max(abs(float(current or structural_entry)) * 0.0006, 1e-9))
    if current is not None:
        if side == "SHORT":
            zone_entry = current + CALIBRATION_ZONE_FRACTION * vol if execution_source == "zone" else current + CALIBRATION_FALLBACK_VOL * vol
            max_entry = current + (CALIBRATION_B_BOOK_MAX_ENTRY_ATR * atr_ref)
            calibration_entry = min(structural_entry, max(zone_entry, current + 0.02 * vol))
            calibration_entry = min(calibration_entry, max_entry)
            calibration_entry = max(calibration_entry, current + 0.01 * vol)
        else:
            zone_entry = current - CALIBRATION_ZONE_FRACTION * vol if execution_source == "zone" else current - CALIBRATION_FALLBACK_VOL * vol
            min_entry = current - (CALIBRATION_B_BOOK_MAX_ENTRY_ATR * atr_ref)
            calibration_entry = max(structural_entry, min(zone_entry, current - 0.02 * vol))
            calibration_entry = max(calibration_entry, min_entry)
            calibration_entry = min(calibration_entry, current - 0.01 * vol)

        if side == "SHORT":
            old_risk = max(sl - structural_entry, 1e-9) * SL_DISTANCE_MULTIPLIER
            sl = calibration_entry + old_risk
            tp1 = calibration_entry - max(TP1_DISTANCE_MULTIPLIER * 0.90 * old_risk, TP1_DISTANCE_MULTIPLIER * 0.40 * vol)
            tp2 = calibration_entry - max(TP2_DISTANCE_MULTIPLIER * 1.35 * old_risk, TP2_DISTANCE_MULTIPLIER * 0.60 * vol)
            if tp2 >= tp1:
                tp2 = tp1 - max(TP2_DISTANCE_MULTIPLIER * 0.45 * old_risk, TP2_DISTANCE_MULTIPLIER * 0.25 * vol)
        else:
            old_risk = max(structural_entry - sl, 1e-9) * SL_DISTANCE_MULTIPLIER
            sl = calibration_entry - old_risk
            tp1 = calibration_entry + max(TP1_DISTANCE_MULTIPLIER * 0.90 * old_risk, TP1_DISTANCE_MULTIPLIER * 0.40 * vol)
            tp2 = calibration_entry + max(TP2_DISTANCE_MULTIPLIER * 1.35 * old_risk, TP2_DISTANCE_MULTIPLIER * 0.60 * vol)
            if tp2 <= tp1:
                tp2 = tp1 + max(TP2_DISTANCE_MULTIPLIER * 0.45 * old_risk, TP2_DISTANCE_MULTIPLIER * 0.25 * vol)

    entry = round_price(sym, calibration_entry)
    structural_entry = round_price(sym, structural_entry)
    sl = round_price(sym, sl)
    tp1 = round_price(sym, tp1)
    tp2 = round_price(sym, tp2)
    entry_distance_atr = None
    if current is not None and atr_ref > 0:
        entry_distance_atr = round(abs(float(entry) - float(current)) / atr_ref, 3)

    rr_metrics = compute_rr_metrics(side, entry, sl, tp1, tp2)

    if side == "SHORT":
        entry_text = f"Sell-limit: {entry} | SL: {sl} | TP1: {tp1} | TP2: {tp2} | RR1: {rr_metrics['rr_tp1']} | RR2: {rr_metrics['rr_tp2']}"
    elif side == "LONG":
        entry_text = f"Buy-limit: {entry} | SL: {sl} | TP1: {tp1} | TP2: {tp2} | RR1: {rr_metrics['rr_tp1']} | RR2: {rr_metrics['rr_tp2']}"
    else:
        entry_text = "Entry/SL/TP levels not reliably readable"

    return {
        "preferred_side": side,
        "entry": entry,
        "calibration_entry": entry,
        "structural_entry": structural_entry,
        "sl": sl,
        "tp1": tp1,
        "tp2": tp2,
        "rr_tp1": rr_metrics["rr_tp1"],
        "rr_tp2": rr_metrics["rr_tp2"],
        "entry_text": entry_text,
        "execution_source": execution_source,
        "entry_distance_atr": entry_distance_atr,
    }

# =========================================================
# CLUSTER TAGGING / OVERLAP PENALTY / SHORTLIST
# =========================================================
def detect_clusters(sym: str, preferred_side: str, w_bias: str, d_bias: str) -> list:
    base, quote = pair_currencies(sym)
    tags = []

    currencies = {base, quote}

    if "USD" in currencies:
        tags.append("USD basket")
    if "JPY" in currencies:
        tags.append("JPY cluster")
    if "CHF" in currencies:
        tags.append("CHF haven cluster")
    if "EUR" in currencies and quote != "USD":
        tags.append("EUR relative-value cluster")
    if currencies & {"AUD", "NZD", "CAD"}:
        tags.append("commodity bloc")
    if currencies & {"MXN", "ZAR"}:
        tags.append("EM carry block")

    if preferred_side == "SHORT" and quote == "JPY":
        tags.append("risk-off short")
    if preferred_side == "LONG" and base == "USD" and quote in {"MXN", "ZAR"}:
        tags.append("EM unwind long USD")
    if preferred_side == "SHORT" and base == "EUR":
        tags.append("EUR weakness")
    if preferred_side == "SHORT" and quote == "CHF":
        tags.append("CHF strength")
    if preferred_side == "LONG" and base == "USD":
        tags.append("USD strength")
    if preferred_side == "SHORT" and quote == "USD":
        tags.append("USD weakness")
    if w_bias == d_bias:
        tags.append("HTF aligned")
    else:
        tags.append("HTF conflict")

    return sorted(set(tags))

def layer_bonus(sym: str) -> float:
    if sym in LAYER_1:
        return 0.30
    if sym in LAYER_2:
        return 0.15
    if sym in LAYER_3:
        return 0.05
    return 0.0

def tradability_bonus(sym: str) -> float:
    if sym in LAYER_1:
        return 0.20
    if sym in {"USDMXN", "USDZAR"}:
        return -0.10
    return 0.0

def execution_bonus(entry_label: str) -> float:
    return {
        "A-tier execution setup": 0.30,
        "B-tier reactive setup": 0.00,
        "C-tier idea only": -0.05,
        "D-tier avoid": -0.60,
    }.get(entry_label, 0.0)


def uniqueness_penalty(sym: str, tags: list, used_currency_counter: Counter, used_cluster_counter: Counter) -> float:
    base, quote = pair_currencies(sym)
    penalty = 0.0
    for ccy in (base, quote):
        count = int(used_currency_counter.get(ccy, 0))
        if count == 1:
            penalty += 0.15
        elif count >= 2:
            penalty += 0.35
    for t in tags:
        count = int(used_cluster_counter.get(t, 0))
        if t == "USD basket":
            penalty += 0.25 if count == 1 else 0.75 if count >= 2 else 0.0
        elif t == "JPY cluster":
            penalty += 0.20 if count == 1 else 0.45 if count >= 2 else 0.0
        elif t == "commodity bloc":
            penalty += 0.15 if count == 1 else 0.35 if count >= 2 else 0.0
        elif t == "HTF conflict":
            penalty += 0.20 if count == 1 else 0.45 if count >= 2 else 0.0
        else:
            penalty += 0.10 * count
    return round(penalty, 4)


def _theme_tags(tags: list) -> list:
    return [t for t in tags if t in {"USD basket", "JPY cluster", "commodity bloc", "HTF conflict"}]


def _soft_fail_penalty(fail_reasons: list) -> float:
    s = set(fail_reasons)
    penalty = 0.0
    has_d_tier = "d_tier" in s
    has_weak_impulse = "weak_impulse" in s
    has_stacked_conflict = "stacked_conflict" in s
    if has_d_tier and has_weak_impulse:
        penalty -= 0.45
    elif has_d_tier:
        penalty -= 0.25
    elif has_weak_impulse:
        penalty -= 0.20
    if has_stacked_conflict:
        penalty -= 0.20
    return round(penalty, 4)


def _archetype_rank_adjustment(archetype: str) -> float:
    if archetype == "relative_value_continuation":
        return 0.25
    if archetype == "continuation":
        return -0.20
    if archetype == "reversal_after_sweep":
        return -0.10
    return 0.0


def _book_rank_adjustment(book: str) -> float:
    if book == "B-book":
        return -0.10
    if book in {"Calibration-soft", "Calibration-challenger"}:
        return -0.05
    return 0.0


def _is_diversified_non_usd(tags: list) -> bool:
    themes = set(_theme_tags(tags))
    return bool(themes) and "USD basket" not in themes


def _challenger_adjustment(row: dict, fail_reasons=None) -> float:
    tags = row.get("Cluster_Tags_List", []) or []
    archetype = str(row.get("Setup_Archetype", "") or "")
    conf = float(row.get("Confidence_Score", 0.0) or 0.0)
    fail_reasons = fail_reasons or []
    adj = 0.0
    if _is_diversified_non_usd(tags):
        adj += V37_CHALLENGER_BONUS_DIVERSIFIED
    if archetype == "relative_value_continuation":
        adj += V37_CHALLENGER_BONUS_RELVAL
    if conf < MEDIUM_CONFIDENCE_MIN_SCORE:
        adj += V37_CHALLENGER_BONUS_LOW_CONF
    if archetype == "continuation" and "USD basket" in tags:
        adj += V37_CHALLENGER_PENALTY_CROWDED_CONTINUATION
    if fail_reasons and set(fail_reasons) == {"stacked_conflict"}:
        adj -= 0.10
    return round(adj, 4)


def _v37_candidate_bucket(cal_passed: bool, soft_candidate: bool, fail_reasons: list, row: dict) -> str:
    if cal_passed:
        return "hard_pass"
    fail_set = set(fail_reasons)
    if fail_set & CALIBRATION_HARD_REJECT_REASONS:
        return "hard_reject"
    if soft_candidate:
        if len(fail_set) == 1 or str(row.get("Setup_Archetype", "") or "") == "relative_value_continuation":
            return "challenger"
        return "soft_pass"
    return "hard_reject"


def _row_theme_family(tags: list) -> str:
    themes = _theme_tags(tags)
    if "USD basket" in themes:
        return "USD basket"
    if themes:
        return themes[0]
    return "no_theme"


def _continuation_subquality(row: dict) -> float:
    if str(row.get("Setup_Archetype", "") or "") != "continuation":
        return 0.0
    tags = row.get("Cluster_Tags_List", []) or []
    rejection = str(row.get("Rejection_Quality", "") or "")
    follow = str(row.get("Follow_Through", "") or "")
    liq_tier = str(row.get("Liquidity_Tier", "") or "")
    rs = str(row.get("RS_RW_Alignment", "") or "")
    pivot_conflict = str(row.get("Pivot_Conflict", "") or "")
    pivot_stretch = str(row.get("Pivot_Stretch", "") or "")
    both_sides = bool(row.get("Both_Sides_Taken_Recently", False))
    mss = str(row.get("MSS_BOS", "") or "")
    exec_q = float(row.get("Decision_Execution_Quality", 0.0) or 0.0)
    setup_q = float(row.get("Decision_Setup_Quality", 0.0) or 0.0)
    score = 0.0
    if rejection == "strong rejection":
        score += 0.22
    elif rejection == "moderate rejection":
        score += 0.10
    elif rejection == "weak/no rejection":
        score -= 0.12
    if follow == "clean follow-through":
        score += 0.12
    elif follow == "limited follow-through":
        score -= 0.04
    if liq_tier == "major":
        score += 0.08
    if rs == "clear alignment":
        score += 0.10
    elif rs == "no clear alignment":
        score -= 0.08
    if mss == "clear MSS/BOS":
        score += 0.10
    elif mss == "partial shift":
        score += 0.03
    else:
        score -= 0.10
    if pivot_conflict == "strong pivot conflict":
        score -= 0.20
    elif pivot_conflict == "mild pivot conflict":
        score -= 0.08
    if pivot_stretch == "heavily stretched":
        score -= 0.15
    elif pivot_stretch == "moderately stretched":
        score -= 0.06
    if both_sides:
        score -= 0.10
    if "HTF conflict" in tags:
        score -= 0.12
    if "USD basket" in tags:
        score -= 0.10
    else:
        score += 0.06
    if exec_q >= 1.90:
        score += 0.08
    if setup_q >= 2.00:
        score += 0.06
    return round(score, 4)

def _v41_fragility_reason(row: dict) -> str:
    fail_reasons = [x.strip() for x in str(row.get("Gate_Fail_Reasons", "") or "").split(",") if x.strip()]
    fail_set = set(fail_reasons)
    archetype = str(row.get("Setup_Archetype", "") or "")
    tags = row.get("Cluster_Tags_List", []) or []
    book = str(row.get("Decision_Book", "") or "")
    exec_q = float(row.get("Decision_Execution_Quality", 0.0) or 0.0)
    setup_q = float(row.get("Decision_Setup_Quality", 0.0) or 0.0)
    cont_subq = float(row.get("Continuation_Subquality", 0.0) or 0.0)
    if row.get("Calibration_Candidate_Bucket") == "hard_reject":
        return "hard_reject"
    if "stacked_conflict" in fail_set:
        return "stacked_conflict"
    if exec_q < 1.25 and fail_set:
        return "weak_execution_plus_fail"
    if book == "B-book" and fail_set and len(fail_set) >= 1:
        return "bbook_plus_fail"
    if archetype == "continuation" and cont_subq < V41_CONTINUATION_SUBQUALITY_FLOOR:
        return "weak_continuation_subquality"
    if archetype == "continuation" and "USD basket" in tags and (book == "B-book" or "weak_impulse" in fail_set or exec_q < 1.70):
        return "crowded_usd_continuation_fragile"
    if fail_set == {"d_tier", "weak_impulse"}:
        return "double_advisory_fail"
    if setup_q < 1.30 and fail_set:
        return "weak_setup_plus_fail"
    return ""

def _v41_idea_family(row: dict) -> str:
    archetype = str(row.get("Setup_Archetype", "") or "")
    tags = row.get("Cluster_Tags_List", []) or []
    theme = _row_theme_family(tags)
    side = str(row.get("Preferred_Side", "") or "")
    usd_flag = "usd" if "USD basket" in tags else "nonusd"
    if archetype == "relative_value_continuation":
        return f"relval|{theme}|{side}|{usd_flag}"
    if archetype == "continuation":
        cont_band = "strong" if float(row.get("Continuation_Subquality", 0.0) or 0.0) >= 0.20 else "normal"
        return f"continuation|{theme}|{side}|{usd_flag}|{cont_band}"
    return f"{archetype}|{theme}|{side}|{usd_flag}"

def _v41_survivor_score(row: dict) -> float:
    setup_q = float(row.get("Decision_Setup_Quality", 0.0) or 0.0)
    exec_q = float(row.get("Decision_Execution_Quality", 0.0) or 0.0)
    dist_atr = _safe_num(row.get("Entry_Distance_ATR"))
    cont_subq = float(row.get("Continuation_Subquality", 0.0) or 0.0)
    score = V41_SETUP_WEIGHT * setup_q + V41_EXECUTION_WEIGHT * exec_q + _robustness_adjustment(row)
    if np.isfinite(dist_atr):
        if dist_atr <= 0.35:
            score += V41_ENTRY_DIST_BONUS_TIGHT
        elif dist_atr <= 0.50:
            score += V41_ENTRY_DIST_BONUS_GOOD
        elif dist_atr > 0.90:
            score += V41_ENTRY_DIST_PENALTY_FAR
    archetype = str(row.get("Setup_Archetype", "") or "")
    if archetype == "relative_value_continuation":
        score += V41_RELVAL_BONUS
    elif archetype == "continuation":
        if cont_subq >= 0.20:
            score += V41_CONT_SUBQ_GOOD
        elif cont_subq < V41_CONTINUATION_SUBQUALITY_FLOOR:
            score += V41_CONT_SUBQ_BAD
    band = str(row.get("Confidence_Band", "") or "")
    if band == "high":
        score += V42B_CONFIDENCE_BONUS_HIGH
    elif band == "medium":
        score += V42B_CONFIDENCE_BONUS_MEDIUM
    else:
        score += V42B_CONFIDENCE_BONUS_LOW
    return round(score, 4)

def _v41_assign_pool(row: dict) -> str:
    bucket = str(row.get("Calibration_Candidate_Bucket", "") or "")
    archetype = str(row.get("Setup_Archetype", "") or "")
    tags = row.get("Cluster_Tags_List", []) or []
    if archetype == "relative_value_continuation":
        return "best_relval"
    if bucket in {"soft_pass", "challenger"}:
        return "best_challenger"
    if _is_diversified_non_usd(tags):
        return "best_diversified"
    return "best_overall"

def _v41_build_survivor_finalists(prepared: list) -> list:
    survivors = []
    for row in prepared:
        row["Tournament_Pool"] = ""
        row["Tournament_Finalist_Flag"] = False
        row["Selection_Passed_Over_For_Diversity"] = ""
        row["Crowding_Block_Reason"] = ""
        fragility = _v41_fragility_reason(row)
        row["Fragility_Reason"] = fragility
        row["Idea_Family"] = _v41_idea_family(row)
        row["Survivor_Score"] = _v41_survivor_score(row)
        if fragility:
            continue
        survivors.append(row)

    best_by_family = {}
    for row in sorted(survivors, key=lambda x: (float(x.get("Survivor_Score", 0.0) or 0.0), float(x.get("Decision_Rank_Score", 0.0) or 0.0)), reverse=True):
        fam = str(row.get("Idea_Family", "") or "")
        if fam and fam in best_by_family:
            continue
        best_by_family[fam] = dict(row)

    deduped = list(best_by_family.values())
    pools = {"best_relval": [], "best_diversified": [], "best_challenger": [], "best_overall": []}
    for row in deduped:
        pool = _v41_assign_pool(row)
        item = dict(row)
        item["Tournament_Pool"] = pool
        item["Local_Pool_Score"] = float(row.get("Survivor_Score", row.get("Decision_Rank_Score", 0.0)) or 0.0)
        pools[pool].append(item)
        pools["best_overall"].append(dict(item))

    limits = {
        "best_relval": V41_POOL_TOP_RELVAL_COUNT,
        "best_diversified": V41_POOL_TOP_DIVERSIFIED_COUNT,
        "best_challenger": V41_POOL_TOP_CHALLENGER_COUNT,
        "best_overall": V41_POOL_TOP_OVERALL_COUNT,
    }
    finalists_by_symbol = {}
    for pool, rows in pools.items():
        rows.sort(key=lambda x: (float(x.get("Local_Pool_Score", 0.0) or 0.0), float(x.get("Decision_Execution_Quality", 0.0) or 0.0)), reverse=True)
        for item in rows[:limits[pool]]:
            sym = item["Instrument"]
            existing = finalists_by_symbol.get(sym)
            if existing is None or float(item.get("Local_Pool_Score", 0.0) or 0.0) > float(existing.get("Local_Pool_Score", 0.0) or 0.0):
                finalists_by_symbol[sym] = item

    finalists = list(finalists_by_symbol.values())
    finalists.sort(key=lambda x: (float(x.get("Local_Pool_Score", 0.0) or 0.0), float(x.get("Final_Rank_Score", 0.0) or 0.0), float(x.get("Selection_Score", 0.0) or 0.0)), reverse=True)
    for item in finalists:
        item["Tournament_Finalist_Flag"] = True
        item["Tournament_Pool_Display"] = _pool_display_name(str(item.get("Tournament_Pool", "") or ""))
    return finalists


def _pool_bonus(row: dict, pool: str) -> float:
    tags = row.get("Cluster_Tags_List", []) or []
    bonus = 0.0
    if pool == "best_relval":
        bonus += V40_RELVAL_POOL_BONUS
        if "USD basket" not in tags:
            bonus += 0.02
    elif pool == "best_diversified":
        bonus += V40_DIVERSIFIED_POOL_BONUS
    elif pool == "best_challenger":
        bonus += V40_CHALLENGER_POOL_BONUS
    elif pool == "best_continuation":
        bonus += V40_CONTINUATION_POOL_BONUS
    return round(bonus, 4)


def _robustness_adjustment(row: dict) -> float:
    exec_q = float(row.get("Decision_Execution_Quality", 0.0) or 0.0)
    dist_atr = _safe_num(row.get("Entry_Distance_ATR"))
    fail_reasons = [x.strip() for x in str(row.get("Gate_Fail_Reasons", "") or "").split(",") if x.strip()]
    fail_set = set(fail_reasons)
    tags = row.get("Cluster_Tags_List", []) or []
    book = str(row.get("Decision_Book", "") or "")
    adj = 0.0
    if exec_q >= 1.90:
        adj += 0.10
    if np.isfinite(dist_atr) and dist_atr <= 0.50:
        adj += 0.10
    elif np.isfinite(dist_atr) and dist_atr <= 0.80:
        adj += 0.05
    if not fail_set:
        adj += 0.10
    elif len(fail_set) == 1 and fail_set.issubset(CALIBRATION_SOFT_FAIL_REASONS):
        adj += 0.05
    if "stacked_conflict" in fail_set:
        adj -= 0.15
    if book == "B-book":
        adj -= 0.10
    if "USD basket" in tags:
        adj -= 0.05
    return round(adj, 4)


def _eligible_tournament_pools(row: dict) -> list:
    bucket = str(row.get("Calibration_Candidate_Bucket", "") or "")
    archetype = str(row.get("Setup_Archetype", "") or "")
    tags = row.get("Cluster_Tags_List", []) or []
    fail_reasons = [x.strip() for x in str(row.get("Gate_Fail_Reasons", "") or "").split(",") if x.strip()]
    exec_q = float(row.get("Decision_Execution_Quality", 0.0) or 0.0)
    setup_q = float(row.get("Decision_Setup_Quality", 0.0) or 0.0)
    cont_subq = float(row.get("Continuation_Subquality", 0.0) or 0.0)

    pools = []
    continuation_ok = (
        bucket in {"hard_pass", "soft_pass"}
        and archetype == "continuation"
        and exec_q >= V40_CONTINUATION_MIN_EXECUTION_QUALITY
        and setup_q >= V40_CONTINUATION_MIN_SETUP_QUALITY
        and cont_subq >= V40_CONTINUATION_MIN_SUBQUALITY
    )
    if continuation_ok:
        pools.append("best_continuation")
    if bucket in {"hard_pass", "soft_pass", "challenger"} and archetype == "relative_value_continuation" and exec_q >= 1.40:
        pools.append("best_relval")
    if bucket in {"hard_pass", "soft_pass"} and _is_diversified_non_usd(tags) and exec_q >= 1.40 and setup_q >= 1.40:
        pools.append("best_diversified")
    if bucket in {"soft_pass", "challenger"} and set(fail_reasons).issubset(CALIBRATION_SOFT_FAIL_REASONS) and exec_q >= 1.35 and setup_q >= 1.35:
        pools.append("best_challenger")
    return pools


def _local_pool_score(row: dict, pool: str) -> float:
    setup_q = float(row.get("Decision_Setup_Quality", 0.0) or 0.0)
    exec_q = float(row.get("Decision_Execution_Quality", 0.0) or 0.0)
    score = V41_SETUP_WEIGHT * setup_q + V41_EXECUTION_WEIGHT * exec_q + _robustness_adjustment(row) + _pool_bonus(row, pool)
    dist_atr = _safe_num(row.get("Entry_Distance_ATR"))
    if np.isfinite(dist_atr):
        if dist_atr <= 0.35:
            score += V41_ENTRY_DIST_BONUS_TIGHT
        elif dist_atr <= 0.50:
            score += V41_ENTRY_DIST_BONUS_GOOD
        elif dist_atr > 0.90:
            score += V41_ENTRY_DIST_PENALTY_FAR
    return round(score, 4)


def _same_theme_family(a: dict, b: dict) -> bool:
    return _row_theme_family(a.get("Cluster_Tags_List", []) or []) == _row_theme_family(b.get("Cluster_Tags_List", []) or [])


def _tournament_uniqueness_penalty(sym: str, tags: list, used_currency_counter: Counter, used_cluster_counter: Counter, theme_counter: Counter, continuation_count: int = 0, archetype: str = "", shortlist: list | None = None) -> float:
    base, quote = pair_currencies(sym)
    penalty = 0.0
    for ccy in (base, quote):
        count = int(used_currency_counter.get(ccy, 0))
        if count == 1:
            penalty += 0.25
        elif count >= 2:
            penalty += 0.60
    for t in tags:
        count = int(used_cluster_counter.get(t, 0))
        if count == 1:
            penalty += 0.25
        elif count >= 2:
            penalty += 0.60
    for th in _theme_tags(tags):
        count = int(theme_counter.get(th, 0))
        if count == 1:
            penalty += 0.45
        elif count >= 2:
            penalty += 1.00
    if "USD basket" in tags:
        usd_count = int(theme_counter.get("USD basket", 0))
        if usd_count == 1:
            penalty += 0.40
        elif usd_count >= 2:
            penalty += 1.00
    if archetype == "continuation":
        if continuation_count == 1:
            penalty += 0.15
        elif continuation_count >= 2:
            penalty += 0.40
        if "USD basket" in tags and int(theme_counter.get("USD basket", 0)) >= V38_CONTINUATION_USD_SOFT_CAP:
            penalty += 0.35
    if V38_NO_ADJACENT_SAME_THEME and shortlist:
        last_row = shortlist[-1]
        if _same_theme_family(last_row, {"Cluster_Tags_List": tags}):
            penalty += 0.60
    return round(penalty, 4)


def _selection_block_reason(row: dict, used_currency_counter: Counter, used_cluster_counter: Counter, theme_counter: Counter, shortlist: list, soft_count: int, bbook_count: int, continuation_count: int, slot_name: str) -> str:
    sym = row["Instrument"]
    base, quote = pair_currencies(sym)
    tags = row.get("Cluster_Tags_List", [])
    themes = _theme_tags(tags)
    bucket = str(row.get("Calibration_Candidate_Bucket", "") or "")
    archetype = str(row.get("Setup_Archetype", "") or "")

    if any(x.get("Instrument") == sym for x in shortlist):
        return "duplicate_symbol"
    if used_currency_counter[base] >= MAX_SAME_BASE_OR_QUOTE_IN_SHORTLIST:
        return f"base_cap:{base}"
    if used_currency_counter[quote] >= MAX_SAME_BASE_OR_QUOTE_IN_SHORTLIST:
        return f"quote_cap:{quote}"
    for t in tags:
        if used_cluster_counter[t] >= MAX_SAME_CLUSTER_IN_SHORTLIST:
            return f"cluster_cap:{t}"
    for t in themes:
        if t != "USD basket" and theme_counter[t] >= MAX_THEME_IN_SHORTLIST:
            return f"theme_cap:{t}"
    if "USD basket" in themes and theme_counter["USD basket"] >= MAX_USD_BASKET_IN_SHORTLIST:
        return "theme_cap:USD basket"
    if row.get("Decision_Book") == "B-book" and bbook_count >= MAX_BBOOK_IN_SHORTLIST:
        return "bbook_cap"
    if bucket in {"soft_pass", "challenger"} and soft_count >= V36_MAX_SOFT_ROWS_IN_SHORTLIST:
        return "soft_cap"
    if archetype == "relative_value_continuation":
        relval_count = sum(1 for x in shortlist if str(x.get("Setup_Archetype", "") or "") == "relative_value_continuation")
        if relval_count >= V49_RELVAL_MAX_IN_SHORTLIST:
            return "relval_cap"
    if archetype == "continuation" and continuation_count >= MAX_CONTINUATION_IN_SHORTLIST:
        return "continuation_cap"
    if archetype == "continuation":
        cont_subq = float(row.get("Continuation_Subquality", 0.0) or 0.0)
        if slot_name == "continuation":
            if V40_REQUIRE_ELITE_CONTINUATION and not bool(row.get("Continuation_Elite_Eligible", False)):
                return "continuation_requires_elite"
            if cont_subq < V40_CONTINUATION_MIN_SUBQUALITY:
                return "continuation_subquality_floor"
        if "USD basket" in themes and theme_counter["USD basket"] >= V38_CONTINUATION_USD_SOFT_CAP:
            return "crowded_usd_continuation_soft_cap"
    if slot_name == "challenger" and str(row.get("Tournament_Pool", "") or "") != "best_challenger":
        return "slot_requires_challenger"
    if slot_name == "continuation" and str(row.get("Tournament_Pool", "") or "") != "best_continuation":
        return "slot_requires_continuation"
    if slot_name == "relval" and str(row.get("Tournament_Pool", "") or "") != "best_relval":
        return "slot_requires_relval"
    if slot_name == "diversified" and str(row.get("Tournament_Pool", "") or "") != "best_diversified":
        return "slot_requires_diversified"
    if V38_NO_ADJACENT_SAME_THEME and shortlist:
        last_row = shortlist[-1]
        if _same_theme_family(last_row, row) and _row_theme_family(tags) != "no_theme":
            return f"adjacent_theme_block:{_row_theme_family(tags)}"
    return ""


def _mark_passed_over(finalist: dict, reason: str):
    if not reason:
        return
    prior = str(finalist.get("Selection_Passed_Over_For_Diversity", "") or "").strip()
    finalist["Selection_Passed_Over_For_Diversity"] = f"{prior}; {reason}".strip("; ") if prior else reason


def _pool_display_name(pool: str) -> str:
    return {
        "clean_continuation": "Pool A - Clean Continuation",
        "relative_value_continuation": "Pool B - Relative-Value Continuation",
        "diversified_non_usd": "Pool C - Diversified / Non-USD",
        "challenger_recovery": "Pool D - Challenger / Soft Recovery",
        "best_execution": "Pool E - Best Execution",
        "best_overall": "Pool Z - Best Overall",
        "best_relval": "Pool B - Relative-Value Survivor",
        "best_diversified": "Pool C - Diversified Survivor",
        "best_challenger": "Pool D - Challenger Survivor",
    }.get(pool, pool)


def _build_tournament_finalists(prepared: list) -> list:
    pools = {
        "best_continuation": [],
        "best_relval": [],
        "best_diversified": [],
        "best_challenger": [],
        "best_reserve": [],
    }

    for row in prepared:
        row["Tournament_Pool"] = ""
        row["Tournament_Finalist_Flag"] = False
        row["Selection_Passed_Over_For_Diversity"] = ""
        row["Crowding_Block_Reason"] = ""
        eligible = _eligible_tournament_pools(row)
        fail_set = {x.strip() for x in str(row.get("Gate_Fail_Reasons", "") or "").split(",") if x.strip()}
        if fail_set and fail_set.issubset(CALIBRATION_SOFT_FAIL_REASONS):
            eligible = list(dict.fromkeys(list(eligible) + ["best_reserve", "best_challenger"]))
        elif not row.get("Calibration_Gate_Passed") and not (fail_set & CALIBRATION_HARD_REJECT_REASONS):
            eligible = list(dict.fromkeys(list(eligible) + ["best_reserve"]))
        row["Tournament_Pool_Eligible"] = ", ".join(eligible)
        if eligible:
            row["Tournament_Pool"] = eligible[0]
        for pool in eligible:
            local = _local_pool_score(row, pool)
            if pool == "best_reserve":
                local = float(row.get("Final_Rank_Score", 0.0) or 0.0) + 0.15 * float(row.get("Opportunity_Score_10", 0.0) or 0.0)
            row[f"Local_Pool_Score_{pool}"] = local
            item = dict(row)
            item["Tournament_Pool"] = pool
            item["Local_Pool_Score"] = local
            pools[pool].append(item)

    limits = {
        "best_continuation": max(2, V40_POOL_TOP_CONTINUATION_COUNT),
        "best_relval": max(1, V40_POOL_TOP_RELVAL_COUNT),
        "best_diversified": max(2, V40_POOL_TOP_DIVERSIFIED_COUNT),
        "best_challenger": max(2, V40_POOL_TOP_CHALLENGER_COUNT),
        "best_reserve": max(3, TOP_SHORTLIST_N),
    }

    finalists_by_symbol = {}
    for pool, rows in pools.items():
        rows.sort(key=lambda x: (float(x.get("Local_Pool_Score", 0.0) or 0.0), float(x.get("Final_Rank_Score", 0.0) or 0.0), float(x.get("Continuation_Subquality", 0.0) or 0.0)), reverse=True)
        for item in rows[:limits[pool]]:
            sym = item["Instrument"]
            existing = finalists_by_symbol.get(sym)
            if existing is None or float(item.get("Local_Pool_Score", 0.0) or 0.0) > float(existing.get("Local_Pool_Score", 0.0) or 0.0):
                finalists_by_symbol[sym] = item

    overall = sorted(prepared, key=lambda x: (float(x.get("Final_Rank_Score", 0.0) or 0.0), float(x.get("Selection_Score", 0.0) or 0.0), float(x.get("Opportunity_Score_10", 0.0) or 0.0)), reverse=True)
    for row in overall[:max(8, TOP_SHORTLIST_N * 2)]:
        sym = row["Instrument"]
        if sym not in finalists_by_symbol:
            item = dict(row)
            item["Tournament_Pool"] = "best_overall"
            item["Local_Pool_Score"] = float(row.get("Final_Rank_Score", 0.0) or 0.0)
            finalists_by_symbol[sym] = item

    finalists = list(finalists_by_symbol.values())
    finalists.sort(key=lambda x: (float(x.get("Local_Pool_Score", 0.0) or 0.0), float(x.get("Final_Rank_Score", 0.0) or 0.0)), reverse=True)
    for item in finalists:
        item["Tournament_Finalist_Flag"] = True
        item["Tournament_Pool_Display"] = _pool_display_name(str(item.get("Tournament_Pool", "") or ""))
    return finalists

def _safe_num(x, default=np.nan):
    try:
        return float(x)
    except Exception:
        return default


def classify_setup_archetype(row: dict) -> str:
    liq = str(row.get("Liquidity_Condition", ""))
    rej = str(row.get("Rejection_Quality", ""))
    align = str(row.get("Alignment", ""))
    rs = str(row.get("RS_RW_Alignment", ""))
    mss = str(row.get("MSS_BOS", ""))
    disp = str(row.get("Displacement_Quality", ""))
    if (
        "external liquidity taken" in liq
        and rej == MIN_REVERSAL_REJECTION_FOR_PRIORITY
        and mss == "clear MSS/BOS"
        and disp in {"strong displacement", "moderate displacement"}
        and align != "full conflict"
    ):
        return "reversal_after_sweep"
    if rs in {"strong alignment", "aligned", "clear alignment"} and align == "aligned":
        return "relative_value_continuation"
    return "continuation"


def compute_setup_quality(row: dict) -> float:
    score = 0.0
    score += 1.10 if row.get("Alignment") == "aligned" else 0.45 if row.get("Alignment") == "mild conflict" else -0.70
    score += 0.90 if row.get("Displacement_Quality") == "strong displacement" else 0.35 if row.get("Displacement_Quality") == "moderate displacement" else -0.60
    score += 0.85 if row.get("MSS_BOS") == "clear MSS/BOS" else 0.20 if row.get("MSS_BOS") == "partial shift" else -0.65
    score += 0.55 if row.get("Rejection_Quality") == "strong rejection" else 0.30 if row.get("Rejection_Quality") == "moderate rejection" else 0.0
    score += 0.35 if row.get("Liquidity_Tier") == "major" else 0.15 if row.get("Liquidity_Tier") == "minor" else 0.0
    score += 0.30 if row.get("Pivot_Conflict") == "no meaningful pivot conflict" else -0.55 if row.get("Pivot_Conflict") == "strong pivot conflict" else -0.15
    score += execution_bonus(row.get("Entry_Label", ""))
    return round(max(0.0, min(4.0, score + 1.0)), 2)


def compute_execution_quality(row: dict) -> float:
    side = str(row.get("Preferred_Side", "") or "").strip().lower()
    entry = _safe_num(row.get("Best_Entry"))
    sl = _safe_num(row.get("SL"))
    tp1 = _safe_num(row.get("TP1"))
    current = _safe_num(row.get("Current_Price"))
    atr_h1 = _safe_num(row.get("ATR_H1"))
    if not all(np.isfinite(v) for v in [entry, sl, tp1, current]):
        return 0.0
    risk = abs(entry - sl)
    reward = abs(tp1 - entry)
    if risk <= 0:
        return 0.0
    proximity = abs(entry - current)
    atr_ref = atr_h1 if np.isfinite(atr_h1) and atr_h1 > 0 else max(abs(current) * 0.0012, risk)
    prox_ratio = proximity / max(atr_ref, 1e-9)
    rr = reward / max(risk, 1e-9)
    score = 0.0
    score += 1.30 if prox_ratio <= 0.45 else 0.95 if prox_ratio <= 0.80 else 0.45 if prox_ratio <= 1.15 else -0.30
    score += 1.05 if 0.9 <= rr <= 2.6 else 0.70 if 0.7 <= rr <= 3.2 else 0.15 if 0.5 <= rr <= 4.0 else -0.40
    score += 0.85 if 0.20 <= risk / max(atr_ref, 1e-9) <= 1.80 else 0.35 if 0.10 <= risk / max(atr_ref, 1e-9) <= 2.40 else -0.35
    if side in {"long", "buy", "buy-limit", "buy_limit"} and not (sl < entry < tp1):
        score -= 1.0
    elif side in {"short", "sell", "sell-limit", "sell_limit"} and not (tp1 < entry < sl):
        score -= 1.0
    return round(max(0.0, min(4.0, score + 0.6)), 2)




def compute_technical_quality_score_10(row: dict) -> float:
    score = 5.0
    align = str(row.get("Alignment", "") or "")
    disp = str(row.get("Displacement_Quality", "") or "")
    mss = str(row.get("MSS_BOS", "") or "")
    rej = str(row.get("Rejection_Quality", "") or "")
    liq_tier = str(row.get("Liquidity_Tier", "") or "")
    pivot_conflict = str(row.get("Pivot_Conflict", "") or "")
    archetype = str(row.get("Setup_Archetype", "") or "")

    score += 1.0 if align == "aligned" else 0.25 if align == "mild conflict" else -1.4
    score += 1.0 if disp == "strong displacement" else 0.35 if disp == "moderate displacement" else -1.0
    score += 0.9 if mss == "clear MSS/BOS" else 0.2 if mss == "partial shift" else -0.8
    score += 0.8 if rej == "strong rejection" else 0.4 if rej == "moderate rejection" else -0.3
    score += 0.4 if liq_tier == "major" else 0.15 if liq_tier == "minor" else 0.0
    score += 0.5 if pivot_conflict == "no meaningful pivot conflict" else -1.0 if pivot_conflict == "strong pivot conflict" else -0.2
    score += 0.4 if archetype == "relative_value_continuation" else -0.2 if archetype == "continuation" else 0.0
    return round(max(0.0, min(10.0, score)), 2)


def compute_execution_realism_score_10(row: dict) -> float:
    score = min(10.0, max(0.0, float(row.get("Decision_Execution_Quality", 0.0) or 0.0) * 2.5))
    dist_atr = _safe_num(row.get("Entry_Distance_ATR"))
    rr_tp1 = _safe_num(row.get("RR_TP1"))
    if np.isfinite(dist_atr):
        if dist_atr <= 0.35:
            score += 1.0
        elif dist_atr <= 0.60:
            score += 0.5
        elif dist_atr > 1.10:
            score -= 1.25
    if np.isfinite(rr_tp1):
        if 0.8 <= rr_tp1 <= 2.8:
            score += 0.35
        elif rr_tp1 > 4.0 or rr_tp1 < 0.45:
            score -= 0.6
    return round(max(0.0, min(10.0, score)), 2)


def compute_calibrated_confidence_from_row(row: dict) -> dict:
    score = 5.0
    tech10 = _safe_num(row.get("Technical_Quality_Score_10"))
    exec10 = _safe_num(row.get("Execution_Realism_Score_10"))
    legacy_band = str(row.get("Legacy_Confidence_Band", row.get("Confidence_Band", "")) or "")
    archetype = str(row.get("Setup_Archetype", "") or "")
    fail_reasons = [x.strip() for x in str(row.get("Gate_Fail_Reasons", "") or "").split(",") if x.strip()]
    fail_set = set(fail_reasons)
    align = str(row.get("Alignment", "") or "")
    disp = str(row.get("Displacement_Quality", "") or "")
    rej = str(row.get("Rejection_Quality", "") or "")
    pivot_conflict = str(row.get("Pivot_Conflict", "") or "")

    if np.isfinite(tech10):
        score += (tech10 - 5.0) * 0.22
    if np.isfinite(exec10):
        score += (exec10 - 5.0) * 0.28

    if legacy_band == "high":
        score -= 0.7
    elif legacy_band == "medium":
        score += 0.25

    if row.get("Calibration_Gate_Passed"):
        score -= 0.35
    elif fail_set and fail_set.issubset(CALIBRATION_SOFT_FAIL_REASONS):
        score += 0.45

    if align == "aligned":
        score += 0.45
    elif align == "full conflict":
        score -= 0.9
    if disp == "strong displacement":
        score += 0.35
    elif disp == "weak/no displacement":
        score -= 0.75
    if rej == "strong rejection":
        score += 0.55
    elif rej == "weak/no rejection":
        score -= 0.45
    if pivot_conflict == "strong pivot conflict":
        score -= 0.8

    if archetype == "relative_value_continuation":
        score += 0.45
    elif archetype == "continuation":
        score -= 0.25

    score = round(max(0.0, min(10.0, score)), 2)
    norm = round(score / 10.0, 3)
    band = "high" if norm >= HIGH_CONFIDENCE_MIN_SCORE else "medium" if norm >= MEDIUM_CONFIDENCE_MIN_SCORE else "low"
    return {"score_10": score, "score": norm, "band": band}


def compute_context_quality_score_10(row: dict) -> float:
    score = 5.0
    align = str(row.get("Alignment", "") or "")
    pivot_conflict = str(row.get("Pivot_Conflict", "") or "")
    liq_cond = str(row.get("Liquidity_Condition", "") or "")
    liq_tier = str(row.get("Liquidity_Tier", "") or "")
    follow = str(row.get("Follow_Through", "") or "")
    price_side = str(row.get("Price_Side_vs_D1_Range", "") or "")
    score += 1.1 if align == "aligned" else 0.35 if align == "mild conflict" else -1.3
    score += 0.55 if liq_cond == "external liquidity taken" else -0.15 if liq_cond == "no clear liquidity event" else 0.10
    score += 0.45 if liq_tier == "major" else 0.15 if liq_tier == "minor" else 0.0
    score += 0.35 if follow == "clean follow-through" else -0.20 if follow == "stalled follow-through" else 0.0
    score += 0.20 if price_side in {"discount for longs", "premium for shorts"} else -0.15 if price_side in {"premium for longs", "discount for shorts"} else 0.0
    score += 0.40 if pivot_conflict == "no meaningful pivot conflict" else -1.15 if pivot_conflict == "strong pivot conflict" else -0.20
    return round(max(0.0, min(10.0, score)), 2)


def compute_trigger_quality_score_10(row: dict) -> float:
    score = 5.0
    disp = str(row.get("Displacement_Quality", "") or "")
    mss = str(row.get("MSS_BOS", "") or "")
    rej = str(row.get("Rejection_Quality", "") or "")
    both_sides = str(row.get("Both_Sides_Taken_Recently", "") or "")
    session = str(row.get("Session_Quality", "") or "")
    score += 1.10 if disp == "strong displacement" else 0.45 if disp == "moderate displacement" else -1.10
    score += 0.95 if mss == "clear MSS/BOS" else 0.25 if mss == "partial shift" else -0.90
    score += 0.80 if rej == "strong rejection" else 0.30 if rej == "moderate rejection" else -0.50
    score += -0.35 if both_sides == "yes" else 0.15 if both_sides == "no" else 0.0
    score += 0.20 if session == "clean session timing" else -0.10 if session == "poor session timing" else 0.0
    return round(max(0.0, min(10.0, score)), 2)


def compute_conflict_penalty_score_10(row: dict) -> float:
    penalty = 0.0
    align = str(row.get("Alignment", "") or "")
    pivot_conflict = str(row.get("Pivot_Conflict", "") or "")
    fail_set = {x.strip() for x in str(row.get("Gate_Fail_Reasons", "") or "").split(",") if x.strip()}
    entry_label = str(row.get("Entry_Label", "") or "")
    if align == "full conflict":
        penalty += 3.0
    elif align == "mild conflict":
        penalty += 0.8
    if pivot_conflict == "strong pivot conflict":
        penalty += 2.2
    elif pivot_conflict == "minor pivot conflict":
        penalty += 0.7
    if "stacked_conflict" in fail_set:
        penalty += 2.5
    if "weak_impulse" in fail_set:
        penalty += 1.1
    if entry_label == "D-tier avoid":
        penalty += 1.6
    if str(row.get("Data_Quality", "") or "") == "poor":
        penalty += 2.8
    return round(max(0.0, min(10.0, penalty)), 2)


def compute_balance_score_10(*scores: float) -> float:
    vals = [float(x) for x in scores if np.isfinite(float(x))]
    if not vals:
        return 0.0
    mn = min(vals)
    mx = max(vals)
    spread = mx - mn
    score = 10.0 - 0.9 * spread - 0.45 * max(0.0, 5.8 - mn)
    return round(max(0.0, min(10.0, score)), 2)


def compute_opportunity_score_10(row: dict) -> float:
    score = 5.0
    fail_set = {x.strip() for x in str(row.get("Gate_Fail_Reasons", "") or "").split(",") if x.strip()}
    hard = bool(fail_set & CALIBRATION_HARD_REJECT_REASONS)
    soft_only = bool(fail_set) and fail_set.issubset(CALIBRATION_SOFT_FAIL_REASONS)
    archetype = str(row.get("Setup_Archetype", "") or "")
    cont_subq = _safe_num(row.get("Continuation_Subquality"))
    if hard:
        score -= 2.2
    elif soft_only:
        score += 1.0
    if row.get("Calibration_Gate_Passed"):
        score -= 0.35
    if archetype == "relative_value_continuation":
        score -= 0.7
    elif archetype == "continuation":
        score += 0.35 if np.isfinite(cont_subq) and cont_subq >= 0.10 else -0.10
    if bool(row.get("Soft_Candidate")):
        score += 0.8
    return round(max(0.0, min(10.0, score)), 2)


def compute_kill_switch_score_10(row: dict) -> float:
    fail_set = {x.strip() for x in str(row.get("Gate_Fail_Reasons", "") or "").split(",") if x.strip()}
    score = 0.0
    if row.get("status") != "OK":
        score += 4.0
    if str(row.get("Data_Quality", "") or "") == "poor":
        score += 3.5
    if str(row.get("Entry_Label", "") or "") == "D-tier avoid":
        score += 2.5
    if str(row.get("Alignment", "") or "") == "full conflict":
        score += 2.2
    if str(row.get("Pivot_Conflict", "") or "") == "strong pivot conflict":
        score += 1.8
    if str(row.get("Displacement_Quality", "") or "") in {"weak/no displacement", "weak / no displacement"}:
        score += 1.6
    if str(row.get("MSS_BOS", "") or "") == "no clear shift":
        score += 1.4
    if "stacked_conflict" in fail_set:
        score += 1.8
    if "weak_impulse" in fail_set:
        score += 1.2
    if "d_tier" in fail_set:
        score += 1.4
    if fail_set & CALIBRATION_HARD_REJECT_REASONS:
        score += 2.0
    return round(max(0.0, min(10.0, score)), 2)


def compute_false_positive_risk_score_10(row: dict) -> float:
    score = 3.6
    archetype = str(row.get("Setup_Archetype", "") or "")
    align = str(row.get("Alignment", "") or "")
    disp = str(row.get("Displacement_Quality", "") or "")
    rej = str(row.get("Rejection_Quality", "") or "")
    liq_cond = str(row.get("Liquidity_Condition", "") or "")
    pivot_conflict = str(row.get("Pivot_Conflict", "") or "")
    exec10 = _safe_num(row.get("Execution_Realism_Score_10"))
    tech10 = _safe_num(row.get("Technical_Quality_Score_10"))
    fail_set = {x.strip() for x in str(row.get("Gate_Fail_Reasons", "") or "").split(",") if x.strip()}
    if archetype == "relative_value_continuation":
        score += 2.1
    elif archetype == "continuation":
        score += 0.5
    if row.get("Calibration_Gate_Passed"):
        score += 0.9
    if align == "aligned" and pivot_conflict != "no meaningful pivot conflict":
        score += 0.7
    if disp in {"strong displacement", "moderate displacement"} and rej in {"weak/no rejection", "", "none"}:
        score += 0.8
    if liq_cond == "no clear liquidity event":
        score += 0.8
    if pivot_conflict == "strong pivot conflict":
        score += 0.9
    if fail_set and fail_set.issubset(CALIBRATION_SOFT_FAIL_REASONS):
        score -= 0.8
    if np.isfinite(exec10) and exec10 >= 6.4:
        score -= 0.4
    if np.isfinite(tech10) and tech10 >= 7.0 and not fail_set:
        score += 0.5
    return round(max(0.0, min(10.0, score)), 2)


def compute_archetype_tax_score_10(row: dict) -> float:
    archetype = str(row.get("Setup_Archetype", "") or "")
    cont_subq = _safe_num(row.get("Continuation_Subquality"))
    if archetype == "relative_value_continuation":
        score = 7.2
    elif archetype == "continuation":
        score = 3.8
        if np.isfinite(cont_subq):
            score -= 0.8 if cont_subq >= 0.20 else 0.4 if cont_subq < 0.05 else 0.0
    elif archetype == "reversal_after_sweep":
        score = 2.2
    else:
        score = 4.5
    return round(max(0.0, min(10.0, score)), 2)


def compute_survivability_score_10(row: dict) -> float:
    context10 = _safe_num(row.get("Context_Quality_Score_10"))
    trigger10 = _safe_num(row.get("Trigger_Quality_Score_10"))
    exec10 = _safe_num(row.get("Execution_Realism_Score_10"))
    conflict10 = _safe_num(row.get("Conflict_Penalty_Score_10"), 0.0)
    kill10 = _safe_num(row.get("Kill_Switch_Score_10"), 0.0)
    vals = [v for v in (context10, trigger10, exec10) if np.isfinite(v)]
    if not vals:
        return 0.0
    mn = min(vals)
    hm = len(vals) / sum(1.0 / max(0.35, v) for v in vals)
    score = 0.55 * hm + 0.45 * mn - 0.22 * conflict10 - 0.18 * kill10
    if bool(row.get("Soft_Candidate")):
        score += 0.45
    return round(max(0.0, min(10.0, score)), 2)


def compute_asymmetry_score_10(row: dict) -> float:
    rr1 = _safe_num(row.get("RR_TP1"))
    rr2 = _safe_num(row.get("RR_TP2"))
    dist_atr = _safe_num(row.get("Entry_Distance_ATR"))
    follow = str(row.get("Follow_Through", "") or "")
    rej = str(row.get("Rejection_Quality", "") or "")
    score = 5.0
    if np.isfinite(rr1):
        if 0.9 <= rr1 <= 2.4:
            score += 1.1
        elif 0.65 <= rr1 <= 3.2:
            score += 0.45
        else:
            score -= 0.8
    if np.isfinite(rr2):
        if 1.5 <= rr2 <= 4.0:
            score += 0.8
        elif rr2 > 5.5:
            score -= 0.6
    if np.isfinite(dist_atr):
        if dist_atr <= 0.18:
            score += 0.9
        elif dist_atr <= 0.40:
            score += 0.45
        elif dist_atr > 0.85:
            score -= 1.0
    if follow == "clean follow-through":
        score += 0.6
    elif follow == "stalled follow-through":
        score -= 0.4
    if rej == "strong rejection":
        score += 0.5
    elif rej == "weak/no rejection":
        score -= 0.6
    return round(max(0.0, min(10.0, score)), 2)


def compute_calibration_utility_score_10(row: dict) -> float:
    score = 5.0
    fail_set = {x.strip() for x in str(row.get("Gate_Fail_Reasons", "") or "").split(",") if x.strip()}
    hard = bool(fail_set & CALIBRATION_HARD_REJECT_REASONS)
    soft_only = bool(fail_set) and fail_set.issubset(CALIBRATION_SOFT_FAIL_REASONS)
    archetype = str(row.get("Setup_Archetype", "") or "")
    if hard:
        score -= 2.2
    elif soft_only:
        score += 1.7
    if row.get("Calibration_Gate_Passed"):
        score -= 0.9
    else:
        score += 0.35
    if archetype == "relative_value_continuation":
        score -= 1.0
    elif archetype == "reversal_after_sweep":
        score += 0.9
    if bool(row.get("Soft_Candidate")):
        score += 0.8
    if str(row.get("Decision_Book", "") or "") == "Reserve":
        score += 0.6
    if str(row.get("Data_Quality", "") or "") == "good":
        score += 0.3
    return round(max(0.0, min(10.0, score)), 2)



def compute_radical_confidence_from_row(row: dict) -> dict:
    surv10 = _safe_num(row.get("Survivability_Score_10"))
    asym10 = _safe_num(row.get("Asymmetry_Score_10"))
    util10 = _safe_num(row.get("Calibration_Utility_Score_10"))
    kill10 = _safe_num(row.get("Kill_Switch_Score_10"), 0.0)
    fp10 = _safe_num(row.get("False_Positive_Risk_Score_10"), 0.0)
    vals = [max(0.35, v) for v in (surv10, asym10, util10) if np.isfinite(v)]
    if not vals:
        score10 = 0.0
    else:
        hm = len(vals) / sum(1.0 / v for v in vals)
        score10 = hm - 0.20 * kill10 - 0.18 * fp10
    score10 = round(max(0.0, min(10.0, score10)), 2)
    norm = round(score10 / 10.0, 3)
    band = "high" if score10 >= 7.0 else "medium" if score10 >= 5.6 else "low"
    return {"score_10": score10, "score": norm, "band": band}


def _percentile_rank_map(values: list[float]) -> dict[float, float]:
    clean = [float(v) for v in values if np.isfinite(v)]
    if not clean:
        return {}
    ordered = sorted(clean)
    n = len(ordered)
    if n == 1:
        return {ordered[0]: 1.0}
    out = {}
    for idx, val in enumerate(ordered):
        out[val] = idx / (n - 1)
    return out


def _assign_comparative_metrics(rows: list[dict]) -> None:
    metrics = {
        "util": [float(_safe_num(r.get("Calibration_Utility_Score_10"), 0.0)) for r in rows],
        "asym": [float(_safe_num(r.get("Asymmetry_Score_10"), 0.0)) for r in rows],
        "trig": [float(_safe_num(r.get("Trigger_Quality_Score_10"), 0.0)) for r in rows],
        "surv": [float(_safe_num(r.get("Survivability_Score_10"), 0.0)) for r in rows],
        "neg_fp": [float(10.0 - _safe_num(r.get("False_Positive_Risk_Score_10"), 0.0)) for r in rows],
        "neg_kill": [float(10.0 - _safe_num(r.get("Kill_Switch_Score_10"), 0.0)) for r in rows],
        "neg_leak": [float(10.0 - min(10.0, 2.2 * _safe_num(r.get("Leakage_Penalty_Score"), 0.0))) for r in rows],
    }
    rank_maps = {k: _percentile_rank_map(v) for k, v in metrics.items()}
    for row in rows:
        p_util = rank_maps["util"].get(float(_safe_num(row.get("Calibration_Utility_Score_10"), 0.0)), 0.0)
        p_asym = rank_maps["asym"].get(float(_safe_num(row.get("Asymmetry_Score_10"), 0.0)), 0.0)
        p_trig = rank_maps["trig"].get(float(_safe_num(row.get("Trigger_Quality_Score_10"), 0.0)), 0.0)
        p_surv = rank_maps["surv"].get(float(_safe_num(row.get("Survivability_Score_10"), 0.0)), 0.0)
        p_neg_fp = rank_maps["neg_fp"].get(float(10.0 - _safe_num(row.get("False_Positive_Risk_Score_10"), 0.0)), 0.0)
        p_neg_kill = rank_maps["neg_kill"].get(float(10.0 - _safe_num(row.get("Kill_Switch_Score_10"), 0.0)), 0.0)
        p_neg_leak = rank_maps["neg_leak"].get(float(10.0 - min(10.0, 2.2 * _safe_num(row.get("Leakage_Penalty_Score"), 0.0))), 0.0)
        core = [max(0.05, x) for x in (p_util, p_asym, p_trig, p_surv, p_neg_fp, p_neg_kill, p_neg_leak)]
        comparative = len(core) / sum(1.0 / x for x in core)
        floor = min(core)
        dominance = 0.70 * comparative + 0.30 * floor
        row["Comparative_Edge_Score_10"] = round(10.0 * comparative, 2)
        row["Comparator_Floor_Score_10"] = round(10.0 * floor, 2)
        row["Dominance_Score_10"] = round(10.0 * dominance, 2)


def _classify_admission(row: dict) -> tuple[str, str]:
    archetype = str(row.get("Setup_Archetype", "") or "")
    gate_passed = bool(row.get("Calibration_Gate_Passed"))
    soft_candidate = bool(row.get("Soft_Candidate"))
    util10 = _safe_num(row.get("Calibration_Utility_Score_10"), 0.0)
    asym10 = _safe_num(row.get("Asymmetry_Score_10"), 0.0)
    trig10 = _safe_num(row.get("Trigger_Quality_Score_10"), 0.0)
    fp10 = _safe_num(row.get("False_Positive_Risk_Score_10"), 0.0)
    kill10 = _safe_num(row.get("Kill_Switch_Score_10"), 0.0)
    dom10 = _safe_num(row.get("Dominance_Score_10"), 0.0)
    veto_reasons = str(row.get("Veto_Reasons", "") or "")
    fail_set = {x.strip() for x in str(row.get("Gate_Fail_Reasons", "") or "").split(",") if x.strip()}

    if fail_set & CALIBRATION_HARD_REJECT_REASONS:
        return "blocked", "hard_reject"
    if kill10 >= V49_KILL_SWITCH_BLOCK:
        return "blocked", "kill_switch_block"
    if fp10 >= V49_FALSE_POSITIVE_BLOCK and not (util10 >= 8.6 and asym10 >= 8.4 and trig10 >= 7.0):
        return "blocked", "false_positive_block"

    if archetype == "relative_value_continuation":
        rel_override = (
            util10 >= V49_RELVAL_OVERRIDE_UTIL
            and asym10 >= V49_RELVAL_OVERRIDE_ASYM
            and trig10 >= V49_RELVAL_OVERRIDE_TRIGGER
            and fp10 <= V49_RELVAL_OVERRIDE_FP_MAX
            and dom10 >= 7.2
            and (soft_candidate or not gate_passed)
        )
        if not rel_override:
            return "blocked", "relval_hard_block"
        return "override", "relval_override"

    if gate_passed:
        gate_override = (
            util10 >= V49_GATEPASS_REQUIRE_UTIL
            and asym10 >= V49_GATEPASS_REQUIRE_ASYM
            and trig10 >= V49_GATEPASS_REQUIRE_TRIGGER
            and dom10 >= 6.8
            and "gate_pass_leak" not in veto_reasons
        )
        if not gate_override:
            return "blocked", "gatepass_hard_block"
        return "override", "gatepass_override"

    if soft_candidate and util10 >= 6.4 and dom10 >= 5.8:
        return "preferred", "soft_survivor"
    if util10 >= 7.0 and asym10 >= 6.8 and dom10 >= 6.4:
        return "preferred", "utility_dominant"
    if dom10 >= 7.0:
        return "preferred", "comparative_edge"
    return "eligible", ""


def compute_selection_score(row: dict) -> tuple[float, float]:
    surv10 = _safe_num(row.get("Survivability_Score_10"))
    asym10 = _safe_num(row.get("Asymmetry_Score_10"))
    util10 = _safe_num(row.get("Calibration_Utility_Score_10"))
    trig10 = _safe_num(row.get("Trigger_Quality_Score_10"))
    kill10 = _safe_num(row.get("Kill_Switch_Score_10"), 0.0)
    fp10 = _safe_num(row.get("False_Positive_Risk_Score_10"), 0.0)
    archetype_tax10 = _safe_num(row.get("Archetype_Tax_Score_10"), 0.0)
    archetype = str(row.get("Setup_Archetype", "") or "")
    fail_set = {x.strip() for x in str(row.get("Gate_Fail_Reasons", "") or "").split(",") if x.strip()}
    soft_only = bool(fail_set) and fail_set.issubset(CALIBRATION_SOFT_FAIL_REASONS) and bool(row.get("Soft_Candidate"))
    gate_passed = bool(row.get("Calibration_Gate_Passed"))

    core_vals = [max(0.35, v) for v in (surv10, asym10, util10, trig10) if np.isfinite(v)]
    if len(core_vals) < 3:
        row["Admission_Class"] = "blocked"
        row["Override_Reason"] = "insufficient_metrics"
        return 0.0, -99.0

    gm = float(np.prod(core_vals)) ** (1.0 / len(core_vals))
    floor = min(core_vals)
    row_quality = 0.55 * gm + 0.45 * floor

    leakage_penalty = 0.0
    veto_reasons = []

    if kill10 >= V49_KILL_SWITCH_BLOCK:
        veto_reasons.append("kill_switch_block")
    if fp10 >= V49_FALSE_POSITIVE_BLOCK and not (np.isfinite(asym10) and asym10 >= 8.4 and np.isfinite(util10) and util10 >= 8.6 and trig10 >= 7.0):
        veto_reasons.append("false_positive_block")
    if gate_passed and ((not np.isfinite(asym10) or asym10 < V49_GATEPASS_REQUIRE_ASYM) or (not np.isfinite(util10) or util10 < V49_GATEPASS_REQUIRE_UTIL)):
        leakage_penalty += 1.65
        veto_reasons.append("gate_pass_leak")
    if archetype == "relative_value_continuation":
        rel_ok = (
            np.isfinite(asym10) and asym10 >= V49_RELVAL_OVERRIDE_ASYM
            and np.isfinite(util10) and util10 >= V49_RELVAL_OVERRIDE_UTIL
            and trig10 >= V49_RELVAL_OVERRIDE_TRIGGER
            and fp10 <= V49_RELVAL_OVERRIDE_FP_MAX
            and (soft_only or not gate_passed)
        )
        if not rel_ok:
            leakage_penalty += 2.20
            veto_reasons.append("relval_hard_block")

    row["Leakage_Penalty_Score"] = round(leakage_penalty, 4)
    row["Veto_Flag"] = bool(veto_reasons)
    row["Veto_Reasons"] = ", ".join(sorted(set(veto_reasons))) if veto_reasons else ""

    comparative10 = _safe_num(row.get("Comparative_Edge_Score_10"), np.nan)
    floor10 = _safe_num(row.get("Comparator_Floor_Score_10"), np.nan)
    dominance10 = _safe_num(row.get("Dominance_Score_10"), np.nan)
    if not np.isfinite(comparative10):
        comparative10 = 0.0
    if not np.isfinite(floor10):
        floor10 = 0.0
    if not np.isfinite(dominance10):
        dominance10 = 0.0

    score = (
        V49_COMPARATIVE_WEIGHT * (0.68 * (dominance10 / 10.0) + 0.32 * (comparative10 / 10.0)) * 10.0
        + V49_ROW_QUALITY_WEIGHT * row_quality
        - 0.35 * kill10
        - 0.30 * fp10
        - 0.16 * archetype_tax10
        - leakage_penalty
    )

    admission_class, override_reason = _classify_admission(row)
    row["Admission_Class"] = admission_class
    row["Override_Reason"] = override_reason

    if admission_class == "blocked":
        score -= V49_BLOCK_FLOOR_PENALTY
    elif admission_class == "override":
        score += V49_OVERRIDE_BONUS
    elif admission_class == "preferred":
        score += 0.20

    confidence = _safe_num(row.get("Confidence_Score"), 0.0)
    confidence_bonus = 0.05 if confidence >= 0.72 else 0.01 if confidence >= 0.56 else -0.06
    final_rank = score + confidence_bonus + 0.06 * (floor10 / 10.0)
    return round(score, 4), round(final_rank, 4)


def passes_live_gates(row: dict) -> tuple[bool, list, str]:
    reasons = []
    if row.get("status") != "OK":
        reasons.append("status_not_ok")
    if row.get("Data_Quality") == "poor":
        reasons.append("poor_data")
    if row.get("Entry_Label") == "D-tier avoid":
        reasons.append("d_tier")
    if row.get("Alignment") == "full conflict":
        reasons.append("full_conflict")
    if row.get("Displacement_Quality") == "weak / no displacement":
        reasons.append("weak_displacement")
    if row.get("MSS_BOS") == "no clear shift":
        reasons.append("no_clear_shift")
    if row.get("Preferred_Side") in {None, "", "N/A"}:
        reasons.append("no_side")
    exec_q = float(row.get("Decision_Execution_Quality", 0.0) or 0.0)
    setup_q = float(row.get("Decision_Setup_Quality", 0.0) or 0.0)
    dist_atr = _safe_num(row.get("Entry_Distance_ATR"))
    if exec_q < 1.80:
        reasons.append("weak_execution")
    if np.isfinite(dist_atr) and dist_atr > CALIBRATION_A_BOOK_MAX_ENTRY_ATR:
        reasons.append("entry_too_far_live")
    if row.get("Pivot_Conflict") == "strong pivot conflict" and not (setup_q >= 3.30 and exec_q >= 2.40 and row.get("Entry_Label") == "A-tier execution setup"):
        reasons.append("strong_pivot_conflict")
    if reasons:
        return False, reasons, "Rejected"
    return True, [], "A-book"


def passes_calibration_gates(row: dict) -> tuple[bool, list, str]:
    reasons = []
    if row.get("status") != "OK":
        reasons.append("status_not_ok")
    if row.get("Data_Quality") == "poor":
        reasons.append("poor_data")
    if row.get("Entry_Label") == "D-tier avoid":
        reasons.append("d_tier")
    if row.get("Preferred_Side") in {None, "", "N/A"}:
        reasons.append("no_side")
    exec_q = float(row.get("Decision_Execution_Quality", 0.0) or 0.0)
    setup_q = float(row.get("Decision_Setup_Quality", 0.0) or 0.0)
    dist_atr = _safe_num(row.get("Entry_Distance_ATR"))
    label = row.get("Entry_Label")
    max_dist = CALIBRATION_A_BOOK_MAX_ENTRY_ATR if label == "A-tier execution setup" else CALIBRATION_B_BOOK_MAX_ENTRY_ATR
    if exec_q < 1.10:
        reasons.append("weak_execution")
    if row.get("Displacement_Quality") == "weak / no displacement" and row.get("MSS_BOS") != "clear MSS/BOS":
        reasons.append("weak_impulse")
    if row.get("Alignment") == "full conflict" and row.get("Pivot_Conflict") == "strong pivot conflict":
        reasons.append("stacked_conflict")
    if np.isfinite(dist_atr) and dist_atr > max_dist:
        reasons.append("entry_too_far_calibration")
    if reasons:
        advisory_only = {"weak_impulse", "stacked_conflict", "d_tier"}
        bbook_ok = (
            label in {"B-tier reactive setup", "C-tier idea only", "A-tier execution setup", "D-tier avoid"}
            and "status_not_ok" not in reasons and "poor_data" not in reasons and "no_side" not in reasons
            and exec_q >= 1.05 and setup_q >= 1.20
            and (not np.isfinite(dist_atr) or dist_atr <= CALIBRATION_B_BOOK_MAX_ENTRY_ATR)
            and row.get("MSS_BOS") in {"clear MSS/BOS", "partial shift"}
            and row.get("Displacement_Quality") in {"strong displacement", "moderate displacement", "weak / no displacement"}
            and set(reasons).issubset(advisory_only)
        )
        if bbook_ok:
            return True, reasons, "B-book"
        return False, reasons, "Rejected"
    return True, [], "A-book"


def finalize_decision_fields(row: dict) -> dict:
    row = dict(row)
    row["Setup_Archetype"] = classify_setup_archetype(row)
    row["Decision_Setup_Quality"] = compute_setup_quality(row)
    row["Decision_Execution_Quality"] = compute_execution_quality(row)
    row["Technical_Quality_Score_10"] = compute_technical_quality_score_10(row)
    row["Execution_Realism_Score_10"] = compute_execution_realism_score_10(row)
    live_passed, live_reasons, live_book = passes_live_gates(row)
    cal_passed, cal_reasons, decision_book = passes_calibration_gates(row)
    row["Live_Gate_Passed"] = bool(live_passed)
    row["Calibration_Gate_Passed"] = bool(cal_passed)
    row["Gate_Passed"] = bool(cal_passed)
    fail_reasons = cal_reasons if cal_reasons else live_reasons
    fail_reason_set = set(fail_reasons)
    soft_candidate = (
        not (fail_reason_set & CALIBRATION_HARD_REJECT_REASONS)
        and bool(fail_reason_set)
        and fail_reason_set.issubset(CALIBRATION_SOFT_FAIL_REASONS)
        and float(row.get("Decision_Execution_Quality", 0.0) or 0.0) >= 1.00
        and float(row.get("Decision_Setup_Quality", 0.0) or 0.0) >= 1.00
    )
    reserve_candidate = (
        not bool(fail_reason_set & CALIBRATION_HARD_REJECT_REASONS)
        and float(row.get("Decision_Execution_Quality", 0.0) or 0.0) >= 0.90
        and float(row.get("Decision_Setup_Quality", 0.0) or 0.0) >= 0.90
    )
    row["Gate_Fail_Reasons"] = ", ".join(fail_reasons) if fail_reasons else ""
    row["Calibration_Soft_Candidate"] = bool(soft_candidate)
    candidate_bucket = _v37_candidate_bucket(cal_passed, soft_candidate, fail_reasons, row)
    row["Calibration_Candidate_Bucket"] = candidate_bucket
    row["Decision_Book"] = decision_book if cal_passed else ("Reserve" if reserve_candidate else decision_book)
    row["Soft_Candidate"] = bool(soft_candidate)
    row["Soft_Fail_Adjustment"] = round(_soft_fail_penalty(fail_reasons) if soft_candidate else 0.0, 4)
    row["Continuation_Subquality"] = _continuation_subquality(row)
    continuation_subquality = float(row.get("Continuation_Subquality", 0.0) or 0.0)
    row["Continuation_Elite_Eligible"] = bool(
        str(row.get("Setup_Archetype", "") or "") == "continuation"
        and continuation_subquality >= max(0.00, V38_CONTINUATION_MIN_SUBQUALITY - 0.05)
        and float(row.get("Decision_Execution_Quality", 0.0) or 0.0) >= (V38_CONTINUATION_MIN_EXECUTION_QUALITY - 0.20)
        and float(row.get("Decision_Setup_Quality", 0.0) or 0.0) >= (V38_CONTINUATION_MIN_SETUP_QUALITY - 0.20)
    )
    row["Context_Quality_Score_10"] = compute_context_quality_score_10(row)
    row["Trigger_Quality_Score_10"] = compute_trigger_quality_score_10(row)
    row["Conflict_Penalty_Score_10"] = compute_conflict_penalty_score_10(row)
    row["Opportunity_Score_10"] = compute_opportunity_score_10(row)
    row.setdefault("Balance_Score_10", compute_balance_score_10(
        _safe_num(row.get("Context_Quality_Score_10")),
        _safe_num(row.get("Trigger_Quality_Score_10")),
        _safe_num(row.get("Execution_Realism_Score_10")),
    ))
    row["Kill_Switch_Score_10"] = compute_kill_switch_score_10(row)
    row["False_Positive_Risk_Score_10"] = compute_false_positive_risk_score_10(row)
    row["Archetype_Tax_Score_10"] = compute_archetype_tax_score_10(row)
    row["Survivability_Score_10"] = compute_survivability_score_10(row)
    row["Asymmetry_Score_10"] = compute_asymmetry_score_10(row)
    row["Calibration_Utility_Score_10"] = compute_calibration_utility_score_10(row)
    radical_conf = compute_radical_confidence_from_row(row)
    row["Radical_Confidence_Score_10"] = radical_conf["score_10"]
    row["Calibrated_Confidence_Score_10"] = radical_conf["score_10"]
    row["Confidence_Score"] = radical_conf["score"]
    row["Confidence_Band"] = radical_conf["band"]
    selection_score, final_rank_score = compute_selection_score(row)
    row["Selection_Score"] = selection_score
    row["Final_Rank_Score"] = final_rank_score
    row["Decision_Rank_Score"] = round(final_rank_score, 4)
    row["Base_Ranking_Score"] = row["Selection_Score"]
    row["Ranking_Score"] = row["Final_Rank_Score"]
    row["Selector_Profile"] = "v5.5_prediction_ready_selector"
    row["Fragility_Reason"] = _v41_fragility_reason(row)
    row["Idea_Family"] = _v41_idea_family(row)
    row["Survivor_Score"] = round(0.65 * _safe_num(row.get("Survivability_Score_10"), 0.0) + 0.20 * _safe_num(row.get("Calibration_Utility_Score_10"), 0.0) - 0.25 * _safe_num(row.get("False_Positive_Risk_Score_10"), 0.0), 4)
    row["Tournament_Pool"] = "radical_board"
    row["Tournament_Pool_Display"] = "Radical board"
    row["Tournament_Pool_Eligible"] = "radical_board"
    row["Local_Pool_Score"] = row.get("Final_Rank_Score", row["Decision_Rank_Score"])
    row["Tournament_Finalist_Flag"] = False
    row.setdefault("Selection_Lane", "")
    row.setdefault("Veto_Flag", False)
    row.setdefault("Veto_Reasons", "")
    row.setdefault("Leakage_Penalty_Score", 0.0)
    row["Shortlist_Slot_Name"] = ""
    row["Shortlist_Slot_Order"] = np.nan
    row["Crowding_Block_Reason"] = ""
    row["Selection_Passed_Over_For_Diversity"] = ""
    return row

def base_ranking_score(row: dict) -> float:
    for key in ("Final_Rank_Score", "Selection_Score", "Decision_Rank_Score"):
        if row.get(key) is not None:
            try:
                return float(row.get(key))
            except Exception:
                pass
    setup_q = float(compute_setup_quality(row))
    exec_q = float(compute_execution_quality(row))
    dist_atr = _safe_num(row.get("Entry_Distance_ATR"))
    archetype = str(row.get("Setup_Archetype", "") or "")
    cont_subq = float(row.get("Continuation_Subquality", 0.0) or 0.0)
    score = V40_SETUP_WEIGHT * setup_q + V40_EXECUTION_WEIGHT * exec_q + _robustness_adjustment(row)
    if np.isfinite(dist_atr):
        if dist_atr <= 0.35:
            score += V40_ENTRY_DIST_BONUS_TIGHT
        elif dist_atr <= 0.50:
            score += V40_ENTRY_DIST_BONUS_GOOD
        elif dist_atr > 0.90:
            score += V40_ENTRY_DIST_PENALTY_FAR
    if archetype == "relative_value_continuation":
        score += V41_RELVAL_BONUS
    elif archetype == "continuation":
        if cont_subq >= 0.20:
            score += V41_CONT_SUBQ_GOOD
        elif cont_subq < V41_CONTINUATION_SUBQUALITY_FLOOR:
            score += V41_CONT_SUBQ_BAD
    return round(score, 4)


def _choose_from_finalists(finalists: list, slot_name: str, shortlist: list, used_currency_counter: Counter, used_cluster_counter: Counter, theme_counter: Counter, soft_count: int, bbook_count: int, continuation_count: int, slot_order: int):
    def slot_ok(row: dict) -> bool:
        if slot_name == "challenger":
            return str(row.get("Tournament_Pool", "") or "") == "best_challenger"
        if slot_name == "continuation":
            return str(row.get("Tournament_Pool", "") or "") == "best_continuation"
        if slot_name == "relval":
            return str(row.get("Tournament_Pool", "") or "") == "best_relval"
        if slot_name == "diversified":
            return str(row.get("Tournament_Pool", "") or "") == "best_diversified"
        if slot_name == "reserve":
            return str(row.get("Tournament_Pool", "") or "") == "best_reserve"
        return True

    for row in finalists:
        if not slot_ok(row):
            continue
        reason = _selection_block_reason(row, used_currency_counter, used_cluster_counter, theme_counter, shortlist, soft_count, bbook_count, continuation_count, slot_name)
        if reason:
            _mark_passed_over(row, reason)
            continue

        sym = row["Instrument"]
        tags = row.get("Cluster_Tags_List", [])
        archetype = str(row.get("Setup_Archetype", "") or "")
        penalty = _tournament_uniqueness_penalty(sym, tags, used_currency_counter, used_cluster_counter, theme_counter, continuation_count=continuation_count, archetype=archetype, shortlist=shortlist)
        final_rank = round(float(row.get("Local_Pool_Score", row.get("Decision_Rank_Score", 0.0)) or 0.0) - penalty, 4)
        portfolio_fit = round(max(0.0, min(4.0, 4.0 - penalty)), 2)

        row_copy = dict(row)
        row_copy["Overlap_Penalty"] = penalty
        row_copy["Decision_Portfolio_Fit"] = portfolio_fit
        row_copy["Ranking_Score"] = final_rank
        row_copy["Shortlist_Slot_Name"] = slot_name
        row_copy["Shortlist_Slot_Type"] = slot_name
        row_copy["Shortlist_Slot_Order"] = slot_order
        shortlist.append(row_copy)

        base, quote = pair_currencies(sym)
        used_currency_counter[base] += 1
        used_currency_counter[quote] += 1
        for t in tags:
            used_cluster_counter[t] += 1
        for t in _theme_tags(tags):
            theme_counter[t] += 1
        if row.get("Decision_Book") == "B-book":
            bbook_count += 1
        if row.get("Calibration_Candidate_Bucket") in {"soft_pass", "challenger"}:
            soft_count += 1
        if archetype == "continuation":
            continuation_count += 1

        finalists.remove(row)
        return soft_count, bbook_count, continuation_count, True

    return soft_count, bbook_count, continuation_count, False



def _v50_initialize_row_flags(row: dict) -> None:
    row["In_Top_Shortlist"] = False
    row["Primary_Override_Flag"] = False
    row["Primary_Shortlist_Flag"] = False
    row["Shadow_Watchlist_Flag"] = False
    row["Shadow_Watchlist_Reason"] = ""
    row["Shadow_Watchlist_Order"] = np.nan
    row.setdefault("Selection_Lane", "unclassified")
    row.setdefault("Shortlist_Eligibility", "unclassified")
    row.setdefault("Admission_Binding_Status", "unclassified")


def _classify_admission_v50(row: dict) -> tuple[str, str, str, str]:
    archetype = str(row.get("Setup_Archetype", "") or "")
    gate_passed = bool(row.get("Calibration_Gate_Passed"))
    soft_candidate = bool(row.get("Soft_Candidate"))
    util10 = _safe_num(row.get("Calibration_Utility_Score_10"), 0.0)
    asym10 = _safe_num(row.get("Asymmetry_Score_10"), 0.0)
    trig10 = _safe_num(row.get("Trigger_Quality_Score_10"), 0.0)
    fp10 = _safe_num(row.get("False_Positive_Risk_Score_10"), 0.0)
    kill10 = _safe_num(row.get("Kill_Switch_Score_10"), 0.0)
    dom10 = _safe_num(row.get("Dominance_Score_10"), 0.0)
    fail_set = {x.strip() for x in str(row.get("Gate_Fail_Reasons", "") or "").split(",") if x.strip()}

    if fail_set & CALIBRATION_HARD_REJECT_REASONS:
        return "blocked", "hard_reject", "blocked", "blocked_hard"
    if kill10 >= V50_KILL_BLOCK:
        return "blocked", "kill_switch_block", "blocked", "blocked_kill"
    if fp10 >= V50_FALSE_POSITIVE_BLOCK and not (util10 >= 8.7 and asym10 >= 8.5 and trig10 >= 7.2):
        return "blocked", "false_positive_block", "blocked", "blocked_false_positive"

    if archetype == "relative_value_continuation":
        rel_proof = (
            util10 >= V50_RELVAL_PROOF_UTIL
            and asym10 >= V50_RELVAL_PROOF_ASYM
            and trig10 >= V50_RELVAL_PROOF_TRIGGER
            and dom10 >= V50_RELVAL_PROOF_DOM
            and fp10 <= 3.2
            and (soft_candidate or not gate_passed)
        )
        if rel_proof:
            return "quarantined", "relval_shadow_only", "shadow_only", "quarantine_relval"
        return "blocked", "relval_hard_block", "blocked", "blocked_relval"

    if gate_passed:
        gate_proof = (
            util10 >= V50_GATEPASS_PROOF_UTIL
            and asym10 >= V50_GATEPASS_PROOF_ASYM
            and trig10 >= V50_GATEPASS_PROOF_TRIGGER
            and dom10 >= V50_GATEPASS_PROOF_DOM
            and fp10 <= 3.4
        )
        if gate_proof:
            return "quarantined", "gatepass_shadow_only", "shadow_only", "quarantine_gatepass"
        return "blocked", "gatepass_primary_block", "blocked", "blocked_gatepass"

    if soft_candidate and util10 >= 6.4 and dom10 >= 5.8:
        return "preferred", "soft_survivor", "primary", "primary_soft_survivor"
    if util10 >= 7.0 and asym10 >= 6.8 and dom10 >= 6.4:
        return "preferred", "utility_dominant", "primary", "primary_utility_dominant"
    if dom10 >= 6.9:
        return "preferred", "comparative_edge", "primary", "primary_comparative_edge"
    return "eligible", "", "primary", "primary_eligible"


def compute_selection_score(row: dict) -> tuple[float, float]:
    surv10 = _safe_num(row.get("Survivability_Score_10"))
    asym10 = _safe_num(row.get("Asymmetry_Score_10"))
    util10 = _safe_num(row.get("Calibration_Utility_Score_10"))
    trig10 = _safe_num(row.get("Trigger_Quality_Score_10"))
    kill10 = _safe_num(row.get("Kill_Switch_Score_10"), 0.0)
    fp10 = _safe_num(row.get("False_Positive_Risk_Score_10"), 0.0)
    archetype_tax10 = _safe_num(row.get("Archetype_Tax_Score_10"), 0.0)

    core_vals = [max(0.35, v) for v in (surv10, asym10, util10, trig10) if np.isfinite(v)]
    if len(core_vals) < 3:
        row["Admission_Class"] = "blocked"
        row["Override_Reason"] = "insufficient_metrics"
        row["Shortlist_Eligibility"] = "blocked"
        row["Admission_Binding_Status"] = "blocked_insufficient_metrics"
        row["Selection_Lane"] = "blocked_insufficient_metrics"
        return 0.0, -99.0

    gm = float(np.prod(core_vals)) ** (1.0 / len(core_vals))
    floor = min(core_vals)
    row_quality = 0.52 * gm + 0.48 * floor

    comparative10 = _safe_num(row.get("Comparative_Edge_Score_10"), 0.0)
    floor10 = _safe_num(row.get("Comparator_Floor_Score_10"), 0.0)
    dominance10 = _safe_num(row.get("Dominance_Score_10"), 0.0)

    leakage_penalty = 0.0
    veto_reasons = []
    if kill10 >= V50_KILL_BLOCK:
        veto_reasons.append("kill_switch_block")
    if fp10 >= V50_FALSE_POSITIVE_BLOCK and not (np.isfinite(asym10) and asym10 >= 8.5 and np.isfinite(util10) and util10 >= 8.7 and trig10 >= 7.2):
        veto_reasons.append("false_positive_block")

    admission_class, override_reason, shortlist_eligibility, lane = _classify_admission_v50(row)
    row["Admission_Class"] = admission_class
    row["Override_Reason"] = override_reason
    row["Shortlist_Eligibility"] = shortlist_eligibility
    row["Admission_Binding_Status"] = lane
    row["Selection_Lane"] = lane

    if admission_class == "quarantined":
        leakage_penalty += V50_QUARANTINE_TAX
        veto_reasons.append("shadow_only_quarantine")
    elif admission_class == "blocked":
        leakage_penalty += 3.0

    row["Leakage_Penalty_Score"] = round(leakage_penalty, 4)
    row["Veto_Flag"] = bool(veto_reasons)
    row["Veto_Reasons"] = ", ".join(sorted(set(veto_reasons))) if veto_reasons else ""

    score = (
        V50_COMPARATIVE_WEIGHT * (0.72 * (dominance10 / 10.0) + 0.28 * (comparative10 / 10.0)) * 10.0
        + V50_ROW_QUALITY_WEIGHT * row_quality
        - 0.33 * kill10
        - 0.28 * fp10
        - 0.14 * archetype_tax10
        - leakage_penalty
    )

    if admission_class == "blocked":
        score -= V50_BLOCK_FLOOR_PENALTY
    elif admission_class == "preferred":
        score += V50_PRIMARY_PREFERRED_BONUS
    elif admission_class == "eligible":
        score += V50_PRIMARY_ELIGIBLE_BONUS

    confidence = _safe_num(row.get("Confidence_Score"), 0.0)
    confidence_bonus = 0.05 if confidence >= 0.72 else 0.01 if confidence >= 0.56 else -0.06
    final_rank = score + confidence_bonus + 0.08 * (floor10 / 10.0)
    return round(score, 4), round(final_rank, 4)


def _v521_shadow_fallback_candidates(ordered: list[dict], shortlist: list[dict]) -> list[dict]:
    shortlisted = {str(r.get("Instrument", "") or "") for r in shortlist}
    fallback = []
    for row in ordered:
        sym = str(row.get("Instrument", "") or "")
        if not sym or sym in shortlisted:
            continue
        if bool(row.get("In_Top_Shortlist")):
            continue
        if bool(row.get("Calibration_Gate_Passed")):
            continue
        if str(row.get("Setup_Archetype", "") or "") == "relative_value_continuation":
            continue
        if str(row.get("Admission_Class", "") or "") == "blocked":
            continue
        if str(row.get("Shortlist_Eligibility", "") or "") != "primary":
            continue
        util10 = _safe_num(row.get("Calibration_Utility_Score_10"), 0.0)
        asym10 = _safe_num(row.get("Asymmetry_Score_10"), 0.0)
        dom10 = _safe_num(row.get("Dominance_Score_10"), 0.0)
        trig10 = _safe_num(row.get("Trigger_Quality_Score_10"), 0.0)
        fp10 = _safe_num(row.get("False_Positive_Risk_Score_10"), 99.0)
        if util10 < V521_SHADOW_MIN_UTIL or asym10 < V521_SHADOW_MIN_ASYM or dom10 < V521_SHADOW_MIN_DOM or trig10 < V521_SHADOW_MIN_TRIGGER:
            continue
        if fp10 > V521_SHADOW_FP_MAX:
            continue
        row["_shadow_priority"] = round(float(row.get("Final_Rank_Score", 0.0) or 0.0) + V521_SHADOW_FALLBACK_BONUS, 4)
        fallback.append(row)
    fallback.sort(
        key=lambda x: (
            float(x.get("_shadow_priority", x.get("Final_Rank_Score", 0.0)) or 0.0),
            float(x.get("Dominance_Score_10", 0.0) or 0.0),
            float(x.get("Calibration_Utility_Score_10", 0.0) or 0.0),
            float(x.get("Asymmetry_Score_10", 0.0) or 0.0),
            float(x.get("Trigger_Quality_Score_10", 0.0) or 0.0),
        ),
        reverse=True,
    )
    return fallback


def _v521_mark_shadow_row(row: dict, order: int, reason: str) -> None:
    row["Shadow_Watchlist_Flag"] = True
    row["Shadow_Watchlist_Reason"] = reason
    row["Shadow_Watchlist_Order"] = order
    row["Selection_Lane"] = "shadow_watchlist"


def build_shortlist(summary_rows: list, shortlist_n: int = TOP_SHORTLIST_N) -> tuple[list, list]:
    prepared = [finalize_decision_fields(r) for r in summary_rows if r.get("status") == "OK"]
    _assign_comparative_metrics(prepared)

    for row in prepared:
        _v50_initialize_row_flags(row)
        selection_score, final_rank_score = compute_selection_score(row)
        row["Selection_Score"] = selection_score
        row["Final_Rank_Score"] = final_rank_score
        row["Decision_Rank_Score"] = base_ranking_score(row)
        row["Base_Ranking_Score"] = row["Selection_Score"]
        row["Ranking_Score"] = row["Final_Rank_Score"]
        row["Tournament_Finalist_Flag"] = True
        row["Selector_Profile"] = "v5.5_prediction_ready_selector"

    ordered = sorted(
        prepared,
        key=lambda x: (
            float(x.get("Final_Rank_Score", 0.0) or 0.0),
            float(x.get("Dominance_Score_10", 0.0) or 0.0),
            float(x.get("Calibration_Utility_Score_10", 0.0) or 0.0),
            float(x.get("Asymmetry_Score_10", 0.0) or 0.0),
            float(x.get("Trigger_Quality_Score_10", 0.0) or 0.0),
        ),
        reverse=True,
    )

    shortlist = []
    used_currency_counter = Counter()
    used_cluster_counter = Counter()
    theme_counter = Counter()
    soft_count = 0
    bbook_count = 0
    continuation_count = 0
    slot_order = 1

    def add_row(row: dict, lane: str) -> bool:
        nonlocal soft_count, bbook_count, continuation_count, slot_order
        reason = _selection_block_reason(row, used_currency_counter, used_cluster_counter, theme_counter, shortlist, soft_count, bbook_count, continuation_count, lane)
        if reason:
            _mark_passed_over(row, reason)
            if str(row.get("Selection_Lane", "")).startswith("primary"):
                row["Selection_Lane"] = f"passed_over::{reason}"
            return False

        sym = row["Instrument"]
        tags = row.get("Cluster_Tags_List", [])
        archetype = str(row.get("Setup_Archetype", "") or "")
        penalty = _tournament_uniqueness_penalty(sym, tags, used_currency_counter, used_cluster_counter, theme_counter, continuation_count=continuation_count, archetype=archetype, shortlist=shortlist)
        final_rank = round(float(row.get("Final_Rank_Score", 0.0) or 0.0) - penalty, 4)
        portfolio_fit = round(max(0.0, min(4.0, 4.0 - penalty)), 2)
        row["Overlap_Penalty"] = penalty
        row["Decision_Portfolio_Fit"] = portfolio_fit
        row["Ranking_Score"] = final_rank
        row["Shortlist_Slot_Name"] = lane
        row["Shortlist_Slot_Type"] = lane
        row["Selection_Lane"] = lane
        row["Shortlist_Slot_Order"] = slot_order
        row["In_Top_Shortlist"] = True
        row["Primary_Shortlist_Flag"] = True
        shortlist.append(dict(row))

        base, quote = pair_currencies(sym)
        used_currency_counter[base] += 1
        used_currency_counter[quote] += 1
        for t in tags:
            used_cluster_counter[t] += 1
        for t in _theme_tags(tags):
            theme_counter[t] += 1
        if row.get("Decision_Book") == "B-book":
            bbook_count += 1
        if row.get("Calibration_Candidate_Bucket") in {"soft_pass", "challenger"} or bool(row.get("Soft_Candidate")):
            soft_count += 1
        if archetype == "continuation":
            continuation_count += 1
        slot_order += 1
        return True

    primary_pool = [
        r for r in ordered
        if str(r.get("Shortlist_Eligibility", "") or "") == "primary"
        and str(r.get("Admission_Class", "") or "") in {"preferred", "eligible"}
        and bool(r.get("Gate_Passed"))
        and str(r.get("Setup_Archetype", "") or "") != "relative_value_continuation"
        and not bool(r.get("Veto_Flag"))
    ]
    primary_override_pool = [
        r for r in ordered
        if str(r.get("Shortlist_Eligibility", "") or "") == "primary"
        and str(r.get("Admission_Class", "") or "") in {"preferred", "eligible"}
        and not bool(r.get("Gate_Passed"))
        and str(r.get("Setup_Archetype", "") or "") != "relative_value_continuation"
        and not bool(r.get("Veto_Flag"))
        and _safe_num(r.get("Calibration_Utility_Score_10"), 0.0) >= 7.6
        and _safe_num(r.get("Conflict_Penalty_Score_10"), 0.0) <= 1.6
    ]
    best_remaining = list(primary_pool)
    shadow_pool = [r for r in ordered if str(r.get("Shortlist_Eligibility", "") or "") == "shadow_only" and str(r.get("Admission_Class", "") or "") == "quarantined"]

    for row in primary_pool:
        if len(shortlist) >= shortlist_n:
            break
        if any(x.get("Instrument") == row.get("Instrument") for x in shortlist):
            continue
        row["Primary_Override_Flag"] = False
        add_row(row, "primary_gatepass")

    for row in primary_override_pool:
        if len(shortlist) >= shortlist_n:
            break
        if any(x.get("Instrument") == row.get("Instrument") for x in shortlist):
            continue
        row["Primary_Override_Flag"] = True
        row["Override_Reason"] = str(row.get("Override_Reason", "") or "defensible_primary_override")
        add_row(row, "primary_override")

    for row in best_remaining:
        if len(shortlist) >= shortlist_n:
            break
        if any(x.get("Instrument") == row.get("Instrument") for x in shortlist):
            continue
        row["Primary_Override_Flag"] = False
        add_row(row, "primary_best_remaining")

    shadow_count = 0
    shadow_limit = V521_SHADOW_WATCHLIST_N
    for row in shadow_pool:
        if shadow_count >= shadow_limit:
            break
        if row.get("In_Top_Shortlist"):
            continue
        shadow_count += 1
        _v521_mark_shadow_row(row, shadow_count, str(row.get("Override_Reason", "") or "quarantined_exception"))

    if shadow_count < shadow_limit:
        fallback_shadow_pool = _v521_shadow_fallback_candidates(ordered, shortlist)
        for row in fallback_shadow_pool:
            if shadow_count >= shadow_limit:
                break
            if row.get("Shadow_Watchlist_Flag") or row.get("In_Top_Shortlist"):
                continue
            shadow_count += 1
            _v521_mark_shadow_row(row, shadow_count, "near_miss_primary")

    for row in prepared:
        if row.get("In_Top_Shortlist"):
            continue
        if row.get("Shadow_Watchlist_Flag"):
            if str(row.get("Selection_Lane", "")).startswith("quarantine"):
                continue
            row["Selection_Lane"] = "shadow_watchlist"
        elif str(row.get("Admission_Class", "") or "") == "blocked":
            # keep blocking lane from classifier
            pass
        elif str(row.get("Shortlist_Eligibility", "") or "") == "primary":
            if not str(row.get("Selection_Lane", "")).startswith("passed_over::"):
                row["Selection_Lane"] = "primary_not_selected"
        else:
            row["Selection_Lane"] = row.get("Selection_Lane") or "unclassified"

    return [dict(r) for r in prepared if r.get("In_Top_Shortlist")], [dict(r) for r in prepared]

def _validate_selector_export_rows(rows: list[dict], required_fields: list[str], required_nonblank_fields: list[str], expected_profile: str) -> None:
    if not rows:
        return
    missing = []
    blank = []
    wrong_profile = []
    for idx, row in enumerate(rows):
        ident = f"{row.get('Snapshot_Date','?')}::{row.get('Instrument','?')}"
        for fld in required_fields:
            if fld not in row:
                missing.append(f"{ident}:{fld}")
        for fld in required_nonblank_fields:
            val = row.get(fld)
            if val is None or (isinstance(val, str) and not val.strip()):
                blank.append(f"{ident}:{fld}")
        if str(row.get('Selector_Profile','') or '') != expected_profile:
            wrong_profile.append(f"{ident}:{row.get('Selector_Profile')}")
    problems = []
    if missing:
        problems.append('missing=' + ', '.join(missing[:12]))
    if blank:
        problems.append('blank=' + ', '.join(blank[:12]))
    if wrong_profile:
        problems.append('selector_profile=' + ', '.join(wrong_profile[:12]))
    if problems:
        raise RuntimeError('v5.1 export-guard failure: ' + ' | '.join(problems))


def analyze_symbol_ict(sym: str, h1: pd.DataFrame, d1: pd.DataFrame, w1: pd.DataFrame, d1_strength: dict, cache: dict) -> dict:
    d_info = daily_bias_from_last_closed_d1(d1)
    w_info = weekly_bias_from_last_closed_w1(w1)

    dealing = active_dealing_range(d1)
    current_price = float(last_completed(h1).iloc[-1]["close"])
    side = price_side_vs_range(current_price, dealing)
    data_quality = "good" if min(len(last_completed(h1)), len(last_completed(d1)), len(last_completed(w1))) >= 20 else "limited"

    pivots = compute_pivot_pack(d1, w1)
    pivot_context = classify_pivot_context(current_price, pivots, d_info["bias"])

    liq = detect_recent_liquidity_event(h1)
    disp = detect_displacement(h1, liq["idx"])
    mss = detect_mss_bos(h1, liq)
    session_quality = current_session_quality(h1)
    rs_alignment = pair_rs_alignment(sym, d1_strength, d_info["bias"])
    smt_hint = detect_smt_hint(sym, cache)

    entry_zones = build_confluence_entry_zones(h1, d_info, dealing)
    array_quality = classify_array_quality(entry_zones)
    best_zone = entry_zones[0] if entry_zones else None

    a1, alignment = score_bias_clarity(w_info["bias"], d_info["bias"])
    a2 = score_dealing_location(d_info["bias"], side, dealing)
    a3 = score_liquidity(liq)
    b1 = score_displacement(disp)
    b2 = score_mss(mss)
    b3 = score_array_quality(array_quality)
    c1 = score_session(session_quality)
    c2 = score_rs(rs_alignment)
    d_bonus = score_smt(smt_hint)
    p_score = score_pivots(pivot_context)

    technical_raw = a1 + a2 + a3 + b1 + b2 + b3 + c1 + c2 + d_bonus + p_score
    technical_score = apply_penalties(technical_raw, disp, mss, best_zone, session_quality, rs_alignment, pivot_context, liq)
    entry_label = entry_label_from_metrics(disp, mss, array_quality, session_quality, pivot_context, liq)

    if disp["quality"] == "weak / no displacement" and mss["status"] == "no clear shift" and technical_score > 2.5:
        technical_score = 2.5
        if entry_label == "A-tier execution setup":
            entry_label = "B-tier reactive setup"

    confidence = compute_confidence(data_quality, liq, disp, mss, pivot_context)

    pack = {
        "d_info": d_info,
        "w_info": w_info,
        "dealing": dealing,
        "price_side": side,
        "alignment": alignment,
        "liquidity_condition": liq["condition"],
        "sweep_quality": liq["sweep_quality"],
        "liquidity_side": liq.get("side"),
        "liquidity_tier": liq.get("liquidity_tier"),
        "liquidity_reference_type": liq.get("reference_type"),
        "rejection_quality": liq.get("rejection_quality"),
        "follow_through": liq.get("follow_through"),
        "both_sides_taken_recently": liq.get("both_sides_taken_recently"),
        "displacement_quality": disp["quality"],
        "mss_bos": mss["status"],
        "array_quality": array_quality,
        "session_quality": session_quality,
        "rs_rw_alignment": rs_alignment,
        "smt_hint": smt_hint,
        "technical_score": round(technical_score, 2),
        "entry_label": entry_label,
        "entry_zones": entry_zones,
        "execution": derive_execution_plan(sym, h1, d_info, w_info, {"entry_zones": entry_zones}),
        "layer": instrument_layer(sym),
        "cluster_tags": detect_clusters(sym, derive_execution_plan(sym, h1, d_info, w_info, {"entry_zones": entry_zones})["preferred_side"], w_info["bias"], d_info["bias"]),
        "pivot_context": pivot_context,
        "pivot_pack": pivots,
        "confidence": confidence,
        "data_quality": data_quality,
    }
    return pack

# =========================================================
# PLOTTING
# =========================================================
def plot_candles(ax, df: pd.DataFrame, body_width: float = 0.70):
    for i, row in df.iterrows():
        o, h, l, c = row["open"], row["high"], row["low"], row["close"]
        color = BULL_COLOR if c >= o else BEAR_COLOR
        ax.vlines(i, l, h, linewidth=1, color=color, alpha=0.9)
        body_low = min(o, c)
        body_h = abs(c - o)
        if body_h == 0:
            body_h = (h - l) * 0.03
        ax.add_patch(
            plt.Rectangle(
                (i - body_width / 2, body_low),
                body_width,
                body_h,
                facecolor=color,
                edgecolor=color,
                alpha=0.65,
            )
        )

def _basic_axis(ax, df, fmt: str, ticks_n: int = 8):
    ticks = np.linspace(0, len(df) - 1, min(ticks_n, len(df)), dtype=int)
    ax.set_xticks(ticks)
    ax.set_xticklabels([pd.Timestamp(ensure_datetime_column(df).loc[i, "datetime"]).strftime(fmt) for i in ticks], rotation=30, ha="right", fontsize=8)
    ax.grid(True, linewidth=0.5, alpha=0.3)
    ax.set_ylabel("Price")

def plot_weekly_perspective(symbol: str, w1: pd.DataFrame, w_info: dict, out_png: Path):
    df = w1.copy()
    if len(df) > W1_PLOT_BARS:
        df = df.iloc[-W1_PLOT_BARS:].reset_index(drop=True)

    fig = plt.figure(figsize=(12, 6.5))
    ax = fig.add_axes([0.07, 0.17, 0.90, 0.75])
    plot_candles(ax, df, body_width=0.60)

    pwh, pwl, weq = w_info["pwh"], w_info["pwl"], w_info["weq"]
    ax.axhline(pwh, linewidth=1.3, linestyle="-")
    ax.axhline(pwl, linewidth=1.3, linestyle="-")
    ax.axhline(weq, linewidth=1.0, linestyle="--")

    ymin = min(df["low"].min(), pwl) * 0.999
    ymax = max(df["high"].max(), pwh) * 1.001
    ax.set_ylim(ymin, ymax)
    ax.axhspan(weq, ymax, alpha=0.08)
    ax.axhspan(ymin, weq, alpha=0.08)

    ax.set_title(f"{symbol} — W1 Perspective | Weekly Bias: {w_info['bias']} | PW: {w_info['pw_date']}")
    ax.text(
        0.01, 0.02,
        f"PWH={pwh:.5f} | PWL={pwl:.5f} | WEQ(50%)={weq:.5f}",
        transform=ax.transAxes, fontsize=9, va="bottom"
    )
    _basic_axis(ax, df, "%Y-%m-%d", ticks_n=8)

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=200)
    plt.close(fig)

def plot_daily_perspective(symbol: str, d1: pd.DataFrame, d_info: dict, w_info: dict, out_png: Path):
    df = d1.copy()
    if len(df) > D1_PLOT_BARS:
        df = df.iloc[-D1_PLOT_BARS:].reset_index(drop=True)

    fig = plt.figure(figsize=(12, 6.5))
    ax = fig.add_axes([0.07, 0.17, 0.90, 0.75])
    plot_candles(ax, df, body_width=0.65)

    pdh, pdl, eq = d_info["pdh"], d_info["pdl"], d_info["eq"]
    weq = w_info["weq"]

    ax.axhline(pdh, linewidth=1.3, linestyle="-")
    ax.axhline(pdl, linewidth=1.3, linestyle="-")
    ax.axhline(eq, linewidth=1.0, linestyle="--")
    ax.axhline(weq, linewidth=1.0, linestyle=":")

    ymin = min(df["low"].min(), pdl) * 0.999
    ymax = max(df["high"].max(), pdh) * 1.001
    ax.set_ylim(ymin, ymax)
    ax.axhspan(eq, ymax, alpha=0.08)
    ax.axhspan(ymin, eq, alpha=0.08)

    ax.set_title(f"{symbol} — D1 Perspective | Daily Bias: {d_info['bias']} | Weekly Bias: {w_info['bias']} | PD: {d_info['pd_date']}")
    ax.text(
        0.01, 0.02,
        f"PDH={pdh:.5f} | PDL={pdl:.5f} | DEQ={eq:.5f} | WEQ={weq:.5f}",
        transform=ax.transAxes, fontsize=9, va="bottom"
    )
    _basic_axis(ax, df, "%m-%d", ticks_n=8)

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=200)
    plt.close(fig)

def plot_h1(symbol: str, h1: pd.DataFrame, d_info: dict, w_info: dict, entry_zones: list, ict_pack: dict, out_png: Path):
    df = h1.copy()
    if len(df) > H1_PLOT_BARS:
        df = df.iloc[-H1_PLOT_BARS:].reset_index(drop=True)

    fig = plt.figure(figsize=(12, 7.6))
    ax = fig.add_axes([0.07, 0.18, 0.90, 0.73])

    plot_candles(ax, df, body_width=0.70)

    pdh, pdl, deq = d_info["pdh"], d_info["pdl"], d_info["eq"]
    weq = w_info["weq"]

    ax.axhline(pdh, linewidth=1.3, linestyle="-")
    ax.axhline(pdl, linewidth=1.3, linestyle="-")
    ax.axhline(deq, linewidth=1.0, linestyle="--")
    ax.axhline(weq, linewidth=1.0, linestyle=":")

    ymin = min(df["low"].min(), pdl) * 0.999
    ymax = max(df["high"].max(), pdh) * 1.001
    ax.set_ylim(ymin, ymax)

    ax.axhspan(deq, ymax, alpha=0.08)
    ax.axhspan(ymin, deq, alpha=0.08)

    for idx, z in enumerate(entry_zones, start=1):
        ax.axhspan(z["lo"], z["hi"], alpha=0.25)
        label = "+".join(["OTE"] + z["arrays"])
        ax.text(
            0.985,
            (z["lo"] + z["hi"]) / 2.0,
            f"Entry {idx}: {label} | score {z['score']} | touches {z.get('touches', 0)}",
            ha="right",
            va="center",
            fontsize=9,
            transform=ax.get_yaxis_transform(),
        )

    exec_text = ict_pack["execution"]["entry_text"]
    cluster_text = ", ".join(ict_pack["cluster_tags"])

    ax.set_title(
        f"{symbol} — H1 | Layer: {ict_pack['layer']} | D1 Bias: {d_info['bias']} | "
        f"W1 Bias: {w_info['bias']} | Tech={ict_pack['technical_score']:.2f} | {ict_pack['entry_label']}"
    )

    diagnostics = (
        f"liquidity={ict_pack['liquidity_condition']} / {ict_pack['sweep_quality']}\n"
        f"displacement={ict_pack['displacement_quality']} | MSS/BOS={ict_pack['mss_bos']}\n"
        f"array={ict_pack['array_quality']} | session={ict_pack['session_quality']}\n"
        f"RS/RW={ict_pack['rs_rw_alignment']} | SMT={ict_pack['smt_hint']}\n"
        f"clusters={cluster_text}\n"
        f"{exec_text}"
    )

    ax.text(
        0.01, 0.02, diagnostics,
        transform=ax.transAxes,
        fontsize=8.3,
        va="bottom",
        ha="left",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.75),
    )

    _basic_axis(ax, df, "%m-%d %H:%M", ticks_n=8)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=200)
    plt.close(fig)

# =========================================================
# EXPORT HELPERS
# =========================================================
def json_ready(obj):
    if isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, dict):
        return {k: json_ready(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [json_ready(v) for v in obj]
    return obj

def build_analyst_summary(analysis_records: list, title: str) -> str:
    lines = []
    lines.append(f"# {title} — {DATE_STR}")
    lines.append("")
    lines.append("This file is intended as a structured technical summary for downstream LLM analysis.")
    lines.append("Use this as primary technical source; use charts as secondary visual confirmation.")
    lines.append("")

    ranked = sorted(
        [r for r in analysis_records if r.get("status") == "OK"],
        key=lambda x: x.get("Ranking_Score", x.get("Technical_Score_0_4", 0.0)),
        reverse=True,
    )

    for r in ranked:
        lines.append(f"## {r['Instrument']}")
        lines.append(f"- Layer: {r.get('Universe_Layer', 'N/A')}")
        lines.append(f"- Clusters: {r.get('Cluster_Tags', 'N/A')}")
        lines.append(f"- Preferred side: {r.get('Preferred_Side') or 'N/A'}")
        lines.append(f"- W1 bias: {r.get('W1_Bias', 'N/A')}")
        lines.append(f"- D1 bias: {r.get('D1_Bias', 'N/A')}")
        lines.append(f"- Alignment: {r.get('Alignment', 'N/A')}")
        lines.append(f"- Technical score: {r.get('Technical_Score_0_4', 'N/A')}/4.0")
        lines.append(f"- Base ranking score: {r.get('Base_Ranking_Score', 'N/A')}")
        lines.append(f"- Overlap penalty: {r.get('Overlap_Penalty', 'N/A')}")
        lines.append(f"- Final ranking score: {r.get('Ranking_Score', r.get('Technical_Score_0_4', 'N/A'))}")
        lines.append(f"- Entry label: {r.get('Entry_Label', 'N/A')}")
        lines.append(f"- Price side vs D1 dealing range: {r.get('Price_Side_vs_D1_Range', 'N/A')}")
        lines.append(f"- Liquidity: {r.get('Liquidity_Condition', 'N/A')} | Sweep: {r.get('Sweep_Quality', 'N/A')}")
        lines.append(f"- Displacement: {r.get('Displacement_Quality', 'N/A')}")
        lines.append(f"- MSS/BOS: {r.get('MSS_BOS', 'N/A')}")
        lines.append(f"- Array quality: {r.get('Array_Quality', 'N/A')}")
        lines.append(f"- Session quality: {r.get('Session_Quality', 'N/A')}")
        lines.append(f"- RS/RW alignment: {r.get('RS_RW_Alignment', 'N/A')}")
        lines.append(f"- SMT hint: {r.get('SMT_Hint', 'N/A')}")
        lines.append(f"- Entry plan: {r.get('Execution_Line', 'N/A')}")

        num_zones = int(r.get("Num_entry_zones", 0) or 0)
        if num_zones > 0:
            for i in range(1, num_zones + 1):
                lo = r.get(f"Entry{i}_lo")
                hi = r.get(f"Entry{i}_hi")
                arrays = r.get(f"Entry{i}_arrays")
                score = r.get(f"Entry{i}_score")
                touches = r.get(f"Entry{i}_touches")
                deep = r.get(f"Entry{i}_deep_mitigated")
                lines.append(
                    f"  - Entry {i}: lo={lo} hi={hi} arrays={arrays} score={score} touches={touches} deep_mitigated={deep}"
                )
        lines.append("")

    return "\n".join(lines)

# =========================================================
# RUN
# =========================================================

def build_hist_url(pair: str, interval: str, outputsize: int, end_dt: datetime | None = None) -> str:
    url = (
        "https://api.twelvedata.com/time_series"
        f"?symbol={pair}"
        f"&interval={interval}"
        f"&outputsize={outputsize}"
        f"&timezone={TIMEZONE}"
        "&format=CSV"
    )
    if end_dt is not None:
        end_str = end_dt.strftime("%Y-%m-%d %H:%M:%S")
        url += f"&end_date={end_str}"
    return url

def _ensure_dt_index(df: pd.DataFrame) -> pd.DataFrame:
    x = ensure_datetime_column(df)
    x["datetime"] = pd.to_datetime(x["datetime"], errors="coerce")
    x = x.dropna(subset=["datetime"]).sort_values("datetime").set_index("datetime")
    return x

def slice_until(df: pd.DataFrame, cutoff_dt: datetime) -> pd.DataFrame:
    x = _ensure_dt_index(df)
    out = x.loc[x.index <= pd.Timestamp(cutoff_dt)].copy()
    return out.reset_index().rename(columns={out.index.name or "index": "datetime"})

def forward_slice(df: pd.DataFrame, start_dt: datetime, hours: int) -> tuple[pd.DataFrame, dict]:
    x = _ensure_dt_index(df)
    start_ts = pd.Timestamp(start_dt)
    post = x.loc[x.index > start_ts].copy()
    if post.empty:
        empty = post.reset_index().rename(columns={post.index.name or "index": "datetime"})
        return empty, {
            "Window_Bars": 0,
            "Window_Calendar_Hours": 0.0,
            "Window_Weekend_Gap_Hours": 0.0,
            "Window_Mode": VERIFIER_HORIZON_MODE,
            "Window_End_Time": None,
        }

    if VERIFIER_HORIZON_MODE == "trading_hours":
        out = post.iloc[: max(int(hours), 0)].copy()
    else:
        end_dt = start_ts + timedelta(hours=hours)
        out = post.loc[post.index <= end_dt].copy()

    if out.empty:
        calendar_hours = 0.0
        weekend_gap_hours = 0.0
        window_end_time = None
    else:
        window_end_ts = pd.Timestamp(out.index[-1])
        calendar_hours = max(0.0, (window_end_ts - start_ts).total_seconds() / 3600.0)
        weekend_gap_hours = max(0.0, calendar_hours - float(len(out)))
        window_end_time = str(window_end_ts)

    meta = {
        "Window_Bars": int(len(out)),
        "Window_Calendar_Hours": round(float(calendar_hours), 4),
        "Window_Weekend_Gap_Hours": round(float(weekend_gap_hours), 4),
        "Window_Mode": VERIFIER_HORIZON_MODE,
        "Window_End_Time": window_end_time,
    }
    return out.reset_index().rename(columns={out.index.name or "index": "datetime"}), meta

def resolve_snapshot_dates(cache: dict) -> list:
    candidate = None
    for sym, dfs in cache.items():
        if dfs is None:
            continue
        h1 = _ensure_dt_index(dfs[0])
        dates = sorted({ts.date() for ts in h1.index})
        if candidate is None or len(dates) < len(candidate):
            candidate = dates
    if not candidate:
        raise RuntimeError("No H1 dates available to build snapshot schedule.")
    if BACKTEST_END_DATE:
        end_date = pd.Timestamp(BACKTEST_END_DATE).date()
    else:
        end_date = candidate[-1]
    usable = [d for d in candidate if d < end_date]
    if len(usable) < BACKTEST_SNAPSHOT_DAYS:
        raise RuntimeError(f"Not enough historical dates to build {BACKTEST_SNAPSHOT_DAYS} snapshots before {end_date}.")
    return usable[-BACKTEST_SNAPSHOT_DAYS:]

def evaluate_execution_plan(sym: str, preferred_side: str, entry, sl, tp1, tp2, future_h1: pd.DataFrame) -> dict:
    result = {
        "Triggered": False,
        "Trigger_Time": None,
        "TP1_Hit": False,
        "TP2_Hit": False,
        "SL_Hit": False,
        "First_Event": "none",
        "Outcome_Label": "not_triggered",
        "MFE": None,
        "MAE": None,
        "Forward_Bars": int(len(future_h1)),
    }
    if future_h1 is None or future_h1.empty:
        result["Outcome_Label"] = "no_forward_data"
        return result
    try:
        entry = float(entry); sl = float(sl); tp1 = float(tp1); tp2 = float(tp2)
    except Exception:
        result["Outcome_Label"] = "invalid_execution_values"
        return result
    values = [entry, sl, tp1, tp2]
    if not all(np.isfinite(v) for v in values):
        result["Outcome_Label"] = "invalid_execution_values"
        return result

    side_norm = str(preferred_side).strip().lower() if preferred_side is not None else ""
    if side_norm in {"long", "buy", "buy-limit", "buy_limit"}:
        preferred_side = "buy-limit"
    elif side_norm in {"short", "sell", "sell-limit", "sell_limit"}:
        preferred_side = "sell-limit"
    else:
        if sl < entry and tp1 > entry and tp2 > entry:
            preferred_side = "buy-limit"
        elif sl > entry and tp1 < entry and tp2 < entry:
            preferred_side = "sell-limit"
        else:
            result["Outcome_Label"] = "no_trade_plan"
            return result

    if preferred_side == "buy-limit":
        if not (sl < entry and max(tp1, tp2) > entry):
            result["Outcome_Label"] = "invalid_execution_values"
            return result
        if tp2 < tp1:
            tp1, tp2 = tp2, tp1
    else:
        if not (sl > entry and min(tp1, tp2) < entry):
            result["Outcome_Label"] = "invalid_execution_values"
            return result
        if tp2 > tp1:
            tp1, tp2 = tp2, tp1

    fwd = _ensure_dt_index(future_h1)
    bars = []
    triggered_idx = None

    for ts, row in fwd.iterrows():
        hi = float(row["high"]); lo = float(row["low"])
        if preferred_side == "buy-limit":
            if lo <= entry:
                triggered_idx = ts
                result["Triggered"] = True
                result["Trigger_Time"] = str(ts)
                break
        else:
            if hi >= entry:
                triggered_idx = ts
                result["Triggered"] = True
                result["Trigger_Time"] = str(ts)
                break

    if triggered_idx is None:
        return result

    post = fwd.loc[fwd.index >= triggered_idx]
    mfe = 0.0
    mae = 0.0

    for ts, row in post.iterrows():
        hi = float(row["high"]); lo = float(row["low"])
        if preferred_side == "buy-limit":
            favorable = hi - entry
            adverse = entry - lo
            tp2_hit = hi >= tp2
            tp1_hit = hi >= tp1
            sl_hit = lo <= sl
        else:
            favorable = entry - lo
            adverse = hi - entry
            tp2_hit = lo <= tp2
            tp1_hit = lo <= tp1
            sl_hit = hi >= sl

        mfe = max(mfe, favorable)
        mae = max(mae, adverse)

        events = []
        if tp2_hit:
            events.append("tp2")
        elif tp1_hit:
            events.append("tp1")
        if sl_hit:
            events.append("sl")

        if len(events) >= 2:
            result["TP1_Hit"] = result["TP1_Hit"] or tp1_hit or tp2_hit
            result["TP2_Hit"] = result["TP2_Hit"] or tp2_hit
            result["SL_Hit"] = result["SL_Hit"] or sl_hit
            result["First_Event"] = "ambiguous_same_bar"
            result["Outcome_Label"] = "ambiguous_same_bar"
            result["MFE"] = round_price(sym, mfe)
            result["MAE"] = round_price(sym, mae)
            return result

        if tp2_hit:
            result["TP1_Hit"] = True
            result["TP2_Hit"] = True
            result["First_Event"] = "tp2"
            result["Outcome_Label"] = "tp2_hit"
            result["MFE"] = round_price(sym, mfe)
            result["MAE"] = round_price(sym, mae)
            return result
        if tp1_hit and not result["TP1_Hit"]:
            result["TP1_Hit"] = True
            result["First_Event"] = "tp1"

        if sl_hit:
            result["SL_Hit"] = True
            if result["TP1_Hit"]:
                result["Outcome_Label"] = "tp1_then_stop"
                result["First_Event"] = result["First_Event"] if result["First_Event"] != "none" else "tp1"
            else:
                result["First_Event"] = "sl"
                result["Outcome_Label"] = "stopped"
            result["MFE"] = round_price(sym, mfe)
            result["MAE"] = round_price(sym, mae)
            return result

    result["MFE"] = round_price(sym, mfe)
    result["MAE"] = round_price(sym, mae)
    if result["TP1_Hit"]:
        result["Outcome_Label"] = "tp1_only_open"
    else:
        result["Outcome_Label"] = "triggered_no_resolution"
    return result

def build_calibration_master_table(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        empty_columns = list(dict.fromkeys(CALIBRATION_MASTER_COLUMNS + ["Outcome_Bucket", "Triggered_Flag", "Resolved_Flag"]))
        return pd.DataFrame(columns=empty_columns)

    master = df.copy()
    if "Cluster_Tags" in master.columns:
        master["Cluster_Tags"] = master["Cluster_Tags"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)

    outcome_map = {
        "tp2_hit": "full_win",
        "tp1_then_stop": "partial_win",
        "tp1_only_open": "partial_open",
        "triggered_no_resolution": "open",
        "stopped": "loss",
        "not_triggered": "not_triggered",
        "ambiguous_same_bar": "ambiguous",
        "no_forward_data": "no_forward_data",
        "no_trade_plan": "no_trade_plan",
        "invalid_execution_values": "invalid_execution_values",
    }
    if "Verifier_Outcome_Label" in master.columns:
        master["Outcome_Bucket"] = master["Verifier_Outcome_Label"].map(outcome_map).fillna(master["Verifier_Outcome_Label"])
    else:
        master["Outcome_Bucket"] = None

    if "Verifier_Triggered" in master.columns:
        master["Triggered_Flag"] = master["Verifier_Triggered"].fillna(False).astype(bool)
    else:
        master["Triggered_Flag"] = None

    if "Verifier_Outcome_Label" in master.columns:
        unresolved = {"triggered_no_resolution", "tp1_only_open", "not_triggered", "no_forward_data", "no_trade_plan", "invalid_execution_values"}
        master["Resolved_Flag"] = ~master["Verifier_Outcome_Label"].isin(unresolved)
    else:
        master["Resolved_Flag"] = None

    cols = list(dict.fromkeys([c for c in CALIBRATION_MASTER_COLUMNS if c in master.columns] + ["Outcome_Bucket", "Triggered_Flag", "Resolved_Flag"]))
    master_out = master[cols].copy()
    duplicate_columns = master_out.columns[master_out.columns.duplicated()].tolist()
    if duplicate_columns:
        raise RuntimeError(f"Duplicate master_df columns detected: {duplicate_columns}")
    return master_out



def build_selector_audit_table(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=SELECTOR_AUDIT_COLUMNS)

    audit = df.copy()
    if "Cluster_Tags" in audit.columns:
        audit["Cluster_Tags"] = audit["Cluster_Tags"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)

    cols = [c for c in SELECTOR_AUDIT_COLUMNS if c in audit.columns]
    return audit[cols].copy()



def _prediction_grade_band(score_100: float) -> str:
    # v5.5 recalibration: make the board communicative instead of collapsing almost everything into band E.
    if score_100 >= 70:
        return "A"
    if score_100 >= 55:
        return "B"
    if score_100 >= 40:
        return "C"
    if score_100 >= 25:
        return "D"
    return "E"

def _prediction_factor_map(row: dict) -> dict:
    return {
        "survivability": _safe_num(row.get("Survivability_Score_10"), 0.0),
        "asymmetry": _safe_num(row.get("Asymmetry_Score_10"), 0.0),
        "utility": _safe_num(row.get("Calibration_Utility_Score_10"), 0.0),
        "trigger": _safe_num(row.get("Trigger_Quality_Score_10"), 0.0),
        "execution": _safe_num(row.get("Execution_Realism_Score_10"), 0.0),
        "context": _safe_num(row.get("Context_Quality_Score_10"), 0.0),
        "opportunity": _safe_num(row.get("Opportunity_Score_10"), 0.0),
        "balance": _safe_num(row.get("Balance_Score_10"), 0.0),
        "confidence": _safe_num(row.get("Calibrated_Confidence_Score_10"), 0.0),
        "comparative_edge": _safe_num(row.get("Comparative_Edge_Score_10"), 0.0),
        "dominance": _safe_num(row.get("Dominance_Score_10"), 0.0),
        "conflict": _safe_num(row.get("Conflict_Penalty_Score_10"), 0.0),
        "false_positive": _safe_num(row.get("False_Positive_Risk_Score_10"), 0.0),
        "kill_switch": _safe_num(row.get("Kill_Switch_Score_10"), 0.0),
        "archetype_tax": _safe_num(row.get("Archetype_Tax_Score_10"), 0.0),
        "entry_distance_atr": _safe_num(row.get("Entry_Distance_ATR"), np.nan),
    }

def _prediction_input_fingerprint(row: dict) -> str:
    payload = {k: row.get(k) for k in PREDICTION_INPUT_FIELDS}
    raw = json.dumps(json_ready(payload), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

def compute_prediction_quality_grade(row: dict) -> dict:
    factors = _prediction_factor_map(row)

    positive_score_10 = (
        0.15 * factors["survivability"]
        + 0.14 * factors["asymmetry"]
        + 0.13 * factors["utility"]
        + 0.12 * factors["trigger"]
        + 0.11 * factors["execution"]
        + 0.09 * factors["context"]
        + 0.08 * factors["opportunity"]
        + 0.06 * factors["balance"]
        + 0.05 * factors["confidence"]
        + 0.04 * factors["comparative_edge"]
        + 0.03 * factors["dominance"]
    )

    penalty_score_10 = (
        0.14 * factors["conflict"]
        + 0.14 * factors["false_positive"]
        + 0.12 * factors["kill_switch"]
        + 0.06 * factors["archetype_tax"]
    )

    fail_set = {x.strip() for x in str(row.get("Gate_Fail_Reasons", "") or "").split(",") if x.strip()}
    gate_penalty = 0.0
    if fail_set:
        if fail_set & CALIBRATION_HARD_REJECT_REASONS:
            gate_penalty += 1.10
        elif fail_set.issubset(CALIBRATION_SOFT_FAIL_REASONS):
            gate_penalty += 0.45
        else:
            gate_penalty += 0.65

    if bool(row.get("Veto_Flag")):
        gate_penalty += 0.55
    if str(row.get("Admission_Class", "") or "") == "blocked":
        gate_penalty += 0.85
    elif str(row.get("Admission_Class", "") or "") == "quarantined":
        gate_penalty += 0.45

    structure_bonus = 0.0
    if bool(row.get("Primary_Shortlist_Flag")):
        structure_bonus += 0.30
    elif str(row.get("Shortlist_Eligibility", "") or "") == "primary":
        structure_bonus += 0.14

    entry_dist = factors["entry_distance_atr"]
    if np.isfinite(entry_dist):
        if entry_dist <= 0.75:
            structure_bonus += 0.18
        elif entry_dist <= 1.50:
            structure_bonus += 0.08
        elif entry_dist >= 2.50:
            gate_penalty += 0.30

    score_10 = positive_score_10 - penalty_score_10 - gate_penalty + structure_bonus
    score_10 = max(0.0, min(10.0, score_10))
    score_100 = round(score_10 * 10.0, 1)
    band = _prediction_grade_band(score_100)

    positive_rank = {
        "survivability": factors["survivability"],
        "asymmetry": factors["asymmetry"],
        "utility": factors["utility"],
        "trigger": factors["trigger"],
        "execution": factors["execution"],
        "context": factors["context"],
        "opportunity": factors["opportunity"],
        "dominance": factors["dominance"],
    }
    negative_rank = {
        "conflict": factors["conflict"],
        "false_positive_risk": factors["false_positive"],
        "kill_switch": factors["kill_switch"],
        "archetype_tax": factors["archetype_tax"],
        "gate_pressure": gate_penalty * 10.0 / 1.10 if gate_penalty > 0 else 0.0,
    }
    top_pos = sorted(positive_rank.items(), key=lambda kv: kv[1], reverse=True)[:3]
    top_neg = [kv for kv in sorted(negative_rank.items(), key=lambda kv: kv[1], reverse=True)[:2] if kv[1] > 0]
    top_pos_text = ", ".join(f"{k} {round(v,1)}" for k, v in top_pos if v > 0) or "none"
    top_neg_text = ", ".join(f"{k} {round(v,1)}" for k, v in top_neg) or "none"

    breakdown = (
        f"{row.get('Preferred_Side', 'none')} {row.get('Setup_Archetype', 'unknown')}; "
        f"strengths: {top_pos_text}; risks: {top_neg_text}; "
        f"admission: {row.get('Admission_Class', 'n/a')} / {row.get('Selection_Lane', 'n/a')}"
    )

    return {
        "Setup_Quality_Grade_10": round(score_10, 2),
        "Setup_Quality_Grade_100": score_100,
        "Setup_Quality_Band": band,
        "Prediction_Top_Strengths": top_pos_text,
        "Prediction_Main_Risks": top_neg_text,
        "Prediction_Breakdown": breakdown,
        "Prediction_Score_Version": PREDICTION_SCORE_VERSION,
        "Prediction_Uses_Only_Contemporaneous_Inputs": True,
        "Prediction_Forbidden_Field_Leak": False,
        "Prediction_Input_Fingerprint": _prediction_input_fingerprint(row),
    }


def _validate_prediction_snapshot_clock(snapshot_meta: dict) -> None:
    ts_raw = snapshot_meta.get("prediction_reference_timestamp")
    if ts_raw in (None, ""):
        raise ValueError("prediction_reference_timestamp missing")
    ts = pd.Timestamp(ts_raw)
    if ts.year < 2025 or ts == pd.Timestamp("1970-01-01"):
        raise ValueError(f"prediction_reference_timestamp invalid: {ts_raw}")
    snap_raw = snapshot_meta.get("snapshot_date")
    if snap_raw in (None, ""):
        raise ValueError("prediction snapshot_date missing")
    snap = pd.Timestamp(snap_raw)
    if snap.year < 2025 or snap == pd.Timestamp("1970-01-01"):
        raise ValueError(f"prediction snapshot_date invalid: {snap_raw}")


def build_today_prediction_rows(cache: dict) -> tuple[list[dict], list[dict], dict]:
    build_reference_ts = pd.Timestamp(datetime.now()).floor("s")
    live_cache = {}
    for sym in SYMBOLS:
        if cache.get(sym) is None:
            live_cache[sym] = None
            continue
        h1, d1, w1 = cache[sym]
        if len(h1) < 80 or len(d1) < 40 or len(w1) < 20:
            live_cache[sym] = None
        else:
            live_cache[sym] = (h1, d1, w1)

    d1_strength = compute_currency_strength(live_cache, tf="D1")
    rows = []
    last_ts_values = []

    for sym in SYMBOLS:
        if live_cache.get(sym) is None:
            row = {
                "Snapshot_Date": str(build_reference_ts.date()),
                "Prediction_Reference_Timestamp": str(build_reference_ts),
                "Instrument": sym,
                "status": "ERROR",
                "Universe_Layer": instrument_layer(sym),
                "Prediction_Integrity_Status": "insufficient_data",
                "Setup_Quality_Grade_100": 0.0,
                "Setup_Quality_Band": "E",
                "Prediction_Breakdown": "insufficient_data",
            }
            rows.append(row)
            continue

        h1, d1, w1 = live_cache[sym]
        market_ts = pd.Timestamp(last_timestamp_from_df(last_completed(h1)))
        last_ts_values.append(market_ts)
        ict_pack = analyze_symbol_ict(sym, h1, d1, w1, d1_strength, live_cache)
        d_info = ict_pack["d_info"]
        w_info = ict_pack["w_info"]
        entry_zones = ict_pack["entry_zones"]
        execution = ict_pack["execution"]

        current_price = round_price(sym, float(last_completed(h1).iloc[-1]["close"]))
        try:
            atr_series = atr(last_completed(h1), ATR_LEN)
            atr_h1 = round_price(sym, float(atr_series.dropna().iloc[-1])) if len(atr_series.dropna()) > 0 else None
        except Exception:
            atr_h1 = None

        row = {
            "Snapshot_Date": str(build_reference_ts.date()),
            "Prediction_Reference_Timestamp": str(build_reference_ts),
            "Market_Reference_Timestamp": str(market_ts),
            "Instrument": sym,
            "status": "OK",
            "Universe_Layer": ict_pack["layer"],
            "Cluster_Tags": ", ".join(ict_pack["cluster_tags"]),
            "W1_Bias": w_info["bias"],
            "D1_Bias": d_info["bias"],
            "Price_Side_vs_D1_Range": ict_pack["price_side"],
            "Alignment": ict_pack["alignment"],
            "Liquidity_Condition": ict_pack["liquidity_condition"],
            "Sweep_Quality": ict_pack["sweep_quality"],
            "Liquidity_Side": ict_pack["liquidity_side"],
            "Liquidity_Tier": ict_pack["liquidity_tier"],
            "Liquidity_Reference_Type": ict_pack["liquidity_reference_type"],
            "Rejection_Quality": ict_pack["rejection_quality"],
            "Follow_Through": ict_pack["follow_through"],
            "Both_Sides_Taken_Recently": ict_pack["both_sides_taken_recently"],
            "Displacement_Quality": ict_pack["displacement_quality"],
            "MSS_BOS": ict_pack["mss_bos"],
            "Array_Quality": ict_pack["array_quality"],
            "Session_Quality": ict_pack["session_quality"],
            "RS_RW_Alignment": ict_pack["rs_rw_alignment"],
            "SMT_Hint": ict_pack["smt_hint"],
            "Pivot_Regime": ict_pack["pivot_context"]["pivot_regime"],
            "Pivot_Zone_Fit": ict_pack["pivot_context"]["pivot_zone_fit"],
            "Pivot_Confluence": ict_pack["pivot_context"]["pivot_confluence"],
            "Pivot_Conflict": ict_pack["pivot_context"]["pivot_conflict"],
            "Pivot_Stretch": ict_pack["pivot_context"]["pivot_stretch"],
            "Technical_Score_0_4": ict_pack["technical_score"],
            "Legacy_Confidence_Score": ict_pack["confidence"].get("legacy_score", ict_pack["confidence"]["score"]),
            "Legacy_Confidence_Band": ict_pack["confidence"].get("legacy_band", ict_pack["confidence"]["band"]),
            "Confidence_Score": ict_pack["confidence"]["score"],
            "Confidence_Band": ict_pack["confidence"]["band"],
            "Technical_Quality_Score_10": np.nan,
            "Execution_Realism_Score_10": np.nan,
            "Calibrated_Confidence_Score_10": ict_pack["confidence"].get("score_10", np.nan),
            "Selection_Score": 0.0,
            "Final_Rank_Score": 0.0,
            "Data_Quality": ict_pack["data_quality"],
            "Entry_Label": ict_pack["entry_label"],
            "Preferred_Side": execution["preferred_side"],
            "Best_Entry": execution["entry"],
            "Structural_Entry": execution.get("structural_entry"),
            "Calibration_Entry": execution.get("calibration_entry", execution["entry"]),
            "Entry_Distance_ATR": execution.get("entry_distance_atr"),
            "SL": execution["sl"],
            "TP1": execution["tp1"],
            "TP2": execution["tp2"],
            "Current_Price": current_price,
            "ATR_H1": atr_h1,
            "RR_TP1": execution.get("rr_tp1"),
            "RR_TP2": execution.get("rr_tp2"),
            "Execution_Line": execution["entry_text"],
            "Execution_Source": execution.get("execution_source", "zone"),
            "Setup_Archetype": None,
            "Decision_Book": None,
            "Live_Gate_Passed": False,
            "Calibration_Gate_Passed": False,
            "Gate_Passed": False,
            "Gate_Fail_Reasons": "",
            "Decision_Setup_Quality": 0.0,
            "Decision_Execution_Quality": 0.0,
            "Decision_Portfolio_Fit": 0.0,
            "Decision_Rank_Score": 0.0,
            "Base_Ranking_Score": 0.0,
            "Overlap_Penalty": 0.0,
            "Ranking_Score": 0.0,
        }
        row = finalize_decision_fields(row)
        rows.append(row)

    _, selector_state_rows = build_shortlist(rows, shortlist_n=min(TOP_SHORTLIST_N, len(SYMBOLS)))
    selector_state_by_instrument = {r["Instrument"]: r for r in selector_state_rows}
    selector_fields = [
        "Overlap_Penalty", "Ranking_Score", "Decision_Portfolio_Fit", "Decision_Book",
        "Comparative_Edge_Score_10", "Comparator_Floor_Score_10", "Dominance_Score_10",
        "Admission_Class", "Override_Reason", "Selection_Score", "Final_Rank_Score",
        "Selection_Lane", "Primary_Shortlist_Flag", "Primary_Override_Flag", "Shadow_Watchlist_Flag", "Shadow_Watchlist_Reason", "Shadow_Watchlist_Order", "Shortlist_Eligibility",
        "Admission_Binding_Status", "Veto_Flag", "Veto_Reasons", "Leakage_Penalty_Score",
        "Selector_Profile", "Shortlist_Slot_Name", "Shortlist_Slot_Type", "Shortlist_Slot_Order",
        "In_Top_Shortlist"
    ]
    for r in rows:
        sr = selector_state_by_instrument.get(r.get("Instrument"))
        if sr is None:
            continue
        for fld in selector_fields:
            if fld in sr:
                r[fld] = sr.get(fld)
        r["In_Top_Shortlist"] = bool(sr.get("In_Top_Shortlist"))
        pred = compute_prediction_quality_grade(r)
        r.update(pred)
        r["Prediction_Integrity_Status"] = "clean_contemporaneous_only"

    rows = sorted(
        rows,
        key=lambda r: (
            _safe_num(r.get("Setup_Quality_Grade_100"), 0.0),
            _safe_num(r.get("Final_Rank_Score"), -999.0),
            _safe_num(r.get("Selection_Score"), -999.0),
        ),
        reverse=True,
    )
    for idx, r in enumerate(rows, start=1):
        r["Prediction_Rank"] = idx

    latest_ts = build_reference_ts
    nonnull_forbidden = 0
    for r in rows:
        for fld in PREDICTION_FORBIDDEN_FIELDS:
            if fld in r and r.get(fld) not in (None, "", False):
                nonnull_forbidden += 1

    integrity_rows = [
        {"Metric": "prediction_rows", "Value": len(rows)},
        {"Metric": "prediction_uses_verifier_fields", "Value": False},
        {"Metric": "prediction_uses_historical_outcome_fields", "Value": False},
        {"Metric": "prediction_forbidden_fields_nonnull_count", "Value": nonnull_forbidden},
        {"Metric": "primary_shortlist_rows_in_prediction_snapshot", "Value": int(sum(bool(r.get("Primary_Shortlist_Flag")) for r in rows))},
        {"Metric": "shadow_watchlist_rows_in_prediction_snapshot", "Value": int(sum(bool(r.get("Shadow_Watchlist_Flag")) for r in rows))},
    ]
    snapshot_meta = {
        "prediction_enabled": True,
        "prediction_score_version": PREDICTION_SCORE_VERSION,
        "prediction_reference_timestamp": str(latest_ts) if latest_ts is not None else None,
        "snapshot_date": str(build_reference_ts.date()),
        "prediction_input_fields": PREDICTION_INPUT_FIELDS,
        "prediction_forbidden_fields": PREDICTION_FORBIDDEN_FIELDS,
        "prediction_top_n": min(PREDICTION_TOP_N, len(rows)),
    }
    return rows, integrity_rows, snapshot_meta



def _safe_unlink(path: Path) -> None:
    try:
        if path.exists():
            path.unlink()
    except Exception:
        pass


def _json_dump(path: Path, payload) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(json_ready(payload), f, indent=2, ensure_ascii=False)


def _write_text(path: Path, text: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _prediction_summary_text(prediction_rows: list[dict], integrity_rows: list[dict], snapshot_meta: dict) -> str:
    lines = []
    lines.append("# today_prediction_summary")
    lines.append("")
    lines.append(f"prediction_score_version: {snapshot_meta.get('prediction_score_version')}")
    lines.append(f"prediction_reference_timestamp: {snapshot_meta.get('prediction_reference_timestamp')}")
    lines.append(f"snapshot_date: {snapshot_meta.get('snapshot_date')}")
    lines.append(f"prediction_top_n: {snapshot_meta.get('prediction_top_n')}")
    lines.append("")
    lines.append("## integrity")
    for row in integrity_rows:
        lines.append(f"- {row.get('Metric')}: {row.get('Value')}")
    lines.append("")
    lines.append("## ranking")
    for i, row in enumerate(prediction_rows, start=1):
        inst = row.get("Instrument")
        side = row.get("Preferred_Side")
        grade10 = row.get("Setup_Quality_Grade_10")
        grade100 = row.get("Setup_Quality_Grade_100")
        band = row.get("Setup_Quality_Band")
        entry = row.get("Best_Entry")
        sl = row.get("SL")
        tp1 = row.get("TP1")
        tp2 = row.get("TP2")
        lines.append(
            f"{i}. {inst} | side={side} | grade10={grade10} | grade100={grade100} | "
            f"band={band} | entry={entry} | sl={sl} | tp1={tp1} | tp2={tp2}"
        )
    lines.append("")
    return "\n".join(lines)


def export_latest_prediction_files(latest_dir: Path, prediction_rows: list[dict], integrity_rows: list[dict], snapshot_meta: dict) -> dict:
    latest_dir.mkdir(parents=True, exist_ok=True)

    ranking_csv = latest_dir / "today_prediction_ranking.csv"
    ranking_json = latest_dir / "today_prediction_ranking.json"
    summary_txt = latest_dir / "today_prediction_summary.txt"
    integrity_json = latest_dir / "prediction_integrity_report.json"
    today_zip = latest_dir / "Today_Predictions.zip"

    pred_df = pd.DataFrame(prediction_rows)

    pred_df.to_csv(ranking_csv, index=False)
    _json_dump(
        ranking_json,
        {
            "snapshot_meta": snapshot_meta,
            "predictions": prediction_rows,
        },
    )
    _json_dump(
        integrity_json,
        {
            "snapshot_meta": snapshot_meta,
            "integrity_rows": integrity_rows,
        },
    )
    _write_text(summary_txt, _prediction_summary_text(prediction_rows, integrity_rows, snapshot_meta))

    _safe_unlink(today_zip)
    with zipfile.ZipFile(today_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for fp in [ranking_json, ranking_csv, summary_txt, integrity_json]:
            if fp.exists():
                zf.write(fp, arcname=fp.name)

    return {
        "latest_prediction_files": [
            ranking_json.name,
            ranking_csv.name,
            summary_txt.name,
            integrity_json.name,
        ],
        "latest_today_predictions_zip": today_zip.name,
    }


def export_prediction_pack(outdir: Path, prediction_rows: list[dict], integrity_rows: list[dict], snapshot_meta: dict) -> dict:
    pred_df = pd.DataFrame(prediction_rows)
    integrity_df = pd.DataFrame(integrity_rows)

    full_csv = outdir / f"today_prediction_ranking_{BACKTEST_SYMBOLS_LABEL}.csv"
    full_json = outdir / f"today_prediction_ranking_{BACKTEST_SYMBOLS_LABEL}.json"
    full_md = outdir / f"today_prediction_ranking_{BACKTEST_SYMBOLS_LABEL}.md"
    top_csv = outdir / f"today_prediction_top_{BACKTEST_SYMBOLS_LABEL}.csv"
    top_json = outdir / f"today_prediction_top_{BACKTEST_SYMBOLS_LABEL}.json"
    top_md = outdir / f"today_prediction_top_{BACKTEST_SYMBOLS_LABEL}.md"
    integrity_csv = outdir / f"prediction_integrity_report_{BACKTEST_SYMBOLS_LABEL}.csv"
    integrity_json = outdir / f"prediction_integrity_report_{BACKTEST_SYMBOLS_LABEL}.json"
    integrity_md = outdir / f"prediction_integrity_report_{BACKTEST_SYMBOLS_LABEL}.md"

    pred_df.to_csv(full_csv, index=False)
    _json_dump(full_json, prediction_rows)

    top_n = int(snapshot_meta.get("prediction_top_n", min(PREDICTION_TOP_N, len(pred_df))))
    top_rows = prediction_rows[: min(top_n, len(prediction_rows))]
    top_df = pd.DataFrame(top_rows)
    top_df.to_csv(top_csv, index=False)
    _json_dump(top_json, top_rows)

    md_cols = [c for c in ["Prediction_Rank", "Instrument", "Preferred_Side", "Setup_Quality_Grade_100", "Setup_Quality_Band", "Setup_Archetype", "Confidence_Band", "Prediction_Breakdown"] if c in pred_df.columns]
    with open(full_md, "w", encoding="utf-8") as f:
        f.write("# Today Prediction Ranking\n\n")
        if snapshot_meta.get("prediction_reference_timestamp"):
            f.write(f"Reference timestamp: {snapshot_meta['prediction_reference_timestamp']}\n\n")
        f.write(pred_df[md_cols].to_markdown(index=False) if (not pred_df.empty and md_cols) else "No prediction rows")
    with open(top_md, "w", encoding="utf-8") as f:
        f.write("# Today Prediction Top List\n\n")
        f.write(top_df[md_cols].to_markdown(index=False) if (not top_df.empty and md_cols) else "No top prediction rows")

    integrity_df.to_csv(integrity_csv, index=False)
    _json_dump(
        integrity_json,
        {
            "snapshot_meta": snapshot_meta,
            "integrity_rows": integrity_rows,
        },
    )
    with open(integrity_md, "w", encoding="utf-8") as f:
        f.write(integrity_df.to_markdown(index=False) if not integrity_df.empty else "No integrity rows")

    latest_export_info = export_latest_prediction_files(
        latest_dir=LATEST_DIR,
        prediction_rows=prediction_rows,
        integrity_rows=integrity_rows,
        snapshot_meta=snapshot_meta,
    )

    return {
        "prediction_files": [full_csv.name, full_json.name, full_md.name, top_csv.name, top_json.name, top_md.name, integrity_csv.name, integrity_json.name, integrity_md.name],
        "prediction_reference_timestamp": snapshot_meta.get("prediction_reference_timestamp"),
        "prediction_top_n": top_n,
        "today_predictions_zip": latest_export_info.get("latest_today_predictions_zip"),
        "today_predictions_manifest": {
            "latest_dir": str(LATEST_DIR),
            "latest_prediction_files": latest_export_info.get("latest_prediction_files", []),
            "latest_today_predictions_zip": latest_export_info.get("latest_today_predictions_zip"),
        },
    }


def export_today_predictions_bundle(outdir: Path, prediction_export_info: dict, snapshot_meta: dict) -> dict:
    prediction_files = list(prediction_export_info.get("prediction_files", []) or [])
    latest_manifest = dict(prediction_export_info.get("today_predictions_manifest", {}) or {})
    bundle_manifest = {
        "bundle_name": TODAY_PREDICTIONS_ZIP_NAME,
        "generated_at": datetime.now().isoformat(),
        "script_version": SCRIPT_VERSION,
        "intended_prompt": TODAY_PREDICTIONS_PROMPT_NAME,
        "prediction_score_version": snapshot_meta.get("prediction_score_version"),
        "prediction_reference_timestamp": snapshot_meta.get("prediction_reference_timestamp"),
        "snapshot_date": snapshot_meta.get("snapshot_date"),
        "preferred_input_order": [
            "daily_outputs/latest/today_prediction_ranking.json",
            "daily_outputs/latest/prediction_integrity_report.json",
            "daily_outputs/latest/today_prediction_ranking.csv",
            "daily_outputs/latest/today_prediction_summary.txt",
            f"today_prediction_ranking_{BACKTEST_SYMBOLS_LABEL}.json",
            f"today_prediction_top_{BACKTEST_SYMBOLS_LABEL}.json",
            f"prediction_integrity_report_{BACKTEST_SYMBOLS_LABEL}.json",
        ],
        "included_files": prediction_files,
        "latest_outputs": latest_manifest,
        "notes": [
            "JSON files are the primary truth if present.",
            "Stable latest outputs are intended for GitHub + ChatGPT reading.",
            "Dated batch files are preserved for archival review.",
        ],
    }
    manifest_path = outdir / "today_predictions_manifest.json"
    _json_dump(manifest_path, bundle_manifest)
    return {
        "today_predictions_bundle_manifest": manifest_path.name,
        "today_predictions_manifest": {
            **latest_manifest,
            "bundle_manifest": manifest_path.name,
        },
    }


def export_day_pack(day_outdir: Path, snapshot_date: str, summary_rows: list, shortlist_rows: list, manifest_extra: dict):
    day_outdir.mkdir(parents=True, exist_ok=True)
    full_df = pd.DataFrame(summary_rows)
    shortlist_df = pd.DataFrame(shortlist_rows)

    full_csv_path = day_outdir / f"full_universe_summary_{BACKTEST_SYMBOLS_LABEL}.csv"
    full_json_path = day_outdir / f"full_universe_summary_{BACKTEST_SYMBOLS_LABEL}.json"
    full_md_path = day_outdir / f"full_universe_summary_{BACKTEST_SYMBOLS_LABEL}.md"
    shortlist_csv_path = day_outdir / f"top_candidates_summary_{BACKTEST_SYMBOLS_LABEL}.csv"
    shortlist_json_path = day_outdir / f"top_candidates_summary_{BACKTEST_SYMBOLS_LABEL}.json"
    shortlist_md_path = day_outdir / f"top_candidates_summary_{BACKTEST_SYMBOLS_LABEL}.md"
    verifier_csv_path = day_outdir / f"forward_verifier_summary_{BACKTEST_SYMBOLS_LABEL}.csv"
    verifier_json_path = day_outdir / f"forward_verifier_summary_{BACKTEST_SYMBOLS_LABEL}.json"
    verifier_md_path = day_outdir / f"forward_verifier_summary_{BACKTEST_SYMBOLS_LABEL}.md"

    full_df.to_csv(full_csv_path, index=False)
    shortlist_df.to_csv(shortlist_csv_path, index=False)
    with open(full_json_path, "w", encoding="utf-8") as f:
        json.dump(json_ready(summary_rows), f, indent=2, ensure_ascii=False)
    with open(shortlist_json_path, "w", encoding="utf-8") as f:
        json.dump(json_ready(shortlist_rows), f, indent=2, ensure_ascii=False)

    with open(full_md_path, "w", encoding="utf-8") as f:
        f.write(build_analyst_summary(summary_rows, f"Full Universe Summary — {snapshot_date}"))
    with open(shortlist_md_path, "w", encoding="utf-8") as f:
        f.write(build_analyst_summary(shortlist_rows, f"Top Candidates Summary — {snapshot_date}"))
    with open(verifier_md_path, "w", encoding="utf-8") as f:
        f.write(build_analyst_summary(shortlist_rows, f"Forward Verifier Summary — {snapshot_date}"))

    verifier_cols = [c for c in shortlist_df.columns if c.startswith("Verifier")]
    verifier_base_cols = ["Snapshot_Date", "Instrument", "Preferred_Side", "Best_Entry", "SL", "TP1", "TP2"]
    verifier_schema = verifier_base_cols + [
        "Verifier_Triggered", "Verifier_TP1_Hit", "Verifier_TP2_Hit", "Verifier_SL_Hit",
        "Verifier_First_Event", "Verifier_Outcome_Label", "Verifier_MFE", "Verifier_MAE", "Verifier_R_Multiple", "Verifier_Weighted_Return_R",
        "Verifier48_Triggered", "Verifier48_TP1_Hit", "Verifier48_TP2_Hit", "Verifier48_SL_Hit",
        "Verifier48_First_Event", "Verifier48_Outcome_Label", "Verifier48_MFE", "Verifier48_MAE", "Verifier48_R_Multiple", "Verifier48_Weighted_Return_R",
        "Verifier72_Triggered", "Verifier72_TP1_Hit", "Verifier72_TP2_Hit", "Verifier72_SL_Hit",
        "Verifier72_First_Event", "Verifier72_Outcome_Label", "Verifier72_MFE", "Verifier72_MAE", "Verifier72_R_Multiple", "Verifier72_Weighted_Return_R"
    ]
    verifier_out_cols = [c for c in verifier_base_cols + verifier_cols if c in shortlist_df.columns]
    if verifier_out_cols:
        verifier_out = shortlist_df[verifier_out_cols].copy()
    else:
        verifier_out = pd.DataFrame(columns=verifier_schema)
    verifier_out.to_csv(verifier_csv_path, index=False)
    with open(verifier_json_path, "w", encoding="utf-8") as f:
        json.dump(json_ready(verifier_out.to_dict(orient="records")), f, indent=2, ensure_ascii=False)

    selector_fields_present = sorted([c for c in SELECTOR_AUDIT_COLUMNS if c in full_df.columns])
    selector_profiles = sorted([str(x) for x in pd.Series(full_df.get("Selector_Profile", pd.Series(dtype=object))).dropna().astype(str).unique().tolist()]) if not full_df.empty else []
    manifest = {
        "script_version": SCRIPT_VERSION,
        "snapshot_date": snapshot_date,
        "run_type": "historical_calibration_snapshot",
        "symbol_count": len(summary_rows),
        "production_mode": PRODUCTION_MODE,
        "execution_payoff_preset": EXECUTION_PAYOFF_PRESET,
        "sl_distance_multiplier": SL_DISTANCE_MULTIPLIER,
        "tp1_distance_multiplier": TP1_DISTANCE_MULTIPLIER,
        "tp2_distance_multiplier": TP2_DISTANCE_MULTIPLIER,
        "tp1_partial_exit_fraction": TP1_PARTIAL_EXIT_FRACTION,
        "symbol_set_selection": BACKTEST_SYMBOLS_SWITCH,
        "symbol_set_label": BACKTEST_SYMBOLS_LABEL,
        "symbol_set_1": BACKTEST_SYMBOLS_SET1,
        "symbol_set_2": BACKTEST_SYMBOLS_SET2,
        "selector_profile": selector_profiles[0] if len(selector_profiles) == 1 else selector_profiles,
        **manifest_extra,
        "files": [],
    }
    changelog_path = day_outdir / "CHANGELOG.md"
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write("# Changelog\n\n")
        for item in CHANGE_LOG:
            f.write(f"- {item}\n")
        f.write("- Historical calibration backtest mode enabled for multi-day snapshot generation.\n")

    output_files = sorted([x for x in day_outdir.iterdir() if x.is_file()])
    manifest["files"] = [fp.name for fp in output_files]
    manifest_path = day_outdir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    zip_path = day_outdir / f"{day_outdir.name}.zip"
    if EXPORT_DAILY_ZIPS:
        output_files = sorted([x for x in day_outdir.iterdir() if x.is_file()])
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for fp in output_files:
                if fp.name == zip_path.name:
                    continue
                zf.write(fp, arcname=fp.name)
    return {
        "full_csv_path": full_csv_path,
        "shortlist_csv_path": shortlist_csv_path,
        "verifier_csv_path": verifier_csv_path,
        "zip_path": zip_path if EXPORT_DAILY_ZIPS else None,
    }

def main():
    global TOTAL_CALLS, CALLS_DONE, START_TS
    CALLS_DONE = 0
    START_TS = time.time()
    TOTAL_CALLS = len(SYMBOLS) * 3

    print("BASE_DIR:", BASE_DIR)
    print("OUTDIR:", OUTDIR)
    print(f"Historical calibration mode for {len(SYMBOLS)} symbols; total calls = {TOTAL_CALLS}. Rate limit={CALLS_PER_MIN}/min.")

    cache = {}
    fetch_end_dt = pd.Timestamp(BACKTEST_END_DATE).to_pydatetime() if BACKTEST_END_DATE else None

    for idx, sym in enumerate(SYMBOLS, start=1):
        try:
            print(f"\n=== {sym} ({idx}/{len(SYMBOLS)}) ===")
            print_progress(prefix=">>> ")
            pair = PAIR_MAP[sym]
            h1 = fetch_csv(build_hist_url(pair, "1h", BACKTEST_H1_OUTPUTSIZE, fetch_end_dt))
            d1 = fetch_csv(build_hist_url(pair, "1day", BACKTEST_D1_OUTPUTSIZE, fetch_end_dt))
            w1 = fetch_csv(build_hist_url(pair, "1week", BACKTEST_W1_OUTPUTSIZE, fetch_end_dt))
            cache[sym] = (_ensure_dt_index(h1), _ensure_dt_index(d1), _ensure_dt_index(w1))
        except Exception as e:
            print(f"[WARN] {sym} failed during fetch: {e}")
            cache[sym] = None

    snapshot_dates = resolve_snapshot_dates(cache)
    print("Snapshot dates:", ", ".join(str(d) for d in snapshot_dates))

    all_rows = []
    all_shortlist_rows = []
    batch_index_rows = []

    for snap_date in snapshot_dates:
        snapshot_date_str = str(snap_date)
        cutoff_dt = datetime.combine(snap_date, datetime.max.time()).replace(hour=23, minute=59, second=59, microsecond=0)
        print(f"\n##### SNAPSHOT {snapshot_date_str} #####")
        day_outdir = OUTDIR / f"{snapshot_date_str}_FX_PACK_{BACKTEST_SYMBOLS_LABEL}"

        day_cache = {}
        for sym in SYMBOLS:
            if cache.get(sym) is None:
                day_cache[sym] = None
                continue
            h1_full, d1_full, w1_full = cache[sym]
            h1 = slice_until(h1_full, cutoff_dt)
            d1 = slice_until(d1_full, cutoff_dt)
            w1 = slice_until(w1_full, cutoff_dt)
            if len(h1) < 80 or len(d1) < 40 or len(w1) < 20:
                day_cache[sym] = None
            else:
                day_cache[sym] = (h1, d1, w1)

        d1_strength = compute_currency_strength(day_cache, tf="D1")
        summary_rows = []
        json_records = []

        for sym in SYMBOLS:
            if day_cache.get(sym) is None:
                row = {
                    "Snapshot_Date": snapshot_date_str,
                    "Instrument": sym,
                    "status": "ERROR",
                    "Universe_Layer": instrument_layer(sym),
                    "W1_Bias": "ERROR",
                    "Error": "Insufficient historical slice",
                }
                summary_rows.append(row)
                json_records.append(row)
                continue

            h1, d1, w1 = day_cache[sym]
            ict_pack = analyze_symbol_ict(sym, h1, d1, w1, d1_strength, day_cache)
            d_info = ict_pack["d_info"]
            w_info = ict_pack["w_info"]
            entry_zones = ict_pack["entry_zones"]
            execution = ict_pack["execution"]

            current_price = round_price(sym, float(last_completed(h1).iloc[-1]["close"]))
            try:
                atr_series = atr(last_completed(h1), ATR_LEN)
                atr_h1 = round_price(sym, float(atr_series.dropna().iloc[-1])) if len(atr_series.dropna()) > 0 else None
            except Exception:
                atr_h1 = None

            row = {
                "Snapshot_Date": snapshot_date_str,
                "Instrument": sym,
                "status": "OK",
                "Universe_Layer": ict_pack["layer"],
                "Cluster_Tags": ", ".join(ict_pack["cluster_tags"]),
                "Cluster_Tags_List": ict_pack["cluster_tags"],
                "W1_Bias": w_info["bias"],
                "PW_date": str(w_info["pw_date"]),
                "PWH": round_price(sym, w_info["pwh"]),
                "PWL": round_price(sym, w_info["pwl"]),
                "WEQ": round_price(sym, w_info["weq"]),
                "D1_Bias": d_info["bias"],
                "PD_date": str(d_info["pd_date"]),
                "PDH": round_price(sym, d_info["pdh"]),
                "PDL": round_price(sym, d_info["pdl"]),
                "DEQ": round_price(sym, d_info["eq"]),
                "D1_Dealing_Hi": round_price(sym, ict_pack["dealing"]["hi"]),
                "D1_Dealing_Lo": round_price(sym, ict_pack["dealing"]["lo"]),
                "D1_Dealing_EQ": round_price(sym, ict_pack["dealing"]["eq"]),
                "Price_Side_vs_D1_Range": ict_pack["price_side"],
                "Alignment": ict_pack["alignment"],
                "Liquidity_Condition": ict_pack["liquidity_condition"],
                "Sweep_Quality": ict_pack["sweep_quality"],
                "Liquidity_Side": ict_pack["liquidity_side"],
                "Liquidity_Tier": ict_pack["liquidity_tier"],
                "Liquidity_Reference_Type": ict_pack["liquidity_reference_type"],
                "Rejection_Quality": ict_pack["rejection_quality"],
                "Follow_Through": ict_pack["follow_through"],
                "Both_Sides_Taken_Recently": ict_pack["both_sides_taken_recently"],
                "Displacement_Quality": ict_pack["displacement_quality"],
                "MSS_BOS": ict_pack["mss_bos"],
                "Array_Quality": ict_pack["array_quality"],
                "Session_Quality": ict_pack["session_quality"],
                "RS_RW_Alignment": ict_pack["rs_rw_alignment"],
                "SMT_Hint": ict_pack["smt_hint"],
                "Pivot_Regime": ict_pack["pivot_context"]["pivot_regime"],
                "Pivot_Zone_Fit": ict_pack["pivot_context"]["pivot_zone_fit"],
                "Pivot_Confluence": ict_pack["pivot_context"]["pivot_confluence"],
                "Pivot_Conflict": ict_pack["pivot_context"]["pivot_conflict"],
                "Pivot_Stretch": ict_pack["pivot_context"]["pivot_stretch"],
                "Technical_Score_0_4": ict_pack["technical_score"],
                "Legacy_Confidence_Score": ict_pack["confidence"].get("legacy_score", ict_pack["confidence"]["score"]),
                "Legacy_Confidence_Band": ict_pack["confidence"].get("legacy_band", ict_pack["confidence"]["band"]),
                "Confidence_Score": ict_pack["confidence"]["score"],
                "Confidence_Band": ict_pack["confidence"]["band"],
                "Technical_Quality_Score_10": np.nan,
                "Execution_Realism_Score_10": np.nan,
                "Calibrated_Confidence_Score_10": ict_pack["confidence"].get("score_10", np.nan),
                "Selection_Score": 0.0,
                "Final_Rank_Score": 0.0,
                "Data_Quality": ict_pack["data_quality"],
                "Entry_Label": ict_pack["entry_label"],
                "Num_entry_zones": len(entry_zones),
                "Preferred_Side": execution["preferred_side"],
                "Best_Entry": execution["entry"],
                "Structural_Entry": execution.get("structural_entry"),
                "Calibration_Entry": execution.get("calibration_entry", execution["entry"]),
                "Entry_Distance_ATR": execution.get("entry_distance_atr"),
                "SL": execution["sl"],
                "TP1": execution["tp1"],
                "TP2": execution["tp2"],
                "Current_Price": current_price,
                "ATR_H1": atr_h1,
                "RR_TP1": execution.get("rr_tp1"),
                "RR_TP2": execution.get("rr_tp2"),
                "Execution_Line": execution["entry_text"],
                "Execution_Source": execution.get("execution_source", "zone"),
                "Setup_Archetype": None,
                "Decision_Book": None,
                "Live_Gate_Passed": False,
                "Calibration_Gate_Passed": False,
                "Gate_Passed": False,
                "Gate_Fail_Reasons": "",
                "Decision_Setup_Quality": 0.0,
                "Decision_Execution_Quality": 0.0,
                "Decision_Portfolio_Fit": 0.0,
                "Decision_Rank_Score": 0.0,
                "Base_Ranking_Score": 0.0,
                "Overlap_Penalty": 0.0,
                "Ranking_Score": 0.0,
                "W1_png": None,
                "D1_png": None,
                "H1_png": None,
            }

            row = finalize_decision_fields(row)

            verifier_horizons = [
                ("Verifier", FORWARD_VERIFY_HOURS),
                ("Verifier48", ALT_FORWARD_VERIFY_HOURS),
                ("Verifier72", THIRD_FORWARD_VERIFY_HOURS),
            ]
            for verifier_prefix, verifier_hours in verifier_horizons:
                future_h1, window_meta = forward_slice(cache[sym][0], cutoff_dt, verifier_hours)
                verifier = evaluate_execution_plan(
                    sym=sym,
                    preferred_side=execution["preferred_side"],
                    entry=execution["entry"],
                    sl=execution["sl"],
                    tp1=execution["tp1"],
                    tp2=execution["tp2"],
                    future_h1=future_h1,
                )
                for k, v in verifier.items():
                    row[f"{verifier_prefix}_{k}"] = v
                row[f"{verifier_prefix}_Window_Bars"] = window_meta["Window_Bars"]
                row[f"{verifier_prefix}_Window_Calendar_Hours"] = window_meta["Window_Calendar_Hours"]
                row[f"{verifier_prefix}_Window_Weekend_Gap_Hours"] = window_meta["Window_Weekend_Gap_Hours"]
                outcome_metrics = outcome_return_multiple(
                    verifier.get("Outcome_Label"),
                    execution.get("rr_tp1"),
                    execution.get("rr_tp2"),
                )
                row[f"{verifier_prefix}_R_Multiple"] = outcome_metrics["R_Multiple"]
                row[f"{verifier_prefix}_Weighted_Return_R"] = outcome_metrics["Weighted_Return_R"]

            for i, z in enumerate(entry_zones, start=1):
                row[f"Entry{i}_lo"] = round_price(sym, z["lo"])
                row[f"Entry{i}_hi"] = round_price(sym, z["hi"])
                row[f"Entry{i}_arrays"] = "+".join(["OTE"] + z["arrays"])
                row[f"Entry{i}_score"] = z["score"]
                row[f"Entry{i}_touches"] = z.get("touches", None)
                row[f"Entry{i}_deep_mitigated"] = z.get("deep_mitigated", None)

            summary_rows.append(row)
            json_records.append(json_ready(row))

        shortlist_rows, selector_state_rows = build_shortlist(summary_rows, shortlist_n=min(TOP_SHORTLIST_N, len(SYMBOLS)))
        selector_state_by_instrument = {r["Instrument"]: r for r in selector_state_rows}

        # Propagate full selector state back into the exported rows, not only shortlisted rows.
        selector_fields = [
            "Overlap_Penalty", "Ranking_Score", "Decision_Portfolio_Fit", "Decision_Book",
            "Comparative_Edge_Score_10", "Comparator_Floor_Score_10", "Dominance_Score_10",
            "Admission_Class", "Override_Reason", "Selection_Score", "Final_Rank_Score",
            "Selection_Lane", "Primary_Shortlist_Flag", "Primary_Override_Flag", "Shadow_Watchlist_Flag", "Shadow_Watchlist_Reason", "Shadow_Watchlist_Order", "Shortlist_Eligibility",
            "Admission_Binding_Status", "Veto_Flag", "Veto_Reasons", "Leakage_Penalty_Score",
            "Selector_Profile", "Shortlist_Slot_Name", "Shortlist_Slot_Type", "Shortlist_Slot_Order",
            "In_Top_Shortlist"
        ]
        for r in summary_rows:
            sr = selector_state_by_instrument.get(r["Instrument"])
            if sr is None:
                continue
            for fld in selector_fields:
                if fld in sr:
                    r[fld] = sr.get(fld)
            r["In_Top_Shortlist"] = bool(sr.get("In_Top_Shortlist"))
        required_fields = [
            "Comparative_Edge_Score_10", "Comparator_Floor_Score_10", "Dominance_Score_10",
            "Admission_Class", "Shortlist_Eligibility", "Admission_Binding_Status",
            "Selection_Lane", "Primary_Shortlist_Flag", "Shadow_Watchlist_Flag", "Shadow_Watchlist_Reason", "Shadow_Watchlist_Order", "Selector_Profile"
        ]
        required_nonblank_fields = [
            "Admission_Class", "Shortlist_Eligibility", "Admission_Binding_Status",
            "Selection_Lane", "Selector_Profile"
        ]
        _validate_selector_export_rows(
            summary_rows,
            required_fields=required_fields,
            required_nonblank_fields=required_nonblank_fields,
            expected_profile="v5.5_prediction_ready_selector",
        )
        shortlist_rows = [dict(r) for r in summary_rows if r.get("In_Top_Shortlist")]

        exported = export_day_pack(
            day_outdir=day_outdir,
            snapshot_date=snapshot_date_str,
            summary_rows=summary_rows,
            shortlist_rows=shortlist_rows,
            manifest_extra={
                "forward_verify_hours": FORWARD_VERIFY_HOURS,
                "alt_forward_verify_hours": ALT_FORWARD_VERIFY_HOURS,
                "third_forward_verify_hours": THIRD_FORWARD_VERIFY_HOURS,
                "verifier_horizon_mode": VERIFIER_HORIZON_MODE,
                "high_confidence_min_score": HIGH_CONFIDENCE_MIN_SCORE,
                "medium_confidence_min_score": MEDIUM_CONFIDENCE_MIN_SCORE,
                "reversal_archetype_rank_penalty": REVERSAL_ARCHETYPE_RANK_PENALTY,
                "continuation_archetype_rank_bonus": CONTINUATION_ARCHETYPE_RANK_BONUS,
                "symbols": SYMBOLS,
                "symbol_set_selection": BACKTEST_SYMBOLS_SWITCH,
                "symbol_set_label": BACKTEST_SYMBOLS_LABEL,
            },
        )

        all_rows.extend(summary_rows)
        all_shortlist_rows.extend(shortlist_rows)
        batch_index_rows.append({
            "Snapshot_Date": snapshot_date_str,
            "Day_Output_Folder": str(day_outdir),
            "Day_Zip": str(exported["zip_path"]) if exported["zip_path"] else None,
            "Shortlist_Count": len(shortlist_rows),
            "Universe_Count": len(summary_rows),
        })

    # Batch-level exports
    OUTDIR.mkdir(parents=True, exist_ok=True)
    all_df = pd.DataFrame(all_rows)
    shortlist_df = pd.DataFrame(all_shortlist_rows)
    batch_idx_df = pd.DataFrame(batch_index_rows)

    calibration_csv = OUTDIR / f"calibration_dataset_{BACKTEST_SYMBOLS_LABEL}.csv"
    calibration_json = OUTDIR / f"calibration_dataset_{BACKTEST_SYMBOLS_LABEL}.json"
    shortlist_csv = OUTDIR / f"calibration_top_candidates_{BACKTEST_SYMBOLS_LABEL}.csv"
    shortlist_json = OUTDIR / f"calibration_top_candidates_{BACKTEST_SYMBOLS_LABEL}.json"
    batch_idx_csv = OUTDIR / f"batch_index_{BACKTEST_SYMBOLS_LABEL}.csv"
    batch_idx_json = OUTDIR / f"batch_index_{BACKTEST_SYMBOLS_LABEL}.json"
    calibration_md = OUTDIR / f"calibration_dataset_{BACKTEST_SYMBOLS_LABEL}.md"
    selector_audit_csv = OUTDIR / f"selector_audit_table_{BACKTEST_SYMBOLS_LABEL}.csv"
    selector_audit_json = OUTDIR / f"selector_audit_table_{BACKTEST_SYMBOLS_LABEL}.json"
    selector_audit_md = OUTDIR / f"selector_audit_table_{BACKTEST_SYMBOLS_LABEL}.md"
    calibration_master_csv = OUTDIR / f"calibration_master_table_{BACKTEST_SYMBOLS_LABEL}.csv"
    calibration_master_json = OUTDIR / f"calibration_master_table_{BACKTEST_SYMBOLS_LABEL}.json"
    calibration_master_md = OUTDIR / f"calibration_master_table_{BACKTEST_SYMBOLS_LABEL}.md"

    master_df = build_calibration_master_table(all_df)
    selector_audit_df = build_selector_audit_table(all_df)

    all_df.to_csv(calibration_csv, index=False)
    shortlist_df.to_csv(shortlist_csv, index=False)
    batch_idx_df.to_csv(batch_idx_csv, index=False)
    master_df.to_csv(calibration_master_csv, index=False)

    with open(calibration_json, "w", encoding="utf-8") as f:
        json.dump(json_ready(all_rows), f, indent=2, ensure_ascii=False)
    with open(shortlist_json, "w", encoding="utf-8") as f:
        json.dump(json_ready(all_shortlist_rows), f, indent=2, ensure_ascii=False)
    with open(batch_idx_json, "w", encoding="utf-8") as f:
        json.dump(json_ready(batch_index_rows), f, indent=2, ensure_ascii=False)
    with open(calibration_master_json, "w", encoding="utf-8") as f:
        json.dump(json_ready(master_df.to_dict(orient="records")), f, indent=2, ensure_ascii=False)

    with open(calibration_md, "w", encoding="utf-8") as f:
        f.write(build_analyst_summary(all_shortlist_rows, "Calibration Top Candidates Across Snapshots"))
    with open(calibration_master_md, "w", encoding="utf-8") as f:
        f.write(build_analyst_summary(master_df.to_dict(orient="records"), "Calibration Master Table Across Snapshots"))


    # Batch validation report
    validation_rows = []
    def _metric_series(df: pd.DataFrame, col: str) -> pd.Series:
        if col in df.columns:
            return pd.to_numeric(df[col], errors="coerce")
        return pd.Series(dtype=float)

    def _append_horizon_metrics(rows: list, df: pd.DataFrame, label: str, prefix: str):
        r_col = f"{prefix}_R_Multiple"
        wr_col = f"{prefix}_Weighted_Return_R"
        trig_col = f"{prefix}_Triggered"
        tp1_col = f"{prefix}_TP1_Hit"
        tp2_col = f"{prefix}_TP2_Hit"
        sl_col = f"{prefix}_SL_Hit"
        rows.append({"Metric": f"trigger_rate_{label}", "Value": round(float(df.get(trig_col, pd.Series(dtype=float)).fillna(False).astype(bool).mean()), 4)})
        rows.append({"Metric": f"tp1_rate_{label}", "Value": round(float(df.get(tp1_col, pd.Series(dtype=float)).fillna(False).astype(bool).mean()), 4)})
        rows.append({"Metric": f"tp2_rate_{label}", "Value": round(float(df.get(tp2_col, pd.Series(dtype=float)).fillna(False).astype(bool).mean()), 4)})
        rows.append({"Metric": f"sl_rate_{label}", "Value": round(float(df.get(sl_col, pd.Series(dtype=float)).fillna(False).astype(bool).mean()), 4)})
        r_vals = _metric_series(df, r_col).dropna()
        wr_vals = _metric_series(df, wr_col).dropna()
        rows.append({"Metric": f"sum_r_{label}", "Value": round(float(r_vals.sum()), 4) if len(r_vals) else 0.0})
        rows.append({"Metric": f"avg_r_{label}", "Value": round(float(r_vals.mean()), 4) if len(r_vals) else 0.0})
        rows.append({"Metric": f"sum_weighted_r_{label}", "Value": round(float(wr_vals.sum()), 4) if len(wr_vals) else 0.0})
        rows.append({"Metric": f"avg_weighted_r_{label}", "Value": round(float(wr_vals.mean()), 4) if len(wr_vals) else 0.0})

    if not shortlist_df.empty:
        overlap_nonzero = int((pd.to_numeric(shortlist_df.get("Overlap_Penalty", 0), errors="coerce").fillna(0) > 0).sum())
        validation_rows.append({
            "Metric": "shortlist_rows", "Value": int(len(shortlist_df))
        })
        _append_horizon_metrics(validation_rows, shortlist_df, "24h", "Verifier")
        _append_horizon_metrics(validation_rows, shortlist_df, "48h", "Verifier48")
        _append_horizon_metrics(validation_rows, shortlist_df, "72h", "Verifier72")
        for lbl, prefix in [("24h", "Verifier"), ("48h", "Verifier48"), ("72h", "Verifier72")]:
            gap_col = f"{prefix}_Window_Weekend_Gap_Hours"
            bars_col = f"{prefix}_Window_Bars"
            gap_vals = _metric_series(shortlist_df, gap_col).dropna()
            bar_vals = _metric_series(shortlist_df, bars_col).dropna()
            validation_rows.append({"Metric": f"avg_weekend_gap_hours_{lbl}", "Value": round(float(gap_vals.mean()), 4) if len(gap_vals) else 0.0})
            validation_rows.append({"Metric": f"avg_window_bars_{lbl}", "Value": round(float(bar_vals.mean()), 4) if len(bar_vals) else 0.0})
        validation_rows.append({
            "Metric": "nonzero_overlap_rows", "Value": overlap_nonzero
        })
        validation_rows.append({
            "Metric": "primary_override_count", "Value": int(pd.to_numeric(shortlist_df.get("Primary_Override_Flag", 0), errors="coerce").fillna(0).astype(bool).sum())
        })
    else:
        validation_rows.append({"Metric": "shortlist_rows", "Value": 0})
    validation_df = pd.DataFrame(validation_rows)
    validation_csv = OUTDIR / f"batch_validation_report_{BACKTEST_SYMBOLS_LABEL}.csv"
    validation_json = OUTDIR / f"batch_validation_report_{BACKTEST_SYMBOLS_LABEL}.json"
    validation_md = OUTDIR / f"batch_validation_report_{BACKTEST_SYMBOLS_LABEL}.md"
    validation_df.to_csv(validation_csv, index=False)
    with open(validation_json, "w", encoding="utf-8") as f:
        json.dump(json_ready(validation_rows), f, indent=2, ensure_ascii=False)
    with open(validation_md, "w", encoding="utf-8") as f:
        f.write(validation_df.to_markdown(index=False) if not validation_df.empty else "No validation rows")

    prediction_export_info = {}
    prediction_snapshot_meta = {
        "prediction_enabled": False,
        "prediction_score_version": None,
        "prediction_reference_timestamp": None,
        "prediction_input_fields": [],
        "prediction_forbidden_fields": [],
        "prediction_top_n": 0,
    }
    if ENABLE_TODAY_PREDICTION:
        prediction_rows, prediction_integrity_rows, prediction_snapshot_meta = build_today_prediction_rows(cache)
        _validate_prediction_snapshot_clock(prediction_snapshot_meta)
        prediction_export_info = export_prediction_pack(
            outdir=OUTDIR,
            prediction_rows=prediction_rows,
            integrity_rows=prediction_integrity_rows,
            snapshot_meta=prediction_snapshot_meta,
        )
        prediction_export_info.update(export_today_predictions_bundle(OUTDIR, prediction_export_info, prediction_snapshot_meta))

    # Simple batch stats
    selector_fields_present = sorted([c for c in SELECTOR_AUDIT_COLUMNS if c in all_df.columns])
    selector_profiles_present = sorted([str(x) for x in pd.Series(all_df.get("Selector_Profile", pd.Series(dtype=object))).dropna().astype(str).unique().tolist()]) if not all_df.empty else []
    shortlist_slot_names_present = sorted([str(x) for x in pd.Series(all_df.get("Shortlist_Slot_Name", pd.Series(dtype=object))).dropna().astype(str).unique().tolist() if str(x)]) if not all_df.empty else []
    tournament_pools_present = sorted([str(x) for x in pd.Series(all_df.get("Tournament_Pool", pd.Series(dtype=object))).dropna().astype(str).unique().tolist() if str(x)]) if not all_df.empty else []
    batch_manifest = {
        "script_version": SCRIPT_VERSION,
        "generated_at": datetime.now().isoformat(),
        "run_type": "historical_calibration_batch",
        "symbols": SYMBOLS,
        "symbol_set_selection": BACKTEST_SYMBOLS_SWITCH,
        "symbol_set_label": BACKTEST_SYMBOLS_LABEL,
        "symbol_set_1": BACKTEST_SYMBOLS_SET1,
        "symbol_set_2": BACKTEST_SYMBOLS_SET2,
        "snapshot_days": BACKTEST_SNAPSHOT_DAYS,
        "forward_verify_hours": FORWARD_VERIFY_HOURS,
        "alt_forward_verify_hours": ALT_FORWARD_VERIFY_HOURS,
        "third_forward_verify_hours": THIRD_FORWARD_VERIFY_HOURS,
        "verifier_horizon_mode": VERIFIER_HORIZON_MODE,
        "high_confidence_min_score": HIGH_CONFIDENCE_MIN_SCORE,
        "medium_confidence_min_score": MEDIUM_CONFIDENCE_MIN_SCORE,
        "reversal_archetype_rank_penalty": REVERSAL_ARCHETYPE_RANK_PENALTY,
        "continuation_archetype_rank_bonus": CONTINUATION_ARCHETYPE_RANK_BONUS,
        "execution_payoff_preset": EXECUTION_PAYOFF_PRESET,
        "sl_distance_multiplier": SL_DISTANCE_MULTIPLIER,
        "tp1_distance_multiplier": TP1_DISTANCE_MULTIPLIER,
        "tp2_distance_multiplier": TP2_DISTANCE_MULTIPLIER,
        "tp1_partial_exit_fraction": TP1_PARTIAL_EXIT_FRACTION,
        "selector_profile": selector_profiles_present[0] if len(selector_profiles_present) == 1 else selector_profiles_present,
        "selector_fields_present": selector_fields_present,
        "selector_profiles_present": selector_profiles_present,
        "shortlist_slot_names_present": shortlist_slot_names_present,
        "tournament_pools_present": tournament_pools_present,
        "shortlist_driver_set": {
            "hard_rejects": ["status_not_ok", "poor_data", "no_side", "entry_too_far_calibration", "full_conflict", "strong_pivot_conflict", "weak_execution"],
            "ranking_core": ["Decision_Execution_Quality", "Decision_Setup_Quality", "Entry_Distance_ATR", "Continuation_Subquality", "Survivor_Score"],
            "allocator_controls": ["MAX_USD_BASKET_IN_SHORTLIST", "MAX_CONTINUATION_IN_SHORTLIST", "MAX_BBOOK_IN_SHORTLIST", "MAX_THEME_IN_SHORTLIST"],
        },
        "selector_knobs": {
            "TOP_SHORTLIST_N": TOP_SHORTLIST_N,
            "MAX_USD_BASKET_IN_SHORTLIST": MAX_USD_BASKET_IN_SHORTLIST,
            "MAX_CONTINUATION_IN_SHORTLIST": MAX_CONTINUATION_IN_SHORTLIST,
            "MAX_BBOOK_IN_SHORTLIST": MAX_BBOOK_IN_SHORTLIST,
            "MAX_THEME_IN_SHORTLIST": MAX_THEME_IN_SHORTLIST,
            "V41_SETUP_WEIGHT": V41_SETUP_WEIGHT,
            "V41_EXECUTION_WEIGHT": V41_EXECUTION_WEIGHT,
        },
        "output_naming": {
            "batch_folder": OUTDIR.name,
            "batch_zip": f"{OUTDIR.name}.zip",
            "symbol_set_label": BACKTEST_SYMBOLS_LABEL,
        },
        "prediction_enabled": prediction_snapshot_meta.get("prediction_enabled", False),
        "prediction_score_version": prediction_snapshot_meta.get("prediction_score_version"),
        "prediction_reference_timestamp": prediction_snapshot_meta.get("prediction_reference_timestamp"),
        "prediction_snapshot_date": prediction_snapshot_meta.get("snapshot_date"),
        "prediction_input_fields": prediction_snapshot_meta.get("prediction_input_fields", []),
        "prediction_forbidden_fields": prediction_snapshot_meta.get("prediction_forbidden_fields", []),
        "prediction_top_n": prediction_snapshot_meta.get("prediction_top_n", 0),
        "prediction_files": prediction_export_info.get("prediction_files", []),
        "today_predictions_zip": prediction_export_info.get("today_predictions_zip"),
        "today_predictions_manifest": prediction_export_info.get("today_predictions_manifest"),
        "latest_output_dir": str(LATEST_DIR),
        "latest_prediction_files": prediction_export_info.get("today_predictions_manifest", {}).get("latest_prediction_files", []),
        "latest_today_predictions_zip": prediction_export_info.get("today_predictions_manifest", {}).get("latest_today_predictions_zip"),
        "batch_files": [],
    }
    changelog_path = OUTDIR / "CHANGELOG.md"
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write("# Changelog\n\n")
        for item in CHANGE_LOG:
            f.write(f"- {item}\n")
        f.write("- Historical calibration batch mode writes one production-style day-pack per snapshot date.\n")
        f.write("- Added forward verifier outcome fields for basic retrospective calibration.\n")
        f.write("- Added calibration_master_table.csv/json/md as the preferred one-file summary for batch calibration review.\n")
        f.write("- Added selector_audit_table.csv/json/md and promoted selector diagnostics into calibration_master_table for auditability.\n")
        f.write("- v5.5: fixed prediction snapshot clocking with build-time timestamp sanity checks.\n")
        f.write("- v5.5: recalibrated Setup_Quality_Band thresholds for more communicative prediction boards.\n")
        f.write("- v5.5: added Today_Predictions.zip bundle for prompt-native prediction review.\n")
        f.write("- v5.51: added stable daily_outputs/latest exports with unsuffixed json/csv/txt prediction files for GitHub + ChatGPT reading.\n")

    batch_files = sorted([x for x in OUTDIR.iterdir() if x.is_file()])
    batch_manifest["batch_files"] = [fp.name for fp in batch_files]
    manifest_path = OUTDIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(batch_manifest, f, indent=2, ensure_ascii=False)

    batch_zip_path = OUTDIR / f"{OUTDIR.name}.zip"
    if EXPORT_BATCH_ZIP:
        with zipfile.ZipFile(batch_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for day_dir in sorted([x for x in OUTDIR.iterdir() if x.is_dir()]):
                for fp in sorted(day_dir.iterdir()):
                    if fp.is_file():
                        zf.write(fp, arcname=f"{day_dir.name}/{fp.name}")
            for fp in sorted([x for x in OUTDIR.iterdir() if x.is_file()]):
                if fp.name == batch_zip_path.name:
                    continue
                zf.write(fp, arcname=fp.name)

    print("\nDONE.")
    print("Batch output folder:", OUTDIR.resolve())
    print("Calibration dataset CSV:", calibration_csv.resolve())
    print("Calibration top candidates CSV:", shortlist_csv.resolve())
    if EXPORT_BATCH_ZIP:
        print("Batch ZIP file:", batch_zip_path.resolve())
    if prediction_export_info.get("today_predictions_manifest", {}).get("latest_today_predictions_zip"):
        print("Today Predictions ZIP:", (LATEST_DIR / prediction_export_info["today_predictions_manifest"]["latest_today_predictions_zip"]).resolve())
    print("Latest output folder:", LATEST_DIR.resolve())

if __name__ == "__main__":
    main()
