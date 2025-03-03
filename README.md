# Whisper Stream GUI

This project provides a graphical user interface (GUI) for real-time audio transcription using Whisper.

## Introduction

Whisper Stream GUI is a user-friendly application that allows you to transcribe audio in real-time using the Whisper model. It is designed to be easy to use and provides a simple interface for streaming audio and viewing transcriptions.

## Installation

To install and run Whisper Stream GUI, follow these steps:

1.  **Prerequisites:**
    -   Python 3.9 or later installed on your system. You can download Python from [https://www.python.org/](https://www.python.org/).
    -   `pip` package installer. `pip` is usually included with Python installations.
    -   PyTorch version greater than 1.0.0 (You can install the latest version). Follow the installation instructions on [https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/) to install the correct version for your system.

2.  **Install Whisper:**
    Follow the instructions on the Whisper repository to install it: [https://github.com/openai/whisper](https://github.com/openai/whisper).

3.  **Recommended: Install Conda (Optional but Recommended):**
    It is recommended to use Conda to manage your Python environment. You can download Conda from [https://www.anaconda.com/products/distribution](https://www.anaconda.com/products/distribution).

4.  **Create Conda Environment (Optional but Recommended):**
    If you choose to use Conda, create a new environment for this project:

    ```bash
    conda create -n whisper python=3.9
    conda activate whisper
    ```

5.  **Clone the repository:**
    You can clone it to your local machine.

    ```bash
    git clone https://github.com/felixszeto/whisper-stream-gui.git
    cd whisper-stream-gui
    ```

6.  **Install Dependencies:**
    Navigate to the project directory in your terminal and install the required Python packages using pip.

    ```bash
    pip install -r requirements.txt
    ```




7.  **Run the GUI:**
    Execute the `start_gui.bat` batch file to launch the Whisper Stream GUI application.

    ```bash
    start_gui.bat
    ```

    This will start the Gradio interface in your web browser.

    **HTTPS Certificate Configuration (Required for Microphone Access):**
    HTTPS configuration with SSL certificates is **required** for browsers to allow microphone access due to security restrictions for microphone usage over non-secure HTTP.
    To configure HTTPS, you need to set up SSL certificates:
    -   Modify the `gradio_ui.py` script to specify the paths to your SSL certificate files.
    -   Find the `app.launch()` function in `gradio_ui.py`.
    -   Adjust the `ssl_keyfile` and `ssl_certfile` parameters to the correct paths of your key and certificate files.
    -   Ensure that the certificate files (`key.pem` and `chain.pem` by default) are placed in the `ssl/` directory, or update the paths accordingly in the script.

## Whisper Model Selection
You can change the Whisper model used for transcription by modifying the `gradio_ui.py` file.

-   Open the `gradio_ui.py` file.
-   Locate the line `model = whisper.load_model("tiny")`.
-   Replace `"tiny"` with the desired model size. Available models are: `tiny`, `tiny_en`, `base`, `base_en`, `small`, `small_en`, `medium`, `medium_en`, `large`, and `turbo`.

| Size   | Parameters | English-only model | Multilingual model | Required VRAM | Relative speed |
| :----- | :--------- | :----------------- | :----------------- | :------------ | :------------- |
| tiny   | 39 M       | tiny.en            | tiny               | ~1 GB         | ~10x           |
| base   | 74 M       | base.en            | base               | ~1 GB         | ~7x            |
| small  | 244 M      | small.en           | small              | ~2 GB         | ~4x            |
| medium | 769 M      | medium.en          | medium             | ~5 GB         | ~2x            |
| large  | 1550 M     | N/A                | large              | ~10 GB        | 1x             |
| turbo  | 809 M      | N/A                | turbo              | ~6 GB         | ~8x            |


## Usage

1.  Once the GUI is running in your browser, you can select your audio input source.
2.  Start streaming audio.
3.  The transcribed text will be displayed in real-time in the GUI.

## Project Files

-   `gradio_ui.py`: This Python script contains the Gradio UI application code.
-   `start_gui.bat`: This batch file is used to start the Gradio GUI application.
-   `ssl/`: This directory may contain SSL certificate files if the GUI is configured to run over HTTPS.

---

For any issues or questions, please refer to the project documentation or contact the maintainers.
