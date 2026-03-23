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
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;700;900&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] { font-family: 'Noto Sans TC', sans-serif; }
.stApp { background: #070b14; color: #e2e8f0; }
.block-container { padding-top: 1.2rem !important; padding-bottom: 2rem !important; }

/* 側邊欄樣式 */
section[data-testid="stSidebar"] {
    background: #09101f !important;
    border-right: 1px solid #141e30 !important;
    min-width: 180px !important;
    max-width: 200px !important;
}
section[data-testid="stSidebar"] > div { padding: 1rem 0.6rem; }

/* 側邊欄收合按鈕 */
button[data-testid="collapsedControl"] {
    background: #09101f !important;
    border: 1px solid #141e30 !important;
    color: #4f46e5 !important;
}

/* Hero */
.hero {
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 24px; margin-bottom: 16px;
    background: linear-gradient(135deg, #0f172a 0%, #1a1040 100%);
    border-radius: 12px; border: 1px solid #1e1b4b;
}
.hero-title { font-family:'Space Mono',monospace; font-size:1.4rem; font-weight:700; color:#a5b4fc; letter-spacing:2px; margin:0; }
.hero-sub   { font-family:'Noto Sans TC',sans-serif; font-size:0.82rem; color:#64748b; letter-spacing:0.5px; margin-top:4px; }
.hero-time  { font-family:'Space Mono',monospace; font-size:0.82rem; color:#475569; text-align:right; }

/* 側邊欄分頁按鈕 */
.nav-logo {
    font-family:'Space Mono',monospace;
    font-size:0.75rem; letter-spacing:2px; color:#334155;
    text-transform:uppercase; margin-bottom:16px;
    padding-bottom:10px; border-bottom:1px solid #141e30;
}

/* 迷你卡片 */
.mini-card {
    background: #0d1423;
    border: 1px solid #1a2540;
    border-radius: 10px;
    padding: 10px 12px 6px;
    position: relative;
    overflow: hidden;
    height: 100%;
}
.mini-card.active {
    border-color: #818cf8 !important;
    background: #151e38 !important;
    box-shadow: 0 0 0 2px rgba(129,140,248,0.15), 0 4px 20px rgba(79,70,229,0.15);
}
.mini-card.active::after {
    content:'▼';
    position:absolute; bottom:-2px; left:50%; transform:translateX(-50%);
    font-size:0.5rem; color:#818cf8; line-height:1;
}
.mc-name  { font-family:'Noto Sans TC',sans-serif; font-size:0.78rem; font-weight:500; color:#94a3b8; letter-spacing:0.5px; margin-bottom:4px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.mc-price { font-family:'Space Mono',monospace; font-size:1.05rem; font-weight:700; color:#f1f5f9; margin-bottom:3px; }
.mc-up    { font-family:'Space Mono',monospace; font-size:0.78rem; font-weight:600; color:#f87171; }
.mc-down  { font-family:'Space Mono',monospace; font-size:0.78rem; font-weight:600; color:#34d399; }
.mc-flat  { font-family:'Space Mono',monospace; font-size:0.78rem; color:#4b5563; }

/* 分類列標題 */
.cat-bar {
    font-family:'Noto Sans TC',sans-serif;
    font-size:0.82rem; font-weight:700; letter-spacing:2px;
    padding: 6px 0 8px 12px;
    border-left: 3px solid;
    margin: 8px 0 12px;
}

/* 展開 / 操作 按鈕 */
.stButton > button {
    background: #0d1423 !important; color: #64748b !important;
    border: 1px solid #1e293b !important; border-radius: 6px !important;
    font-family: 'Noto Sans TC', sans-serif !important; font-size:0.78rem !important;
    font-weight: 500 !important;
    padding: 3px 6px !important; margin-top: 2px !important;
    transition: all 0.15s !important; width:100% !important;
}
.stButton > button:hover {
    background: #151e38 !important; border-color:#4f46e5 !important; color:#a5b4fc !important;
}

/* Tab 覆寫 */
.stTabs [data-baseweb="tab-list"] { background:#0a0f1e; border-radius:8px 8px 0 0; gap:2px; padding:4px 4px 0; border-bottom:1px solid #1e293b; }
.stTabs [data-baseweb="tab"] { background:#0d1423; color:#94a3b8; border-radius:6px 6px 0 0 !important; font-family:'Noto Sans TC',sans-serif; font-size:0.85rem; font-weight:500; padding:7px 16px; border:1px solid #1a2540; border-bottom:none; }
.stTabs [aria-selected="true"] { background:#1a1f35 !important; color:#a5b4fc !important; border-color:#4f46e5 !important; font-weight:700 !important; }
.stTabs [data-baseweb="tab-panel"] { background:#0a0f1e; border:1px solid #1e293b; border-top:none; border-radius:0 0 8px 8px; padding:18px; }

/* Streamlit 原生元件文字放大 */
.stSelectbox label, .stTextInput label { font-size:0.85rem !important; color:#94a3b8 !important; }
.stSelectbox > div > div, .stTextInput > div > div > input {
    font-size:0.9rem !important; background:#0d1423 !important;
    border-color:#1e293b !important; color:#e2e8f0 !important;
}
div[data-testid="stMarkdownContainer"] p { font-size:0.9rem; line-height:1.7; color:#cbd5e1; }

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
    try:
        df = yf.Ticker(ticker).history(period="30d", interval="1d")
        df.index = pd.to_datetime(df.index)
        return df
    except:
        return pd.DataFrame()


@st.cache_data(ttl=60)
def get_intraday(ticker: str) -> pd.DataFrame:
    """取得當日即時分鐘線（5 分鐘間隔，快取 1 分鐘）"""
    try:
        df = yf.Ticker(ticker).history(period="1d", interval="5m")
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


def mini_sparkline(sym: str, color: str, width: int = 110, height: int = 30) -> str:
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
    first_x = pts[0].split(",")[0]
    last_x  = pts[-1].split(",")[0]
    fill_pts = f"{first_x},{height} " + polyline + f" {last_x},{height}"
    return (
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
        f'<polygon points="{fill_pts}" fill="{hex_to_rgba(color, 0.12)}"/>'
        f'<polyline points="{polyline}" fill="none" stroke="{color}" stroke-width="1.5" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
        f'</svg>'
    )


# ══════════════════════════════════════════════════════════
# 商品定義
# ══════════════════════════════════════════════════════════

PAGES = {
    "🌐 市場概況": {
        "icon": "🌐", "label": "市場概況",
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
        "icon": "💱", "label": "貨幣",
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
    "🏭 期貨原物料": {
        "icon": "🏭", "label": "期貨原物料",
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
        "icon": "🪙", "label": "加密貨幣",
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

# 個股分頁識別鍵
STOCK_PAGE_KEY = "📋 個股查詢"

# 各市場熱門股票預設清單
MARKET_PRESETS = {
    "🇹🇼 台股": [
        ("台積電",   "2330.TW"), ("鴻海",     "2317.TW"), ("聯發科",   "2454.TW"),
        ("廣達",     "2382.TW"), ("富邦金",   "2881.TW"), ("國泰金",   "2882.TW"),
        ("中華電",   "2412.TW"), ("台塑",     "1301.TW"), ("南亞",     "1303.TW"),
        ("統一",     "1216.TW"), ("台達電",   "2308.TW"), ("日月光投", "3711.TW"),
    ],
    "🇺🇸 美股": [
        ("Apple",      "AAPL"),   ("NVIDIA",     "NVDA"),   ("Microsoft",  "MSFT"),
        ("Amazon",     "AMZN"),   ("Tesla",      "TSLA"),   ("Meta",       "META"),
        ("Alphabet",   "GOOGL"),  ("Broadcom",   "AVGO"),   ("TSMC ADR",   "TSM"),
        ("Netflix",    "NFLX"),   ("AMD",        "AMD"),    ("Intel",      "INTC"),
    ],
    "🇯🇵 日股": [
        ("Toyota",     "7203.T"), ("Sony",       "6758.T"), ("SoftBank",   "9984.T"),
        ("Keyence",    "6861.T"), ("Fanuc",      "6954.T"), ("Nintendo",   "7974.T"),
        ("Fast Retailing","9983.T"),("Mitsubishi","8058.T"), ("Recruit",   "6098.T"),
        ("Shin-Etsu",  "4063.T"), ("Hitachi",    "6501.T"), ("Honda",      "7267.T"),
    ],
}


# ══════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════

page_keys = list(PAGES.keys())
if "page"          not in st.session_state: st.session_state.page          = page_keys[0]
if "sel_sym"       not in st.session_state: st.session_state.sel_sym       = PAGES[page_keys[0]]["items"][0][1]
if "sel_name"      not in st.session_state: st.session_state.sel_name      = PAGES[page_keys[0]]["items"][0][0]
if "sel_kind"      not in st.session_state: st.session_state.sel_kind      = PAGES[page_keys[0]]["items"][0][2]
if "detail_period" not in st.session_state: st.session_state.detail_period = "1y"
if "stock_sym"      not in st.session_state: st.session_state.stock_sym      = "2330.TW"
if "stock_name"     not in st.session_state: st.session_state.stock_name     = "台積電"
if "stock_market"   not in st.session_state: st.session_state.stock_market   = "🇹🇼 台股"
if "stock_period"   not in st.session_state: st.session_state.stock_period   = "1y"
if "watchlist"      not in st.session_state:
    st.session_state.watchlist = [
        ("台積電",  "2330.TW"), ("鴻海",   "2317.TW"), ("聯發科", "2454.TW"),
        ("Apple",   "AAPL"),    ("NVIDIA", "NVDA"),    ("Tesla",  "TSLA"),
    ]
if "wl_add_sym"     not in st.session_state: st.session_state.wl_add_sym  = ""
if "wl_add_name"    not in st.session_state: st.session_state.wl_add_name = ""


# ══════════════════════════════════════════════════════════
# 側邊欄導覽
# ══════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(
        '<div class="nav-logo">📡 FINANCE<br>RADAR</div>',
        unsafe_allow_html=True,
    )

    for pname, pdata in PAGES.items():
        is_active = (st.session_state.page == pname)
        color = pdata["color"]
        btn_label = f"{pdata['icon']}  {pdata['label']}"

        if st.button(btn_label, key=f"nav_{pname}", use_container_width=True):
            st.session_state.page = pname
            first = pdata["items"][0]
            st.session_state.sel_sym  = first[1]
            st.session_state.sel_name = first[0]
            st.session_state.sel_kind = first[2]
            st.rerun()

    # 個股查詢分頁按鈕
    if st.button(f"📋  個股查詢", key=f"nav_{STOCK_PAGE_KEY}", use_container_width=True):
        st.session_state.page = STOCK_PAGE_KEY
        st.rerun()

    st.markdown("---")

    if st.button("🔄 更新資料", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown(
        f'<div style="font-family:Space Mono;font-size:0.6rem;color:#1e293b;'
        f'margin-top:12px;line-height:1.8;">'
        f'資料來源<br>Yahoo Finance<br><br>'
        f'快取 5 分鐘<br>{datetime.now().strftime("%H:%M:%S")}</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════
# 主內容區
# ══════════════════════════════════════════════════════════

cur_page = st.session_state.page

# ── 個股查詢分頁（獨立邏輯）──────────────────────────────
if cur_page == STOCK_PAGE_KEY:

    accent = "#e879f9"

    st.markdown(f"""
    <div class="hero">
      <div>
        <div class="hero-title">📋 個股查詢</div>
        <div class="hero-sub">台股 · 美股 · 日股 自選個股走勢</div>
      </div>
      <div class="hero-time">
        {datetime.now().strftime('%Y.%m.%d')}<br>
        {datetime.now().strftime('%H:%M')} TST
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ══ 上方工具列：新增股票 ════════════════════════════════
    add_c1, add_c2, add_c3, add_c4 = st.columns([2, 2, 1, 3])

    with add_c1:
        market_choice = st.selectbox(
            "市場",
            list(MARKET_PRESETS.keys()),
            index=list(MARKET_PRESETS.keys()).index(st.session_state.stock_market),
            key="stock_market_sel",
            label_visibility="collapsed",
        )
        if market_choice != st.session_state.stock_market:
            st.session_state.stock_market = market_choice

    suffix_hint = {"🇹🇼 台股": "代號，如 2330.TW", "🇺🇸 美股": "代號，如 AAPL", "🇯🇵 日股": "代號，如 7203.T"}

    with add_c2:
        new_sym = st.text_input("代號", placeholder=suffix_hint.get(st.session_state.stock_market,"代號"),
                                key="wl_new_sym", label_visibility="collapsed")
    with add_c3:
        new_name = st.text_input("名稱（選填）", placeholder="名稱", key="wl_new_name",
                                 label_visibility="collapsed")
    with add_c4:
        btn_add_col, btn_preset_col = st.columns([1, 2])
        with btn_add_col:
            if st.button("➕ 新增", key="wl_add_btn", use_container_width=True):
                sym_in = new_sym.strip().upper()
                if sym_in:
                    already = [s for _, s in st.session_state.watchlist]
                    if sym_in in already:
                        st.warning(f"{sym_in} 已在清單中")
                    else:
                        q_test = get_quote(sym_in)
                        if q_test["price"] > 0:
                            disp_name = new_name.strip() if new_name.strip() else sym_in
                            st.session_state.watchlist.append((disp_name, sym_in))
                            st.session_state.stock_sym  = sym_in
                            st.session_state.stock_name = disp_name
                            st.rerun()
                        else:
                            st.error(f"找不到 `{sym_in}`，請確認代號格式")
        with btn_preset_col:
            # 快速加入預設
            preset_names = [f"{n}（{s}）" for n, s in MARKET_PRESETS[st.session_state.stock_market]]
            preset_sel = st.selectbox("快速加入熱門股", ["— 選擇 —"] + preset_names,
                                      key="wl_preset_sel", label_visibility="collapsed")
            if preset_sel != "— 選擇 —":
                idx_p = preset_names.index(preset_sel)
                p_name, p_sym = MARKET_PRESETS[st.session_state.stock_market][idx_p]
                already = [s for _, s in st.session_state.watchlist]
                if p_sym not in already:
                    st.session_state.watchlist.append((p_name, p_sym))
                    st.session_state.stock_sym  = p_sym
                    st.session_state.stock_name = p_name
                    st.rerun()

    # ══ 自選清單卡片區 ════════════════════════════════════
    st.markdown(
        f'<div class="cat-bar" style="border-color:{accent};color:{accent};">'
        f'📌 自選清單 &nbsp;<span style="color:#374151;font-size:0.55rem;">共 {len(st.session_state.watchlist)} 支</span></div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.watchlist:
        st.info("清單為空，請用上方「➕ 新增」或「快速加入熱門股」加入個股")
    else:
        SCOLS = 6
        to_delete = None   # 記錄要刪除的代號

        for row_s in range(0, len(st.session_state.watchlist), SCOLS):
            row_it = st.session_state.watchlist[row_s:row_s+SCOLS]
            padded = row_it + [None] * (SCOLS - len(row_it))
            scols  = st.columns(SCOLS)

            for col, item in zip(scols, padded):
                if item is None:
                    col.empty()
                    continue

                s_name, s_sym = item
                sq     = get_quote(s_sym)
                sp_str = fmt_price(sq["price"], "stock", s_name)
                s_arrow = "▲" if sq["pct"] >= 0 else "▼"
                s_dcls  = "mc-up" if sq["pct"] > 0 else ("mc-down" if sq["pct"] < 0 else "mc-flat")
                is_sel  = (st.session_state.stock_sym == s_sym)
                s_card  = "mini-card active" if is_sel else "mini-card"
                s_bdr   = f"border-color:{accent};" if is_sel else ""
                spark   = mini_sparkline(s_sym, accent if is_sel else "#1e3a5f")

                col.markdown(f"""
                <div class="{s_card}" style="{s_bdr}">
                  <div class="mc-name">{s_name}<span style="color:#1e293b;margin-left:4px;font-size:0.5rem;">{s_sym}</span></div>
                  <div class="mc-price">{sp_str}</div>
                  <div class="{s_dcls}">{s_arrow} {sq['pct']:+.2f}%</div>
                  <div style="margin-top:4px;">{spark}</div>
                </div>
                """, unsafe_allow_html=True)

                # 展開 / 刪除 按鈕（2欄）
                b1, b2 = col.columns([3, 1])
                if b1.button("▼ 展開", key=f"wl_sel_{s_sym}"):
                    st.session_state.stock_sym  = s_sym
                    st.session_state.stock_name = s_name
                    st.rerun()
                if b2.button("✕", key=f"wl_del_{s_sym}", help=f"從清單移除 {s_name}"):
                    to_delete = s_sym

        if to_delete:
            st.session_state.watchlist = [(n, s) for n, s in st.session_state.watchlist if s != to_delete]
            # 若刪除的是目前選中的，改選第一支
            if st.session_state.stock_sym == to_delete and st.session_state.watchlist:
                st.session_state.stock_sym  = st.session_state.watchlist[0][1]
                st.session_state.stock_name = st.session_state.watchlist[0][0]
            st.rerun()

    # ── 個股詳細圖表 ──────────────────────────────────────
    stk_sym  = st.session_state.stock_sym
    stk_name = st.session_state.stock_name
    stk_q    = get_quote(stk_sym)

    stk_price = fmt_price(stk_q["price"], "stock", stk_name)
    stk_arrow = "▲" if stk_q["pct"] >= 0 else "▼"
    stk_dclr  = "#f87171" if stk_q["pct"] > 0 else ("#34d399" if stk_q["pct"] < 0 else "#6b7280")

    st.markdown('<hr style="border:none;border-top:1px solid #141e30;margin:16px 0 12px;">', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;">
      <span style="font-family:Space Mono;font-size:0.9rem;font-weight:700;color:{accent};
            background:{hex_to_rgba(accent,0.1)};padding:3px 10px;border-radius:5px;
            border:1px solid {hex_to_rgba(accent,0.3)};">{stk_name}</span>
      <span style="font-family:Space Mono;font-size:0.75rem;color:#475569;">{stk_sym}</span>
      <span style="font-family:Space Mono;font-size:1.8rem;font-weight:700;color:#f1f5f9;">{stk_price}</span>
      <span style="font-family:Space Mono;font-size:0.95rem;color:{stk_dclr};">
        {stk_arrow} {stk_q['change']:+.4f} ({stk_q['pct']:+.2f}%)
      </span>
    </div>
    """, unsafe_allow_html=True)

    # 期間選擇
    stk_period_map = {"1M": "1mo", "3M": "3mo", "6M": "6mo", "1Y": "1y", "2Y": "2y"}
    sp_cols = st.columns([1,1,1,1,1,8])
    for pc, (lbl, val) in zip(sp_cols[:5], stk_period_map.items()):
        if pc.button(lbl, key=f"sp_{val}"):
            st.session_state.stock_period = val
            st.rerun()

    stk_df = get_history(stk_sym, st.session_state.stock_period)

    CHART_BG2 = "#09101f"
    GRID_CLR2 = "#141e30"

    if not stk_df.empty:
        s_today_tab, s_chart_tab, s_news_tab = st.tabs(["⚡ 今日走勢", "📊 圖表分析", "📰 相關新聞"])

        # 今日走勢
        with s_today_tab:
            stk_intra = get_intraday(stk_sym)
            if not stk_intra.empty and len(stk_intra) > 1:
                stk_prev_df = get_history(stk_sym, "5d")
                stk_prev_close = float(stk_prev_df["Close"].iloc[-2]) if len(stk_prev_df) >= 2 else float(stk_intra["Open"].iloc[0])
                stk_open   = float(stk_intra["Open"].iloc[0])
                stk_last   = float(stk_intra["Close"].iloc[-1])
                stk_ichg   = stk_last - stk_prev_close
                stk_ipct   = (stk_ichg / stk_prev_close * 100) if stk_prev_close else 0
                stk_iclr   = "#f87171" if stk_ichg >= 0 else "#34d399"
                stk_iarrow = "▲" if stk_ichg >= 0 else "▼"
                stk_high   = float(stk_intra["High"].max())
                stk_low    = float(stk_intra["Low"].min())
                stk_vol    = int(stk_intra["Volume"].sum()) if "Volume" in stk_intra else 0

                ca, cb, cc, cd, ce = st.columns(5)
                for c, lbl, val in [
                    (ca, "前收",   fmt_price(stk_prev_close, "stock")),
                    (cb, "開盤",   fmt_price(stk_open, "stock")),
                    (cc, "最高",   fmt_price(stk_high, "stock")),
                    (cd, "最低",   fmt_price(stk_low,  "stock")),
                    (ce, "成交量", f"{stk_vol:,}" if stk_vol else "—"),
                ]:
                    c.markdown(f"""
                    <div style="background:#0d1423;border:1px solid #1a2540;border-radius:8px;
                         padding:10px 14px;margin-bottom:12px;">
                      <div style="font-family:Space Mono;font-size:0.6rem;color:#475569;
                           letter-spacing:1px;margin-bottom:4px;">{lbl}</div>
                      <div style="font-family:Space Mono;font-size:1rem;font-weight:700;
                           color:#f1f5f9;">{val}</div>
                    </div>
                    """, unsafe_allow_html=True)

                stk_prev_ts = stk_intra.index[0] - pd.Timedelta(minutes=5)
                stk_anchor  = pd.DataFrame(
                    {"Open": stk_prev_close, "High": stk_prev_close,
                     "Low": stk_prev_close, "Close": stk_prev_close, "Volume": 0},
                    index=[stk_prev_ts],
                )
                stk_plot = pd.concat([stk_anchor, stk_intra])
                stk_prices = list(stk_plot["Close"].dropna())
                sy_min = min(stk_prices); sy_max = max(stk_prices)
                sy_pad = (sy_max - sy_min) * 0.15 if sy_max != sy_min else sy_max * 0.005
                sy_range = [sy_min - sy_pad, sy_max + sy_pad * 2]

                fig_si = go.Figure()
                fig_si.add_hline(y=stk_prev_close,
                    line=dict(color="#475569", width=1, dash="dash"),
                    annotation_text=f"前收 {fmt_price(stk_prev_close, 'stock')}",
                    annotation_font=dict(color="#6b7280", size=10, family="Space Mono"),
                    annotation_position="left")
                fig_si.add_trace(go.Scatter(
                    x=stk_plot.index, y=stk_plot["Close"],
                    mode="lines", line=dict(color=stk_iclr, width=2),
                    fill="none", name="成交價",
                    hovertemplate="%{x|%H:%M}<br>%{y:,.2f}<extra></extra>",
                ))
                if "Volume" in stk_intra and stk_intra["Volume"].sum() > 0:
                    sv_c = ["#f87171" if c >= o else "#34d399"
                            for c, o in zip(stk_intra["Close"], stk_intra["Open"])]
                    fig_si.add_trace(go.Bar(
                        x=stk_intra.index, y=stk_intra["Volume"],
                        marker_color=sv_c, opacity=0.25, name="成交量", yaxis="y2"))
                fig_si.add_trace(go.Scatter(
                    x=[stk_intra.index[-1]], y=[stk_last],
                    mode="markers+text",
                    marker=dict(color=stk_iclr, size=9, symbol="circle"),
                    text=[fmt_price(stk_last, "stock")], textposition="top right",
                    textfont=dict(color=stk_iclr, size=11, family="Space Mono"),
                    name="最新", showlegend=False))
                fig_si.update_layout(
                    paper_bgcolor=CHART_BG2, plot_bgcolor=CHART_BG2,
                    font=dict(color="#94a3b8", family="Space Mono", size=11),
                    xaxis=dict(gridcolor=GRID_CLR2, tickformat="%H:%M", rangeslider=dict(visible=False)),
                    yaxis=dict(gridcolor=GRID_CLR2, side="right", range=sy_range, tickformat=",.2f"),
                    yaxis2=dict(overlaying="y", side="left", showgrid=False, showticklabels=False,
                                range=[0, stk_intra["Volume"].max()*8] if stk_vol else [0,1]),
                    legend=dict(orientation="h", y=1.06, font=dict(size=10, color="#6b7280"), bgcolor="rgba(0,0,0,0)"),
                    margin=dict(l=0, r=80, t=28, b=10), height=400, hovermode="x unified",
                )
                st.plotly_chart(fig_si, use_container_width=True)
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:16px;padding:6px 4px;flex-wrap:wrap;">
                  <span style="font-family:Noto Sans TC,sans-serif;font-size:0.82rem;font-weight:500;color:#64748b;">今日區間</span>
                  <span style="font-family:Space Mono;font-size:0.88rem;font-weight:600;color:#34d399;">▼ {fmt_price(stk_low,"stock")}</span>
                  <span style="font-family:Space Mono;font-size:0.88rem;color:#374151;">—</span>
                  <span style="font-family:Space Mono;font-size:0.88rem;font-weight:600;color:#f87171;">▲ {fmt_price(stk_high,"stock")}</span>
                  <span style="font-family:Space Mono;font-size:0.85rem;font-weight:600;color:{stk_iclr};margin-left:12px;">
                    {stk_iarrow} 較前收 {stk_ichg:+.4f} ({stk_ipct:+.2f}%)
                  </span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("⏰ 目前非交易時間，或尚無今日盤中資料。")

        # 圖表分析
        with s_chart_tab:
            stk_df2 = stk_df.copy()
            stk_df2["MA5"]   = stk_df2["Close"].rolling(5).mean()
            stk_df2["MA20"]  = stk_df2["Close"].rolling(20).mean()
            stk_df2["MA60"]  = stk_df2["Close"].rolling(60).mean()
            stk_df2["MA240"] = stk_df2["Close"].rolling(240).mean()
            fig_s = go.Figure()
            fig_s.add_trace(go.Candlestick(
                x=stk_df2.index,
                open=stk_df2["Open"], high=stk_df2["High"],
                low=stk_df2["Low"],   close=stk_df2["Close"],
                increasing_line_color="#f87171", increasing_fillcolor="#f87171",
                decreasing_line_color="#34d399", decreasing_fillcolor="#34d399",
                name="K線",
            ))
            for cn, clr, lbl in [
                ("MA5","#facc15","5日線"),("MA20","#60a5fa","月線(20)"),
                ("MA60","#f97316","季線(60)"),("MA240","#c084fc","年線(240)"),
            ]:
                fig_s.add_trace(go.Scatter(x=stk_df2.index, y=stk_df2[cn],
                    mode="lines", line=dict(color=clr, width=1.4), name=lbl))
            if "Volume" in stk_df2 and stk_df2["Volume"].sum() > 0:
                sv2 = ["#f87171" if c >= o else "#34d399"
                       for c, o in zip(stk_df2["Close"], stk_df2["Open"])]
                fig_s.add_trace(go.Bar(x=stk_df2.index, y=stk_df2["Volume"],
                    marker_color=sv2, opacity=0.22, name="成交量", yaxis="y2"))
            fig_s.update_layout(
                paper_bgcolor=CHART_BG2, plot_bgcolor=CHART_BG2,
                font=dict(color="#94a3b8", family="Space Mono", size=11),
                xaxis=dict(gridcolor=GRID_CLR2, rangeslider=dict(visible=False)),
                yaxis=dict(gridcolor=GRID_CLR2, side="right"),
                yaxis2=dict(overlaying="y", side="left", showgrid=False, showticklabels=False,
                            range=[0, stk_df2["Volume"].max()*5] if stk_df2["Volume"].sum()>0 else [0,1]),
                legend=dict(orientation="h", y=1.06, font=dict(size=10,color="#6b7280"), bgcolor="rgba(0,0,0,0)"),
                margin=dict(l=0, r=10, t=28, b=10), height=480, hovermode="x unified",
            )
            st.plotly_chart(fig_s, use_container_width=True)
            st.markdown("""
            <div style="display:flex;gap:20px;padding:6px 4px 0;flex-wrap:wrap;">
              <span style="font-family:Space Mono;font-size:0.8rem;color:#facc15;">━ 5日線</span>
              <span style="font-family:Space Mono;font-size:0.8rem;color:#60a5fa;">━ 月線(MA20)</span>
              <span style="font-family:Space Mono;font-size:0.8rem;color:#f97316;">━ 季線(MA60)</span>
              <span style="font-family:Space Mono;font-size:0.8rem;color:#c084fc;">━ 年線(MA240)</span>
              <span style="font-family:Space Mono;font-size:0.8rem;color:#f87171;">█ 漲</span>
              <span style="font-family:Space Mono;font-size:0.8rem;color:#34d399;">█ 跌</span>
            </div>
            """, unsafe_allow_html=True)

        # 相關新聞
        with s_news_tab:
            snews = get_news(stk_sym, n=10)
            if snews:
                for item in snews:
                    title  = item.get("title","（無標題）")
                    link   = item.get("link","#")
                    pub_ts = item.get("providerPublishTime",0)
                    source = item.get("publisher","未知來源")
                    pub_dt = datetime.fromtimestamp(pub_ts).strftime("%Y-%m-%d %H:%M") if pub_ts else ""
                    st.markdown(f"""
                    <div style="background:#0d1423;border:1px solid #1a2540;border-radius:8px;
                         padding:12px 16px;margin-bottom:8px;">
                      <a href="{link}" target="_blank" style="text-decoration:none;">
                        <div style="font-size:0.95rem;color:#dde6f5;font-weight:500;line-height:1.6;">{title}</div>
                      </a>
                      <div style="font-size:0.75rem;color:#475569;font-family:Space Mono;margin-top:6px;">
                        📰 {source} &nbsp;·&nbsp; {pub_dt}
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("目前無相關新聞")
    else:
        st.warning(f"⚠ 無法取得 **{stk_name}**（`{stk_sym}`）的歷史資料")

else:
    # ── 一般分頁 ──────────────────────────────────────────
    page_data = PAGES[cur_page]
    accent    = page_data["color"]
    items     = page_data["items"]

    # Hero
    st.markdown(f"""
    <div class="hero">
      <div>
        <div class="hero-title">{page_data['icon']} {page_data['label']}</div>
        <div class="hero-sub">{page_data['subtitle']}</div>
      </div>
      <div class="hero-time">
        {datetime.now().strftime('%Y.%m.%d')}<br>
        {datetime.now().strftime('%H:%M')} TST
      </div>
    </div>
    """, unsafe_allow_html=True)


    # ── 迷你卡片網格（每列 6 個）──────────────────────────────
    COLS_PER_ROW = 6
    
    for row_start in range(0, len(items), COLS_PER_ROW):
        row_items = items[row_start : row_start + COLS_PER_ROW]
        padded = row_items + [None] * (COLS_PER_ROW - len(row_items))
        cols = st.columns(COLS_PER_ROW)
    
        for col, item in zip(cols, padded):
            if item is None:
                col.empty()
                continue
    
            name, sym, kind = item
            q = fetch_q(sym, kind)
            price_str = fmt_price(q["price"], kind, name)
            arrow  = "▲" if q["pct"] >= 0 else "▼"
            d_cls  = "mc-up" if q["pct"] > 0 else ("mc-down" if q["pct"] < 0 else "mc-flat")
            is_sel = (st.session_state.sel_sym == sym)
            card_cls = "mini-card active" if is_sel else "mini-card"
            border_style = f"border-color:{accent};" if is_sel else ""
            spark = mini_sparkline(sym, accent if is_sel else "#1e3a5f")
    
            col.markdown(f"""
            <div class="{card_cls}" style="{border_style}">
              <div class="mc-name">{name}</div>
              <div class="mc-price">{price_str}</div>
              <div class="{d_cls}">{arrow} {q['pct']:+.2f}%</div>
              <div style="margin-top:4px;">{spark}</div>
            </div>
            """, unsafe_allow_html=True)
    
            if col.button("▼ 展開", key=f"sel_{sym}"):
                st.session_state.sel_sym  = sym
                st.session_state.sel_name = name
                st.session_state.sel_kind = kind
                st.rerun()
    
    
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
    
    st.markdown('<hr style="border:none;border-top:1px solid #141e30;margin:16px 0 12px;">', unsafe_allow_html=True)
    
    # 標題列
    h1, h2 = st.columns([5, 1])
    with h1:
        st.markdown(f"""
        <div style="display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;">
          <span style="font-family:Space Mono;font-size:0.9rem;font-weight:700;color:{accent};
                background:{hex_to_rgba(accent,0.1)};padding:3px 10px;border-radius:5px;
                border:1px solid {hex_to_rgba(accent,0.3)};">{sel_name}</span>
          <span style="font-family:Space Mono;font-size:1.8rem;font-weight:700;color:#f1f5f9;">{price_str}</span>
          <span style="font-family:Space Mono;font-size:0.95rem;color:{delta_color};">
            {arrow} {q['change']:+.4f} &nbsp;({q['pct']:+.2f}%)
          </span>
        </div>
        """, unsafe_allow_html=True)
    
    with h2:
        pass
    
    # 期間選擇
    period_map = {"1M": "1mo", "3M": "3mo", "6M": "6mo", "1Y": "1y", "2Y": "2y"}
    pcols = st.columns([1, 1, 1, 1, 1, 8])
    for pc, (lbl, val) in zip(pcols[:5], period_map.items()):
        if pc.button(lbl, key=f"dp_{val}"):
            st.session_state.detail_period = val
            st.rerun()
    
    detail_period = st.session_state.detail_period
    df = get_history(sel_sym, detail_period)
    
    CHART_BG = "#09101f"
    GRID_CLR = "#141e30"
    
    if not df.empty:
        today_tab, chart_tab, news_tab = st.tabs(["⚡ 今日走勢", "📊 圖表分析", "📰 相關新聞"])
    
        # ── 今日即時走勢 ──────────────────────────────────────
        with today_tab:
            df_intra = get_intraday(sel_sym)
    
            if not df_intra.empty and len(df_intra) > 1:
                # ── 取得前一交易日收盤作為走勢起點 ──────────────
                df_prev = get_history(sel_sym, "5d")
                if not df_prev.empty and len(df_prev) >= 2:
                    prev_close = float(df_prev["Close"].iloc[-2])
                else:
                    prev_close = float(df_intra["Open"].iloc[0])
    
                open_price = float(df_intra["Open"].iloc[0])
                last_price = float(df_intra["Close"].iloc[-1])
    
                # 漲跌相對前一日收盤計算
                intra_chg   = last_price - prev_close
                intra_pct   = (intra_chg / prev_close * 100) if prev_close else 0
                intra_color = "#f87171" if intra_chg >= 0 else "#34d399"
                intra_arrow = "▲" if intra_chg >= 0 else "▼"
                today_high  = float(df_intra["High"].max())
                today_low   = float(df_intra["Low"].min())
                today_vol   = int(df_intra["Volume"].sum()) if "Volume" in df_intra else 0
    
                # ── 統計小卡（增加前收欄位）────────────────────
                col_a, col_b, col_c, col_d, col_e = st.columns(5)
                for c, label, val in [
                    (col_a, "前收",   fmt_price(prev_close, sel_kind, sel_name)),
                    (col_b, "開盤",   fmt_price(open_price, sel_kind, sel_name)),
                    (col_c, "最高",   fmt_price(today_high, sel_kind, sel_name)),
                    (col_d, "最低",   fmt_price(today_low,  sel_kind, sel_name)),
                    (col_e, "成交量", f"{today_vol:,}" if today_vol else "—"),
                ]:
                    c.markdown(f"""
                    <div style="background:#0d1423;border:1px solid #1a2540;border-radius:8px;
                         padding:10px 14px;margin-bottom:12px;">
                      <div style="font-family:Space Mono;font-size:0.6rem;color:#475569;
                           letter-spacing:1px;margin-bottom:4px;">{label}</div>
                      <div style="font-family:Space Mono;font-size:1rem;font-weight:700;
                           color:#f1f5f9;">{val}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
                # ── 走勢圖：前收起點 → 今日分鐘線 ─────────────
                # 在盤中資料前插入前一日收盤點，讓折線從前收出發
                prev_ts = df_intra.index[0] - pd.Timedelta(minutes=5)
                anchor_row = pd.DataFrame(
                    {"Open": prev_close, "High": prev_close,
                     "Low": prev_close, "Close": prev_close, "Volume": 0},
                    index=[prev_ts],
                )
                df_plot = pd.concat([anchor_row, df_intra])
    
                fig_intra = go.Figure()
    
                # 前收基準線（實線，帶標籤）
                fig_intra.add_hline(
                    y=prev_close,
                    line=dict(color="#475569", width=1, dash="dash"),
                    annotation_text=f"前收 {fmt_price(prev_close, sel_kind)}",
                    annotation_font=dict(color="#6b7280", size=10, family="Space Mono"),
                    annotation_position="left",
                )
    
                # 今日開盤參考線（點線）
                if abs(open_price - prev_close) / prev_close > 0.001:
                    fig_intra.add_hline(
                        y=open_price,
                        line=dict(color="#334155", width=1, dash="dot"),
                        annotation_text=f"開盤 {fmt_price(open_price, sel_kind)}",
                        annotation_font=dict(color="#475569", size=9, family="Space Mono"),
                        annotation_position="left",
                    )
    
                # ── 計算 Y 軸範圍：以前收為中心，加上緩衝 ────
                line_color = intra_color
                all_prices = list(df_plot["Close"].dropna())
                y_min = min(all_prices)
                y_max = max(all_prices)
                y_pad = (y_max - y_min) * 0.15 if y_max != y_min else y_max * 0.005
                y_range = [y_min - y_pad, y_max + y_pad * 2]   # 上方多留空間放標籤
    
                # 走勢面積線（從前收起點開始，fill 到 y_min 而非 0）
                fig_intra.add_trace(go.Scatter(
                    x=df_plot.index,
                    y=df_plot["Close"],
                    mode="lines",
                    line=dict(color=line_color, width=2),
                    fill="none",
                    name="成交價",
                    hovertemplate="%{x|%H:%M}<br>%{y:,.2f}<extra></extra>",
                ))
    
                # 成交量（獨立子圖，不影響主圖 Y 軸）
                has_vol = "Volume" in df_intra and df_intra["Volume"].sum() > 0
                if has_vol:
                    vol_c = ["#f87171" if c >= o else "#34d399"
                             for c, o in zip(df_intra["Close"], df_intra["Open"])]
                    fig_intra.add_trace(go.Bar(
                        x=df_intra.index, y=df_intra["Volume"],
                        marker_color=vol_c, opacity=0.28,
                        name="成交量", yaxis="y2",
                    ))
    
                # 最新價格標記
                fig_intra.add_trace(go.Scatter(
                    x=[df_intra.index[-1]],
                    y=[last_price],
                    mode="markers+text",
                    marker=dict(color=line_color, size=9, symbol="circle",
                                line=dict(color="#070b14", width=1)),
                    text=[fmt_price(last_price, sel_kind, sel_name)],
                    textposition="top right",
                    textfont=dict(color=line_color, size=11, family="Space Mono"),
                    name="最新", showlegend=False,
                ))
    
                # 前收價右側標籤
                fig_intra.add_annotation(
                    x=1, xref="paper", y=prev_close,
                    text=f"前收 {fmt_price(prev_close, sel_kind)}",
                    showarrow=False,
                    xanchor="left", yanchor="middle",
                    font=dict(color="#6b7280", size=10, family="Space Mono"),
                    bgcolor="rgba(9,16,31,0.7)",
                )
    
                fig_intra.update_layout(
                    paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                    font=dict(color="#94a3b8", family="Space Mono", size=11),
                    xaxis=dict(
                        gridcolor=GRID_CLR, showgrid=True,
                        tickformat="%H:%M",
                        rangeslider=dict(visible=False),
                        showline=True, linecolor=GRID_CLR,
                    ),
                    # 主 Y 軸：縮放到價格區間，右側顯示
                    yaxis=dict(
                        gridcolor=GRID_CLR, showgrid=True,
                        side="right",
                        range=y_range,
                        tickformat=",.0f",
                    ),
                    # 副 Y 軸：成交量，佔圖底部 20%
                    yaxis2=dict(
                        overlaying="y", side="left",
                        showgrid=False, showticklabels=False,
                        range=[0, df_intra["Volume"].max() * 8] if has_vol else [0, 1],
                    ),
                    legend=dict(orientation="h", y=1.06,
                                font=dict(size=10, color="#6b7280"), bgcolor="rgba(0,0,0,0)"),
                    margin=dict(l=0, r=80, t=28, b=10),
                    height=420, hovermode="x unified",
                )
                st.plotly_chart(fig_intra, use_container_width=True)
    
                # 今日摘要列
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:16px;padding:6px 4px;flex-wrap:wrap;">
                  <span style="font-family:Noto Sans TC,sans-serif;font-size:0.82rem;font-weight:500;color:#64748b;">今日區間</span>
                  <span style="font-family:Space Mono;font-size:0.88rem;font-weight:600;color:#34d399;">▼ {fmt_price(today_low, sel_kind)}</span>
                  <span style="font-family:Space Mono;font-size:0.88rem;color:#374151;">—</span>
                  <span style="font-family:Space Mono;font-size:0.88rem;font-weight:600;color:#f87171;">▲ {fmt_price(today_high, sel_kind)}</span>
                  <span style="font-family:Space Mono;font-size:0.85rem;font-weight:600;color:{intra_color};margin-left:12px;">
                    {intra_arrow} 較前收 {intra_chg:+.4f} ({intra_pct:+.2f}%)
                  </span>
                  <span style="font-family:Space Mono;font-size:0.72rem;color:#334155;margin-left:auto;">
                    每 5 分鐘更新 · {datetime.now().strftime("%H:%M:%S")}
                  </span>
                </div>
                """, unsafe_allow_html=True)
    
            else:
                st.info("⏰ 目前非交易時間，或尚無今日盤中資料。請於交易時段查看。")
    
        with chart_tab:
            df2 = df.copy()
            df2["MA5"]   = df2["Close"].rolling(5).mean()
            df2["MA20"]  = df2["Close"].rolling(20).mean()
            df2["MA60"]  = df2["Close"].rolling(60).mean()
            df2["MA240"] = df2["Close"].rolling(240).mean()
    
            fig = go.Figure()
    
            fig.add_trace(go.Candlestick(
                x=df2.index,
                open=df2["Open"], high=df2["High"],
                low=df2["Low"],   close=df2["Close"],
                increasing_line_color="#f87171", increasing_fillcolor="#f87171",
                decreasing_line_color="#34d399", decreasing_fillcolor="#34d399",
                name="K線",
            ))
    
            for col_n, clr, lbl in [
                ("MA5",   "#facc15", "5日線"),
                ("MA20",  "#60a5fa", "月線(20)"),
                ("MA60",  "#f97316", "季線(60)"),
                ("MA240", "#c084fc", "年線(240)"),
            ]:
                fig.add_trace(go.Scatter(
                    x=df2.index, y=df2[col_n],
                    mode="lines", line=dict(color=clr, width=1.4),
                    name=lbl,
                ))
    
            if "Volume" in df2 and df2["Volume"].sum() > 0:
                vol_colors = ["#f87171" if c >= o else "#34d399"
                              for c, o in zip(df2["Close"], df2["Open"])]
                fig.add_trace(go.Bar(
                    x=df2.index, y=df2["Volume"],
                    marker_color=vol_colors, opacity=0.22,
                    name="成交量", yaxis="y2",
                ))
    
            fig.update_layout(
                paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                font=dict(color="#94a3b8", family="Space Mono", size=11),
                xaxis=dict(gridcolor=GRID_CLR, rangeslider=dict(visible=False), showgrid=True),
                yaxis=dict(gridcolor=GRID_CLR, side="right", showgrid=True),
                yaxis2=dict(overlaying="y", side="left", showgrid=False, showticklabels=False,
                            range=[0, df2["Volume"].max() * 5] if "Volume" in df2 and df2["Volume"].sum() > 0 else [0, 1]),
                legend=dict(orientation="h", y=1.06, font=dict(size=10, color="#6b7280"), bgcolor="rgba(0,0,0,0)"),
                margin=dict(l=0, r=10, t=28, b=10),
                height=480, hovermode="x unified",
            )
            st.plotly_chart(fig, use_container_width=True)
    
            st.markdown("""
            <div style="display:flex;gap:20px;padding:6px 4px 0;flex-wrap:wrap;">
              <span style="font-family:Space Mono;font-size:0.8rem;color:#facc15;">━ 5日線</span>
              <span style="font-family:Space Mono;font-size:0.8rem;color:#60a5fa;">━ 月線 (MA20)</span>
              <span style="font-family:Space Mono;font-size:0.8rem;color:#f97316;">━ 季線 (MA60)</span>
              <span style="font-family:Space Mono;font-size:0.8rem;color:#c084fc;">━ 年線 (MA240)</span>
              <span style="font-family:Space Mono;font-size:0.8rem;color:#f87171;">█ 漲</span>
              <span style="font-family:Space Mono;font-size:0.8rem;color:#34d399;">█ 跌</span>
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
                        <div style="font-size:0.95rem;color:#dde6f5;font-weight:500;line-height:1.6;">{title}</div>
                      </a>
                      <div style="font-size:0.75rem;color:#475569;font-family:Space Mono;margin-top:6px;">
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
    f'<div style="text-align:center;font-family:Space Mono;font-size:0.55rem;'
    f'color:#141e30;margin-top:28px;">'
    f'Yahoo Finance · 快取 5min · {datetime.now().strftime("%H:%M:%S")}</div>',
    unsafe_allow_html=True,
)
