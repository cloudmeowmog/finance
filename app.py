import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ── 頁面設定 ──────────────────────────────────────────────
st.set_page_config(
    page_title="每日財經雷達",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;700;900&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] { font-family: 'Noto Sans TC', sans-serif; }
.stApp { background: #07090f; color: #e2e8f0; }
section[data-testid="stSidebar"] {
    background: #0d1224 !important;
    border-right: 1px solid #1e293b;
}
.hero {
    display: flex; align-items: center; justify-content: space-between;
    padding: 18px 28px; margin-bottom: 8px;
    background: linear-gradient(135deg, #0f172a 0%, #1a1040 100%);
    border-radius: 12px; border: 1px solid #1e1b4b;
}
.hero-title {
    font-family: 'Space Mono', monospace; font-size: 1.5rem;
    font-weight: 700; color: #a5b4fc; letter-spacing: 2px; margin: 0;
}
.hero-sub {
    font-family: 'Space Mono', monospace; font-size: 0.72rem;
    color: #475569; letter-spacing: 1px; margin-top: 2px;
}
.hero-time {
    font-family: 'Space Mono', monospace; font-size: 0.85rem;
    color: #64748b; text-align: right;
}
.cat-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem; letter-spacing: 2.5px; text-transform: uppercase;
    color: #4f46e5; margin: 20px 0 8px 2px;
    border-left: 2px solid #4f46e5; padding-left: 8px;
}
.qcard {
    background: #0f1623;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 12px 14px 8px;
    position: relative;
}
.qcard.selected {
    border-color: #818cf8 !important;
    background: #1a1f35 !important;
    box-shadow: 0 0 0 2px rgba(129,140,248,0.2);
}
.qcard-name {
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem; color: #4b5563;
    letter-spacing: 1px; margin-bottom: 4px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.qcard-price {
    font-family: 'Space Mono', monospace;
    font-size: 1rem; font-weight: 700; color: #f1f5f9;
    margin-bottom: 2px;
}
.up   { font-family: 'Space Mono', monospace; font-size: 0.7rem; color: #f87171; }
.down { font-family: 'Space Mono', monospace; font-size: 0.7rem; color: #34d399; }
.flat { font-family: 'Space Mono', monospace; font-size: 0.7rem; color: #6b7280; }
.night-badge {
    font-size: 0.52rem; background: #1e1b4b; color: #a5b4fc;
    padding: 1px 5px; border-radius: 3px; vertical-align: middle; margin-left: 3px;
}
.stButton > button {
    background: #0c1020 !important;
    color: #6366f1 !important;
    border: 1px solid #1e293b !important;
    border-radius: 0 0 8px 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.65rem !important;
    padding: 3px 8px !important;
    margin-top: -2px !important;
    width: 100% !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    background: #1a1f35 !important;
    border-color: #4f46e5 !important;
    color: #a5b4fc !important;
}
.block-container { padding-top: 1rem !important; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #07090f; }
::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# 資料函式
# ══════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def get_quote(ticker: str) -> dict:
    try:
        t = yf.Ticker(ticker)
        info = t.fast_info
        hist = t.history(period="5d", interval="1d")
        prev_close = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else float(info.previous_close or 0)
        price = float(info.last_price or 0)
        chg = price - prev_close
        pct = (chg / prev_close * 100) if prev_close else 0
        return {"price": price, "change": chg, "pct": pct, "prev": prev_close}
    except Exception:
        return {"price": 0, "change": 0, "pct": 0, "prev": 0}


@st.cache_data(ttl=600)
def get_history(ticker: str, period: str = "6mo") -> pd.DataFrame:
    try:
        df = yf.Ticker(ticker).history(period=period)
        df.index = pd.to_datetime(df.index)
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=600)
def get_news(ticker: str, n: int = 8) -> list:
    try:
        t = yf.Ticker(ticker)
        return t.news[:n] if t.news else []
    except Exception:
        return []


@st.cache_data(ttl=300)
def get_usd_twd() -> float:
    return get_quote("TWD=X")["price"]


def fx_to_twd(sym: str, mode: str) -> dict:
    usd_twd = get_usd_twd()
    q = get_quote(sym)
    raw, prev = q["price"], q["prev"] or q["price"]
    if raw == 0:
        return {"price": 0, "change": 0, "pct": 0, "prev": 0}
    if mode == "direct":
        p, pv = raw, prev
    elif mode == "mul":
        p, pv = raw * usd_twd, prev * usd_twd
    else:
        p  = (1 / raw)  * usd_twd
        pv = (1 / prev) * usd_twd if prev else p
    chg = p - pv
    pct = (chg / pv * 100) if pv else 0
    return {"price": p, "change": chg, "pct": pct, "prev": pv}


def hex_to_rgba(h: str, a: float = 0.08) -> str:
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{a})"


def fetch_quote(sym: str, kind: str) -> dict:
    if kind == "fx_direct": return fx_to_twd(sym, "direct")
    if kind == "fx_mul":    return fx_to_twd(sym, "mul")
    if kind == "fx_inv":    return fx_to_twd(sym, "inv")
    return get_quote(sym)


def fmt_price(price: float, kind: str, name: str) -> str:
    if kind.startswith("fx"):
        return f"{price:.4f}"
    if kind == "crypto":
        if price < 1:   return f"{price:.5f}"
        if price > 1000: return f"{price:,.0f}"
        return f"{price:,.2f}"
    if price > 10000: return f"{price:,.0f}"
    return f"{price:,.2f}"


# ══════════════════════════════════════════════════════════
# 商品定義
# ══════════════════════════════════════════════════════════

CATEGORIES = {
    "🌐 全球指數": [
        ("台灣加權",  "^TWII",      "index",    None),
        ("台灣夜盤",  "TWN=F",      "index",    "夜盤"),
        ("S&P 500",   "^GSPC",      "index",    None),
        ("NASDAQ",    "^IXIC",      "index",    None),
        ("道瓊",      "^DJI",       "index",    None),
        ("日經 225",  "^N225",      "index",    None),
        ("恒生指數",  "^HSI",       "index",    None),
        ("上証",      "000001.SS",  "index",    None),
        ("德國 DAX",  "^GDAXI",     "index",    None),
        ("VIX",       "^VIX",       "index",    None),
    ],
    "💱 外匯（對台幣）": [
        ("美元 USD",   "TWD=X",    "fx_direct", None),
        ("歐元 EUR",   "EURUSD=X", "fx_mul",    None),
        ("日圓 JPY",   "JPY=X",    "fx_inv",    None),
        ("英鎊 GBP",   "GBPUSD=X", "fx_mul",    None),
        ("人民幣 CNY", "CNY=X",    "fx_inv",    None),
        ("港幣 HKD",   "HKD=X",    "fx_inv",    None),
        ("澳幣 AUD",   "AUDUSD=X", "fx_mul",    None),
        ("韓圜 KRW",   "KRW=X",    "fx_inv",    None),
    ],
    "🪙 虛擬貨幣": [
        ("比特幣 BTC",  "BTC-USD",  "crypto", None),
        ("以太幣 ETH",  "ETH-USD",  "crypto", None),
        ("泰達幣 USDT", "USDT-USD", "crypto", None),
        ("USDC",        "USDC-USD", "crypto", None),
    ],
    "🏭 大宗商品": [
        ("黃金",     "GC=F", "commodity", None),
        ("WTI 原油", "CL=F", "commodity", None),
        ("布蘭特",   "BZ=F", "commodity", None),
        ("天然氣",   "NG=F", "commodity", None),
        ("白銀",     "SI=F", "commodity", None),
    ],
}

CAT_COLORS = {
    "🌐 全球指數":       "#818cf8",
    "💱 外匯（對台幣）": "#34d399",
    "🪙 虛擬貨幣":       "#f59e0b",
    "🏭 大宗商品":       "#94a3b8",
}


# ══════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════

if "selected_sym"  not in st.session_state:
    st.session_state.selected_sym  = "^TWII"
if "selected_name" not in st.session_state:
    st.session_state.selected_name = "台灣加權"
if "selected_kind" not in st.session_state:
    st.session_state.selected_kind = "index"
if "chart_period"  not in st.session_state:
    st.session_state.chart_period  = "6mo"


# ══════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════

st.markdown(f"""
<div class="hero">
  <div>
    <div class="hero-title">📡 每日財經雷達</div>
    <div class="hero-sub">DAILY FINANCIAL INTELLIGENCE</div>
  </div>
  <div class="hero-time">
    {datetime.now().strftime('%Y.%m.%d')}<br>
    <span style="color:#1e293b;">{datetime.now().strftime('%A').upper()}</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# 商品卡片區
# ══════════════════════════════════════════════════════════

for cat_name, items in CATEGORIES.items():
    accent = CAT_COLORS[cat_name]
    st.markdown(
        f'<div class="cat-label" style="border-color:{accent};color:{accent};">'
        f'{cat_name}</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(len(items))
    for col, (name, sym, kind, badge) in zip(cols, items):
        q = fetch_quote(sym, kind)
        price_str = fmt_price(q["price"], kind, name)
        arrow = "▲" if q["pct"] >= 0 else "▼"
        delta_cls = "up" if q["pct"] > 0 else ("down" if q["pct"] < 0 else "flat")
        is_sel = (st.session_state.selected_sym == sym)
        badge_html = f'<span class="night-badge">{badge}</span>' if badge else ""
        sel_style = f"border-color:{accent};" if is_sel else ""
        card_cls = "qcard selected" if is_sel else "qcard"

        col.markdown(f"""
        <div class="{card_cls}" style="{sel_style}">
          <div class="qcard-name">{name}{badge_html}</div>
          <div class="qcard-price">{price_str}</div>
          <div class="{delta_cls}">{arrow} {q['pct']:+.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

        if col.button("▶ 查看", key=f"btn_{sym}"):
            st.session_state.selected_sym  = sym
            st.session_state.selected_name = name
            st.session_state.selected_kind = kind
            st.rerun()


# ══════════════════════════════════════════════════════════
# 走勢圖區
# ══════════════════════════════════════════════════════════

sym    = st.session_state.selected_sym
name   = st.session_state.selected_name
kind   = st.session_state.selected_kind
period = st.session_state.chart_period
q      = fetch_quote(sym, kind)

# 找對應 accent 色
accent = "#818cf8"
for cat_name, items in CATEGORIES.items():
    if any(s == sym for _, s, _, _ in items):
        accent = CAT_COLORS[cat_name]
        break

st.markdown(f'<hr style="border:none;border-top:1px solid #1e293b;margin:16px 0;">', unsafe_allow_html=True)

# 標題列 + 期間按鈕
hcols = st.columns([4, 1, 1, 1, 1, 1])
hcols[0].markdown(
    f'<div style="font-family:Space Mono;font-size:1.1rem;font-weight:700;'
    f'color:{accent};padding-top:4px;">📈 {name} 走勢圖</div>',
    unsafe_allow_html=True,
)
for i, (opt, lbl) in enumerate(zip(
    ["1mo", "3mo", "6mo", "1y", "2y"],
    ["1個月", "3個月", "6個月", "1年", "2年"]
)):
    if hcols[i+1].button(lbl, key=f"p_{opt}"):
        st.session_state.chart_period = opt
        st.rerun()

# 報價大字
price_str   = fmt_price(q["price"], kind, name)
arrow       = "▲" if q["pct"] >= 0 else "▼"
delta_color = "#f87171" if q["pct"] > 0 else ("#34d399" if q["pct"] < 0 else "#6b7280")

st.markdown(f"""
<div style="display:flex;align-items:baseline;gap:16px;margin:10px 0 16px;">
  <span style="font-family:Space Mono;font-size:2rem;font-weight:700;color:#f1f5f9;">{price_str}</span>
  <span style="font-family:Space Mono;font-size:1rem;color:{delta_color};">
    {arrow} {q['change']:+.4f} &nbsp;({q['pct']:+.2f}%)
  </span>
  <span style="font-family:Space Mono;font-size:0.68rem;color:#374151;">期間：{period}</span>
</div>
""", unsafe_allow_html=True)

# 載入歷史資料
df = get_history(sym, period)

CHART_BG = "#0d1117"
GRID_CLR = "#161f2e"

if not df.empty:
    tab_candle, tab_line, tab_ma, tab_news = st.tabs(
        ["🕯 K 線", "📈 折線", "〰 均線", "📰 新聞"]
    )

    # ── K 線 ──
    with tab_candle:
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df["Open"], high=df["High"],
            low=df["Low"],   close=df["Close"],
            increasing_line_color="#f87171", increasing_fillcolor="#f87171",
            decreasing_line_color="#34d399", decreasing_fillcolor="#34d399",
            name="K線",
        ))
        vol_colors = ["#f87171" if c >= o else "#34d399"
                      for c, o in zip(df["Close"], df["Open"])]
        fig.add_trace(go.Bar(
            x=df.index, y=df["Volume"],
            marker_color=vol_colors, opacity=0.28,
            name="成交量", yaxis="y2",
        ))
        fig.update_layout(
            paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
            font=dict(color="#94a3b8", family="Space Mono"),
            xaxis=dict(gridcolor=GRID_CLR, rangeslider=dict(visible=False)),
            yaxis=dict(gridcolor=GRID_CLR, side="right"),
            yaxis2=dict(overlaying="y", side="left", showgrid=False,
                        showticklabels=False, range=[0, df["Volume"].max() * 4]),
            legend=dict(orientation="h", y=1.04, font=dict(size=10, color="#4b5563")),
            margin=dict(l=0, r=10, t=20, b=10), height=440,
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── 折線 ──
    with tab_line:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df.index, y=df["Close"],
            mode="lines",
            line=dict(color=accent, width=2),
            fill="tozeroy",
            fillcolor=hex_to_rgba(accent, 0.07),
        ))
        fig2.update_layout(
            paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
            font=dict(color="#94a3b8", family="Space Mono"),
            xaxis=dict(gridcolor=GRID_CLR),
            yaxis=dict(gridcolor=GRID_CLR),
            margin=dict(l=0, r=10, t=10, b=10), height=420,
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── 均線 ──
    with tab_ma:
        df2 = df.copy()
        df2["MA5"]  = df2["Close"].rolling(5).mean()
        df2["MA20"] = df2["Close"].rolling(20).mean()
        df2["MA60"] = df2["Close"].rolling(60).mean()
        fig3 = go.Figure()
        for col_n, clr, lbl in [
            ("Close", accent,    "收盤"),
            ("MA5",   "#34d399", "MA5"),
            ("MA20",  "#fbbf24", "MA20"),
            ("MA60",  "#f87171", "MA60"),
        ]:
            fig3.add_trace(go.Scatter(
                x=df2.index, y=df2[col_n],
                mode="lines", line=dict(color=clr, width=1.8), name=lbl,
            ))
        fig3.update_layout(
            paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
            font=dict(color="#94a3b8", family="Space Mono"),
            xaxis=dict(gridcolor=GRID_CLR),
            yaxis=dict(gridcolor=GRID_CLR),
            legend=dict(orientation="h", y=1.04, font=dict(size=10, color="#4b5563")),
            margin=dict(l=0, r=10, t=20, b=10), height=420,
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ── 新聞 ──
    with tab_news:
        news_list = get_news(sym, n=10)
        if news_list:
            for item in news_list:
                title  = item.get("title", "（無標題）")
                link   = item.get("link", "#")
                pub_ts = item.get("providerPublishTime", 0)
                source = item.get("publisher", "未知來源")
                pub_dt = datetime.fromtimestamp(pub_ts).strftime("%Y-%m-%d %H:%M") if pub_ts else ""
                st.markdown(f"""
                <div style="background:#0f1623;border:1px solid #1e293b;border-radius:8px;
                     padding:12px 16px;margin-bottom:8px;">
                  <a href="{link}" target="_blank" style="text-decoration:none;">
                    <div style="font-size:0.92rem;color:#c7d2fe;font-weight:500;line-height:1.5;">{title}</div>
                  </a>
                  <div style="font-size:0.7rem;color:#374151;font-family:Space Mono;margin-top:6px;">
                    📰 {source} &nbsp;·&nbsp; {pub_dt}
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("目前無相關新聞")
else:
    st.warning(f"⚠ 無法取得 **{name}**（`{sym}`）的歷史資料，請稍後再試。")

# 頁尾
st.markdown(
    f'<div style="text-align:center;font-family:Space Mono;font-size:0.62rem;'
    f'color:#1a2033;margin-top:32px;padding-bottom:12px;">'
    f'資料來源 Yahoo Finance · 快取 5 min · {datetime.now().strftime("%H:%M:%S")}</div>',
    unsafe_allow_html=True,
)
