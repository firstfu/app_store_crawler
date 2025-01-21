# App Store 爬蟲程式

這是一個簡單的 Apple App Store 爬蟲程式，可以搜索並顯示應用程式的詳細信息，獲取用戶評論，計算應用可信度評分，並將所有數據保存到 JSON 文件中。

## 功能特點

- 支持關鍵字搜索
- 顯示應用詳細信息（名稱、開發者、評分等）
- 獲取應用最新評論（預設每個應用獲取 50 條）
- 智能可信度評分系統
- 詳細的價格分析（免費/付費、應用內購買等）
- 支持自定義搜索地區和結果數量
- 自動將結果保存為 JSON 文件（按可信度評分排序）
- 可選擇是否在終端顯示詳細信息

## 可信度評分系統

程式使用多維度分析來計算應用的可信度評分（0-100 分），考慮以下因素：

1. **評分權重 (40%)**

   - 應用的平均評分

2. **評分數量權重 (30%)**

   - 使用對數函數平滑處理評分數量
   - 防止評分數量過少的應用獲得過高權重

3. **評論質量 (20%)**

   - 評論內容長度
   - 有效評論比例（過濾無意義評論）
   - 評論內容多樣性檢測

4. **時間衰減 (10%)**
   - 根據應用更新時間計算時間衰減因子
   - 優先展示較新的應用

額外的評分調整：

- 付費應用評分獲得 10%的加權（因為付費應用一般評分更嚴格）
- 對於高分（>4.8）但評分數量少（<100）的應用進行降權
- 檢測重複或無意義的評論

## 價格分析系統

程式會詳細分析每個應用的價格信息：

1. **基本價格信息**

   - 價格類型（免費/付費）
   - 當前價格
   - 幣種
   - 原價（如果有）
   - 價格等級（Tier）

2. **應用內購買**

   - 是否支持應用內購買
   - 購買選項（如果有）

3. **統計分析**
   - 總應用數量
   - 免費應用數量
   - 付費應用數量
   - 平均價格
   - 最高價格
   - 最低付費價格

## 安裝依賴

```bash
pip install -r requirements.txt
```

## 使用方法

1. 運行程式：

```bash
python app_store_crawler.py
```

2. 根據提示輸入要搜索的應用關鍵字

3. 程式會自動：
   - 搜索相關應用
   - 獲取每個應用的最新評論
   - 分析價格信息
   - 計算可信度評分
   - 將數據保存到 JSON 文件（文件名格式：app*store*關鍵字\_時間戳.json）
   - 詢問是否要在終端顯示詳細信息

## 輸出信息

### JSON 文件結構

文件包含兩個主要部分：

#### 1. 統計信息

- 總應用數
- 免費應用數
- 付費應用數
- 平均價格
- 最高價格
- 最低付費價格

#### 2. 應用列表（按可信度評分排序）

每個應用包含：

##### 基本信息

- 應用名稱
- 開發者
- 應用類別
- 價格信息（類型、當前價格、幣種、原價等）
- 評分
- 評分數量
- 版本
- 應用大小
- 最低系統要求
- App Store 链接
- 更新日期
- 應用描述
- 可信度評分

##### 評論數據

每個應用包含一個評論數組，每條評論包含：

- 評論者
- 評分
- 標題
- 內容
- 版本
- 時間

### 終端輸出（可選）

顯示應用基本信息，包括名稱、開發者、完整價格信息、評分和可信度評分等。
