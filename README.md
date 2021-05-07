# 歷年水庫水情資料爬取

2020年台灣梅雨季降雨不豐，加上遭逢56年來罕見夏季無颱風登陸的窘境，各地水庫紛紛見底，旱象至今未見緩解跡象。這場旱災有多嚴重？哪邊的水庫最渴？為了解答這些問題，就必須先拿到各地水庫的水情資料。

### 資料搜集方式
用Python的selenium自動化從「[台灣地區主要水庫蓄水量報告表](https://fhy.wra.gov.tw/ReservoirPage_2011/StorageCapacity.aspx)」下載歷年資料。

### 資料限制
資料中並無水庫的地理位置資料，若要結合地理特徵，需另結合[水庫的地理資料](https://gic.wra.gov.tw/Gis/Gic/DataIndex/Data/Main.aspx)。

### 參考資料
- [GitHub]infographicstw/[reservoir-history-crawler專案](https://github.com/infographicstw/reservoir-history-crawler)

- 《天下雜誌》「[即時水情地圖》下雨了，台灣水庫解渴了嗎？｜互動專題｜天下雜誌](https://web.cw.com.tw/drought-2021/index.html)
」
