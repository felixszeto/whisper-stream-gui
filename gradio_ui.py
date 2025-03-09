import gradio as gr
import whisper
import numpy as np
import soundfile as sf
import tempfile
from datetime import datetime
import time
from vad import VAD
import random
import os
from scipy.signal import resample

from faster_whisper import WhisperModel
model = WhisperModel("faster-whisper-large-v3/",  # 创建 faster_whisper 模型实例
                             device="cuda",  # 设置设备
                             compute_type="float16")  # 设置计算类型

# model = whisper.load_model("large-v3")
audio_np_long = np.array([], dtype=np.float32)  # Initialize as empty NumPy array

vad = VAD()

def transcribe_audio(audio_data, history_state):
    global audio_np_long

    history = history_state or []
    if audio_data is None:
        history.append((None, "No audio recorded!"))
        return history, history

    sample_rate, audio_np = audio_data

    trunk = np.frombuffer(audio_np, np.int16).flatten().astype(np.float32) / 32768.0
    no_speech = vad.no_speech(trunk, sample_rate)

    if no_speech:
        if len(audio_np_long) <= 0:
            audio_np_long = np.array([], dtype=np.float32)
            return history, history
        audio_np_do = audio_np_long.copy()
        audio_np_long = np.array([], dtype=np.float32) # Reset as empty NumPy array
        

        # Save accumulated audio to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            sf.write(tmpfile.name, audio_np_do, sample_rate)
            audio_path = tmpfile.name

            history_string = "".join([x[1] for x in history])

            # result = model.transcribe(tmpfile.name, language="yue")
            # text = result.get("text")  # Get the transcribed text

            decoded_text = ""  # 初始化解码文本
            previous_segment = ""  # 初始化前一个片段文本
            segments, info = model.transcribe(tmpfile.name,  # 使用 faster_whisper 模型转录音频
                                                language="yue",  # 设置语言
                                                initial_prompt=history_string  # 传递解码选项
                                                    )
            for segment in segments:  # 遍历片段
                if segment.text != previous_segment:  # 如果当前片段文本与前一个片段文本不同
                    decoded_text += segment.text  # 添加片段文本到解码文本
                    previous_segment = segment.text  # 更新前一个片段文本

            text = decoded_text
            # timestamp = datetime.now().strftime("%H:%M:%S")
            # formatted_text = f"[{timestamp}] {text}"
            formatted_text = f"{text}"
            print(formatted_text)
        os.remove(audio_path)
        if text.strip():  # Only append if text is not empty or just whitespace
            history.append((None, formatted_text))
    else:
        if len(audio_np_long) == 0:
            audio_np_long = audio_np
        else:
            audio_np_long = np.concatenate((audio_np_long, audio_np))
    return history, history


with gr.Blocks(title="Streaming Audio Translator") as app:
    gr.WaveformOptions(sample_rate=192000)
    history = gr.State([]) # Initialize history as an empty list
    audio_input = gr.Audio(streaming=True, sources=["microphone"])
    output_text = gr.Chatbot()
    clear_button = gr.ClearButton([audio_input, output_text, history])
    # audio_input.change(fn=transcribe_audio, inputs=[audio_input, history], outputs=[output_text, history])
    audio_input.stream(fn=transcribe_audio, inputs=[audio_input, history], outputs=[output_text, history], stream_every=1)
app.launch(server_name="0.0.0.0", server_port=7860, share=False, ssl_keyfile="ssl/key.pem", ssl_certfile="ssl/chain.pem", ssl_verify=False)
