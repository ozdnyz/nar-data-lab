from datetime import datetime
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
# 🎨 カスタムCSS（アンバーゴールド基調・実戦運用仕様）
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

    /* 🌟 ラジオボタン */
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

    /* 🌟 タブデザイン */
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
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #151A24 !important;
        border: 1px solid #2D3548 !important;
        border-radius: 8px !important;
        color: #F3F4F6 !important;
        padding: 5px 12px !important;
        font-size: 0.85rem !important;
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
    .stTabs [data-baseweb="tab-panel"] {
        padding: 0px !important;
        margin: 0px !important;
    }

    .right-card-header {
        height: 38px !important;
        min-height: 38px !important;
        margin-bottom: 8px !important;
        display: flex !important;
        align-items: center !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        padding: 0 4px !important;
    }

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
        width: 36px;
        height: 36px;
        background: #D97706;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        color: white;
    }
    .user-info { display: flex; flex-direction: column; }
    .user-name { font-size: 0.85rem; font-weight: 600; color: #F8FAFC; }
    .user-status { font-size: 0.75rem; color: #F59E0B; display: flex; align-items: center; gap: 4px; }

    .main-title {
        font-size: 1.85rem;
        font-weight: 700;
        color: #FFFFFF !important;
        margin-bottom: 4px;
        line-height: 1.25;
    }
    .last-update { font-size: 0.85rem; color: #94A3B8; margin-bottom: 1rem; }

    button[kind="secondary"], button[kind="primary"], [data-testid="stButton"] button {
        background-color: #1A202C !important;
        color: #E2E8F0 !important;
        border: 1px solid #2D3748 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    [data-testid="stButton"] button p { color: #E2E8F0 !important; }
    [data-testid="stButton"] button:hover {
        background-color: #292012 !important;
        border-color: #F59E0B !important;
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

    .stForm [data-testid="stFormSubmitButton"] button, [data-testid="stFormSubmitButton"] button, button[kind="formSubmit"] {
        background-color: #D97706 !important;
        border: 1px solid #F59E0B !important;
        border-radius: 8px !important;
        padding: 0.65rem 1.6rem !important;
        font-weight: 700 !important;
        min-height: 48px !important;
        box-shadow: 0 4px 14px rgba(217, 119, 6, 0.4) !important;
        width: 100% !important;
    }
    .stForm [data-testid="stFormSubmitButton"] button * { color: #FFFFFF !important; font-weight: 700 !important; font-size: 1.05rem !important; }

    [data-testid="stForm"] {
        background-color: #151A24 !important;
        border: 1px solid #262F42 !important;
        border-radius: 12px !important;
        padding: 1.4rem !important;
    }

    /* 🌟 リッチKPIカード */
    .kpi-rich-card {
        background: #151A24 !important;
        border: 1px solid #262F42 !important;
        border-radius: 14px !important;
        padding: 1.1rem 1.25rem !important;
        margin-bottom: 0.8rem !important;
        height: 165px !important;
        min-height: 165px !important;
        max-height: 165px !important;
        box-sizing: border-box !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
    }
    .kpi-bar-amber  { border-left: 4px solid #F59E0B !important; }
    .kpi-bar-green  { border-left: 4px solid #10B981 !important; }

    .kpi-rich-title {
        font-size: 0.88rem;
        color: #E2E8F0;
        font-weight: 700;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .kpi-main-metrics {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        margin-bottom: 0.6rem;
        border-bottom: 1px solid #262F42;
        padding-bottom: 0.5rem;
        flex-wrap: wrap;
        gap: 8px;
    }
    .kpi-big-val { font-size: 1.95rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.5px; }
    .kpi-sub-rate { font-size: 1rem; color: #CBD5E1; font-weight: 700; }
    .kpi-money-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.86rem;
        color: #CBD5E1;
        flex-wrap: wrap;
        gap: 4px;
    }
    .kpi-profit-pos { color: #10B981; font-weight: 700; }
    .kpi-profit-neg { color: #EF4444; font-weight: 700; }

    .race-card {
        background: #151A24;
        border: 1px solid #262F42;
        border-radius: 12px;
        padding: 1.1rem;
        margin-bottom: 1rem;
    }
    .race-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #262F42;
        padding-bottom: 0.5rem;
        margin-bottom: 0.8rem;
        flex-wrap: wrap;
        gap: 6px;
    }
    .race-name { font-size: 1.05rem; font-weight: 700; color: #FFFFFF; }
    .race-badge {
        background-color: #292012;
        color: #FBBF24;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 4px;
        border: 1px solid #F59E0B;
    }

    .status-badge-buy {
        background: rgba(245, 158, 11, 0.15);
        border: 1px solid #F59E0B;
        color: #FBBF24;
        font-size: 0.88rem;
        font-weight: 700;
        padding: 6px 12px;
        border-radius: 6px;
        display: inline-block;
        margin-bottom: 10px;
    }
    .status-badge-skip {
        background: rgba(148, 163, 184, 0.12);
        border: 1px solid #475569;
        color: #CBD5E1;
        font-size: 0.88rem;
        font-weight: 600;
        padding: 6px 12px;
        border-radius: 6px;
        display: inline-block;
        margin-bottom: 10px;
    }

    @media screen and (max-width: 768px) {
        .main-title { font-size: 1.35rem !important; margin-bottom: 2px !important; }
        .last-update { font-size: 0.75rem !important; margin-bottom: 0.8rem !important; }
        .kpi-big-val { font-size: 1.5rem !important; }
        .sidebar-user { position: relative !important; bottom: auto !important; left: auto !important; width: 100% !important; margin-top: 2rem !important; }
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 🔐 スプレッドシート接続処理（PEM秘密鍵改行自動修復）
# ==========================================
SS_NAME = "地方競馬AI予想管理"


@st.cache_resource
def get_gspread_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    try:
        creds_dict = None
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
        elif "gcp_json" in st.secrets:
            creds_dict = json.loads(st.secrets["gcp_json"])

        if creds_dict:
            # 🌟 秘密鍵のバックスラッシュ・改行エスケープ（symbol 92）を安全に自動修復
            if "private_key" in creds_dict:
                pk = str(creds_dict["private_key"]).strip().strip('"').strip("'")
                pk = pk.replace("\\n", "\n")
                creds_dict["private_key"] = pk
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            return gspread.authorize(creds)

        # ローカル実行時のフォールバック
        for p in [
            "key.json",
            os.path.expanduser("~/nar_system/key.json"),
            os.path.expanduser("~/key.json"),
        ]:
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
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    try:
        ss = gc.open(SS_NAME)

        # 1. 当日予想シート
        df_today = pd.DataFrame()
        try:
            ws_today = ss.worksheet("当日予想")
            vals = ws_today.get_all_values()
            if vals and len(vals) > 1:
                df_today = pd.DataFrame(vals[1:], columns=vals[0])
        except Exception:
            pass

        # 2. 日次収支シート
        df_daily = pd.DataFrame()
        try:
            ws_daily = ss.worksheet("日次収支")
            vals_d = ws_daily.get_all_values()
            if vals_d and len(vals_d) > 1:
                df_daily = pd.DataFrame(vals_d[1:], columns=vals_d[0])
        except Exception:
            pass

        # 3. Jpn予想シート（ダートグレード用仮枠）
        df_jpn = pd.DataFrame()
        try:
            ws_jpn = ss.worksheet("Jpn予想")
            vals_j = ws_jpn.get_all_values()
            if vals_j and len(vals_j) > 1:
                df_jpn = pd.DataFrame(vals_j[1:], columns=vals_j[0])
        except Exception:
            pass

        return df_today, df_daily, df_jpn
    except Exception:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


df_today, df_daily_log, df_jpn = load_sheet_data()


def extract_selected_picks(df_src):
    """当日予想シートから事前確定ルール合致馬（1レース1頭厳選）を抽出"""
    if df_src is None or df_src.empty:
        return pd.DataFrame()

    rule_col = (
        "事前確定判定"
        if "事前確定判定" in df_src.columns
        else ("黄金ルール詳細" if "黄金ルール詳細" in df_src.columns else "")
    )
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


# ==========================================
# 🌟 運用サイクルのポップアップダイアログ
# ==========================================
@st.dialog("🔄 地方競馬AI (NAR Data-Lab) 運用サイクル")
def show_flow_modal():
    st.markdown(
        """
    <div style="font-size:1rem; color:#FFFFFF; font-weight:700; margin-bottom:14px;">
        直前オッズに依存しない「完全事前確定型」のスマート運用フローです。
    </div>
    <div style="background:#151A24; border:1px solid #2D3548; border-left:5px solid #F59E0B; border-radius:10px; padding:14px 16px; margin-bottom:12px;">
        <div style="font-size:1.05rem; font-weight:700; color:#FFFFFF; margin-bottom:8px;">🌅 1. 【前日夜 or 朝】 事前確定予想 ＆ 原稿出力（publish_today.py）</div>
        <div style="font-size:0.9rem; color:#F3F4F6; line-height:1.7;">
            <span style="color:#FBBF24; font-weight:700;">・処理</span>: 出馬表から地力・適性・枠順バイアスを解析し、黒字ゾーン合致馬を抽出<br>
            <span style="color:#FBBF24; font-weight:700;">・配信</span>: 左メニュー「📝 レジまぐ投稿原稿」からタイトルと本文をコピーして投稿<br>
            <span style="color:#FBBF24; font-weight:700;">・投票</span>: オッズ不問のため、朝の段階でPAT事前投票が完了
        </div>
    </div>
    <div style="background:#151A24; border:1px solid #2D3548; border-left:5px solid #10B981; border-radius:10px; padding:14px 16px; margin-bottom:12px;">
        <div style="font-size:1.05rem; font-weight:700; color:#FFFFFF; margin-bottom:8px;">🌙 2. 【レース終了後】 実戦収支記録</div>
        <div style="font-size:0.9rem; color:#F3F4F6; line-height:1.7;">
            <span style="color:#34D399; font-weight:700;">・操作</span>: 左メニュー「💰 収支入力・管理」から開催会場・購入額・払戻額を保存<br>
            <span style="color:#34D399; font-weight:700;">・集計</span>: ダッシュボードの「会場別タブ」に自動で実戦実績が蓄積されます
        </div>
    </div>
    <div style="background:#151A24; border:1px solid #2D3548; border-left:5px solid #06B6D4; border-radius:10px; padding:14px 16px;">
        <div style="font-size:1.05rem; font-weight:700; color:#FFFFFF; margin-bottom:8px;">🔍 3. 【週1回】 砂の入れ替え・枠順バイアス点検</div>
        <div style="font-size:0.9rem; color:#F3F4F6; line-height:1.7;">
            <span style="color:#38BDF8; font-weight:700;">・処理</span>: マニュアル内の「砂入れ替え＆バイアス監視コマンド」を実行<br>
            <span style="color:#38BDF8; font-weight:700;">・目的</span>: 白砂への入れ替えやクッション砂厚変更によるバイアス急変を早期検知
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
            <div class="user-status">● 実戦運用モード</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

# 最新日のデータ抽出
latest_date_str = ""
df_today_latest = pd.DataFrame()
df_picks_latest = pd.DataFrame()

if df_today is not None and not df_today.empty and "日付" in df_today.columns:
    latest_date_str = df_today["日付"].max()
    df_today_latest = df_today[df_today["日付"] == latest_date_str].copy()
    df_picks_latest = extract_selected_picks(df_today_latest)

# ==========================================
# 🚀 画面 1: 📊 ダッシュボード（デモ完全削除・実戦連動）
# ==========================================
if menu == "📊 ダッシュボード":
    col_h_left, col_h_right = st.columns([7, 3])
    now_str = datetime.now().strftime("%Y年%m月%d日 %H:%M")

    with col_h_left:
        st.markdown(
            f"""
            <div class="main-title">地方競馬 実戦収支ダッシュボード</div>
            <div class="last-update">最終更新: {now_str} (日次収支シート完全同期)</div>
            """,
            unsafe_allow_html=True,
        )

    with col_h_right:
        c_space, c_help, c_btn = st.columns([1.5, 1, 2.5])
        with c_help:
            if st.button("❓", key="help_modal_btn", help="運用サイクルを確認"):
                show_flow_modal()
        with c_btn:
            if st.button("🔄 データ更新", key="refresh_btn"):
                st.cache_data.clear()
                st.rerun()

    # 実戦収支の集計（デモデータは完全排除し、日次収支シートのみから計算）
    df_daily_calc = pd.DataFrame()
    if df_daily_log is not None and not df_daily_log.empty:
        df_daily_calc = df_daily_log.copy()
        for col in df_daily_calc.columns:
            if any(k in col for k in ["投資", "回収", "払戻", "レース", "的中"]):
                df_daily_calc[col] = pd.to_numeric(
                    df_daily_calc[col].astype(str).str.replace(",", ""), errors="coerce"
                ).fillna(0)

    def get_real_venue_stats(venue_name):
        """スプレッドシート『日次収支』の実戦記録のみを集計"""
        if df_daily_calc.empty:
            return 0.0, 0.0, 0, 0, 0, 0, False

        sub = df_daily_calc
        if venue_name != "総合" and "会場" in df_daily_calc.columns:
            sub = df_daily_calc[df_daily_calc["会場"].astype(str).str.contains(venue_name, na=False)]

        inv_col = "ユーザー投資額" if "ユーザー投資額" in sub.columns else ("投資額" if "投資額" in sub.columns else "")
        ret_col = "ユーザー回収額" if "ユーザー回収額" in sub.columns else ("払戻額" if "払戻額" in sub.columns else "")
        rc_col = "ユーザーレース数" if "ユーザーレース数" in sub.columns else ("レース数" if "レース数" in sub.columns else "")
        ht_col = "ユーザー的中数" if "ユーザー的中数" in sub.columns else ("的中数" if "的中数" in sub.columns else "")

        inv = int(sub[inv_col].sum()) if inv_col else 0
        ret = int(sub[ret_col].sum()) if ret_col else 0
        races = int(sub[rc_col].sum()) if rc_col else 0
        hits = int(sub[ht_col].sum()) if ht_col else 0

        if inv > 0 and races > 0:
            roi = round(ret / inv * 100, 1)
            hit_r = round(hits / races * 100, 1)
            return roi, hit_r, hits, races, inv, ret, True
        return 0.0, 0.0, 0, 0, 0, 0, False

    venue_list = ["総合", "大井", "川崎", "船橋", "浦和", "佐賀"]
    v_tabs = st.tabs([f"📍 {v}" for v in venue_list])

    for idx_v, v_name in enumerate(venue_list):
        with v_tabs[idx_v]:
            u_roi, u_hit, u_hits, u_races, u_inv, u_ret, is_real = get_real_venue_stats(v_name)
            c1, c2 = st.columns(2)

            with c1:
                if is_real:
                    u_prof = u_ret - u_inv
                    u_p_class = "kpi-profit-pos" if u_prof >= 0 else "kpi-profit-neg"
                    u_p_sign = "+" if u_prof > 0 else ""
                    st.markdown(
                        f"""
                        <div class="kpi-rich-card kpi-bar-amber">
                            <div class="kpi-rich-title">👤 実戦通算収支【{v_name}】 <span style="color:#F59E0B; font-weight:600;">(日次収支連動)</span></div>
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
                                <span class="{u_p_class}">損益: {u_p_sign}{u_prof:,}円</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="kpi-rich-card kpi-bar-amber">
                            <div class="kpi-rich-title">👤 実戦通算収支【{v_name}】 <span style="color:#94A3B8; font-weight:600;">(未入力)</span></div>
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
                                <span style="color:#94A3B8;">0 レース</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            with c2:
                # 的中・未的中カウントカード
                misses = u_races - u_hits if is_real else 0
                st.markdown(
                    f"""
                    <div class="kpi-rich-card kpi-bar-green">
                        <div class="kpi-rich-title">🎯 的中内訳【{v_name}】</div>
                        <div class="kpi-main-metrics">
                            <div>
                                <span style="font-size:0.8rem; color:#CBD5E1;">総購入レース数</span><br>
                                <span class="kpi-big-val">{u_races}</span><span style="font-size:1.1rem; color:#CBD5E1;">鞍</span>
                            </div>
                            <div style="text-align:right;">
                                <span style="font-size:0.8rem; color:#CBD5E1;">的中 / 不的中</span><br>
                                <span class="kpi-sub-rate" style="color:#10B981;">{u_hits}的中</span> <span style="font-size:0.85rem; color:#94A3B8;">/ {misses}不的中</span>
                            </div>
                        </div>
                        <div class="kpi-money-row">
                            <span>1R平均投資: <b>{int(u_inv / u_races):,}円</b></span>
                            <span style="color:#38BDF8;">1点1,000円推奨</span>
                        </div>
                    </div>
                    """ if is_real else f"""
                    <div class="kpi-rich-card kpi-bar-green">
                        <div class="kpi-rich-title">🎯 的中内訳【{v_name}】</div>
                        <div class="kpi-main-metrics">
                            <div>
                                <span style="font-size:0.8rem; color:#CBD5E1;">総購入レース数</span><br>
                                <span class="kpi-big-val">0</span><span style="font-size:1.1rem; color:#CBD5E1;">鞍</span>
                            </div>
                            <div style="text-align:right;">
                                <span style="font-size:0.8rem; color:#CBD5E1;">的中 / 不的中</span><br>
                                <span class="kpi-sub-rate">-</span>
                            </div>
                        </div>
                        <div class="kpi-money-row">
                            <span>レース後の結果入力を待機中</span>
                            <span style="color:#94A3B8;">未記録</span>
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
    today_investment = today_target_count * 1000

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
                <div style="font-size:0.82rem; color:#CBD5E1;">💸 本日推奨投資額 (単勝1点1,000円換算)</div>
                <div style="font-size:1.4rem; font-weight:700; color:#FBBF24;">{today_investment:,} <span style="font-size:0.85rem; color:#94A3B8; font-weight:400;">円</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # 実戦回収率の推移グラフ（実データがある場合のみプロット、デモデータは完全排除）
    st.markdown(
        '<div style="font-size:1.1rem; font-weight:700; color:#FFFFFF; margin-bottom:8px;">📈 実戦 累積回収率推移</div>',
        unsafe_allow_html=True,
    )

    has_plot_data = False
    if not df_daily_calc.empty and "日付" in df_daily_calc.columns:
        df_p = df_daily_calc.copy()
        inv_col = "ユーザー投資額" if "ユーザー投資額" in df_p.columns else ("投資額" if "投資額" in df_p.columns else "")
        ret_col = "ユーザー回収額" if "ユーザー回収額" in df_p.columns else ("払戻額" if "払戻額" in df_p.columns else "")
        if inv_col and ret_col and df_p[inv_col].sum() > 0:
            df_p["cum_i"] = df_p[inv_col].cumsum()
            df_p["cum_r"] = df_p[ret_col].cumsum()
            df_p["cum_roi"] = (df_p["cum_r"] / df_p["cum_i"]) * 100

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=df_p["日付"].tolist(),
                    y=df_p["cum_roi"].tolist(),
                    mode="lines+markers",
                    name="実戦通算回収率",
                    line=dict(color="#F59E0B", width=2.5),
                    marker=dict(size=7, color="#F59E0B"),
                    hovertemplate="%{x}<br>累積回収率: %{y:.1f}%<extra></extra>",
                )
            )
            fig.add_hline(
                y=100,
                line_dash="dash",
                line_color="#94A3B8",
                annotation_text="損益分岐点 (100%)",
                annotation_position="bottom right",
            )
            fig.update_layout(
                height=280,
                margin=dict(l=10, r=10, t=15, b=10),
                paper_bgcolor="#151A24",
                plot_bgcolor="#151A24",
                font=dict(color="#CBD5E1", size=11),
                yaxis=dict(ticksuffix="%", gridcolor="#262F42"),
                xaxis=dict(gridcolor="#262F42"),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            has_plot_data = True

    if not has_plot_data:
        st.markdown(
            """
            <div style="background:#151A24; border:1px dashed #2D3548; border-radius:10px; padding:2.5rem 1rem; text-align:center;">
                <div style="font-size:1.05rem; color:#FBBF24; font-weight:700; margin-bottom:6px;">📊 実戦収支データが未登録です</div>
                <div style="font-size:0.85rem; color:#94A3B8;">
                    レース終了後、左メニュー「💰 収支入力・管理」から今日の購入額・払戻額を保存すると、ここに累積回収率の推移グラフが自動描画されます。
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ==========================================
# 🎯 画面 2: 厳選勝負レース
# ==========================================
elif menu == "🎯 厳選勝負レース":
    st.markdown(
        f'<div class="main-title">本日の厳選勝負レース ({latest_date_str or "最新"})</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="last-update">スプレッドシート「当日予想」から事前確定ルール合致馬を自動抽出（オッズ不問・単勝1点勝負）</div>',
        unsafe_allow_html=True,
    )

    if not df_picks_latest.empty:
        for _, row in df_picks_latest.iterrows():
            rule_txt = row.get("事前確定判定", row.get("黄金ルール詳細", ""))
            mark_txt = row.get("評価", row.get("印", ""))
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
                    <div style="background:#1C2230; padding:10px 14px; border-radius:8px; border-left:4px solid #F59E0B;">
                        <div style="font-size:0.9rem; color:#E2E8F0;">
                            📊 <b>指数順位</b>: 地力値 <b>{row['RL']}位</b> ／ コース適性 <b>{row['CL']}位</b> （総合スコア: {row['AIスコア']}）<br>
                            🏆 <b>採用根拠</b>: <span style="color:#34D399; font-weight:700;">{rule_txt}</span><br>
                            🎫 <b>推奨買い目</b>: <b>単勝 {row['馬番']}番</b> （※手堅く運用する場合は単複併用）
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("現在、事前確定ルールに合致する勝負レースはありません（または `publish_today.py` 未実行です）。")

# ==========================================
# 📝 画面 3: レジまぐ投稿原稿（タイトル・本文分離コピー）
# ==========================================
elif menu == "📝 レジまぐ投稿原稿":
    st.markdown(
        '<div class="main-title">📝 レジまぐ投稿用 原稿ジェネレーター</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="last-update">各枠の右上にある「コピーアイコン」を押すだけで、タイトル・無料枠・有料枠へそのまま貼り付けられます</div>',
        unsafe_allow_html=True,
    )

    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        style_opt = st.radio(
            "タイトル表現",
            ["標準（計○鞍）", "厳選強調（渾身の○鞍勝負）"],
            horizontal=True,
        )
    with col_opt2:
        ticket_opt = st.radio(
            "推奨券種の表記",
            ["単勝（複勝併用可）", "単勝1点勝負"],
            horizontal=True,
        )

    n_picks = len(df_picks_latest)
    dt_disp = latest_date_str if latest_date_str else datetime.now().strftime("%Y/%m/%d")

    if not df_picks_latest.empty and "会場" in df_picks_latest.columns:
        venues_str = "・".join(df_picks_latest["会場"].unique())
    else:
        venues_str = "南関・佐賀"

    # 1. タイトル生成
    if "渾身" in style_opt:
        title_text = f"【{venues_str}】データマイニング厳選馬券レポート（{dt_disp}・渾身の{n_picks}鞍勝負）"
    else:
        title_text = f"【{venues_str}】データマイニング厳選馬券レポート（{dt_disp}・計{n_picks}鞍）"

    # 2. 無料エリア本文生成
    race_list_lines = []
    if not df_picks_latest.empty:
        for _, r in df_picks_latest.iterrows():
            race_list_lines.append(
                f"・[{r['会場']}] {r['R']} ({r.get('発走時刻', '')}発走 / ダ{r['距離']}) {r['レース名']}"
            )
    else:
        race_list_lines.append("・本日は基準に合致する厳選レースはありません（見送り）。")

    race_list_str = "\n".join(race_list_lines)

    free_body_text = f"""南関東4場（大井・川崎・船橋・浦和）および佐賀競馬の統計解析レポートです。

出馬表確定時点における枠順バイアス・コース砂質・ラップ適性を数値化し、過去4年半のバックテスト（単勝的中率25.6%・複勝率57.3%・回収率100%超）に裏付けられた統計的優位性の高いレースのみを抽出しています。

◆ 本日の公開対象レース（計{n_picks}鞍）
{race_list_str}

◆ 運用ポリシー
・地力指数と砂・コース適性を融合した多面的スクリーニング
・オッズの直前変動に振り回されない「事前確定型」の低ドローダウン運用
・推奨馬のオッズが何倍であっても機械的に購入することで長期的な確率収束を図る設計

※勝馬投票券の購入は余剰資金の範囲内で自己責任にてお願いいたします。"""

    # 3. 有料エリア本文生成
    paid_lines = [f"本日の厳選勝負レース・買い目一覧です（計{n_picks}鞍）。\n"]
    if not df_picks_latest.empty:
        for _, p in df_picks_latest.iterrows():
            rule_txt = p.get("事前確定判定", p.get("黄金ルール詳細", ""))
            mark_txt = p.get("評価", p.get("印", ""))
            t_str = (
                f"単勝 {p['馬番']}番（※手堅くいく場合は複勝併用推奨）"
                if "併用" in ticket_opt
                else f"単勝 {p['馬番']}番（1点勝負）"
            )
            paid_lines.append(
                f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 【{p['会場']} {p['R']}】 ({p.get('発走時刻', '')}発走 / ダ{p['距離']}) {p['レース名']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
■ 推奨馬 : {mark_txt} 【{p['馬番']}番 {p['馬名']}】 ({p['枠番']}枠 / 騎手:{p.get('騎手', '-')})
■ 指数順位: 地力値 {p['RL']}位 ／ コース適性 {p['CL']}位
■ 採用根拠: {rule_txt}
■ 推奨馬券: {t_str}
"""
            )
    else:
        paid_lines.append("本日は基準を満たす勝負レースがありませんでした。")
    paid_lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    paid_body_text = "\n".join(paid_lines)

    st.markdown("#### ① 記事タイトル（右上のボタンでコピー）")
    st.code(title_text, language="text")

    st.markdown("#### ② 無料エリア本文（右上のボタンでコピー）")
    st.code(free_body_text, language="text")

    st.markdown("#### ③ 有料エリア本文（右上のボタンでコピー）")
    st.code(paid_body_text, language="text")

# ==========================================
# 👑 画面 4: Jpn重賞専用予想（Jpn1/Jpn2/Jpn3 仮枠）
# ==========================================
elif menu == "👑 Jpn重賞専用予想":
    st.markdown(
        '<div class="main-title">👑 ダートグレード競走（Jpn1・Jpn2・Jpn3）専用予想</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="last-update">JRA勢×地方代表馬が激突する交流重賞（Jpn1/Jpn2/Jpn3）の専用解析枠です</div>',
        unsafe_allow_html=True,
    )

    c_jpn1, c_jpn2 = st.columns(2)
    with c_jpn1:
        sel_grade = st.radio(
            "対象グレード選択",
            ["🏆 全て", "👑 Jpn1", "🥈 Jpn2", "🥉 Jpn3"],
            horizontal=True,
        )
    with c_jpn2:
        sel_baba_jpn = st.radio(
            "馬場状態シミュレーション",
            ["☀️ 良", "⛅ 稍重", "☂️ 重", "🌀 不良"],
            horizontal=True,
        )

    if df_jpn is not None and not df_jpn.empty:
        st.dataframe(df_jpn, use_container_width=True, hide_index=True)
    else:
        st.markdown(
            """
            <div class="race-card" style="border: 1px dashed #F59E0B; margin-top: 1rem;">
                <div class="race-header">
                    <span class="race-name" style="color:#FBBF24;">🚧 ダートグレード（Jpn1 / Jpn2 / Jpn3）専用ロジック 準備中枠</span>
                    <span class="race-badge">Jpn Special</span>
                </div>
                <div style="font-size:0.92rem; color:#CBD5E1; line-height:1.7;">
                    ・スプレッドシートに「<b>Jpn予想</b>」シートが追加されると、自動的にこの画面へJpn1〜Jpn3の専用買い目が表示されます。<br>
                    ・交流重賞特有の「JRA所属馬の地方深い砂への適性」「地方所属馬の食い込み条件（内枠・先行バイアス）」を今後ここへ統合可能です。
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ==========================================
# 🏇 画面 5: 全レース出馬表
# ==========================================
elif menu == "🏇 全レース出馬表":
    st.markdown(
        f'<div class="main-title">全レース出馬表 ＆ 指数一覧 ({latest_date_str or "最新"})</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="last-update">各レースのRL（地力順位）・CL（適性順位）・評価印・事前確定判定を確認できます</div>',
        unsafe_allow_html=True,
    )

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
                    has_hit = (
                        rule_col in sub_df.columns
                        and (sub_df[rule_col].astype(str).str.strip() != "").any()
                    )
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

                        disp_cols = [
                            c
                            for c in ["枠番", "馬番", "評価", "馬名", "騎手", "RL", "CL", "AIスコア", rule_col]
                            if c in sub_df.columns
                        ]
                        st.dataframe(sub_df[disp_cols], use_container_width=True, hide_index=True)
    else:
        st.info("スプレッドシート「当日予想」にデータがありません。")

# ==========================================
# 💰 画面 6: 収支入力・管理（会場別選択対応）
# ==========================================
elif menu == "💰 収支入力・管理":
    st.markdown(
        '<div class="main-title">日次・会場別 実収支の記録</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="last-update">会場を選んで保存すると、ダッシュボードの会場別タブに自動反映されます</div>',
        unsafe_allow_html=True,
    )

    with st.form("shushi_form"):
        c_top1, c_top2 = st.columns(2)
        with c_top1:
            st.markdown('<div style="font-size:0.9rem; font-weight:700; color:#FFFFFF; margin-bottom:4px;">🗓️ 開催日</div>', unsafe_allow_html=True)
            target_date = st.date_input("開催日", datetime.now(), label_visibility="collapsed")
        with c_top2:
            st.markdown('<div style="font-size:0.9rem; font-weight:700; color:#FFFFFF; margin-bottom:4px;">🏟️ 対象会場</div>', unsafe_allow_html=True)
            target_venue = st.selectbox("対象会場", ["大井", "川崎", "船橋", "浦和", "佐賀", "複数会場"], label_visibility="collapsed")

        c_in1, c_in2 = st.columns(2)
        with c_in1:
            st.markdown('<div style="font-size:0.9rem; font-weight:700; color:#FFFFFF; margin-bottom:4px;">💸 総購入額 (円)</div>', unsafe_allow_html=True)
            usr_inv = st.number_input("総購入額", min_value=0, value=0, step=100, label_visibility="collapsed")
        with c_in2:
            st.markdown('<div style="font-size:0.9rem; font-weight:700; color:#FFFFFF; margin-bottom:4px;">💰 総払戻額 (円)</div>', unsafe_allow_html=True)
            usr_ret = st.number_input("総払戻額", min_value=0, value=0, step=100, label_visibility="collapsed")

        c_in3, c_in4 = st.columns(2)
        with c_in3:
            st.markdown('<div style="font-size:0.9rem; font-weight:700; color:#FFFFFF; margin-bottom:4px;">🏇 購入レース数</div>', unsafe_allow_html=True)
            usr_races = st.number_input("購入レース数", min_value=0, value=0, step=1, label_visibility="collapsed")
        with c_in4:
            st.markdown('<div style="font-size:0.9rem; font-weight:700; color:#FFFFFF; margin-bottom:4px;">🎯 的中レース数</div>', unsafe_allow_html=True)
            usr_hits = st.number_input("的中レース数", min_value=0, value=0, step=1, label_visibility="collapsed")

        st.write("")
        submit = st.form_submit_button("💾 スプレッドシートに保存")

        if submit:
            gc = get_gspread_client()
            if gc:
                date_str = target_date.strftime("%Y/%m/%d")
                try:
                    ss = gc.open(SS_NAME)
                    std_h = ["日付", "会場", "ユーザー投資額", "ユーザー回収額", "ユーザーレース数", "ユーザー的中数"]
                    try:
                        ws = ss.worksheet("日次収支")
                    except Exception:
                        ws = ss.add_worksheet(title="日次収支", rows="500", cols="10")
                        ws.append_row(std_h)

                    ws.append_row([date_str, target_venue, usr_inv, usr_ret, usr_races, usr_hits])
                    st.success(f"✅ {date_str} [{target_venue}] の収支を記録しました！（投資: {usr_inv:,}円 / 払戻: {usr_ret:,}円）")
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"保存エラー: {e}")

# ==========================================
# 💻 画面 7: ターミナル操作マニュアル（砂入れ替え・バイアス監視コード付き）
# ==========================================
elif menu == "💻 ターミナル操作マニュアル":
    st.markdown(
        '<div class="main-title">💻 ターミナル操作 ＆ 砂・バイアス監視マニュアル</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="last-update">右上のコピーボタンを押してChromebookのターミナルに貼り付けて実行してください</div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### ⚡ 1. 当日（今日）の予想 ＆ レジまぐ原稿生成")
    st.code("~/keiba_env/bin/python ~/nar_system/publish_today.py", language="bash")

    st.markdown("#### 🌙 2. 前日に「明日」の予想 ＆ レジまぐ原稿生成（日付8桁指定）")
    st.code("~/keiba_env/bin/python ~/nar_system/publish_today.py 20261015", language="bash")

    st.markdown("---")
    st.markdown(
        """
        <div style="background:#241E14; border:1px solid #F59E0B; border-left:5px solid #F59E0B; border-radius:12px; padding:1.1rem; margin-bottom:1rem;">
            <h4 style="color:#FBBF24; margin-top:0; font-size:1.05rem;">🏖️ 3. 【週1回推奨】地方競馬「砂の全面入れ替え・コース改修・枠順バイアス異常」チェック</h4>
            <div style="font-size:0.88rem; color:#E2E8F0; line-height:1.6;">
                南関4場・佐賀の公式サイト情報から「砂の入れ替え・クッション砂厚変更・走路改修」に関する告知を自動検索し、さらに直近レースの枠順バイアス（内枠・中枠・外枠の勝率）が過去基準から急変していないかを一括診断します。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("**▼ 初回のみ：監視スクリプト（`check_sand_bias.py`）の作成コマンド**")
    sand_script_code = """cat << 'EOF' > ~/nar_system/check_sand_bias.py
import os, re, urllib.request
import pandas as pd
from bs4 import BeautifulSoup

print("=================================================================")
print("🏖️ 地方競馬（南関4場・佐賀）砂入れ替え告知 ＆ 枠順バイアス異常診断")
print("=================================================================\\n")

SOURCES = {
    "大井(TCK)": "https://www.tokyocitykeiba.com/news/",
    "川崎競馬": "https://www.kawasaki-keiba.jp/news/",
    "船橋競馬": "https://www.f-keiba.com/news/",
    "浦和競馬": "https://www.urawa-keiba.jp/info/",
    "地方競馬情報(NAR)": "https://www.keiba.go.jp/topics/"
}
KEYWORDS = ["砂", "白砂", "入れ替え", "入替", "補充", "クッション", "改修", "走路", "馬場"]

print("📡 【STEP 1】各競馬場公式サイトの馬場・砂関連ニュースをスキャン中...")
found_news = 0
for name, url in SOURCES.items():
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as res:
            soup = BeautifulSoup(res.read(), "html.parser")
            for a in soup.find_all("a"):
                txt = re.sub(r"\\s+", " ", a.text.strip())
                if any(k in txt for k in KEYWORDS) and len(txt) > 6:
                    print(f"  ⚠️ [{name}] 検知: {txt[:60]}")
                    found_news += 1
    except Exception:
        pass
if found_news == 0:
    print("  ✅ 直近のニュース一覧に「砂入れ替え・走路改修」の特記ワードはありません。")

CSV_PATH = os.path.expanduser("~/nar_system/data/all_years_combined.csv")
if os.path.exists(CSV_PATH):
    print("\\n📊 【STEP 2】会場別・枠順バイアス（内枠 vs 外枠）の直近乖離チェック...")
    df = pd.read_csv(CSV_PATH, usecols=["日付", "会場", "枠番", "着順"], low_memory=False)
    df["着順"] = pd.to_numeric(df["着順"], errors="coerce")
    df["枠番"] = pd.to_numeric(df["枠番"], errors="coerce")
    df = df.dropna(subset=["着順", "枠番"]).copy()
    df["is_win"] = (df["着順"] == 1).astype(int)
    df["w_cat"] = "中枠(4-5)"
    df.loc[df["枠番"].between(1, 3), "w_cat"] = "内枠(1-3)"
    df.loc[df["枠番"].between(6, 8), "w_cat"] = "外枠(6-8)"
    df = df.sort_values("日付")

    for t in ["大井", "川崎", "船橋", "浦和", "佐賀"]:
        sub = df[df["会場"] == t]
        if len(sub) < 500: continue
        recent = sub.tail(int(len(sub) * 0.12))
        base_in = round(sub[sub["w_cat"]=="内枠(1-3)"]["is_win"].mean()*100, 1)
        rec_in  = round(recent[recent["w_cat"]=="内枠(1-3)"]["is_win"].mean()*100, 1)
        base_out = round(sub[sub["w_cat"]=="外枠(6-8)"]["is_win"].mean()*100, 1)
        rec_out  = round(recent[recent["w_cat"]=="外枠(6-8)"]["is_win"].mean()*100, 1)
        diff_in = round(rec_in - base_in, 1)
        diff_out = round(rec_out - base_out, 1)
        alert = "⚠️バイアス変化注意" if (abs(diff_in) >= 2.0 or abs(diff_out) >= 2.0) else "✅安定"
        print(f"  ・[{t}] 内枠勝率: {base_in}% ➔ 直近 {rec_in}% ({diff_in:+.1f}%) | 外枠勝率: {base_out}% ➔ 直近 {rec_out}% ({diff_out:+.1f}%) [{alert}]")
print("=================================================================")
EOF"""
    st.code(sand_script_code, language="bash")

    st.markdown("**▼ 毎週の点検時：実行コマンド**")
    st.code("~/keiba_env/bin/python ~/nar_system/check_sand_bias.py", language="bash")

# ==========================================
# 🗄️ 画面 8: 過去データ分析（バックテスト実績）
# ==========================================
elif menu == "🗄️ 過去データ分析":
    st.markdown(
        '<div class="main-title">オッズ非依存・事前確定ポートフォリオ検証実績（4.5年間）</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="last-update">出馬表確定時点で100%買い目が決まる全12ゾーンの確定バックテスト成績（1点1,000円換算）</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="overflow-x: auto; border-radius: 8px; border: 1px solid #262F42; margin-top: 1rem;">
        <table style="width:100%; border-collapse: collapse; color: #F3F4F6; background-color: #151A24; font-size: 0.92rem;">
            <thead>
                <tr style="background-color: #10141D; color: #FBBF24; border-bottom: 2px solid #262F42; text-align: left;">
                    <th style="padding: 12px 14px;">会場・距離区分</th>
                    <th style="padding: 12px 14px;">事前確定条件（オッズ不問）</th>
                    <th style="padding: 12px 14px;">単勝回収率</th>
                    <th style="padding: 12px 14px;">単勝的中率 (複勝率)</th>
                    <th style="padding: 12px 14px;">純利益 (1,000円/R)</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid #262F42;">
                    <td style="padding: 12px 14px; font-weight:700;">🌃 大井・短距離 (<=1200m)</td>
                    <td style="padding: 12px 14px;">印【▲】× RL 1〜2位 × 中枠(4-5)</td>
                    <td style="padding: 12px 14px; font-weight:700; color:#FBBF24;">132.8%</td>
                    <td style="padding: 12px 14px;">25.7% (複 52.8%)</td>
                    <td style="padding: 12px 14px; color:#10B981; font-weight:700;">+70,100円</td>
                </tr>
                <tr style="border-bottom: 1px solid #262F42;">
                    <td style="padding: 12px 14px; font-weight:700;">🌃 大井・長距離 (>=1700m)</td>
                    <td style="padding: 12px 14px;">印【◎】× RL&CL 2位以内 × 外枠(6-8)</td>
                    <td style="padding: 12px 14px; font-weight:700; color:#FBBF24;">110.1%</td>
                    <td style="padding: 12px 14px;">36.7% (複 55.4%)</td>
                    <td style="padding: 12px 14px; color:#10B981; font-weight:700;">+14,100円</td>
                </tr>
                <tr style="border-bottom: 1px solid #262F42;">
                    <td style="padding: 12px 14px; font-weight:700;">🐎 川崎・短距離 (<=1200m)</td>
                    <td style="padding: 12px 14px;">印【◯】× RL&CL 2位以内 × 全枠</td>
                    <td style="padding: 12px 14px; font-weight:700; color:#FBBF24;">122.1%</td>
                    <td style="padding: 12px 14px;">16.9% (複 50.6%)</td>
                    <td style="padding: 12px 14px; color:#10B981; font-weight:700;">+17,000円</td>
                </tr>
                <tr style="border-bottom: 1px solid #262F42;">
                    <td style="padding: 12px 14px; font-weight:700;">🐎 川崎・長距離 (>=1700m)</td>
                    <td style="padding: 12px 14px;">印【◯】× CL 1〜2位 × 外枠(6-8)</td>
                    <td style="padding: 12px 14px; font-weight:700; color:#FBBF24;">103.2%</td>
                    <td style="padding: 12px 14px;">16.1% (複 53.2%)</td>
                    <td style="padding: 12px 14px; color:#10B981; font-weight:700;">+2,000円</td>
                </tr>
                <tr style="border-bottom: 1px solid #262F42;">
                    <td style="padding: 12px 14px; font-weight:700;">⚓ 船橋・中距離 (1300-1600m)</td>
                    <td style="padding: 12px 14px;">印【◯】× CL 1〜2位 × 内枠(1-3)</td>
                    <td style="padding: 12px 14px; font-weight:700; color:#FBBF24;">187.8%</td>
                    <td style="padding: 12px 14px;">29.7% (複 56.8%)</td>
                    <td style="padding: 12px 14px; color:#10B981; font-weight:700;">+32,500円</td>
                </tr>
                <tr style="border-bottom: 1px solid #262F42;">
                    <td style="padding: 12px 14px; font-weight:700;">⚓ 船橋・長距離 (>=1700m)</td>
                    <td style="padding: 12px 14px;">印【◯】× RL 1〜3位 × 内枠(1-3)</td>
                    <td style="padding: 12px 14px; font-weight:700; color:#FBBF24;">156.2%</td>
                    <td style="padding: 12px 14px;">38.5% (複 69.2%)</td>
                    <td style="padding: 12px 14px; color:#10B981; font-weight:700;">+29,200円</td>
                </tr>
                <tr style="border-bottom: 1px solid #262F42;">
                    <td style="padding: 12px 14px; font-weight:700;">🌸 浦和・全距離合計 (短・中・長)</td>
                    <td style="padding: 12px 14px;">印【◯】× 上位適性・外枠バイアス</td>
                    <td style="padding: 12px 14px; font-weight:700; color:#FBBF24;">106.2%</td>
                    <td style="padding: 12px 14px;">23.5% (複 58.2%)</td>
                    <td style="padding: 12px 14px; color:#10B981; font-weight:700;">+57,000円</td>
                </tr>
                <tr style="border-bottom: 1px solid #262F42;">
                    <td style="padding: 12px 14px; font-weight:700;">🔥 佐賀・全距離合計 (短・中・長)</td>
                    <td style="padding: 12px 14px;">内枠(1-3) × 印【▲/◯】× 実力適性上位</td>
                    <td style="padding: 12px 14px; font-weight:700; color:#FBBF24;">123.2%</td>
                    <td style="padding: 12px 14px;">30.5% (複 61.0%)</td>
                    <td style="padding: 12px 14px; color:#10B981; font-weight:700;">+43,400円</td>
                </tr>
                <tr style="background-color: #10141D; font-weight:800;">
                    <td style="padding: 14px;">🌐 総合ポートフォリオ (1,658R)</td>
                    <td style="padding: 14px;">1日平均 2.01鞍 ／ 重複レース1点集約</td>
                    <td style="padding: 14px; color:#F59E0B; font-size:1.1rem;">115.3%</td>
                    <td style="padding: 14px;">25.6% (複 57.3%)</td>
                    <td style="padding: 14px; color:#10B981; font-size:1.1rem;">+252,900円</td>
                </tr>
            </tbody>
        </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ==========================================
# 📈 画面 9: スプレッドシート連携
# ==========================================
elif menu == "📈 スプレッドシート連携":
    st.markdown(
        '<div class="main-title">Google スプレッドシート連携ステータス</div>',
        unsafe_allow_html=True,
    )
    gc = get_gspread_client()
    if gc:
        st.success(f"🔐 連携成功: 「{SS_NAME}」と正常に同期しています。")
        if not df_today_latest.empty:
            st.write(f"▼ 最新取得データ（{latest_date_str}・全{len(df_today_latest)}頭）")
            st.dataframe(df_today_latest, use_container_width=True, hide_index=True)
    else:
        st.error("🚨 スプレッドシートに接続できませんでした。")
