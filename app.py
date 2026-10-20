from datetime import datetime, timedelta
import json
import os
import re
from google.oauth2.service_account import Credentials
import gspread
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ページ基本設定
st.set_page_config(
    page_title="NAR Data-Lab",
    page_icon="🏇",
    layout="wide",
    initial_sidebar_state="auto",
)

# ==========================================
# 🎨 カスタムCSS（アンバーゴールド基調・完全リッチ仕様）
# ==========================================
st.markdown(
    """
<style>
    .stApp {
        background-color: #0B0E14 !important;
        color: #F3F4F6 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    [data-testid="stSidebar"] {
        background-color: #10141D !important;
        border-right: 1px solid #262C3A !important;
    }
    
    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 1.35rem;
        font-weight: 700;
        color: #F59E0B !important;
        padding: 0.5rem 0.5rem 1.5rem 0.5rem;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        background-color: transparent !important;
        padding: 10px 12px !important;
        border-radius: 8px !important;
        margin-bottom: 4px !important;
        cursor: pointer !important;
        border: none !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
        width: 0px !important;
        height: 0px !important;
        opacity: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        position: absolute !important;
        pointer-events: none !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] p {
        color: #94A3B8 !important;
        font-size: 1.02rem !important;
        font-weight: 600 !important;
        margin-left: 5px !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"],
    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
        background-color: #241E14 !important;
        border-left: 3px solid #F59E0B !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] p,
    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p {
        color: #FFFFFF !important;
    }

    /* フォーム・入力ラベル */
    [data-testid="stWidgetLabel"] p, label p {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
    }

    /* ラジオ切り替えボタン */
    div[data-testid="stRadio"] div[role="radiogroup"] label {
        background-color: #151A24 !important;
        border: 1px solid #2D3548 !important;
        border-radius: 8px !important;
        padding: 6px 14px !important;
        margin-right: 8px !important;
        cursor: pointer !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
        border-color: #F59E0B !important;
        background-color: #241E14 !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
        background-color: #292012 !important;
        border-color: #F59E0B !important;
        box-shadow: 0 0 10px rgba(245, 158, 11, 0.35) !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label p {
        color: #FFFFFF !important;
        font-size: 0.92rem !important;
        font-weight: 700 !important;
    }

    /* タブデザイン */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px !important;
        background-color: transparent !important;
        margin-bottom: 8px !important;
        padding: 0 !important;
        height: 38px !important;
        min-height: 38px !important;
        align-items: center !important;
        border-bottom: none !important;
        flex-wrap: wrap !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none !important; }
    .stTabs [data-baseweb="tab"] {
        background-color: #151A24 !important;
        border: 1px solid #2D3548 !important;
        border-radius: 8px !important;
        color: #F3F4F6 !important;
        padding: 5px 12px !important;
        font-size: 0.86rem !important;
        font-weight: 700 !important;
        height: 34px !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #FFFFFF !important;
        border-color: #F59E0B !important;
        background-color: #241E14 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #292012 !important;
        border-color: #F59E0B !important;
        color: #FBBF24 !important;
        box-shadow: 0 0 10px rgba(245, 158, 11, 0.35) !important;
    }
    .stTabs [data-baseweb="tab-panel"] { padding: 0px !important; margin: 0px !important; }

    [data-testid="stExpander"] details {
        background-color: #151A24 !important;
        border: 1px solid #262F42 !important;
        border-radius: 8px !important;
    }
    [data-testid="stExpander"] summary {
        background-color: #1C2230 !important;
        padding: 12px 16px !important;
        border-radius: 8px !important;
    }
    [data-testid="stExpander"] summary p {
        color: #F3F4F6 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    [data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
        background-color: #0B0E14 !important;
        padding: 12px 8px !important;
    }

    .sidebar-user {
        position: fixed !important;
        bottom: 24px !important;
        left: 18px !important;
        width: 220px !important;
        z-index: 99999 !important;
        background-color: #10141D !important;
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        padding: 8px 10px !important;
        border-radius: 8px !important;
        border: 1px solid #262C3A !important;
    }
    .user-avatar {
        width: 36px; height: 36px; background: #D97706; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-weight: 700; color: white;
    }
    .user-info { display: flex; flex-direction: column; }
    .user-name { font-size: 0.85rem; font-weight: 600; color: #F8FAFC; }
    .user-status { font-size: 0.75rem; color: #F59E0B; display: flex; align-items: center; gap: 4px; }

    .main-title {
        font-size: 1.85rem; font-weight: 700; color: #FFFFFF !important;
        margin-bottom: 4px; line-height: 1.25;
    }
    .last-update { font-size: 0.85rem; color: #94A3B8; margin-bottom: 1rem; }

    button[kind="secondary"], button[kind="primary"], [data-testid="stButton"] button {
        background-color: #1A202C !important; color: #E2E8F0 !important;
        border: 1px solid #2D3748 !important; border-radius: 8px !important; font-weight: 600 !important;
    }
    [data-testid="stButton"] button:hover {
        background-color: #292012 !important; border-color: #F59E0B !important;
    }

    div[class*="st-key-help_modal_btn"] button {
        width: 38px !important; height: 38px !important; min-height: 38px !important;
        max-width: 38px !important; border-radius: 50% !important; padding: 0 !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
        font-size: 0.95rem !important; margin-left: auto !important;
    }
    div[class*="st-key-refresh_btn"] button {
        height: 38px !important; min-height: 38px !important; padding: 0 16px !important;
        font-size: 0.88rem !important; border-radius: 8px !important; width: auto !important;
        white-space: nowrap !important; display: inline-flex !important; align-items: center !important;
    }

    .stForm [data-testid="stFormSubmitButton"] button {
        background-color: #D97706 !important; border: 1px solid #F59E0B !important;
        border-radius: 8px !important; padding: 0.65rem 1.6rem !important; font-weight: 700 !important;
        min-height: 48px !important; box-shadow: 0 4px 14px rgba(217, 119, 6, 0.4) !important; width: 100% !important;
    }
    .stForm [data-testid="stFormSubmitButton"] button * { color: #FFFFFF !important; font-weight: 700 !important; font-size: 1.05rem !important; }

    [data-testid="stForm"] {
        background-color: #151A24 !important; border: 1px solid #262F42 !important;
        border-radius: 12px !important; padding: 1.4rem !important;
    }

    /* KPIカード */
    .kpi-rich-card {
        background: #151A24 !important; border: 1px solid #262F42 !important;
        border-radius: 14px !important; padding: 1.1rem 1.25rem !important;
        margin-bottom: 0.8rem !important; height: 165px !important; min-height: 165px !important;
        box-sizing: border-box !important; display: flex !important; flex-direction: column !important;
        justify-content: space-between !important;
    }
    .kpi-bar-amber { border-left: 4px solid #F59E0B !important; }
    .kpi-bar-green { border-left: 4px solid #10B981 !important; }

    .kpi-rich-title {
        font-size: 0.88rem; color: #E2E8F0; font-weight: 700; margin-bottom: 0.5rem;
        display: flex; align-items: center; gap: 6px;
    }
    .kpi-main-metrics {
        display: flex; align-items: baseline; justify-content: space-between;
        margin-bottom: 0.6rem; border-bottom: 1px solid #262F42; padding-bottom: 0.5rem;
        flex-wrap: wrap; gap: 8px;
    }
    .kpi-big-val { font-size: 1.95rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.5px; }
    .kpi-sub-rate { font-size: 1rem; color: #CBD5E1; font-weight: 700; }
    .kpi-money-row {
        display: flex; justify-content: space-between; align-items: center;
        font-size: 0.86rem; color: #CBD5E1; flex-wrap: wrap; gap: 4px;
    }
    .kpi-profit-pos { color: #10B981; font-weight: 700; }
    .kpi-profit-neg { color: #EF4444; font-weight: 700; }

    .race-card {
        background: #151A24; border: 1px solid #262F42; border-radius: 12px;
        padding: 1.1rem; margin-bottom: 1rem;
    }
    .race-header {
        display: flex; justify-content: space-between; align-items: center;
        border-bottom: 1px solid #262F42; padding-bottom: 0.5rem; margin-bottom: 0.8rem;
        flex-wrap: wrap; gap: 6px;
    }
    .race-name { font-size: 1.05rem; font-weight: 700; color: #FFFFFF; }
    .race-badge {
        background-color: #292012; color: #FBBF24; font-size: 0.75rem; font-weight: 700;
        padding: 3px 10px; border-radius: 4px; border: 1px solid #F59E0B;
    }

    .status-badge-buy {
        background: rgba(245, 158, 11, 0.15); border: 1px solid #F59E0B; color: #FBBF24;
        font-size: 0.88rem; font-weight: 700; padding: 6px 12px; border-radius: 6px;
        display: inline-block; margin-bottom: 10px;
    }
    .status-badge-skip {
        background: rgba(148, 163, 184, 0.12); border: 1px solid #475569; color: #CBD5E1;
        font-size: 0.88rem; font-weight: 600; padding: 6px 12px; border-radius: 6px;
        display: inline-block; margin-bottom: 10px;
    }

    @media screen and (max-width: 768px) {
        .main-title { font-size: 1.35rem !important; }
        .kpi-big-val { font-size: 1.5rem !important; }
        .sidebar-user { position: relative !important; bottom: auto !important; left: auto !important; width: 100% !important; margin-top: 2rem !important; }
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 🔐 スプレッドシート接続処理
# ==========================================
SS_NAME = "地方競馬AI予想管理"


@st.cache_resource
def get_gspread_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        creds_dict = None
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
        elif "gcp_json" in st.secrets:
            creds_dict = json.loads(st.secrets["gcp_json"])

        if creds_dict:
            if "private_key" in creds_dict:
                pk = str(creds_dict["private_key"]).strip().strip('"').strip("'")
                pk = pk.replace("\\n", "\n")
                creds_dict["private_key"] = pk
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            return gspread.authorize(creds)

        for p in ["key.json", os.path.expanduser("~/nar_system/key.json"), os.path.expanduser("~/key.json")]:
            if os.path.exists(p):
                creds = Credentials.from_service_account_file(p, scopes=scopes)
                return gspread.authorize(creds)
    except Exception as e:
        st.sidebar.error(f"認証エラー: {e}")
    return None


@st.cache_data(ttl=60)
def load_sheet_data():
    gc = get_gspread_client()
    if not gc:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    try:
        ss = gc.open(SS_NAME)

        df_today = pd.DataFrame()
        try:
            ws_today = ss.worksheet("当日予想")
            vals = ws_today.get_all_values()
            if vals and len(vals) > 1:
                df_today = pd.DataFrame(vals[1:], columns=vals[0])
        except Exception:
            pass

        df_daily = pd.DataFrame()
        try:
            ws_daily = ss.worksheet("日次収支")
            vals_d = ws_daily.get_all_values()
            if vals_d and len(vals_d) > 1:
                std_cols = ["日付", "会場", "AI投資額", "AI回収額", "AIレース数", "AI的中数", "ユーザー投資額", "ユーザー回収額", "ユーザーレース数", "ユーザー的中数"]
                first_row = vals_d[0]
                if "日付" not in first_row and re.match(r"^\d{4}[/-]\d{2}", str(vals_d[1][0])):
                    df_daily = pd.DataFrame(vals_d[1:], columns=std_cols[:len(vals_d[1])])
                else:
                    df_daily = pd.DataFrame(vals_d[1:], columns=first_row[:len(vals_d[1])])
        except Exception:
            pass

        df_jpn = pd.DataFrame()
        try:
            ws_jpn = ss.worksheet("Jpn予想")
            vals_j = ws_jpn.get_all_values()
            if vals_j and len(vals_j) > 1:
                df_jpn = pd.DataFrame(vals_j[1:], columns=vals_j[0])
        except Exception:
            pass

        df_skip = pd.DataFrame()
        try:
            ws_skip = ss.worksheet("見送りレース")
            vals_s = ws_skip.get_all_values()
            if vals_s and len(vals_s) > 1:
                df_skip = pd.DataFrame(vals_s[1:], columns=vals_s[0])
        except Exception:
            pass

        return df_today, df_daily, df_jpn, df_skip
    except Exception:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


df_today, df_daily_log, df_jpn, df_skip = load_sheet_data()


def extract_selected_picks(df_src):
    if df_src is None or df_src.empty:
        return pd.DataFrame()

    rule_col = "事前確定判定" if "事前確定判定" in df_src.columns else ("黄金ルール詳細" if "黄金ルール詳細" in df_src.columns else "")
    if not rule_col:
        return pd.DataFrame()

    hits = df_src[df_src[rule_col].astype(str).str.strip() != ""].copy()
    if hits.empty:
        return pd.DataFrame()

    mark_col = "評価" if "評価" in hits.columns else ("印" if "印" in hits.columns else "")
    mark_priority = {"◎": 1, "◯": 2, "▲": 3, "△": 4}
    if mark_col:
        hits["_m_prio"] = hits[mark_col].map(mark_priority).fillna(9)
    else:
        hits["_m_prio"] = 9

    hits["_r_num"] = hits["R"].astype(str).str.extract(r"(\d+)").astype(float).fillna(99)
    hits = (
        hits.sort_values(["会場", "_r_num", "_m_prio"])
        .drop_duplicates(subset=["日付", "会場", "R"], keep="first")
        .sort_values(["会場", "_r_num"])
        .drop(columns=["_m_prio", "_r_num"])
        .reset_index(drop=True)
    )
    return hits


def get_hybrid_partners(df_src, venue, r_code, axis_umaban):
    """同一レースからAIスコア（またはRL）上位2頭の相手馬を抽出"""
    if df_src is None or df_src.empty:
        return []
    sub = df_src[(df_src["会場"].astype(str) == str(venue)) & (df_src["R"].astype(str) == str(r_code))].copy()
    if sub.empty:
        return []
    others = sub[sub["馬番"].astype(str) != str(axis_umaban)].copy()
    if others.empty:
        return []
    if "AIスコア" in others.columns:
        others["_sc"] = pd.to_numeric(others["AIスコア"], errors="coerce").fillna(99.0)
        sorted_o = others.sort_values("_sc").reset_index(drop=True)
    elif "RL" in others.columns:
        others["_sc"] = pd.to_numeric(others["RL"], errors="coerce").fillna(99.0)
        sorted_o = others.sort_values("_sc").reset_index(drop=True)
    else:
        sorted_o = others.reset_index(drop=True)
    return sorted_o.to_dict("records")


# ==========================================
# 🌟 運用サイクルのポップアップダイアログ
# ==========================================
@st.dialog("🔄 地方競馬AI (NAR Data-Lab) 運用サイクル・フロー")
def show_flow_modal():
    st.markdown(
        """
    <div style="font-size:1rem; color:#FFFFFF; font-weight:700; margin-bottom:14px;">
        直前オッズに依存しない「単勝＋ワイド2点 ハイブリッド運用」の自動運用サイクルです。
    </div>
    <div style="background:#151A24; border:1px solid #2D3548; border-left:5px solid #F59E0B; border-radius:10px; padding:14px 16px; margin-bottom:12px;">
        <div style="font-size:1.05rem; font-weight:700; color:#FFFFFF; margin-bottom:8px;">🌅 1. 【前日夜 or 朝】 予測・出撃フェーズ（publish_today.py）</div>
        <div style="font-size:0.9rem; color:#F3F4F6; line-height:1.7;">
            <span style="color:#FBBF24; font-weight:700;">・処理</span>: 全5場巡回 ➔ 特注15ゾーン＋全場均等ゾーン合致馬を自動選出（1日2〜4鞍）<br>
            <span style="color:#FBBF24; font-weight:700;">・配信</span>: 左メニュー「📝 レジまぐ投稿原稿」からハイブリッド原稿をコピーして予約投稿<br>
            <span style="color:#FBBF24; font-weight:700;">・投票</span>: 単勝1点（1,000円）＋ ワイド2点（各500円）を事前投票
        </div>
    </div>
    <div style="background:#151A24; border:1px solid #2D3548; border-left:5px solid #10B981; border-radius:10px; padding:14px 16px; margin-bottom:12px;">
        <div style="font-size:1.05rem; font-weight:700; color:#FFFFFF; margin-bottom:8px;">🌙 2. 【夜 21:00】 収支確定フェーズ（result.py）</div>
        <div style="font-size:0.9rem; color:#F3F4F6; line-height:1.7;">
            <span style="color:#34D399; font-weight:700;">・処理</span>: 確定着順と配当を自動回収 ➔ 単勝＆ワイドのダブル的中を判定<br>
            <span style="color:#34D399; font-weight:700;">・反映先</span>: 「日次収支」シートへAI公式実績を自動記録（会場別も自動集計）<br>
            <span style="color:#34D399; font-weight:700;">・操作</span>: 左メニュー「💰 収支入力」から実戦投票額を保存
        </div>
    </div>
    <div style="background:#151A24; border:1px solid #2D3548; border-left:5px solid #06B6D4; border-radius:10px; padding:14px 16px;">
        <div style="font-size:1.05rem; font-weight:700; color:#FFFFFF; margin-bottom:8px;">🔍 3. 【週1回】 砂入れ替え ＆ バイアス点検フェーズ</div>
        <div style="font-size:0.9rem; color:#F3F4F6; line-height:1.7;">
            <span style="color:#38BDF8; font-weight:700;">・処理</span>: 公式サイトのニュース巡回 ＆ 内外枠バイアスの急変を検知
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


# ==========================================
# 🗂️ サイドバー メニュー構築
# ==========================================
with st.sidebar:
    st.markdown(
        """
    <div class="sidebar-logo">
        <span>🏇</span> NAR Data-Lab
    </div>
    """,
        unsafe_allow_html=True,
    )

    menu = st.radio(
        "",
        [
            "📊 ダッシュボード",
            "🎯 厳選勝負レース",
            "📝 レジまぐ投稿原稿",
            "👑 Jpn重賞専用予想",
            "🏇 全レース出馬表",
            "💰 収支入力・管理",
            "💻 ターミナル操作マニュアル",
            "🗄️ 過去データ分析",
            "📈 スプレッドシート連携",
        ],
        label_visibility="collapsed",
    )

    st.markdown(
        """
    <div class="sidebar-user">
        <div class="user-avatar">N</div>
        <div class="user-info">
            <div class="user-name">Owner (Private)</div>
            <div class="user-status">● ハイブリッド運用稼働中</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

latest_date_str = ""
df_today_latest = pd.DataFrame()
df_picks_latest = pd.DataFrame()

if df_today is not None and not df_today.empty and "日付" in df_today.columns:
    latest_date_str = df_today["日付"].max()
    df_today_latest = df_today[df_today["日付"] == latest_date_str].copy()
    df_picks_latest = extract_selected_picks(df_today_latest)

# ==========================================
# 🚀 画面 1: 📊 ダッシュボード
# ==========================================
if menu == "📊 ダッシュボード":
    col_h_left, col_h_right = st.columns([7, 3])
    now_str = datetime.now().strftime("%Y年%m月%d日 %H:%M")

    with col_h_left:
        st.markdown(
            f"""
            <div class="main-title">地方競馬 実戦収支ダッシュボード</div>
            <div class="last-update">最終更新: {now_str} (日次収支シート完全自動同期)</div>
            """,
            unsafe_allow_html=True,
        )

    with col_h_right:
        c_space, c_help, c_btn = st.columns([1.5, 1, 2.5])
        with c_help:
            if st.button("❓", key="help_modal_btn", help="運用フローを確認"):
                show_flow_modal()
        with c_btn:
            if st.button("🔄 データ更新", key="refresh_btn"):
                st.cache_data.clear()
                st.rerun()

    df_daily_calc = pd.DataFrame()
    if df_daily_log is not None and not df_daily_log.empty:
        df_daily_calc = df_daily_log.copy()
        for col in df_daily_calc.columns:
            if any(k in col for k in ["投資", "回収", "払戻", "レース", "的中"]):
                df_daily_calc[col] = pd.to_numeric(
                    df_daily_calc[col].astype(str).str.replace(",", ""), errors="coerce"
                ).fillna(0)

    def get_stats(prefix, venue_name):
        if df_daily_calc.empty:
            return 0.0, 0.0, 0, 0, 0, 0, False

        sub = df_daily_calc.copy()
        if "会場" in sub.columns:
            if venue_name == "総合":
                non_total = sub[sub["会場"].astype(str).str.strip() != "総合"]
                if not non_total.empty:
                    sub = non_total
            else:
                sub = sub[sub["会場"].astype(str).str.contains(venue_name, na=False)]

        inv_col = f"{prefix}投資額" if f"{prefix}投資額" in sub.columns else ("投資額" if "投資額" in sub.columns else "")
        ret_col = f"{prefix}回収額" if f"{prefix}回収額" in sub.columns else ("払戻額" if "払戻額" in sub.columns else "")
        rc_col = f"{prefix}レース数" if f"{prefix}レース数" in sub.columns else ("レース数" if "レース数" in sub.columns else "")
        ht_col = f"{prefix}的中数" if f"{prefix}的中数" in sub.columns else ("的中数" if "的中数" in sub.columns else "")

        inv = int(sub[inv_col].sum()) if inv_col else 0
        ret = int(sub[ret_col].sum()) if ret_col else 0
        races = int(sub[rc_col].sum()) if rc_col else 0
        hits = int(sub[ht_col].sum()) if ht_col else 0

        if inv > 0 or races > 0:
            roi = round(ret / inv * 100, 1) if inv > 0 else 0.0
            hit_r = round(hits / races * 100, 1) if races > 0 else 0.0
            return roi, hit_r, hits, races, inv, ret, True
        return 0.0, 0.0, 0, 0, 0, 0, False

    venue_tabs = [
        ("🌐 総合", "総合"),
        ("🌃 大井", "大井"),
        ("🐎 川崎", "川崎"),
        ("⚓ 船橋", "船橋"),
        ("🌸 浦和", "浦和"),
        ("🔥 佐賀", "佐賀"),
    ]

    c1, c2 = st.columns(2)

    with c1:
        v_tabs_ai = st.tabs([label for label, _ in venue_tabs])
        for idx_v, (v_label, v_name) in enumerate(venue_tabs):
            with v_tabs_ai[idx_v]:
                ai_roi, ai_hit, ai_hits, ai_races, ai_inv, ai_ret, has_ai = get_stats("AI", v_name)
                if has_ai:
                    ai_prof = ai_ret - ai_inv
                    ai_p_class = "kpi-profit-pos" if ai_prof >= 0 else "kpi-profit-neg"
                    ai_p_sign = "+" if ai_prof > 0 else ""
                    st.markdown(
                        f"""
                        <div class="kpi-rich-card kpi-bar-amber">
                            <div class="kpi-rich-title">🤖 AI運用 実績【{v_label}】 <span style="color:#F59E0B; font-weight:600;">(result.py 自動回収)</span></div>
                            <div class="kpi-main-metrics">
                                <div>
                                    <span style="font-size:0.8rem; color:#CBD5E1;">通算回収率</span><br>
                                    <span class="kpi-big-val">{ai_roi:.1f}</span><span style="font-size:1.1rem; color:#CBD5E1;">%</span>
                                </div>
                                <div style="text-align:right;">
                                    <span style="font-size:0.8rem; color:#CBD5E1;">通算的中率</span><br>
                                    <span class="kpi-sub-rate">{ai_hit:.1f}%</span> <span style="font-size:0.82rem; color:#CBD5E1;">({ai_hits}/{ai_races}R)</span>
                                </div>
                            </div>
                            <div class="kpi-money-row">
                                <span>投資: <b>{ai_inv:,}円</b> ➔ 払戻: <b>{ai_ret:,}円</b></span>
                                <span class="{ai_p_class}">損益: {ai_p_sign}{ai_prof:,}円</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="kpi-rich-card kpi-bar-amber">
                            <div class="kpi-rich-title">🤖 AI運用 実績【{v_label}】 <span style="color:#94A3B8; font-weight:600;">(自動回収待機中)</span></div>
                            <div class="kpi-main-metrics">
                                <div>
                                    <span style="font-size:0.8rem; color:#CBD5E1;">通算回収率</span><br>
                                    <span class="kpi-big-val">-</span><span style="font-size:1.1rem; color:#CBD5E1;">%</span>
                                </div>
                                <div style="text-align:right;">
                                    <span style="font-size:0.8rem; color:#CBD5E1;">通算的中率</span><br>
                                    <span class="kpi-sub-rate">-</span>
                                </div>
                            </div>
                            <div class="kpi-money-row">
                                <span>夜に `result.py` を実行すると自動反映</span>
                                <span style="color:#94A3B8;">0 レース</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    with c2:
        v_tabs_usr = st.tabs([label for label, _ in venue_tabs])
        for idx_u, (v_label, v_name) in enumerate(venue_tabs):
            with v_tabs_usr[idx_u]:
                u_roi, u_hit, u_hits, u_races, u_inv, u_ret, has_usr = get_stats("ユーザー", v_name)
                if has_usr:
                    u_prof = u_ret - u_inv
                    u_p_class = "kpi-profit-pos" if u_prof >= 0 else "kpi-profit-neg"
                    u_p_sign = "+" if u_prof > 0 else ""
                    st.markdown(
                        f"""
                        <div class="kpi-rich-card kpi-bar-green">
                            <div class="kpi-rich-title">👤 実投票 実績【{v_label}】 <span style="color:#10B981; font-weight:600;">(日次収支連動)</span></div>
                            <div class="kpi-main-metrics">
                                <div>
                                    <span style="font-size:0.8rem; color:#CBD5E1;">実戦回収率</span><br>
                                    <span class="kpi-big-val">{u_roi:.1f}</span><span style="font-size:1.1rem; color:#CBD5E1;">%</span>
                                </div>
                                <div style="text-align:right;">
                                    <span style="font-size:0.8rem; color:#CBD5E1;">実戦的中率</span><br>
                                    <span class="kpi-sub-rate">{u_hit:.1f}%</span> <span style="font-size:0.82rem; color:#CBD5E1;">({u_hits}/{u_races}R)</span>
                                </div>
                            </div>
                            <div class="kpi-money-row">
                                <span>投資: <b>{u_inv:,}円</b> ➔ 払戻: <b>{u_ret:,}円</b></span>
                                <span class="{u_p_class}">収支: {u_p_sign}{u_prof:,}円</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="kpi-rich-card kpi-bar-green">
                            <div class="kpi-rich-title">👤 実投票 実績【{v_label}】 <span style="color:#10B981; font-weight:600;">(日次収支連動)</span></div>
                            <div class="kpi-main-metrics">
                                <div>
                                    <span style="font-size:0.8rem; color:#CBD5E1;">実戦回収率</span><br>
                                    <span class="kpi-big-val">-</span><span style="font-size:1.1rem; color:#CBD5E1;">%</span>
                                </div>
                                <div style="text-align:right;">
                                    <span style="font-size:0.8rem; color:#CBD5E1;">実戦的中率</span><br>
                                    <span class="kpi-sub-rate">-</span>
                                </div>
                            </div>
                            <div class="kpi-money-row">
                                <span>左メニュー「💰 収支入力」から記録可能</span>
                                <span style="color:#94A3B8;">未入力</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    today_target_count = len(df_picks_latest)
    today_race_count = (
        len(df_today_latest[["会場", "R"]].drop_duplicates())
        if not df_today_latest.empty and "会場" in df_today_latest.columns
        else 0
    )
    today_investment = today_target_count * 2000  # 単勝1,000円＋ワイド2点計1,000円 = 2,000円

    c3, c4 = st.columns(2)
    with c3:
        st.markdown(
            f"""
            <div style="background:#151A24; border:1px solid #262F42; border-radius:10px; padding:0.9rem 1.1rem; margin-bottom:0.6rem;">
                <div style="font-size:0.82rem; color:#CBD5E1;">🎯 本日勝負レース数 ({latest_date_str or '未取得'})</div>
                <div style="font-size:1.4rem; font-weight:700; color:#FFFFFF;">{today_target_count} <span style="font-size:0.85rem; color:#94A3B8; font-weight:400;">鞍 / 全{today_race_count}R中</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            f"""
            <div style="background:#151A24; border:1px solid #262F42; border-radius:10px; padding:0.9rem 1.1rem; margin-bottom:0.6rem;">
                <div style="font-size:0.82rem; color:#CBD5E1;">💸 本日推奨投資額目安 (単勝＋ワイド計2,000円/R換算)</div>
                <div style="font-size:1.4rem; font-weight:700; color:#FBBF24;">{today_investment:,} <span style="font-size:0.85rem; color:#94A3B8; font-weight:400;">円</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # 回収率推移グラフ
    col_chart_title, col_chart_select = st.columns([6, 4])
    with col_chart_title:
        st.markdown('<div style="font-size:1.1rem; font-weight:700; color:#FFFFFF; margin-bottom:4px;">回収率推移</div>', unsafe_allow_html=True)
    with col_chart_select:
        chart_mode = st.selectbox(
            "期間・単位",
            [
                "全期間 (累積推移)",
                "日毎 (直近10日)",
                "日毎 (直近30日)",
                "月ごと (月別集計)",
                "年ごと (年別集計)",
            ],
            label_visibility="collapsed",
        )

    fig = go.Figure()
    has_plot = False

    if not df_daily_calc.empty and "日付" in df_daily_calc.columns:
        sub_raw = df_daily_calc.copy()
        if "会場" in sub_raw.columns:
            non_total = sub_raw[sub_raw["会場"].astype(str).str.strip() != "総合"]
            if not non_total.empty:
                sub_raw = non_total

        ai_inv_col = "AI投資額" if "AI投資額" in sub_raw.columns else ("投資額" if "投資額" in sub_raw.columns else "")
        ai_ret_col = "AI回収額" if "AI回収額" in sub_raw.columns else ("払戻額" if "払戻額" in sub_raw.columns else "")
        usr_inv_col = "ユーザー投資額" if "ユーザー投資額" in sub_raw.columns else ""
        usr_ret_col = "ユーザー回収額" if "ユーザー回収額" in sub_raw.columns else ""

        agg_cols_daily = {c: "sum" for c in [ai_inv_col, ai_ret_col, usr_inv_col, usr_ret_col] if c}
        sub_all = sub_raw.groupby("日付", as_index=False).agg(agg_cols_daily)
        sub_all["日付_dt"] = pd.to_datetime(sub_all["日付"], errors="coerce")
        sub_all = sub_all.dropna(subset=["日付_dt"]).sort_values("日付_dt").reset_index(drop=True)

        if not sub_all.empty:
            if chart_mode == "月ごと (月別集計)":
                sub_all["集計キー"] = sub_all["日付_dt"].dt.strftime("%Y/%m")
                plot_df = sub_all.groupby("集計キー", as_index=False).agg(agg_cols_daily).sort_values("集計キー")
                x_vals = plot_df["集計キー"].tolist()

                if ai_inv_col and ai_ret_col and plot_df[ai_inv_col].sum() > 0:
                    ai_vals = np.where(plot_df[ai_inv_col] > 0, (plot_df[ai_ret_col] / plot_df[ai_inv_col]) * 100, 0.0)
                    fig.add_trace(go.Scatter(x=x_vals, y=ai_vals, name="AI理論 (月別)", mode="lines+markers", line=dict(color="#F59E0B", width=2.5), marker=dict(size=7, color="#F59E0B"), hovertemplate="%{x}<br>AI月別回収率: %{y:.1f}%<extra></extra>"))
                    has_plot = True
                if usr_inv_col and usr_ret_col and plot_df[usr_inv_col].sum() > 0:
                    u_vals = np.where(plot_df[usr_inv_col] > 0, (plot_df[usr_ret_col] / plot_df[usr_inv_col]) * 100, 0.0)
                    fig.add_trace(go.Scatter(x=x_vals, y=u_vals, name="実戦 (月別)", mode="lines+markers", line=dict(color="#10B981", width=2.5), marker=dict(size=7, color="#10B981"), hovertemplate="%{x}<br>実戦月別回収率: %{y:.1f}%<extra></extra>"))
                    has_plot = True

            elif chart_mode == "年ごと (年別集計)":
                sub_all["集計キー"] = sub_all["日付_dt"].dt.strftime("%Y年")
                plot_df = sub_all.groupby("集計キー", as_index=False).agg(agg_cols_daily).sort_values("集計キー")
                x_vals = plot_df["集計キー"].tolist()

                if ai_inv_col and ai_ret_col and plot_df[ai_inv_col].sum() > 0:
                    ai_vals = np.where(plot_df[ai_inv_col] > 0, (plot_df[ai_ret_col] / plot_df[ai_inv_col]) * 100, 0.0)
                    fig.add_trace(go.Scatter(x=x_vals, y=ai_vals, name="AI理論 (年別)", mode="lines+markers", line=dict(color="#F59E0B", width=2.5), marker=dict(size=7, color="#F59E0B"), hovertemplate="%{x}<br>AI年別回収率: %{y:.1f}%<extra></extra>"))
                    has_plot = True
                if usr_inv_col and usr_ret_col and plot_df[usr_inv_col].sum() > 0:
                    u_vals = np.where(plot_df[usr_inv_col] > 0, (plot_df[usr_ret_col] / plot_df[usr_inv_col]) * 100, 0.0)
                    fig.add_trace(go.Scatter(x=x_vals, y=u_vals, name="実戦 (年別)", mode="lines+markers", line=dict(color="#10B981", width=2.5), marker=dict(size=7, color="#10B981"), hovertemplate="%{x}<br>実戦年別回収率: %{y:.1f}%<extra></extra>"))
                    has_plot = True

            else:
                if ai_inv_col and ai_ret_col:
                    sub_all["AI_ROI"] = np.where(sub_all[ai_inv_col].cumsum() > 0, (sub_all[ai_ret_col].cumsum() / sub_all[ai_inv_col].cumsum()) * 100, 0.0)
                if usr_inv_col and usr_ret_col:
                    sub_all["U_ROI"] = np.where(sub_all[usr_inv_col].cumsum() > 0, (sub_all[usr_ret_col].cumsum() / sub_all[usr_inv_col].cumsum()) * 100, 0.0)

                if chart_mode == "日毎 (直近10日)":
                    plot_df = sub_all.tail(10).copy()
                elif chart_mode == "日毎 (直近30日)":
                    plot_df = sub_all.tail(30).copy()
                else:
                    plot_df = sub_all.copy()

                x_vals = plot_df["日付_dt"].dt.strftime("%m/%d").tolist()
                if ai_inv_col and ai_ret_col and "AI_ROI" in plot_df.columns and plot_df[ai_inv_col].sum() > 0:
                    fig.add_trace(go.Scatter(x=x_vals, y=plot_df["AI_ROI"], name="AI理論 (累積)", mode="lines+markers", line=dict(color="#F59E0B", width=2.5, shape="spline"), marker=dict(size=7, color="#F59E0B"), hovertemplate="%{x}<br>AI通算回収率: %{y:.1f}%<extra></extra>"))
                    has_plot = True
                if usr_inv_col and usr_ret_col and "U_ROI" in plot_df.columns and plot_df[usr_inv_col].sum() > 0:
                    fig.add_trace(go.Scatter(x=x_vals, y=plot_df["U_ROI"], name="実戦 (累積)", mode="lines+markers", line=dict(color="#10B981", width=2.5, shape="spline"), marker=dict(size=7, color="#10B981"), hovertemplate="%{x}<br>実戦通算回収率: %{y:.1f}%<extra></extra>"))
                    has_plot = True

    if has_plot:
        fig.add_hline(y=100, line_dash="dash", line_color="#94A3B8", annotation_text="100%", annotation_position="bottom right")
        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=15, b=10),
            paper_bgcolor="#151A24",
            plot_bgcolor="#151A24",
            font=dict(color="#CBD5E1", size=11),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(size=11, color="#CBD5E1")),
            xaxis=dict(showgrid=True, gridcolor="#262F42", zeroline=False),
            yaxis=dict(showgrid=True, gridcolor="#262F42", zeroline=True, zerolinecolor="#334155", ticksuffix="%"),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.markdown(
            """
            <div style="background:#151A24; border:1px dashed #2D3548; border-radius:10px; padding:2.5rem 1rem; text-align:center;">
                <div style="font-size:1.05rem; color:#FBBF24; font-weight:700; margin-bottom:6px;">📊 収支データが未登録です</div>
                <div style="font-size:0.85rem; color:#94A3B8;">
                    ナイター終了後に <code>~/keiba_env/bin/python ~/nar_system/result.py</code> を実行すると、AIの確定回収率が自動でグラフ描画されます。
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ==========================================
# 🎯 画面 2: 厳選勝負レース（ハイブリッド仕様）
# ==========================================
elif menu == "🎯 厳選勝負レース":
    st.markdown(f'<div class="main-title">本日の厳選勝負レース ({latest_date_str or "最新"})</div>', unsafe_allow_html=True)
    st.markdown('<div class="last-update">出馬表から特注ゾーンおよび全場均等ルール合致馬（単＋ワイド2点）を自動選出</div>', unsafe_allow_html=True)

    if not df_picks_latest.empty:
        for _, row in df_picks_latest.iterrows():
            rule_txt = row.get("事前確定判定", row.get("黄金ルール詳細", ""))
            mark_txt = row.get("評価", row.get("印", ""))

            # 相手2頭の抽出
            partners = get_hybrid_partners(df_today_latest, row["会場"], row["R"], row["馬番"])
            if len(partners) >= 2:
                p1, p2 = partners[0], partners[1]
                p_text = f"{p1['馬番']}番 {p1.get('馬名','')} ／ {p2['馬番']}番 {p2.get('馬名','')}"
                w_text = f"ワイド {row['馬番']} － {p1['馬番']}, {p2['馬番']}（計2点）"
            elif len(partners) == 1:
                p1 = partners[0]
                p_text = f"{p1['馬番']}番 {p1.get('馬名','')}"
                w_text = f"ワイド {row['馬番']} － {p1['馬番']}（計1点）"
            else:
                p_text = "相手選出中"
                w_text = f"ワイド {row['馬番']} 流し"

            st.markdown(
                f"""
                <div class="race-card">
                    <div class="race-header">
                        <span class="race-name">📍 [{row['会場']} {row['R']}] {row['レース名']} ({row.get('発走時刻', '')}発走 / ダ{row['距離']})</span>
                        <span class="race-badge">👑 事前確定・勝負レース</span>
                    </div>
                    <div style="font-size: 1.05rem; color: #FFFFFF; margin-bottom: 0.6rem;">
                        🎯 <b>推奨馬</b> : <span style="color: #FBBF24; font-weight:800;">{mark_txt} 【{row['馬番']}番 {row['馬名']}】</span>
                        <span style="font-size:0.9rem; color:#CBD5E1; margin-left:10px;">({row['枠番']}枠 / 騎手: {row.get('騎手', '-')})</span>
                    </div>
                    <div style="background:#1C2230; padding:10px 14px; border-radius:8px; border-left:4px solid #F59E0B; margin-bottom:0.8rem;">
                        <div style="font-size:0.9rem; color:#E2E8F0;">
                            📊 <b>指数順位</b>: 地力値 <b>{row['RL']}位</b> ／ コース適性 <b>{row['CL']}位</b> （総合スコア: {row['AIスコア']}）<br>
                            🏆 <b>採用根拠</b>: <span style="color:#34D399; font-weight:700;">{rule_txt}</span>
                        </div>
                    </div>
                    <div style="display:flex; gap:10px; flex-wrap:wrap;">
                        <div style="background:#1B2338; padding:10px 14px; border-radius:8px; border-left:3px solid #F59E0B; flex:1; min-width:220px;">
                            <b style="font-size:0.95rem; color:#FFFFFF;">🚀 【本線・回収狙い】単勝 {row['馬番']}番</b><br>
                            <span style="font-size:0.82rem; color:#CBD5E1;">推奨: 1,000円（利益を伸ばすメイン馬券）</span>
                        </div>
                        <div style="background:#1B2338; padding:10px 14px; border-radius:8px; border-left:3px solid #10B981; flex:1.2; min-width:260px;">
                            <b style="font-size:0.95rem; color:#FFFFFF;">🛡️ 【抑え・上乗せ】{w_text}</b><br>
                            <span style="font-size:0.82rem; color:#CBD5E1;">相手本線: {p_text}（推奨各500円 / ダブル的中狙い）</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("現在、事前確定ルールに合致する勝負レースはありません（無理に買わず完全見送りを推奨）。")

    if df_skip is not None and not df_skip.empty:
        st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
        with st.expander("✋ 本日の見送りレース一覧（直前オッズ変動による買い転換チェック）", expanded=False):
            st.markdown(
                '<div style="font-size:0.85rem; color:#94A3B8; margin-bottom:10px;">※オッズ変動で期待値が跳ね上がる可能性のあるレースを監視できます。</div>',
                unsafe_allow_html=True,
            )
            st.dataframe(df_skip, use_container_width=True, hide_index=True)

# ==========================================
# 📝 画面 3: レジまぐ投稿原稿（ハイブリッド対応）
# ==========================================
elif menu == "📝 レジまぐ投稿原稿":
    st.markdown('<div class="main-title">📝 レジまぐ投稿用 原稿ジェネレーター</div>', unsafe_allow_html=True)
    st.markdown('<div class="last-update">右上のボタンでタイトル・無料枠・有料枠をそのままコピー可能</div>', unsafe_allow_html=True)

    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        style_opt = st.radio("タイトル表現", ["標準（計○鞍）", "厳選強調（渾身の○鞍勝負）"], horizontal=True)
    with col_opt2:
        ticket_opt = st.radio("推奨券種の表記", ["単勝＋ワイド2点（ハイブリッド推奨）", "単勝1点勝負"], horizontal=True)

    n_picks = len(df_picks_latest)
    dt_disp = latest_date_str if latest_date_str else datetime.now().strftime("%Y/%m/%d")
    venues_str = "・".join(df_picks_latest["会場"].unique()) if not df_picks_latest.empty and "会場" in df_picks_latest.columns else "南関・佐賀"

    if "渾身" in style_opt:
        title_text = f"【{venues_str}】データマイニング厳選馬券レポート（{dt_disp}・渾身の{n_picks}鞍勝負）"
    else:
        title_text = f"【{venues_str}】データマイニング厳選馬券レポート（{dt_disp}・計{n_picks}鞍）"

    race_list_lines = []
    if not df_picks_latest.empty:
        for _, r in df_picks_latest.iterrows():
            race_list_lines.append(f"・[{r['会場']}] {r['R']} ({r.get('発走時刻', '')}発走 / ダ{r['距離']}) {r['レース名']}")
    else:
        race_list_lines.append("・本日は基準に合致する厳選レースはありません（見送り）。")
    race_list_str = "\n".join(race_list_lines)

    free_body_text = f"""南関東4場（大井・川崎・船橋・浦和）および佐賀競馬の統計解析レポートです。

出馬表確定時点における枠順バイアス・コース砂質・ラップ適性を数値化し、過去4年半のバックテスト（レース的中率54.4%・回収率128.3%・純利益+90万円超）に裏付けられた統計的優位性の高いレースのみを抽出しています。

◆ 本日の公開対象レース（計{n_picks}鞍）
{race_list_str}

◆ 運用ポリシー
・地力指数と砂・コース適性を融合した多面的スクリーニング
・オッズの直前変動に振り回されない「事前確定型」の低ドローダウン運用
・基本買い目：単勝1点 ＋ 相手上位へのワイド2点（ダブル的中＆資金防衛ハイブリッド）
・感情を排し、条件合致レースを淡々と買い続けることで確率の収束を図る設計

⚠️【ご購入前に必ずお読みください】
当レポートは数レース単位での短期的な的中や利益を保証するものではありません。確率の偏りにより一時的な連敗（ドローダウン）が発生する場合もございます。長期的な統計的優位性をご理解いただける方のみ、余剰資金の範囲内で自己責任にてご活用ください。※直前オッズ1.4倍以下の場合は見送り推奨"""

    if not df_picks_latest.empty:
        paid_lines = [f"本日の厳選勝負レース・買い目一覧です（計{n_picks}鞍）。\n"]
        for _, p in df_picks_latest.iterrows():
            rule_txt = p.get("事前確定判定", p.get("黄金ルール詳細", ""))
            mark_txt = p.get("評価", p.get("印", ""))

            partners = get_hybrid_partners(df_today_latest, p["会場"], p["R"], p["馬番"])
            if "ハイブリッド" in ticket_opt:
                if len(partners) >= 2:
                    p1, p2 = partners[0], partners[1]
                    t_str = f"""  【本線・回収狙い】単勝 {p['馬番']}番（推奨1,000円）
■ 相手本線   : {p1['馬番']}番({p1.get('馬名','')}), {p2['馬番']}番({p2.get('馬名','')})
■ 抑え・上乗せ : ワイド {p['馬番']} － {p1['馬番']}, {p2['馬番']}（計2点 / 推奨各500円） ※ダブル的中狙い"""
                elif len(partners) == 1:
                    p1 = partners[0]
                    t_str = f"""  【本線・回収狙い】単勝 {p['馬番']}番（推奨1,000円）
■ 相手本線   : {p1['馬番']}番({p1.get('馬名','')})
■ 抑え・上乗せ : ワイド {p['馬番']} － {p1['馬番']}（計1点 / 推奨1,000円） ※ダブル的中狙い"""
                else:
                    t_str = f"単勝 {p['馬番']}番（推奨1,000円）"
            else:
                t_str = f"単勝 {p['馬番']}番（1点勝負）"

            paid_lines.append(
                f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 【{p['会場']} {p['R']}】 ({p.get('発走時刻', '')}発走 / ダ{p['距離']}) {p['レース名']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
■ 推奨馬   : {mark_txt} 【{p['馬番']}番 {p['馬名']}】 ({p['枠番']}枠 / 騎手:{p.get('騎手', '-')})
■ 指数順位 : 地力値 {p['RL']}位 ／ コース適性 {p['CL']}位
■ 採用根拠 : {rule_txt}
■ 推奨馬券 :
{t_str}
"""
            )
        paid_lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        paid_body_text = "\n".join(paid_lines)
    else:
        paid_body_text = """━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【本日の配信について（完全見送り・資金防衛）】
全レースをAIデータ解析した結果、本日は当システムの長期黒字基準（全15ゾーン確定条件）を満たす期待値の高いレースが1鞍もありませんでした。

当配信は「無駄な投票を避けて資金を減らさないこと」を最重要ポリシーとしております。
読者の皆様の資金防衛を最優先とし、本日は【完全見送り（ノーベット）】といたします。
また条件が揃った勝負日に全力出撃いたします。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    st.markdown("#### ① 記事タイトル")
    st.code(title_text, language="text")

    st.markdown("#### ② 無料エリア本文")
    st.code(free_body_text, language="text")

    st.markdown("#### ③ 有料エリア本文")
    st.code(paid_body_text, language="text")

# ==========================================
# 👑 画面 4: Jpn重賞専用予想
# ==========================================
elif menu == "👑 Jpn重賞専用予想":
    st.markdown('<div class="main-title">👑 ダートグレード競走（Jpn1・Jpn2・Jpn3）専用予想</div>', unsafe_allow_html=True)
    c_jpn1, c_jpn2 = st.columns(2)
    with c_jpn1:
        sel_grade = st.radio("対象グレード選択", ["🏆 全て", "👑 Jpn1", "🥈 Jpn2", "🥉 Jpn3"], horizontal=True)
    with c_jpn2:
        sel_baba_jpn = st.radio("馬場状態シミュレーション", ["☀️ 良", "⛅ 稍重", "☂️ 重", "🌀 不良"], horizontal=True)

    if df_jpn is not None and not df_jpn.empty:
        st.dataframe(df_jpn, use_container_width=True, hide_index=True)
    else:
        st.markdown(
            """
            <div class="race-card" style="border: 1px dashed #F59E0B; margin-top: 1rem;">
                <div class="race-header">
                    <span class="race-name" style="color:#FBBF24;">🚧 ダートグレード（Jpn1 / Jpn2 / Jpn3）専用枠</span>
                </div>
                <div style="font-size:0.92rem; color:#CBD5E1; line-height:1.7;">
                    スプレッドシートに「Jpn予想」シートが追加されると、自動的にここへJpn1〜Jpn3の専用買い目が表示されます。
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ==========================================
# 🏇 画面 5: 全レース出馬表
# ==========================================
elif menu == "🏇 全レース出馬表":
    st.markdown(f'<div class="main-title">全レース出馬表 ＆ AI評価印 ({latest_date_str or "最新"})</div>', unsafe_allow_html=True)
    st.markdown('<div class="last-update">各会場の全レース出走馬の指数・評価印を詳細確認できます</div>', unsafe_allow_html=True)

    if not df_today_latest.empty and "会場" in df_today_latest.columns:
        venues = df_today_latest["会場"].unique()
        tabs = st.tabs([f"📍 {v}" for v in venues])

        def extract_r_num(x):
            m = re.search(r"(\d+)", str(x))
            return int(m.group(1)) if m else 99

        for i, venue in enumerate(venues):
            with tabs[i]:
                venue_df = df_today_latest[df_today_latest["会場"] == venue]
                r_list = sorted(venue_df["R"].unique(), key=extract_r_num)

                for r_code in r_list:
                    sub_df = venue_df[venue_df["R"] == r_code].copy()
                    rname = sub_df.iloc[0].get("レース名", "")
                    rtime = sub_df.iloc[0].get("発走時刻", "")
                    rdist = sub_df.iloc[0].get("距離", "")

                    rule_col = "事前確定判定" if "事前確定判定" in sub_df.columns else "黄金ルール詳細"
                    has_hit = rule_col in sub_df.columns and (sub_df[rule_col].astype(str).str.strip() != "").any()
                    hit_badge = " 🔥【勝負対象あり】" if has_hit else ""

                    with st.expander(f"🏁 {venue} {r_code} {rname} （{rtime}発走 / ダ{rdist}）{hit_badge}", expanded=has_hit):
                        if has_hit:
                            hit_row = sub_df[sub_df[rule_col].astype(str).str.strip() != ""].iloc[0]
                            st.markdown(
                                f'<div class="status-badge-buy">🎯 事前確定買い対象: {hit_row.get("評価","")} {hit_row["馬番"]}番 {hit_row["馬名"]} ｜ {hit_row[rule_col]}</div>',
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(
                                '<div class="status-badge-skip">✋ 見送りレース（事前確定条件合致なし）</div>',
                                unsafe_allow_html=True,
                            )

                        disp_cols = ["馬番", "評価", "馬名", "騎手", "単勝オッズ", "人気", "RL", "CL", "AIスコア", rule_col]
                        if "印" in sub_df.columns and "評価" not in sub_df.columns:
                            sub_df = sub_df.rename(columns={"印": "評価"})

                        actual_cols = [c for c in disp_cols if c in sub_df.columns]
                        display_df = sub_df[actual_cols].copy()
                        display_df["馬番"] = pd.to_numeric(display_df["馬番"], errors="coerce")
                        display_df = display_df.sort_values("馬番")

                        html_table = """
                        <div style="overflow-x: auto; -webkit-overflow-scrolling: touch; border-radius: 8px; border: 1px solid #262F42; margin-top:8px;">
                        <table style="width:100%; border-collapse: collapse; text-align: center; color: #F3F4F6; background-color: #151A24; min-width: 580px;">
                            <thead>
                                <tr style="background-color: #10141D; color: #FBBF24; border-bottom: 2px solid #262F42;">
                        """
                        for col in actual_cols:
                            html_table += f"<th style='padding: 10px 8px; font-weight: 700; white-space: nowrap;'>{col}</th>"
                        html_table += "</tr></thead><tbody>"

                        for _, row in display_df.iterrows():
                            html_table += "<tr style='border-bottom: 1px solid #1F2737;'>"
                            for col in actual_cols:
                                val = row[col]
                                if col == "評価":
                                    if val == "◎":
                                        val = "<span style='color: #EF4444; font-weight: 900; font-size: 1.15rem;'>◎</span>"
                                    elif val == "◯":
                                        val = "<span style='color: #38BDF8; font-weight: 900; font-size: 1.15rem;'>◯</span>"
                                    elif val == "▲":
                                        val = "<span style='color: #10B981; font-weight: 900; font-size: 1.15rem;'>▲</span>"
                                    elif "△" in str(val):
                                        val = f"<span style='color: #F59E0B; font-weight: 900; font-size: 1.05rem;'>{val}</span>"

                                if pd.notna(val) and val != "":
                                    try:
                                        if col == "単勝オッズ":
                                            val = f"{float(val):.1f}"
                                        elif col == "AIスコア":
                                            val = f"{float(val):.2f}"
                                        elif col in ["RL", "CL", "人気", "馬番"]:
                                            val = f"{int(float(val))}"
                                    except Exception:
                                        pass
                                else:
                                    val = "-"

                                align = "left" if col == "馬名" else ("left" if col == rule_col else "center")
                                nowrap = "white-space: nowrap;" if col not in ["馬名", rule_col] else ""
                                html_table += f"<td style='padding: 8px 6px; text-align: {align}; {nowrap}'>{val}</td>"
                            html_table += "</tr>"
                        html_table += "</tbody></table></div>"

                        st.markdown(html_table, unsafe_allow_html=True)
    else:
        st.info("スプレッドシート「当日予想」にデータがありません。")

# ==========================================
# 💰 画面 6: 収支入力・管理
# ==========================================
elif menu == "💰 収支入力・管理":
    st.markdown('<div class="main-title">日次・会場別 実収支の記録</div>', unsafe_allow_html=True)
    st.markdown('<div class="last-update">開催会場を選んで保存すると、会場別タブおよび「🌐 総合」タブの両方に自動合算されます</div>', unsafe_allow_html=True)

    with st.form("shushi_form"):
        c_top1, c_top2 = st.columns(2)
        with c_top1:
            st.markdown('<div style="font-size:0.95rem; font-weight:700; color:#FFFFFF; margin-bottom:6px;">🗓️ 競馬開催日</div>', unsafe_allow_html=True)
            target_date = st.date_input("開催日", datetime.now(), label_visibility="collapsed")
        with c_top2:
            st.markdown('<div style="font-size:0.95rem; font-weight:700; color:#FFFFFF; margin-bottom:6px;">🏟️ 対象会場</div>', unsafe_allow_html=True)
            target_venue = st.selectbox("対象会場", ["大井", "川崎", "船橋", "浦和", "佐賀"], label_visibility="collapsed")

        st.markdown('<div style="font-size:0.9rem; font-weight:700; color:#FBBF24; margin-top:14px; margin-bottom:8px;">【収支金額】</div>', unsafe_allow_html=True)
        c_in1, c_in2 = st.columns(2)
        with c_in1:
            st.markdown('<div style="font-size:0.92rem; font-weight:700; color:#FFFFFF; margin-bottom:4px;">💸 今日の総購入額 (円)</div>', unsafe_allow_html=True)
            usr_inv = st.number_input("総購入額", min_value=0, value=0, step=100, label_visibility="collapsed")
        with c_in2:
            st.markdown('<div style="font-size:0.92rem; font-weight:700; color:#FFFFFF; margin-bottom:4px;">💰 今日の総払戻額 (円)</div>', unsafe_allow_html=True)
            usr_ret = st.number_input("総払戻額", min_value=0, value=0, step=100, label_visibility="collapsed")

        st.markdown('<div style="font-size:0.9rem; font-weight:700; color:#34D399; margin-top:14px; margin-bottom:8px;">【的中率カウント】</div>', unsafe_allow_html=True)
        c_in3, c_in4 = st.columns(2)
        with c_in3:
            st.markdown('<div style="font-size:0.92rem; font-weight:700; color:#FFFFFF; margin-bottom:4px;">🏇 実際に購入したレース数</div>', unsafe_allow_html=True)
            usr_races = st.number_input("購入レース数", min_value=0, value=0, step=1, label_visibility="collapsed")
        with c_in4:
            st.markdown('<div style="font-size:0.92rem; font-weight:700; color:#FFFFFF; margin-bottom:4px;">🎯 的中したレース数</div>', unsafe_allow_html=True)
            usr_hits = st.number_input("的中レース数", min_value=0, value=0, step=1, label_visibility="collapsed")

        st.write("")
        submit = st.form_submit_button("💾 スプレッドシートに保存")

        if submit:
            gc = get_gspread_client()
            if gc:
                date_str = target_date.strftime("%Y/%m/%d")
                try:
                    ss = gc.open(SS_NAME)
                    std_h = ["日付", "会場", "AI投資額", "AI回収額", "AIレース数", "AI的中数", "ユーザー投資額", "ユーザー回収額", "ユーザーレース数", "ユーザー的中数"]
                    try:
                        ws = ss.worksheet("日次収支")
                    except Exception:
                        ws = ss.add_worksheet(title="日次収支", rows="500", cols="10")
                        ws.append_row(std_h)

                    ws.update("A1:J1", [std_h])
                    records = ws.get_all_values()
                    found_row = -1
                    for idx_r, row in enumerate(records[1:], start=2):
                        if len(row) > 1 and row[0] == date_str and row[1] == target_venue:
                            found_row = idx_r
                            break

                    if found_row != -1:
                        ws.update_cell(found_row, 7, usr_inv)
                        ws.update_cell(found_row, 8, usr_ret)
                        ws.update_cell(found_row, 9, usr_races)
                        ws.update_cell(found_row, 10, usr_hits)
                        st.success(f"✅ {date_str} [{target_venue}] の実戦記録を更新しました！（投資: {usr_inv:,}円 / 払戻: {usr_ret:,}円）")
                    else:
                        new_row = [date_str, target_venue, 0, 0, 0, 0, usr_inv, usr_ret, usr_races, usr_hits]
                        ws.append_row(new_row)
                        st.success(f"✅ {date_str} [{target_venue}] の実戦記録を新規保存しました！（投資: {usr_inv:,}円 / 払戻: {usr_ret:,}円）")

                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"保存エラー: {e}")

# ==========================================
# 💻 画面 7: ターミナル操作マニュアル
# ==========================================
elif menu == "💻 ターミナル操作マニュアル":
    st.markdown('<div class="main-title">💻 ターミナル操作マニュアル</div>', unsafe_allow_html=True)
    st.markdown('<div class="last-update">各枠右上のコピーボタンを押してChromebookのターミナルに貼り付けてください</div>', unsafe_allow_html=True)

    tomorrow_str = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")

    st.markdown(
        """
    <div style="background:#1C2230; border:1px solid #F59E0B; border-radius:12px; padding:1.1rem; margin-bottom:1.5rem;">
        <h4 style="color:#FFFFFF; margin-top:0; display:flex; align-items:center; gap:8px; font-size:1.1rem;">
            <span>🏁</span> 毎日のナイター競馬 運用やることリスト
        </h4>
        <div style="background:#151A24; border:1px solid #262F42; border-radius:10px; padding:0.9rem 1rem; margin-bottom:0.7rem;">
            <div style="display:flex; align-items:center; gap:8px; font-weight:700; color:#FFFFFF; margin-bottom:0.3rem; font-size:0.95rem;">
                <span style="background:#D97706; color:white; font-size:0.7rem; font-weight:700; padding:2px 6px; border-radius:999px;">STEP 1</span> 予想実行 ＆ レジまぐ投稿
            </div>
            <div style="font-size:0.85rem; color:#CBD5E1;">
                当日の朝、または前日夜に下記コマンドを実行 ➔ アプリの「📝 レジまぐ投稿原稿」をコピーして投稿。
            </div>
        </div>
        <div style="background:#151A24; border:1px solid #262F42; border-radius:10px; padding:0.9rem 1rem; margin-bottom:0.7rem;">
            <div style="display:flex; align-items:center; gap:8px; font-weight:700; color:#FFFFFF; margin-bottom:0.3rem; font-size:0.95rem;">
                <span style="background:#D97706; color:white; font-size:0.7rem; font-weight:700; padding:2px 6px; border-radius:999px;">STEP 2</span> ナイター終了後の結果自動回収（夜 21:00以降）
            </div>
            <div style="font-size:0.85rem; color:#CBD5E1;">
                下記 <b>3. 自動結果回収コマンド（result.py）</b> を実行。確定着順・配当がスプレッドシートへ自動保存されます。
            </div>
        </div>
        <div style="background:#151A24; border:1px solid #262F42; border-radius:10px; padding:0.9rem 1rem; margin-bottom:0;">
            <div style="display:flex; align-items:center; gap:8px; font-weight:700; color:#FFFFFF; margin-bottom:0.3rem; font-size:0.95rem;">
                <span style="background:#D97706; color:white; font-size:0.7rem; font-weight:700; padding:2px 6px; border-radius:999px;">STEP 3</span> ダッシュボードで成果確認
            </div>
            <div style="font-size:0.85rem; color:#CBD5E1;">
                <b>「📊 ダッシュボード」</b> で「🔄 データ更新」を押し、会場別の回収率と的中率をチェック！
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div style="background:#151A24; border:1px solid #262F42; border-radius:12px; padding:1.1rem; margin-bottom:1.2rem;">
        <h4 style="color:#FFFFFF; margin-top:0; font-size:1rem;">⚡ 1. 当日（今日）の予想実行 ＆ 原稿生成</h4>
    """,
        unsafe_allow_html=True,
    )
    st.code("~/keiba_env/bin/python ~/nar_system/publish_today.py", language="bash")
    st.caption("※本日のレース全頭をスクレイピング・指数計算し、勝負レースを抽出します")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
    <div style="background:#151A24; border:1px solid #F59E0B; border-left:5px solid #F59E0B; border-radius:12px; padding:1.1rem; margin-bottom:1.2rem;">
        <h4 style="color:#FBBF24; margin-top:0; font-size:1.05rem;">🌙 2. 前日夜に「明日」の予想実行 ＆ 原稿生成（日付8桁指定）</h4>
        <div style="font-size:0.88rem; color:#CBD5E1; margin-bottom:0.8rem; line-height:1.6;">
            前日の夕方〜夜に出馬表が確定した段階で、末尾に明日の日付（8桁）を付けて実行すると、<b>明日のレース判定とレジまぐ原稿を前夜のうちに作成</b>できます。
        </div>
    """,
        unsafe_allow_html=True,
    )
    st.code(f"~/keiba_env/bin/python ~/nar_system/publish_today.py {tomorrow_str}", language="bash")
    st.caption(f"※例: 明日（{tomorrow_str}）の予想を今夜出したい場合は上記コマンドをそのまま実行")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
    <div style="background:#151A24; border:1px solid #262F42; border-radius:12px; padding:1.1rem; margin-bottom:1.2rem;">
        <h4 style="color:#FFFFFF; margin-top:0; font-size:1rem;">🏁 3. 【夜21:00以降】AI自動結果回収 ＆ 日次収支自動集計</h4>
    """,
        unsafe_allow_html=True,
    )
    st.code("~/keiba_env/bin/python ~/nar_system/result.py", language="bash")
    st.caption("※確定着順と配当を自動取得し、「日次収支」シートへAI実績を自動保存します")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
    <div style="background:#151A24; border:1px solid #262F42; border-radius:12px; padding:1.1rem; margin-bottom:1.2rem;">
        <h4 style="color:#FFFFFF; margin-top:0; font-size:1rem;">🏖️ 4. 【週1回推奨】砂の全面入れ替え・コース改修・枠順バイアス異常チェック</h4>
    """,
        unsafe_allow_html=True,
    )
    st.code("~/keiba_env/bin/python ~/nar_system/check_sand_bias.py", language="bash")
    st.caption("※各競馬場公式サイトのニュース告知と直近の枠順バイアス（勝率乖離）を一括診断します")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
    <div style="background:#151A24; border:1px solid #262F42; border-radius:12px; padding:1.1rem; margin-bottom:1.2rem;">
        <h4 style="color:#FFFFFF; margin-top:0; font-size:1rem;">🧹 5. メモリ解放 ＆ 停止コマンド（緊急用）</h4>
    """,
        unsafe_allow_html=True,
    )
    st.code("killall -9 chromium chromium-driver chromedriver chrome 2>/dev/null", language="bash")
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 🗄️ 画面 8: 過去データ分析（S/A/Bランク完全復活＋主力均等版）
# ==========================================
elif menu == "🗄️ 過去データ分析":
    st.markdown('<div class="main-title">オッズ非依存・事前確定ポートフォリオ検証実績（4.5年間）</div>', unsafe_allow_html=True)
    st.markdown('<div class="last-update">出馬表確定時点で100%買い目が決まる全15ゾーン完全制覇バックテスト成績と推奨ランク格付け（1点1,000円換算）</div>', unsafe_allow_html=True)

    # 🌟 ハイブリッド確定実績のハイライトカード
    st.markdown(
        """
    <div style="display:flex; gap:12px; flex-wrap:wrap; margin-bottom:1.2rem;">
        <div style="background:#151A24; border:1px solid #10B981; border-left:5px solid #10B981; border-radius:10px; padding:12px 16px; flex:1; min-width:200px;">
            <span style="color:#34D399; font-weight:800; font-size:0.92rem;">🛡️ レース的中率</span><br>
            <span style="font-size:1.6rem; font-weight:800; color:#FFFFFF;">54.4%</span>
            <span style="font-size:0.8rem; color:#CBD5E1;">（単勝＋ワイドいずれか的中）</span>
        </div>
        <div style="background:#151A24; border:1px solid #F59E0B; border-left:5px solid #F59E0B; border-radius:10px; padding:12px 16px; flex:1; min-width:200px;">
            <span style="color:#FBBF24; font-weight:800; font-size:0.92rem;">🔥 ハイブリッド通算回収率</span><br>
            <span style="font-size:1.6rem; font-weight:800; color:#FFFFFF;">128.3%</span>
            <span style="font-size:0.8rem; color:#CBD5E1;">（単勝1,000円＋ワイド各500円）</span>
        </div>
        <div style="background:#151A24; border:1px solid #10B981; border-left:5px solid #10B981; border-radius:10px; padding:12px 16px; flex:1; min-width:200px;">
            <span style="color:#34D399; font-weight:800; font-size:0.92rem;">💰 トータル純利益</span><br>
            <span style="font-size:1.6rem; font-weight:800; color:#10B981;">+906,850円</span>
            <span style="font-size:0.8rem; color:#CBD5E1;">（4.5年間累積黒字）</span>
        </div>
        <div style="background:#151A24; border:1px solid #38BDF8; border-left:5px solid #38BDF8; border-radius:10px; padding:12px 16px; flex:1; min-width:200px;">
            <span style="color:#38BDF8; font-weight:800; font-size:0.92rem;">⚡ 年間勝負レース数</span><br>
            <span style="font-size:1.6rem; font-weight:800; color:#FFFFFF;">約650鞍</span>
            <span style="font-size:0.8rem; color:#CBD5E1;">（1日平均 2〜3鞍）</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """<div style="display:flex; gap:10px; flex-wrap:wrap; margin-bottom:1rem;">
<div style="background:#151A24; border:1px solid #10B981; border-left:4px solid #10B981; border-radius:8px; padding:8px 14px; flex:1; min-width:180px;">
<span style="color:#34D399; font-weight:800; font-size:0.95rem;">⚡ 主力均等（全場共通）</span><br>
<span style="color:#CBD5E1; font-size:0.8rem;">1日2〜3鞍を安定供給する高頻度ゾーン</span>
</div>
<div style="background:#151A24; border:1px solid #F59E0B; border-left:4px solid #F59E0B; border-radius:8px; padding:8px 14px; flex:1; min-width:180px;">
<span style="color:#FBBF24; font-weight:800; font-size:0.95rem;">👑 Sランク（特注勝負）</span><br>
<span style="color:#CBD5E1; font-size:0.8rem;">単勝回収率 130%超の最優先ゾーン</span>
</div>
<div style="background:#151A24; border:1px solid #10B981; border-left:4px solid #10B981; border-radius:8px; padding:8px 14px; flex:1; min-width:180px;">
<span style="color:#34D399; font-weight:800; font-size:0.95rem;">🔥 Aランク（主力勝負）</span><br>
<span style="color:#CBD5E1; font-size:0.8rem;">単勝回収率 120%前後の高期待値ゾーン</span>
</div>
<div style="background:#151A24; border:1px solid #38BDF8; border-left:4px solid #38BDF8; border-radius:8px; padding:8px 14px; flex:1; min-width:180px;">
<span style="color:#7DD3FC; font-weight:800; font-size:0.95rem;">⚡ Bランク（標準プラス）</span><br>
<span style="color:#CBD5E1; font-size:0.8rem;">単勝回収率 110%〜120%の安定黒字ゾーン</span>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """<div style="overflow-x: auto; border-radius: 8px; border: 1px solid #262F42; margin-top: 0.5rem;">
<table style="width:100%; border-collapse: collapse; color: #F3F4F6; background-color: #151A24; font-size: 0.92rem;">
<thead>
<tr style="background-color: #10141D; color: #FBBF24; border-bottom: 2px solid #262F42; text-align: left;">
<th style="padding: 12px 14px; text-align:center;">ランク</th>
<th style="padding: 12px 14px;">会場・距離区分</th>
<th style="padding: 12px 14px;">事前確定条件（オッズ不問）</th>
<th style="padding: 12px 14px;">単勝回収率</th>
<th style="padding: 12px 14px;">単勝的中率 (複勝率)</th>
<th style="padding: 12px 14px;">純利益 (1,000円/R)</th>
</tr>
</thead>
<tbody>
<tr style="border-bottom: 2px solid #34D399; background: rgba(16,185,129,0.08);">
<td style="padding: 12px 14px; text-align:center;"><span style="background:rgba(16,185,129,0.25); border:1px solid #10B981; color:#34D399; font-weight:800; padding:3px 10px; border-radius:6px; font-size:0.82rem; white-space:nowrap;">⚡ 主力均等</span></td>
<td style="padding: 12px 14px; font-weight:700; color:#34D399;">🌐 全5場共通 (大井/川崎/船橋/浦和/佐賀)</td>
<td style="padding: 12px 14px;">適性1位(CL1) × 先行上位(FL&lt;=2) × 妙味オッズ(2.5〜15倍)</td>
<td style="padding: 12px 14px; font-weight:700; color:#FBBF24;">116.2%</td>
<td style="padding: 12px 14px;">20.7% (複 57.7%)</td>
<td style="padding: 12px 14px; color:#10B981; font-weight:700;">+273,500円 (年381鞍)</td>
</tr>
<tr style="border-bottom: 1px solid #262F42;">
<td style="padding: 12px 14px; text-align:center;"><span style="background:rgba(245,158,11,0.2); border:1px solid #F59E0B; color:#FBBF24; font-weight:800; padding:3px 10px; border-radius:6px; font-size:0.82rem; white-space:nowrap;">👑 Sランク</span></td>
<td style="padding: 12px 14px; font-weight:700;">🌃 大井・短距離 (&lt;=1200m)</td>
<td style="padding: 12px 14px;">印【◯】× RL 1〜2位 × CL 1〜2位 × 中枠(4-5)</td>
<td style="padding: 12px 14px; font-weight:700; color:#FBBF24;">192.6%</td>
<td style="padding: 12px 14px;">30.2% (複 58.1%)</td>
<td style="padding: 12px 14px; color:#10B981; font-weight:700;">+39,800円</td>
</tr>
<tr style="border-bottom: 1px solid #262F42;">
<td style="padding: 12px 14px; text-align:center;"><span style="background:rgba(245,158,11,0.2); border:1px solid #F59E0B; color:#FBBF24; font-weight:800; padding:3px 10px; border-radius:6px; font-size:0.82rem; white-space:nowrap;">👑 Sランク</span></td>
<td style="padding: 12px 14px; font-weight:700;">🌃 大井・中距離 (1300-1600m)</td>
<td style="padding: 12px 14px;">印【◎/◯】× 外枠(6-8) × 適性1位(CL1) × 先行1位(FL1)</td>
<td style="padding: 12px 14px; font-weight:700; color:#FBBF24;">166.1%</td>
<td style="padding: 12px 14px;">32.2% (複 63.3%)</td>
<td style="padding: 12px 14px; color:#10B981; font-weight:700;">+59,500円</td>
</tr>
<tr style="border-bottom: 1px solid #262F42;">
<td style="padding: 12px 14px; text-align:center;"><span style="background:rgba(245,158,11,0.2); border:1px solid #F59E0B; color:#FBBF24; font-weight:800; padding:3px 10px; border-radius:6px; font-size:0.82rem; white-space:nowrap;">👑 Sランク</span></td>
<td style="padding: 12px 14px; font-weight:700;">🌃 大井・長距離 (&gt;=1700m)</td>
<td style="padding: 12px 14px;">印【◯】× 全枠 × RL 1〜3位 × 先行上位(FL&lt;=2)</td>
<td style="padding: 12px 14px; font-weight:700; color:#FBBF24;">169.9%</td>
<td style="padding: 12px 14px;">29.5% (複 59.0%)</td>
<td style="padding: 12px 14px; color:#10B981; font-weight:700;">+54,500円</td>
</tr>
<tr style="border-bottom: 1px solid #262F42;">
<td style="padding: 12px 14px; text-align:center;"><span style="background:rgba(245,158,11,0.2); border:1px solid #F59E0B; color:#FBBF24; font-weight:800; padding:3px 10px; border-radius:6px; font-size:0.82rem; white-space:nowrap;">👑 Sランク</span></td>
<td style="padding: 12px 14px; font-weight:700;">🐎 川崎・短距離 (&lt;=1200m)</td>
<td style="padding: 12px 14px;">印【◎/◯】× 中枠(4-5) × RL 1〜2位 × 先行上位(FL&lt;=2)</td>
<td style="padding: 12px 14px; font-weight:700; color:#FBBF24;">140.8%</td>
<td style="padding: 12px 14px;">33.3% (複 61.7%)</td>
<td style="padding: 12px 14px; color:#10B981; font-weight:700;">+24,500円</td>
</tr>
<tr style="border-bottom: 1px solid #262F42;">
<td style="padding: 12px 14px; text-align:center;"><span style="background:rgba(245,158,11,0.2); border:1px solid #F59E0B; color:#FBBF24; font-weight:800; padding:3px 10px; border-radius:6px; font-size:0.82rem; white-space:nowrap;">👑 Sランク</span></td>
<td style="padding: 12px 14px; font-weight:700;">🐎 川崎・中距離 (1300-1600m)</td>
<td style="padding: 12px 14px;">印【▲】× 全枠 × 実力1位(RL1)</td>
<td style="padding: 12px 14px; font-weight:700; color:#FBBF24;">150.9%</td>
<td style="padding: 12px 14px;">30.7% (複 62.4%)</td>
<td style="padding: 12px 14px; color:#10B981; font-weight:700;">+147,700円</td>
</tr>
<tr style="border-bottom: 1px solid #262F42;">
<td style="padding: 12px 14px; text-align:center;"><span style="background:rgba(245,158,11,0.2); border:1px solid #F59E0B; color:#FBBF24; font-weight:800; padding:3px 10px; border-radius:6px; font-size:0.82rem; white-space:nowrap;">👑 Sランク</span></td>
<td style="padding: 12px 14px; font-weight:700;">🐎 川崎・長距離 (&gt;=1700m)</td>
<td style="padding: 12px 14px;">印【◯】× 全枠 × CL 1〜3位 × 先行上位(FL&lt;=2)</td>
<td style="padding: 12px 14px; font-weight:700; color:#FBBF24;">150.7%</td>
<td style="padding: 12px 14px;">27.6% (複 58.6%)</td>
<td style="padding: 12px 14px; color:#10B981; font-weight:700;">+14,700円</td>
</tr>
<tr style="border-bottom: 1px solid #262F42;">
<td style="padding: 12px 14px; text-align:center;"><span style="background:rgba(16,185,129,0.2); border:1px solid #10B981; color:#34D399; font-weight:800; padding:3px 10px; border-radius:6px; font-size:0.82rem; white-space:nowrap;">🔥 Aランク</span></td>
<td style="padding: 12px 14px; font-weight:700;">⚓ 船橋・短距離 (&lt;=1200m)</td>
<td style="padding: 12px 14px;">印【◎】× 外枠(6-8) × RL&lt;=3 × 適性1位(CL1) × 単騎ハナ(FL1)</td>
<td style="padding: 12px 14px; font-weight:700; color:#FBBF24;">128.8%</td>
<td style="padding: 12px 14px;">33.8% (複 66.2%)</td>
<td style="padding: 12px 14px; color:#10B981; font-weight:700;">+18,700円</td>
</tr>
<tr style="border-bottom: 1px solid #262F42;">
<td style="padding: 12px 14px; text-align:center;"><span style="background:rgba(245,158,11,0.2); border:1px solid #F59E0B; color:#FBBF24; font-weight:800; padding:3px 10px; border-radius:6px; font-size:0.82rem; white-space:nowrap;">👑 Sランク</span></td>
<td style="padding: 12px 14px; font-weight:700;">⚓ 船橋・中距離 (1300-1600m)</td>
<td style="padding: 12px 14px;">印【▲】× 外枠(6-8) × 適性1位(CL1)</td>
<td style="padding: 12px 14px; font-weight:700; color:#FBBF24;">169.8%</td>
<td style="padding: 12px 14px;">23.0% (複 54.0%)</td>
<td style="padding: 12px 14px; color:#10B981; font-weight:700;">+60,700円</td>
</tr>
<tr style="border-bottom: 1px solid #262F42;">
<td style="padding: 12px 14px; text-align:center;"><span style="background:rgba(245,158,11,0.2); border:1px solid #F59E0B; color:#FBBF24; font-weight:800; padding:3px 10px; border-radius:6px; font-size:0.82rem; white-space:nowrap;">👑 Sランク</span></td>
<td style="padding: 12px 14px; font-weight:700;">⚓ 船橋・長距離 (&gt;=1700m)</td>
<td style="padding: 12px 14px;">印【◯/▲】× 全枠 × 適性1位(CL1)</td>
<td style="padding: 12px 14px; font-weight:700; color:#FBBF24;">182.2%</td>
<td style="padding: 12px 14px;">21.7% (複 53.3%)</td>
<td style="padding: 12px 14px; color:#10B981; font-weight:700;">+75,600円</td>
</tr>
<tr style="border-bottom: 1px solid #262F42;">
<td style="padding: 12px 14px; text-align:center;"><span style="background:rgba(16,185,129,0.2); border:1px solid #10B981; color:#34D399; font-weight:800; padding:3px 10px; border-radius:6px; font-size:0.82rem; white-space:nowrap;">🔥 Aランク</span></td>
<td style="padding: 12px 14px; font-weight:700;">🌸 浦和・短距離 (&lt;=1200m)</td>
<td style="padding: 12px 14px;">印【◯】× 外枠(6-8) × CL 1〜3位</td>
<td style="padding: 12px 14px; font-weight:700; color:#FBBF24;">122.5%</td>
<td style="padding: 12px 14px;">22.9% (複 58.8%)</td>
<td style="padding: 12px 14px; color:#10B981; font-weight:700;">+55,200円</td>
</tr>
<tr style="border-bottom: 1px solid #262F42;">
<td style="padding: 12px 14px; text-align:center;"><span style="background:rgba(245,158,11,0.2); border:1px solid #F59E0B; color:#FBBF24; font-weight:800; padding:3px 10px; border-radius:6px; font-size:0.82rem; white-space:nowrap;">👑 Sランク</span></td>
<td style="padding: 12px 14px; font-weight:700;">🌸 浦和・中距離 (1300-1600m)</td>
<td style="padding: 12px 14px;">印【▲】× 外枠(6-8) × 適性1位(CL1)</td>
<td style="padding: 12px 14px; font-weight:700; color:#FBBF24;">189.2%</td>
<td style="padding: 12px 14px;">20.3% (複 55.7%)</td>
<td style="padding: 12px 14px; color:#10B981; font-weight:700;">+171,200円</td>
</tr>
<tr style="border-bottom: 1px solid #262F42;">
<td style="padding: 12px 14px; text-align:center;"><span style="background:rgba(245,158,11,0.2); border:1px solid #F59E0B; color:#FBBF24; font-weight:800; padding:3px 10px; border-radius:6px; font-size:0.82rem; white-space:nowrap;">👑 Sランク</span></td>
<td style="padding: 12px 14px; font-weight:700;">🌸 浦和・長距離 (&gt;=1700m)</td>
<td style="padding: 12px 14px;">印【◯】× 外枠(6-8) × 適性1位(CL1)</td>
<td style="padding: 12px 14px; font-weight:700; color:#FBBF24;">177.8%</td>
<td style="padding: 12px 14px;">30.4% (複 63.0%)</td>
<td style="padding: 12px 14px; color:#10B981; font-weight:700;">+35,800円</td>
</tr>
<tr style="border-bottom: 1px solid #262F42;">
<td style="padding: 12px 14px; text-align:center;"><span style="background:rgba(245,158,11,0.2); border:1px solid #F59E0B; color:#FBBF24; font-weight:800; padding:3px 10px; border-radius:6px; font-size:0.82rem; white-space:nowrap;">👑 Sランク</span></td>
<td style="padding: 12px 14px; font-weight:700;">🔥 佐賀・短距離 (&lt;=1200m)</td>
<td style="padding: 12px 14px;">印【◯/▲】× 全枠 × RL 1〜3位 × 適性1位(CL1)</td>
<td style="padding: 12px 14px; font-weight:700; color:#FBBF24;">145.5%</td>
<td style="padding: 12px 14px;">36.4% (複 68.2%)</td>
<td style="padding: 12px 14px; color:#10B981; font-weight:700;">+10,000円</td>
</tr>
<tr style="border-bottom: 1px solid #262F42;">
<td style="padding: 12px 14px; text-align:center;"><span style="background:rgba(6,182,212,0.15); border:1px solid #06B6D4; color:#38BDF8; font-weight:800; padding:3px 10px; border-radius:6px; font-size:0.82rem; white-space:nowrap;">⚡ Bランク</span></td>
<td style="padding: 12px 14px; font-weight:700;">🔥 佐賀・中距離 (1300-1600m)</td>
<td style="padding: 12px 14px;">印【◯/▲】× 外枠(6-8) × RL 1〜2位 × 適性1位(CL1)</td>
<td style="padding: 12px 14px; font-weight:700; color:#FBBF24;">119.3%</td>
<td style="padding: 12px 14px;">33.8% (複 67.2%)</td>
<td style="padding: 12px 14px; color:#10B981; font-weight:700;">+38,700円</td>
</tr>
<tr style="border-bottom: 2px solid #334155;">
<td style="padding: 12px 14px; text-align:center;"><span style="background:rgba(245,158,11,0.2); border:1px solid #F59E0B; color:#FBBF24; font-weight:800; padding:3px 10px; border-radius:6px; font-size:0.82rem; white-space:nowrap;">👑 Sランク</span></td>
<td style="padding: 12px 14px; font-weight:700;">🔥 佐賀・長距離 (&gt;=1700m)</td>
<td style="padding: 12px 14px;">印【◯/▲】× 全枠 × 適性1位(CL1)</td>
<td style="padding: 12px 14px; font-weight:700; color:#FBBF24;">200.3%</td>
<td style="padding: 12px 14px;">22.6% (複 56.5%)</td>
<td style="padding: 12px 14px; color:#10B981; font-weight:700;">+124,400円</td>
</tr>
<tr style="background-color: #10141D; font-weight:800;">
<td style="padding: 14px; text-align:center; color:#F59E0B;">ALL</td>
<td style="padding: 14px;">🌐 統合ポートフォリオ (重複集約)</td>
<td style="padding: 14px;">特注ゾーン優先 ＋ 全場均等ゾーン（1レース1頭厳選）</td>
<td style="padding: 14px; color:#F59E0B; font-size:1.1rem;">128.3% (ハイブリッド)</td>
<td style="padding: 14px;">54.4% (レース的中率)</td>
<td style="padding: 14px; color:#10B981; font-size:1.1rem;">+906,850円 (年約650鞍)</td>
</tr>
</tbody>
</table>
</div>""",
        unsafe_allow_html=True,
    )

# ==========================================
# 📈 画面 9: スプレッドシート連携
# ==========================================
elif menu == "📈 スプレッドシート連携":
    st.markdown('<div class="main-title">Google スプレッドシート連携ステータス</div>', unsafe_allow_html=True)
    gc = get_gspread_client()
    if gc:
        st.success(f"🔐 連携成功: 「{SS_NAME}」と正常に同期しています。")
        if not df_today_latest.empty:
            st.write(f"▼ 最新取得データ（{latest_date_str}・全{len(df_today_latest)}頭）")
            st.dataframe(df_today_latest, use_container_width=True, hide_index=True)
    else:
        st.error("🚨 スプレッドシートに接続できませんでした。")
