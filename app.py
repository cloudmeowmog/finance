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
.stApp { background: #070b14; color: #e2e8f0; }
.block-container { padding-top: 1.2rem !important; padding-bottom: 2rem !important; }

section[data-testid="stSidebar"] { display: none; }

/* Hero */
.hero {
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 28px; margin-bottom: 20px;
    background: linear-gradient(135deg, #0f172a 0%, #1a1040 100%);
    border-radius: 12px; border: 1px solid #1e1b4b;
}
.hero-title { font-family:'Space Mono',monospace; font-size:1.4rem; font-weight:700; color:#a5b4fc; letter-spacing:2px; margin:0; }
.hero-sub   { font-family:'Space Mono',monospace; font-size:0.68rem; color:#475569; letter-spacing:1px; margin-top:2px; }
.hero-time  { font-family:'Space Mono',monospace; font-size:0.78rem; color:#475569; text-align:right; }

/* 迷你卡片 */
.mini-card {
    background: #0d1423;
    border: 1px solid #1a2540;
    border-radius: 10px;
    padding: 10px 12px 6px;
    cursor: pointer;
    transition: all 0.15s;
    position: relative;
    overflow: hidden;
}
.mini-card:hover { border-color:#4f46e5; background:#111d35; transform:translateY(-1px); }
.mini-card.active {
    border-color: #818cf8 !important;
    background: #151e38 !important;
    box-shadow: 0 0 0 2px rgba(129,140,248,0.15), 0 4px 20px rgba(79,70,229,0.2);
}
.mini-card.active::after {
    content:'';
    position:absolute; bottom:-1px; left:50%; transform:translateX(-50%);
    border-left:7px solid transparent; border-right:7px solid transparent;
    border-bottom:7px solid #818cf8;
    bottom:-8px;
}
.mc-name  { font-family:'Space Mono',monospace; font-size:0.58rem; color:#475569; letter-spacing:1px; margin-bottom:3px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.mc-price { font-family:'Space Mono',monospace; font-size:0.92rem; font-weight:700; color:#f1f5f9; margin-bottom:1px; }
.mc-up    { font-family:'Space Mono',monospace; font-size:0.65rem; color:#f87171; }
.mc-down  { font-family:'Space Mono',monospace; font-size:0.65rem; color:#34d399; }
.mc-flat  { font-family:'Space Mono',monospace; font-size:0.65rem; color:#4b5563; }

/* 分類列標題 */
.cat-bar {
    font-family:'Space Mono',monospace;
    font-size:0.62rem; letter-spacing:3px; text-transform:uppercase;
    padding: 6px 0 8px 10px;
    border-left: 2px solid;
    margin: 18px 0 10px;
}

/* 詳細圖表區 */
.detail-box {
    background: #0a0f1e;
    border: 1px solid #1e293b;
    border-top: 2px solid #818cf8;
    border-radius: 0 0 12px 12px;
    padding: 20px 20px 12px;
    margin-top: 12px;
}
.detail-name  { font-family:'Space Mono',monospace; font-size:1rem; font-weight:700; color:#e2e8f0; }
.detail-price { font-family:'Space Mono',monospace; font-size:1.9rem; font-weight:700; color:#f1f5f9; }

/* 按鈕覆寫 */
.stButton > button {
    background: #0d1423 !important; color: #6366f1 !important;
    border: 1px solid #1a2540 !important; border-radius: 6px !important;
    font-family: 'Space Mono', monospace !important; font-size:0.62rem !important;
    padding: 3px 6px !important; transition: all 0.15s !important;
}
.stButton > button:hover {
    background: #151e38 !important; border-color:#4f46e5 !important; color:#a5b4fc !important;
}

/* Tab 覆寫 */
.stTabs [data-baseweb="tab-list"] { background:#0a0f1e; border-radius:8px 8px 0 0; gap:2px; padding:4px 4px 0; border-bottom:1px solid #1e293b; }
.stTabs [data-baseweb="tab"] { background:#0d1423; color:#6b7280; border-radius:6px 6px 0 0 !important; font-family:'Space Mono',monospace; font-size:0.72rem; padding:6px 14px; border:1px solid #1a2540; border-bottom:none; }
.stTabs [aria-selected="true"] { background:#1a1f35 !important; color:#a5b4fc !important; border-color:#4f46e5 !important; }
.stTabs [data-baseweb="tab-panel"] { background:#0a0f1e; border:1px solid #1e293b; border-top:none; border-radius:0 0 8px 8px; padding:16px; }

::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:#070b14; }
::-webkit-scrollbar-thumb { background:#1e293b; border-radius:3px; }
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
        prev = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else float(info.previous_close or 0)
        price = float(info.last_price or 0)
        chg = price - prev
        pct = (chg / prev * 100) if prev else 0
        return {"price": price, "change": chg, "pct": pct, "prev": prev}
    except:
        return {"price": 0, "change": 0, "pct": 0, "prev": 0}


@st.cache_data(ttl=600)
def get_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    try:
        df = yf.Ticker(ticker).history(period=period)
        df.index = pd.to_datetime(df.index)
        return df
    except:
        return pd.DataFrame()


@st.cache_data(ttl=600)
def get_mini_history(ticker: str) -> pd.DataFrame:
    """取得 30 天走勢供迷你折線圖"""
    try:
        df = yf.Ticker(ticker).history(period="30d", interval="1d")
        df.index = pd.to_datetime(df.index)
        return df
    except:
        return pd.DataFrame()


@st.cache_data(ttl=600)
def get_news(ticker: str, n: int = 8) -> list:
    try:
        t = yf.Ticker(ticker)
        return t.news[:n] if t.news else []
    except:
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


def fmt_price(price: float, kind: str, name: str = "") -> str:
    if kind.startswith("fx"):
        return f"{price:.4f}"
    if kind == "crypto":
        if price < 0.1:   return f"{price:.5f}"
        if price > 10000: return f"{price:,.0f}"
        return f"{price:,.2f}"
    if price > 10000: return f"{price:,.0f}"
    return f"{price:,.2f}"


def fetch_q(sym: str, kind: str) -> dict:
    if kind == "fx_direct": return fx_to_twd(sym, "direct")
    if kind == "fx_mul":    return fx_to_twd(sym, "mul")
    if kind == "fx_inv":    return fx_to_twd(sym, "inv")
    return get_quote(sym)


# ══════════════════════════════════════════════════════════
# 商品定義
# ══════════════════════════════════════════════════════════

PAGES = {
    "🌐 市場概況": {
        "color": "#818cf8",
        "subtitle": "全球主要股市指數",
        "items": [
            ("台灣加權",  "^TWII",      "index"),
            ("台灣夜盤",  "TWN=F",      "index"),
            ("S&P 500",   "^GSPC",      "index"),
            ("NASDAQ",    "^IXIC",      "index"),
            ("道瓊",      "^DJI",       "index"),
            ("費半",      "^SOX",       "index"),
            ("日經 225",  "^N225",      "index"),
            ("恒生指數",  "^HSI",       "index"),
            ("上証",      "000001.SS",  "index"),
            ("德國 DAX",  "^GDAXI",     "index"),
            ("英國 FTSE", "^FTSE",      "index"),
            ("VIX 恐慌",  "^VIX",       "index"),
        ],
    },
    "💱 貨幣": {
        "color": "#34d399",
        "subtitle": "各國貨幣對新台幣匯率（1 外幣 = ? TWD）",
        "items": [
            ("美元 USD",   "TWD=X",    "fx_direct"),
            ("歐元 EUR",   "EURUSD=X", "fx_mul"),
            ("日圓 JPY",   "JPY=X",    "fx_inv"),
            ("英鎊 GBP",   "GBPUSD=X", "fx_mul"),
            ("人民幣 CNY", "CNY=X",    "fx_inv"),
            ("港幣 HKD",   "HKD=X",    "fx_inv"),
            ("澳幣 AUD",   "AUDUSD=X", "fx_mul"),
            ("紐幣 NZD",   "NZDUSD=X", "fx_mul"),
            ("加幣 CAD",   "CADUSD=X", "fx_mul"),
            ("瑞郎 CHF",   "CHFUSD=X", "fx_mul"),
            ("韓圜 KRW",   "KRW=X",    "fx_inv"),
            ("新幣 SGD",   "SGDUSD=X", "fx_mul"),
        ],
    },
    "🏭 期貨及原物料": {
        "color": "#f59e0b",
        "subtitle": "貴金屬、能源、農產品期貨",
        "items": [
            ("黃金",      "GC=F",  "commodity"),
            ("白銀",      "SI=F",  "commodity"),
            ("鉑金",      "PL=F",  "commodity"),
            ("銅",        "HG=F",  "commodity"),
            ("WTI 原油",  "CL=F",  "commodity"),
            ("布蘭特",    "BZ=F",  "commodity"),
            ("天然氣",    "NG=F",  "commodity"),
            ("小麥",      "ZW=F",  "commodity"),
            ("玉米",      "ZC=F",  "commodity"),
            ("黃豆",      "ZS=F",  "commodity"),
        ],
    },
    "🪙 加密貨幣": {
        "color": "#f472b6",
        "subtitle": "主要加密貨幣對美元（USD）",
        "items": [
            ("比特幣 BTC",    "BTC-USD",  "crypto"),
            ("以太幣 ETH",    "ETH-USD",  "crypto"),
            ("BNB",           "BNB-USD",  "crypto"),
            ("Solana SOL",    "SOL-USD",  "crypto"),
            ("XRP",           "XRP-USD",  "crypto"),
            ("Cardano ADA",   "ADA-USD",  "crypto"),
            ("Dogecoin DOGE", "DOGE-USD", "crypto"),
            ("泰達幣 USDT",   "USDT-USD", "crypto"),
            ("USDC",          "USDC-USD", "crypto"),
        ],
    },
}


# ══════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════

page_keys = list(PAGES.keys())
if "page"     not in st.session_state: st.session_state.page     = page_keys[0]
if "sel_sym"  not in st.session_state: st.session_state.sel_sym  = PAGES[page_keys[0]]["items"][0][1]
if "sel_name" not in st.session_state: st.session_state.sel_name = PAGES[page_keys[0]]["items"][0][0]
if "sel_kind" not in st.session_state: st.session_state.sel_kind = PAGES[page_keys[0]]["items"][0][2]


# ══════════════════════════════════════════════════════════
# 迷你折線圖（SVG inline）
# ══════════════════════════════════════════════════════════

def mini_sparkline(sym: str, color: str, width: int = 120, height: int = 32) -> str:
    df = get_mini_history(sym)
    if df.empty or len(df) < 2:
        return f'<svg width="{width}" height="{height}"></svg>'
    vals = df["Close"].tolist()
    mn, mx = min(vals), max(vals)
    rng = mx - mn if mx != mn else 1
    pad = 2
    pts = []
    for i, v in enumerate(vals):
        x = pad + (i / (len(vals) - 1)) * (width - 2 * pad)
        y = height - pad - ((v - mn) / rng) * (height - 2 * pad)
        pts.append(f"{x:.1f},{y:.1f}")
    polyline = " ".join(pts)
    # 填充區域
    first_x, first_y = pts[0].split(",")
    last_x,  last_y  = pts[-1].split(",")
    fill_pts = f"{first_x},{height} " + polyline + f" {last_x},{height}"
    rgba_fill = hex_to_rgba(color, 0.15)
    return (
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
        f'<polygon points="{fill_pts}" fill="{rgba_fill}"/>'
        f'<polyline points="{polyline}" fill="none" stroke="{color}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>'
        f'</svg>'
    )


# ══════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════

st.markdown(f"""
<div class="hero">
  <div>
    <div class="hero-title">📡 每日財經雷達</div>
    <div class="hero-sub">DAILY FINANCIAL INTELLIGENCE · POWERED BY YAHOO FINANCE</div>
  </div>
  <div class="hero-time">
    {datetime.now().strftime('%Y.%m.%d')}<br>
    <span style="color:#1e293b;">{datetime.now().strftime('%H:%M')} TST</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# 分頁切換列
# ══════════════════════════════════════════════════════════

tab_cols = st.columns(len(PAGES))
for col, pname in zip(tab_cols, PAGES.keys()):
    color = PAGES[pname]["color"]
    is_active = (st.session_state.page == pname)
    style = (
        f"background:{color}22;border:1px solid {color}88;color:{color};"
        if is_active else
        "background:#0d1423;border:1px solid #1a2540;color:#4b5563;"
    )
    if col.button(pname, key=f"page_btn_{pname}", use_container_width=True):
        st.session_state.page = pname
        # 預設選第一項
        first = PAGES[pname]["items"][0]
        st.session_state.sel_sym  = first[1]
        st.session_state.sel_name = first[0]
        st.session_state.sel_kind = first[2]
        st.rerun()


# ══════════════════════════════════════════════════════════
# 目前分頁內容
# ══════════════════════════════════════════════════════════

cur_page  = st.session_state.page
page_data = PAGES[cur_page]
accent    = page_data["color"]
items     = page_data["items"]

st.markdown(
    f'<div class="cat-bar" style="border-color:{accent};color:{accent};">'
    f'{cur_page} &nbsp;·&nbsp; '
    f'<span style="color:#374151;font-size:0.6rem;">{page_data["subtitle"]}</span>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── 迷你卡片網格（每列 6 個）──────────────────────────────
COLS_PER_ROW = 6
for row_start in range(0, len(items), COLS_PER_ROW):
    row_items = items[row_start : row_start + COLS_PER_ROW]
    cols = st.columns(COLS_PER_ROW)

    for col, (name, sym, kind) in zip(cols, row_items):
        q = fetch_q(sym, kind)
        price_str = fmt_price(q["price"], kind, name)
        arrow  = "▲" if q["pct"] >= 0 else "▼"
        d_cls  = "mc-up" if q["pct"] > 0 else ("mc-down" if q["pct"] < 0 else "mc-flat")
        is_sel = (st.session_state.sel_sym == sym)
        card_cls = "mini-card active" if is_sel else "mini-card"
        border_style = f"border-color:{accent};" if is_sel else ""
        spark = mini_sparkline(sym, accent)

        col.markdown(f"""
        <div class="{card_cls}" style="{border_style}">
          <div class="mc-name">{name}</div>
          <div class="mc-price">{price_str}</div>
          <div class="{d_cls}">{arrow} {q['pct']:+.2f}%</div>
          <div style="margin-top:4px;">{spark}</div>
        </div>
        """, unsafe_allow_html=True)

        if col.button("展開", key=f"sel_{sym}"):
            st.session_state.sel_sym  = sym
            st.session_state.sel_name = name
            st.session_state.sel_kind = kind
            st.rerun()

    # 補空欄
    for empty_col in cols[len(row_items):]:
        empty_col.empty()


# ══════════════════════════════════════════════════════════
# 詳細圖表區
# ══════════════════════════════════════════════════════════

sel_sym  = st.session_state.sel_sym
sel_name = st.session_state.sel_name
sel_kind = st.session_state.sel_kind
q = fetch_q(sel_sym, sel_kind)

price_str   = fmt_price(q["price"], sel_kind, sel_name)
arrow       = "▲" if q["pct"] >= 0 else "▼"
delta_color = "#f87171" if q["pct"] > 0 else ("#34d399" if q["pct"] < 0 else "#6b7280")

st.markdown(f'<div style="height:20px;"></div>', unsafe_allow_html=True)

# 標題 + 報價
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown(f"""
    <div style="display:flex;align-items:baseline;gap:16px;padding:0 4px;">
      <span style="font-family:Space Mono;font-size:1.5rem;font-weight:700;color:{accent};">{sel_name}</span>
      <span style="font-family:Space Mono;font-size:2rem;font-weight:700;color:#f1f5f9;">{price_str}</span>
      <span style="font-family:Space Mono;font-size:1rem;color:{delta_color};">
        {arrow} {q['change']:+.4f} &nbsp;({q['pct']:+.2f}%)
      </span>
    </div>
    """, unsafe_allow_html=True)

with h2:
    refresh = st.button("🔄 重新整理", key="refresh_btn")
    if refresh:
        st.cache_data.clear()
        st.rerun()

# 期間選擇
period_map = {"1個月": "1mo", "3個月": "3mo", "6個月": "6mo", "1年": "1y", "2年": "2y"}
if "detail_period" not in st.session_state:
    st.session_state.detail_period = "1y"

pcols = st.columns(len(period_map))
for pc, (lbl, val) in zip(pcols, period_map.items()):
    is_p = (st.session_state.detail_period == val)
    if pc.button(lbl, key=f"dp_{val}"):
        st.session_state.detail_period = val
        st.rerun()

detail_period = st.session_state.detail_period
df = get_history(sel_sym, detail_period)

CHART_BG  = "#09101f"
GRID_CLR  = "#141e30"

if not df.empty:
    chart_tab, news_tab = st.tabs(["📊 圖表分析", "📰 相關新聞"])

    with chart_tab:
        df2 = df.copy()
        # 均線：年線240、季線60、月線20、5日線5
        df2["MA5"]   = df2["Close"].rolling(5).mean()
        df2["MA20"]  = df2["Close"].rolling(20).mean()
        df2["MA60"]  = df2["Close"].rolling(60).mean()
        df2["MA240"] = df2["Close"].rolling(240).mean()

        # K 線圖 + 均線
        fig = go.Figure()

        # K 線
        fig.add_trace(go.Candlestick(
            x=df2.index,
            open=df2["Open"], high=df2["High"],
            low=df2["Low"],   close=df2["Close"],
            increasing_line_color="#f87171", increasing_fillcolor="#f87171",
            decreasing_line_color="#34d399", decreasing_fillcolor="#34d399",
            name="K線", yaxis="y",
        ))

        # 均線
        ma_lines = [
            ("MA5",   "#facc15", "5日線"),
            ("MA20",  "#60a5fa", "月線(20)"),
            ("MA60",  "#f97316", "季線(60)"),
            ("MA240", "#c084fc", "年線(240)"),
        ]
        for col_n, clr, lbl in ma_lines:
            fig.add_trace(go.Scatter(
                x=df2.index, y=df2[col_n],
                mode="lines", line=dict(color=clr, width=1.4),
                name=lbl, yaxis="y",
            ))

        # 成交量
        vol_colors = ["#f87171" if c >= o else "#34d399"
                      for c, o in zip(df2["Close"], df2["Open"])]
        fig.add_trace(go.Bar(
            x=df2.index, y=df2["Volume"],
            marker_color=vol_colors, opacity=0.25,
            name="成交量", yaxis="y2",
        ))

        fig.update_layout(
            paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
            font=dict(color="#94a3b8", family="Space Mono", size=11),
            xaxis=dict(gridcolor=GRID_CLR, rangeslider=dict(visible=False), showgrid=True),
            yaxis=dict(gridcolor=GRID_CLR, side="right", showgrid=True),
            yaxis2=dict(overlaying="y", side="left", showgrid=False,
                        showticklabels=False,
                        range=[0, df2["Volume"].max() * 5] if "Volume" in df2 else [0, 1]),
            legend=dict(
                orientation="h", y=1.06,
                font=dict(size=10, color="#6b7280"),
                bgcolor="rgba(0,0,0,0)",
            ),
            margin=dict(l=0, r=10, t=28, b=10),
            height=480,
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

        # 均線說明
        st.markdown(f"""
        <div style="display:flex;gap:20px;padding:8px 4px;flex-wrap:wrap;">
          <span style="font-family:Space Mono;font-size:0.68rem;color:#facc15;">━ 5日線</span>
          <span style="font-family:Space Mono;font-size:0.68rem;color:#60a5fa;">━ 月線 (MA20)</span>
          <span style="font-family:Space Mono;font-size:0.68rem;color:#f97316;">━ 季線 (MA60)</span>
          <span style="font-family:Space Mono;font-size:0.68rem;color:#c084fc;">━ 年線 (MA240)</span>
          <span style="font-family:Space Mono;font-size:0.68rem;color:#f87171;">█ 漲（紅）</span>
          <span style="font-family:Space Mono;font-size:0.68rem;color:#34d399;">█ 跌（綠）</span>
        </div>
        """, unsafe_allow_html=True)

    with news_tab:
        news_list = get_news(sel_sym, n=10)
        if news_list:
            for item in news_list:
                title  = item.get("title", "（無標題）")
                link   = item.get("link", "#")
                pub_ts = item.get("providerPublishTime", 0)
                source = item.get("publisher", "未知來源")
                pub_dt = datetime.fromtimestamp(pub_ts).strftime("%Y-%m-%d %H:%M") if pub_ts else ""
                st.markdown(f"""
                <div style="background:#0d1423;border:1px solid #1a2540;border-radius:8px;
                     padding:12px 16px;margin-bottom:8px;">
                  <a href="{link}" target="_blank" style="text-decoration:none;">
                    <div style="font-size:0.9rem;color:#c7d2fe;font-weight:500;line-height:1.5;">{title}</div>
                  </a>
                  <div style="font-size:0.68rem;color:#334155;font-family:Space Mono;margin-top:6px;">
                    📰 {source} &nbsp;·&nbsp; {pub_dt}
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("目前無相關新聞")
else:
    st.warning(f"⚠ 無法取得 **{sel_name}**（`{sel_sym}`）的歷史資料")

# 頁尾
st.markdown(
    f'<div style="text-align:center;font-family:Space Mono;font-size:0.58rem;'
    f'color:#141e30;margin-top:28px;">'
    f'資料來源 Yahoo Finance · 快取 5min · {datetime.now().strftime("%H:%M:%S")}</div>',
    unsafe_allow_html=True,
)
