# Seoul-Trip

2026/10/26–10/31 首爾六日旅遊行程，可安裝到手機主畫面的網頁 App（PWA）。

## 使用方式
**iPhone**
1. 用 Safari 打開網站
2. 點「分享」→「加入主畫面」

**Android**
1. 用 Chrome 打開網站
2. 點右上角「⋮」→「安裝應用程式」（或「加到主畫面」）

有網路時先打開一次，之後沒網路也能使用。每次打開都會等伺服器回應最新版；完全連不上網路時才用手機裡存的版本。

## 功能
- 點一下行程：看說明、地址、IG 和 NAVER 地圖連結
- 左右滑動或點上方日期：切換日期
- 點 IG／NAVER 地圖：按鈕變成紙飛機／火車，接著直接打開 Instagram／NAVER Map App（沒裝 App 時可改用網頁）
- 準備頁的確認清單：勾選結果只存在這台手機上

## 檔案
- `index.html`：行程頁面
- `manifest.webmanifest`：App 名稱與圖示設定
- `sw.js`：離線快取
- `icon-*.png`：主畫面圖示
- `tools/build_nmap.py`：新增 NAVER 地圖連結後執行一次，查出地點座標，讓手機能直接打開 NAVER Map App
