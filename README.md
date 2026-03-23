# 📡 每日財經雷達 — Daily Financial Radar

> 一個部署在 Streamlit 上的即時財經儀表板，每天自動擷取全球市場資料。

---

## 🚀 快速啟動（本機）

```bash
# 1. 安裝依賴
pip install -r requirements.txt

# 2. 啟動
streamlit run app.py
```

瀏覽器開啟 `http://localhost:8501` 即可使用。

---

## ☁️ 部署到 Streamlit Cloud（免費）

1. 將此資料夾上傳到你的 **GitHub** 公開 repo
2. 前往 [share.streamlit.io](https://share.streamlit.io)
3. 點選 **New app** → 選擇你的 repo 與 `app.py`
4. 點 **Deploy** — 幾分鐘後即完成

> 無需任何 API Key，所有資料透過 Yahoo Finance 免費取得。

---

## ✨ 功能一覽

| Tab | 功能 |
|-----|------|
| 🌐 市場概覽 | 全球 8 大指數即時報價、S&P 500 / 台灣加權走勢、VIX 恐慌指數 |
| 📈 K 線圖表 | 任意股票代號互動式日 K 線 + MA5/20/60 均線分析 |
| 💱 外匯商品 | USD/TWD、EUR、JPY 等外匯 + 黃金、原油、天然氣大宗商品 |
| 🏭 自選股 | 自訂股票清單、漲跌幅排行、個股走勢 K 線 |
| 📰 財經新聞 | Yahoo Finance 即時財經新聞 |

---

## ⚙️ 股票代號格式

| 市場 | 範例 |
|------|------|
| 台股 | `2330.TW`、`2317.TW` |
| 美股 | `AAPL`、`NVDA`、`TSLA` |
| 指數 | `^GSPC`（S&P 500）、`^TWII`（台灣加權） |
| 外匯 | `TWD=X`（美元兌台幣） |
| 期貨 | `GC=F`（黃金）、`CL=F`（WTI 原油） |

---

## 🔄 快取機制

- 報價資料：每 **5 分鐘** 自動更新
- 歷史 K 線 & 新聞：每 **10 分鐘** 更新
- 側邊欄「立即更新」按鈕可強制清除快取

---

## 📦 技術棧

- **Streamlit** — UI 框架
- **yfinance** — Yahoo Finance 資料擷取
- **Plotly** — 互動式圖表
- **Pandas** — 資料處理
