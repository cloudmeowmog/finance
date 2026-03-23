# 📡 每日財經雷達 — Daily Financial Radar

> 部署在 Streamlit 上的即時財經儀表板，整合全球股市、外匯、期貨原物料、加密貨幣資料。

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

1. 將 `app.py`、`requirements.txt`、`README.md` 上傳到 GitHub 公開 repo
2. 前往 [share.streamlit.io](https://share.streamlit.io)
3. 點選 **New app** → 選擇 repo 與 `app.py`
4. 點 **Deploy** — 約 1~2 分鐘完成

> 不需要任何 API Key，所有資料透過 Yahoo Finance 免費取得。

---

## ✨ 功能一覽

### 四大分頁（左側導覽列）

| 分頁 | 內容 |
|------|------|
| 🌐 市場概況 | 台灣加權、台灣夜盤、S&P500、NASDAQ、道瓊、費半、日經、恒生、上証、DAX、FTSE、VIX |
| 💱 貨幣 | 12 種外幣對新台幣匯率（USD、EUR、JPY、GBP、CNY、HKD、AUD、NZD、CAD、CHF、KRW、SGD） |
| 🏭 期貨原物料 | 黃金、白銀、鉑金、銅、WTI 原油、布蘭特、天然氣、小麥、玉米、黃豆 |
| 🪙 加密貨幣 | BTC、ETH、BNB、SOL、XRP、ADA、DOGE、USDT、USDC（均對美元） |

### 卡片區（上方）
- 每張卡片顯示：名稱、即時價格、漲跌幅、30 日走勢折線圖
- 點「▼ 展開」後，下方顯示詳細大圖

### 詳細圖表區（下方）
- **K 線圖**（漲紅跌綠，台灣模式）+ 成交量
- **均線**：5日線（黃）、月線 MA20（藍）、季線 MA60（橘）、年線 MA240（紫）
- **期間切換**：1M / 3M / 6M / 1Y / 2Y
- **相關新聞**：Yahoo Finance 即時新聞

### 側邊欄
- 四個分頁按鈕，點選切換
- 「🔄 更新資料」可強制清除快取
- 點左上角 `>` 可收合側邊欄，讓主畫面更寬

---

## 📊 股票代號格式參考

| 市場 | 範例 |
|------|------|
| 台股 | `2330.TW`、`2317.TW` |
| 美股 | `AAPL`、`NVDA`、`TSLA` |
| 指數 | `^GSPC`（S&P500）、`^TWII`（台灣加權） |
| 外匯 | `TWD=X`（美元兌台幣） |
| 期貨 | `GC=F`（黃金）、`CL=F`（WTI 原油） |
| 加密 | `BTC-USD`、`ETH-USD` |

---

## 🔄 快取機制

| 資料類型 | 更新頻率 |
|---------|---------|
| 即時報價 | 每 **5 分鐘** |
| 歷史 K 線 / 新聞 / 走勢圖 | 每 **10 分鐘** |
| 手動更新 | 側邊欄「🔄 更新資料」按鈕 |

---

## 📦 技術棧

| 套件 | 用途 |
|------|------|
| **Streamlit** | UI 框架與部署 |
| **yfinance** | Yahoo Finance 資料擷取 |
| **Plotly** | 互動式 K 線與走勢圖 |
| **Pandas** | 資料處理與均線計算 |

---

## 📁 檔案結構

```
finance/
├── app.py            # 主程式
├── requirements.txt  # 套件清單
└── README.md         # 說明文件
```
