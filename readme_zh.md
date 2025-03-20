[English](https://github.com/felixszeto/whisper-stream-gui/blob/main/README.md)

# Whisper Stream GUI

本專案提供了一個圖形使用者介面 (GUI)，用於使用 Whisper 進行即時音訊轉錄。

## 簡介

Whisper Stream GUI 是一個使用者友善的應用程式，讓您可以使用 Whisper 模型即時轉錄音訊。它設計為易於使用，並提供一個簡單的介面來串流音訊和檢視轉錄內容。

<img src="https://github.com/user-attachments/assets/f00cf0ec-01cc-4409-891c-3280af5d2ef5" width="300" alt="Gui for whisper">
<img src="https://github.com/user-attachments/assets/1229ccbe-3884-4e52-869e-a2be958b79e6" width="300" alt="Real-Time transcription">

## 安裝

要安裝和執行 Whisper Stream GUI，請按照以下步驟操作：

1.  **先決條件：**
    -   您的系統上已安裝 Python 3.9 或更高版本。您可以從 [https://www.python.org/](https://www.python.org/) 下載 Python。
    -   `pip` 套件安裝程式。 `pip` 通常包含在 Python 安裝中。
    -   PyTorch 版本大於 1.0.0（您可以安裝最新版本）。請按照 [https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/) 上的安裝說明，為您的系統安裝正確的版本。

2.  **安裝 Whisper：**
    請按照 Whisper 儲存庫上的說明進行安裝：[https://github.com/openai/whisper](https://github.com/openai/whisper)。

3.  **建議：安裝 Conda（可選但建議）：**
    建議使用 Conda 來管理您的 Python 環境。您可以從 [https://www.anaconda.com/products/distribution](https://www.anaconda.com/products/distribution) 下載 Conda。

4.  **建立 Conda 環境（可選但建議）：**
    如果您選擇使用 Conda，請為此專案建立一個新的環境：

    ```bash
    conda create -n whisper python=3.9
    conda activate whisper
    ```

5.  **複製儲存庫：**
    您可以將其複製到您的本機電腦。

    ```bash
    git clone https://github.com/felixszeto/whisper-stream-gui.git
    cd whisper-stream-gui
    ```

6.  **安裝依賴套件：**
    在您的終端機中導航到專案目錄，並使用 pip 安裝所需的 Python 套件。

    ```bash
    pip install -r requirements.txt
    ```


7.  **執行 GUI：**
    執行 `start_gui.bat` 批次檔以啟動 Whisper Stream GUI 應用程式。

    ```bash
    start_gui.bat
    ```

    這將在您的網頁瀏覽器中啟動 Gradio 介面。

    **HTTPS 憑證設定（麥克風存取權限需要）：**
    由於透過不安全的 HTTP 使用麥克風的安全性限制，HTTPS 設定與 SSL 憑證對於瀏覽器允許麥克風存取權限是**必需的**。
    要設定 HTTPS，您需要設定 SSL 憑證：
    -   修改 `app.py` 腳本以指定您的 SSL 憑證檔案的路徑。
    -   在 `app.py` 中找到 `app.launch()` 函數。
    -   將 `ssl_keyfile` 和 `ssl_certfile` 參數調整為您的金鑰和憑證檔案的正確路徑。
    -   確保憑證檔案（預設為 `key.pem` 和 `chain.pem`）放置在 `ssl/` 目錄中，或相應地更新腳本中的路徑。

## Whisper 模型選擇

**預設模型為 `faster-whisper-large-v3`**。

請從 [Hugging Face](https://huggingface.co/Systran/faster-whisper-large-v3) **下載 `faster-whisper-large-v3` 模型文件**，並將它們放在 `faster-whisper-large-v3/` 資料夾中。

您可以透過修改 `app.py` 檔案來變更用於轉錄的 Whisper 模型。

-   開啟 `app.py` 檔案。
-   找到 `model = whisper.load_model("tiny")` 行。
-   將 `"tiny"` 替換為所需的模型大小。可用的模型有：`tiny`、`tiny_en`、`base`、`base_en`、`small`、`small_en`、`medium`、`medium_en`、`large` 和 `turbo`。

| 大小   | 參數     | 僅限英文模型 | 多語言模型 | 需要 VRAM | 相對速度 |
| :----- | :------- | :----------- | :----------- | :-------- | :------- |
| tiny   | 39 M     | tiny.en      | tiny         | ~1 GB     | ~10x     |
| base   | 74 M     | base.en      | base         | ~1 GB     | ~7x      |
| small  | 244 M    | small.en     | small        | ~2 GB     | ~4x      |
| medium | 769 M    | medium.en    | medium       | ~5 GB     | ~2x      |
| large  | 1550 M   | N/A          | large        | ~10 GB    | 1x       |
| turbo  | 809 M    | N/A          | turbo        | ~6 GB     | ~8x      |


## 使用方式

1.  一旦 GUI 在您的瀏覽器中執行，您可以選擇您的音訊輸入來源。
2.  開始串流音訊。
3.  轉錄的文字將即時顯示在 GUI 中。

## 專案檔案

專案檔案結構如下：

```
whisper-stream-gui/
├── .gitignore
├── app.py
├── LICENSE
├── readme_zh.md
├── README.md
├── requirements.txt
├── silero_vad.jit
├── start_gui.bat
├── vad.py
├── css/
│   ├── all.min.css
│   └── bulma.min.css
├── faster-whisper-large-v3/
├── js/
│   └── socket.io.js
├── ssl/
└── templates/
    └── index.html
```

-   `app.py`：此 Python 腳本包含 Gradio UI 應用程式程式碼。
-   `start_gui.bat`：此批次檔用於啟動 Gradio GUI 應用程式。
-   `ssl/`：如果 GUI 設定為透過 HTTPS 執行，則此目錄可能包含 SSL 憑證檔案。

---

如有任何問題或疑問，請參閱專案文件或聯絡維護人員。
