import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import time

# ── 頁面設定 ──────────────────────────────────────────────
st.set_page_config(
    page_title="每日財經雷達",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 自訂 CSS ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;700;900&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans TC', sans-serif;
}

/* 背景 */
.stApp {
    background: #0a0e1a;
    color: #e2e8f0;
}

/* 側邊欄 */
section[data-testid="stSidebar"] {
    background: #0d1224 !important;
    border-right: 1px solid #1e293b;
}

/* 標題區塊 */
.hero-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    border: 1px solid #312e81;
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 30% 50%, rgba(99,102,241,0.08) 0%, transparent 60%);
}
.hero-title {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #a5b4fc;
    letter-spacing: 2px;
    margin: 0;
}
.hero-sub {
    font-size: 0.85rem;
    color: #64748b;
    font-family: 'Space Mono', monospace;
    letter-spacing: 1px;
    margin-top: 4px;
}

/* 指標卡片 */
.metric-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 10px;
    padding: 18px 20px;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: #4f46e5; }
.metric-name {
    font-size: 0.72rem;
    color: #6b7280;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    font-family: 'Space Mono', monospace;
}
.metric-value {
    font-size: 1.6rem;
    font-weight: 700;
    font-family: 'Space Mono', monospace;
    color: #f1f5f9;
    margin: 4px 0 2px;
}
.metric-delta-up   { color: #f87171; font-size: 0.85rem; font-family: 'Space Mono', monospace; }
.metric-delta-down { color: #34d399; font-size: 0.85rem; font-family: 'Space Mono', monospace; }

/* 區塊標題 */
.section-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #818cf8;
    border-left: 3px solid #4f46e5;
    padding-left: 10px;
    margin: 28px 0 14px;
}

/* 新聞卡片 */
.news-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
}
.news-card:hover { border-color: #4f46e5; }
.news-title { font-size: 0.92rem; color: #c7d2fe; font-weight: 500; }
.news-source { font-size: 0.72rem; color: #4b5563; font-family: 'Space Mono', monospace; margin-top: 4px; }

/* 表格 */
.stDataFrame { border-radius: 8px; overflow: hidden; }

/* 按鈕 */
.stButton > button {
    background: #312e81;
    color: #a5b4fc;
    border: 1px solid #4f46e5;
    border-radius: 6px;
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 1px;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: #4338ca;
    color: #fff;
    border-color: #818cf8;
}

/* 捲動條 */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0a0e1a; }
::-webkit-scrollbar-thumb { background: #312e81; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ── 資料擷取函式 ─────────────────────────────────────────

@st.cache_data(ttl=300)
def get_quote(ticker: str) -> dict:
    """取得單一股票/指數即時報價"""
    try:
        t = yf.Ticker(ticker)
        info = t.fast_info
        hist = t.history(period="2d", interval="1d")
        if len(hist) < 2:
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
    """取得歷史 K 線"""
    try:
        t = yf.Ticker(ticker)
        df = t.history(period=period)
        df.index = pd.to_datetime(df.index)
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=600)
def get_news(ticker: str, n: int = 8) -> list:
    """取得相關新聞"""
    try:
        t = yf.Ticker(ticker)
        return t.news[:n] if t.news else []
    except Exception:
        return []


@st.cache_data(ttl=300)
def get_fx_rates() -> dict:
    """取得主要外匯報價"""
    pairs = {
        "USD/TWD": "TWD=X",
        "EUR/USD": "EURUSD=X",
        "USD/JPY": "JPY=X",
        "GBP/USD": "GBPUSD=X",
        "USD/CNY": "CNY=X",
    }
    result = {}
    for label, sym in pairs.items():
        q = get_quote(sym)
        result[label] = q
    return result


@st.cache_data(ttl=300)
def get_commodities() -> dict:
    """取得大宗商品"""
    items = {
        "黃金 (XAU/USD)": "GC=F",
        "原油 WTI":       "CL=F",
        "布蘭特原油":     "BZ=F",
        "天然氣":         "NG=F",
        "白銀":           "SI=F",
    }
    result = {}
    for label, sym in items.items():
        result[label] = get_quote(sym)
    return result


# ── 繪圖函式 ──────────────────────────────────────────────

def candlestick_chart(df: pd.DataFrame, title: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"],
        low=df["Low"],  close=df["Close"],
        increasing_line_color="#f87171",
        decreasing_line_color="#34d399",
        name="K線",
    ))
    # 成交量
    colors = ["#f87171" if c >= o else "#34d399"
              for c, o in zip(df["Close"], df["Open"])]
    fig.add_trace(go.Bar(
        x=df.index, y=df["Volume"],
        marker_color=colors, opacity=0.35,
        name="成交量", yaxis="y2"
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(color="#a5b4fc", size=14, family="Space Mono")),
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font=dict(color="#94a3b8", family="Space Mono"),
        xaxis=dict(
            gridcolor="#1f2937", showgrid=True,
            rangeslider=dict(visible=False),
        ),
        yaxis=dict(gridcolor="#1f2937", showgrid=True, side="right"),
        yaxis2=dict(overlaying="y", side="left", showgrid=False,
                    showticklabels=False, range=[0, df["Volume"].max() * 4]),
        legend=dict(orientation="h", y=1.05,
                    font=dict(size=10, color="#6b7280")),
        margin=dict(l=10, r=10, t=40, b=10),
        height=380,
    )
    return fig


def hex_to_rgba(hex_color: str, alpha: float = 0.08) -> str:
    """Convert #rrggbb to rgba(r,g,b,alpha)"""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def line_chart(df: pd.DataFrame, col: str, title: str, color: str = "#818cf8") -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df[col],
        mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy",
        fillcolor=hex_to_rgba(color, 0.08),
        name=col,
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(color="#a5b4fc", size=13, family="Space Mono")),
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font=dict(color="#94a3b8", family="Space Mono"),
        xaxis=dict(gridcolor="#1f2937"),
        yaxis=dict(gridcolor="#1f2937"),
        margin=dict(l=10, r=10, t=40, b=10),
        height=260,
        showlegend=False,
    )
    return fig


# ── 側邊欄 ────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="section-title">⚙ 設定</div>', unsafe_allow_html=True)

    market = st.selectbox("主要市場", ["台灣 (TWII)", "美國 (SPY)", "日本 (N225)", "香港 (HSI)"])
    MARKET_MAP = {
        "台灣 (TWII)":  "^TWII",
        "美國 (SPY)":   "SPY",
        "日本 (N225)":  "^N225",
        "香港 (HSI)":   "^HSI",
    }
    main_ticker = MARKET_MAP[market]

    period = st.selectbox("K線期間", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)

    st.markdown('<div class="section-title">📌 自選股</div>', unsafe_allow_html=True)
    custom_raw = st.text_area(
        "輸入股票代號（每行一個）",
        value="2330.TW\n2317.TW\nAAPL\nNVDA\nTSLA",
        height=130,
    )
    custom_tickers = [t.strip().upper() for t in custom_raw.splitlines() if t.strip()]

    refresh = st.button("🔄 立即更新資料", use_container_width=True)
    if refresh:
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown(
        '<div style="font-size:0.7rem;color:#374151;font-family:Space Mono;line-height:1.8;">'
        f'更新時間<br>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br><br>'
        '資料來源：Yahoo Finance<br>快取：5 分鐘</div>',
        unsafe_allow_html=True,
    )


# ── 主體 ──────────────────────────────────────────────────

# Hero Header
st.markdown(f"""
<div class="hero-header">
  <div class="hero-title">📡 每日財經雷達</div>
  <div class="hero-sub">DAILY FINANCIAL INTELLIGENCE · {datetime.now().strftime('%Y.%m.%d  %A').upper()}</div>
</div>
""", unsafe_allow_html=True)


# ── Tab 導覽 ──────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["🌐 市場概覽", "📈 K線圖表", "💱 外匯商品", "🏭 自選股", "📰 財經新聞"]
)


# ═══════════════════════════════════════════════
# TAB 1：市場概覽
# ═══════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">全球主要指數</div>', unsafe_allow_html=True)

    INDICES = {
        "台灣加權": "^TWII",
        "台灣夜盤": "TWN=F",
        "S&P 500":  "^GSPC",
        "NASDAQ":   "^IXIC",
        "道瓊":     "^DJI",
        "日經 225": "^N225",
        "恒生指數": "^HSI",
        "上証":     "000001.SS",
        "德國 DAX": "^GDAXI",
    }

    cols = st.columns(4)
    for i, (name, sym) in enumerate(INDICES.items()):
        q = get_quote(sym)
        col = cols[i % 4]
        arrow = "▲" if q["pct"] >= 0 else "▼"
        delta_cls = "metric-delta-up" if q["pct"] >= 0 else "metric-delta-down"
        price_fmt = f"{q['price']:,.2f}" if q['price'] < 100000 else f"{q['price']:,.0f}"
        # 台灣夜盤加上特殊標籤
        night_badge = ' <span style="font-size:0.6rem;background:#1e1b4b;color:#a5b4fc;padding:2px 6px;border-radius:4px;vertical-align:middle;">夜盤</span>' if name == "台灣夜盤" else ""
        col.markdown(f"""
        <div class="metric-card">
          <div class="metric-name">{name}{night_badge}</div>
          <div class="metric-value">{price_fmt}</div>
          <div class="{delta_cls}">{arrow} {q['change']:+.2f} ({q['pct']:+.2f}%)</div>
        </div>
        """, unsafe_allow_html=True)

    # ── 虛擬貨幣 ──────────────────────────────────────────
    st.markdown('<div class="section-title">🪙 虛擬貨幣（對美元）</div>', unsafe_allow_html=True)

    CRYPTO = {
        "比特幣 BTC": "BTC-USD",
        "以太幣 ETH": "ETH-USD",
        "泰達幣 USDT": "USDT-USD",
        "USDC":        "USDC-USD",
    }

    ccols = st.columns(4)
    for col, (name, sym) in zip(ccols, CRYPTO.items()):
        q = get_quote(sym)
        arrow = "▲" if q["pct"] >= 0 else "▼"
        delta_cls = "metric-delta-up" if q["pct"] >= 0 else "metric-delta-down"
        # 穩定幣顯示小數4位，BTC/ETH顯示整數或2位
        if sym in ("USDT-USD", "USDC-USD"):
            price_fmt = f"{q['price']:.4f}"
        elif q["price"] > 1000:
            price_fmt = f"{q['price']:,.0f}"
        else:
            price_fmt = f"{q['price']:,.2f}"
        col.markdown(f"""
        <div class="metric-card" style="border-color:#1e3a5f;">
          <div class="metric-name">{name}</div>
          <div class="metric-value" style="font-size:1.3rem;">{price_fmt}</div>
          <div class="{delta_cls}">{arrow} {q['pct']:+.2f}%</div>
          <div style="font-size:0.7rem;color:#4b5563;font-family:Space Mono;margin-top:2px;">USD</div>
        </div>
        """, unsafe_allow_html=True)

    # BTC & ETH 走勢圖
    st.markdown('<div class="section-title">BTC / ETH 走勢</div>', unsafe_allow_html=True)
    cr1, cr2 = st.columns(2)
    btc_df = get_history("BTC-USD", "3mo")
    eth_df = get_history("ETH-USD", "3mo")
    if not btc_df.empty:
        cr1.plotly_chart(line_chart(btc_df, "Close", "比特幣 BTC · 近 3 個月", "#f59e0b"),
                         use_container_width=True)
    if not eth_df.empty:
        cr2.plotly_chart(line_chart(eth_df, "Close", "以太幣 ETH · 近 3 個月", "#818cf8"),
                         use_container_width=True)

    # 主市場走勢圖
    st.markdown('<div class="section-title">主要市場走勢</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    for col, (label, sym) in zip([c1, c2], [("S&P 500", "^GSPC"), ("台灣加權", "^TWII")]):
        df = get_history(sym, period)
        if not df.empty:
            col.plotly_chart(line_chart(df, "Close", label), use_container_width=True)

    # 恐懼貪婪替代指標（VIX）
    st.markdown('<div class="section-title">市場波動度 (VIX)</div>', unsafe_allow_html=True)
    vix = get_quote("^VIX")
    vix_df = get_history("^VIX", "3mo")
    v1, v2 = st.columns([1, 3])
    with v1:
        level = "🟢 低波動" if vix["price"] < 15 else ("🟡 中度" if vix["price"] < 25 else "🔴 高波動")
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;margin-top:10px;">
          <div class="metric-name">VIX 指數</div>
          <div class="metric-value" style="font-size:2.4rem;">{vix['price']:.2f}</div>
          <div style="color:#a5b4fc;font-size:0.9rem;margin-top:6px;">{level}</div>
        </div>
        """, unsafe_allow_html=True)
    with v2:
        if not vix_df.empty:
            st.plotly_chart(line_chart(vix_df, "Close", "VIX 近 3 個月", "#f59e0b"),
                            use_container_width=True)


# ═══════════════════════════════════════════════
# TAB 2：K線圖表
# ═══════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">互動式 K 線</div>', unsafe_allow_html=True)
    chart_ticker = st.text_input("輸入代號（例：2330.TW / AAPL / ^GSPC）",
                                  value=main_ticker, key="chart_input")
    chart_period = st.select_slider("期間", options=["1mo","3mo","6mo","1y","2y"], value=period)

    if chart_ticker:
        df_k = get_history(chart_ticker.upper(), chart_period)
        if not df_k.empty:
            st.plotly_chart(
                candlestick_chart(df_k, f"{chart_ticker.upper()} · {chart_period}"),
                use_container_width=True,
            )
            # 均線分析
            st.markdown('<div class="section-title">均線分析</div>', unsafe_allow_html=True)
            df_k["MA5"]  = df_k["Close"].rolling(5).mean()
            df_k["MA20"] = df_k["Close"].rolling(20).mean()
            df_k["MA60"] = df_k["Close"].rolling(60).mean()

            fig_ma = go.Figure()
            for col, clr, lbl in [
                ("Close", "#818cf8", "收盤"),
                ("MA5",   "#34d399", "MA5"),
                ("MA20",  "#fbbf24", "MA20"),
                ("MA60",  "#f87171", "MA60"),
            ]:
                fig_ma.add_trace(go.Scatter(
                    x=df_k.index, y=df_k[col],
                    mode="lines", line=dict(color=clr, width=1.5), name=lbl,
                ))
            fig_ma.update_layout(
                paper_bgcolor="#111827", plot_bgcolor="#111827",
                font=dict(color="#94a3b8", family="Space Mono"),
                xaxis=dict(gridcolor="#1f2937"),
                yaxis=dict(gridcolor="#1f2937"),
                legend=dict(orientation="h", y=1.05, font=dict(size=10, color="#6b7280")),
                margin=dict(l=10, r=10, t=20, b=10), height=260,
            )
            st.plotly_chart(fig_ma, use_container_width=True)
        else:
            st.warning("無法取得該代號資料，請確認代號格式")


# ═══════════════════════════════════════════════
# TAB 3：外匯 & 商品
# ═══════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">主要外匯</div>', unsafe_allow_html=True)
    fx = get_fx_rates()
    fcols = st.columns(len(fx))
    for col, (label, q) in zip(fcols, fx.items()):
        arrow = "▲" if q["pct"] >= 0 else "▼"
        delta_cls = "metric-delta-up" if q["pct"] >= 0 else "metric-delta-down"
        col.markdown(f"""
        <div class="metric-card">
          <div class="metric-name">{label}</div>
          <div class="metric-value" style="font-size:1.3rem;">{q['price']:.4f}</div>
          <div class="{delta_cls}">{arrow} {q['pct']:+.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

    # 外匯走勢
    st.markdown('<div class="section-title">TWD 走勢</div>', unsafe_allow_html=True)
    twd_df = get_history("TWD=X", "3mo")
    if not twd_df.empty:
        st.plotly_chart(line_chart(twd_df, "Close", "USD/TWD · 近 3 個月", "#34d399"),
                        use_container_width=True)

    # 大宗商品
    st.markdown('<div class="section-title">大宗商品</div>', unsafe_allow_html=True)
    comms = get_commodities()
    ccols = st.columns(len(comms))
    for col, (label, q) in zip(ccols, comms.items()):
        arrow = "▲" if q["pct"] >= 0 else "▼"
        delta_cls = "metric-delta-up" if q["pct"] >= 0 else "metric-delta-down"
        col.markdown(f"""
        <div class="metric-card">
          <div class="metric-name">{label}</div>
          <div class="metric-value" style="font-size:1.2rem;">{q['price']:,.2f}</div>
          <div class="{delta_cls}">{arrow} {q['pct']:+.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

    # 黃金走勢
    st.markdown('<div class="section-title">黃金走勢</div>', unsafe_allow_html=True)
    gold_df = get_history("GC=F", "6mo")
    oil_df  = get_history("CL=F", "6mo")
    g1, g2 = st.columns(2)
    if not gold_df.empty:
        g1.plotly_chart(line_chart(gold_df, "Close", "黃金 · 近 6 個月", "#fbbf24"),
                        use_container_width=True)
    if not oil_df.empty:
        g2.plotly_chart(line_chart(oil_df, "Close", "WTI 原油 · 近 6 個月", "#94a3b8"),
                        use_container_width=True)


# ═══════════════════════════════════════════════
# TAB 4：自選股
# ═══════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">自選股報價</div>', unsafe_allow_html=True)

    rows = []
    for sym in custom_tickers:
        q = get_quote(sym)
        rows.append({
            "代號": sym,
            "現價": round(q["price"], 2),
            "漲跌": round(q["change"], 2),
            "漲跌幅 %": round(q["pct"], 2),
            "前收": round(q["prev"], 2),
        })

    if rows:
        df_watch = pd.DataFrame(rows)

        # 顏色格式化
        def color_delta(val):
            color = "#f87171" if val > 0 else ("#34d399" if val < 0 else "#94a3b8")
            return f"color: {color}"

        styled = df_watch.style \
            .applymap(color_delta, subset=["漲跌", "漲跌幅 %"]) \
            .format({"現價": "{:,.2f}", "漲跌": "{:+.2f}", "漲跌幅 %": "{:+.2f}%", "前收": "{:,.2f}"})

        st.dataframe(styled, use_container_width=True, hide_index=True)

        # 漲跌長條圖
        st.markdown('<div class="section-title">漲跌幅比較</div>', unsafe_allow_html=True)
        colors = ["#f87171" if v >= 0 else "#34d399" for v in df_watch["漲跌幅 %"]]
        fig_bar = go.Figure(go.Bar(
            x=df_watch["代號"], y=df_watch["漲跌幅 %"],
            marker_color=colors,
            text=df_watch["漲跌幅 %"].apply(lambda x: f"{x:+.2f}%"),
            textposition="outside",
        ))
        fig_bar.update_layout(
            paper_bgcolor="#111827", plot_bgcolor="#111827",
            font=dict(color="#94a3b8", family="Space Mono"),
            xaxis=dict(gridcolor="#1f2937"),
            yaxis=dict(gridcolor="#1f2937", zeroline=True, zerolinecolor="#374151"),
            margin=dict(l=10, r=10, t=20, b=10), height=300,
            showlegend=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # 個股細部 K 線
        st.markdown('<div class="section-title">個股走勢</div>', unsafe_allow_html=True)
        selected = st.selectbox("選擇個股查看走勢", custom_tickers)
        if selected:
            df_s = get_history(selected, period)
            if not df_s.empty:
                st.plotly_chart(candlestick_chart(df_s, selected), use_container_width=True)


# ═══════════════════════════════════════════════
# TAB 5：財經新聞
# ═══════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">財經新聞</div>', unsafe_allow_html=True)

    news_src = st.selectbox(
        "選擇新聞來源（代號）",
        ["SPY", "^TWII", "AAPL", "NVDA", "GC=F", "^GSPC"] + custom_tickers[:5],
    )

    with st.spinner("載入新聞..."):
        news_list = get_news(news_src, n=12)

    if news_list:
        for item in news_list:
            title   = item.get("title", "（無標題）")
            link    = item.get("link", "#")
            pub_ts  = item.get("providerPublishTime", 0)
            source  = item.get("publisher", "未知來源")
            pub_dt  = datetime.fromtimestamp(pub_ts).strftime("%Y-%m-%d %H:%M") if pub_ts else ""

            st.markdown(f"""
            <div class="news-card">
              <a href="{link}" target="_blank" style="text-decoration:none;">
                <div class="news-title">{title}</div>
              </a>
              <div class="news-source">📰 {source} &nbsp;·&nbsp; {pub_dt}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("目前無法取得新聞，請稍後再試")

    # 熱門財經關鍵字（透過 yf 的市場新聞）
    st.markdown('<div class="section-title">市場熱門</div>', unsafe_allow_html=True)
    trending = ["AI 晶片", "聯準會利率", "台積電", "油價", "黃金", "美元走強", "通膨數據", "科技股"]
    tag_html = " ".join(
        f'<span style="background:#1e293b;color:#a5b4fc;padding:4px 10px;'
        f'border-radius:20px;font-size:0.78rem;font-family:Space Mono;'
        f'margin:3px;display:inline-block;">{t}</span>'
        for t in trending
    )
    st.markdown(tag_html, unsafe_allow_html=True)
