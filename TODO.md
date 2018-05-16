- 改善log, 弄成進度條

- 弄成 package
- 新增一個 dev branch
- 取得 gist 裡頭對應的 file name 以最快的速度取得更新結果比對 hash

- 改成log
- 登入 github?
- flask app 當 UI? 輸入 github token, 最近被更新的 gist etc
- 弄成 Github Apps

- add google fire test 
- 允許 新手用 test account 測試, ENV 切換環境

- add initial func in app.main
    * 自動下載 chromedriver
- argc, 讓使用者可以選擇要不要 mulit-process, 等待gist render 時間, 要raw gist 還是截圖 etc..
- evernote 端刪除對應的note, gist 更新的處理（不要產生error)

- 自動設定 Evernote Tags
- 如果 evernote OCR 準度不高, 把 raw gist 也丟入 evernote
    - 可以判斷 gist type 嘛？ 判斷 type 來決定要不要截圖
- multi-thread 一次截多個 page 的圖, 搭配 headless
- 把所有重要的 noteboks, script 弄成 gist 同步
- 用 XHTML style note 內容
- 處理 evernote 單方向刪除已經被同步的 note 
- 切換到 python 3 環境
- Docker

處理圖片最下面重複的部分

加入 References
- 取得最新的 gist raw data 
    - https://stackoverflow.com/a/37997658/3859572
