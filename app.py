from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
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
import base64

from faster_whisper import WhisperModel
model = WhisperModel("faster-whisper-large-v3/",
                             device="cuda",
                             compute_type="float16")

audio_np_long = np.array([], dtype=np.float32)

vad = VAD()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # 允許跨域連線

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('audio_stream')
def handle_audio_stream(data):
    audio_base64 = data['audio_data']
    index = data['index']  # 接收消息索引
    language = data['language'] or "en"  # 從前端接收語言設定，如果沒有則預設為 "en"
    audio_bytes = base64.b64decode(audio_base64)
    sample_rate = 16000  # 前端採樣率
    transcribed_text = transcribe_audio_logic((sample_rate, audio_bytes), language) # 將 language 傳遞給轉錄函數
    if transcribed_text:
        socketio.emit('transcription', {'text': transcribed_text, 'index': index})  # 返回消息索引
    else:
        socketio.emit('loading', {'status': False})


def transcribe_audio_logic(audio_data, language="en"): # 轉錄函數接收 language 參數
    global audio_np_long

    filter_words = ['字幕由 Amara.org 社群提供',
                        '開啟小鈴鐺可以收到最新消息',
                        '感謝您的觀看',
                        '響鐘',
                        '謝謝',''
                        '字幕志愿者 李宗盛',
                        '謝謝大家',
                        '字幕by索兰娅',
                        '字幕志愿者 杨栋梁',
                        '多謝您收睇時局新聞,再會!',
                        '中文字幕製作',
                        '詞曲 李宗盛',
                        '開啟小鈴鐺,再按下小鈴鐺就能收到通知',
                        '開啟小鈴鐺就能收到最新消息',
                        '字幕提供者 李宗盛',
                        'Thank you for watching.',
                        '中文字幕志愿者 杨洁']

    if audio_data is None:
        return ""

    sample_rate, audio_bytes = audio_data  # 音訊資料以 bytes 接收

    audio_np = np.frombuffer(audio_bytes, np.int16).flatten().astype(np.float32) / 32768.0  # 轉換為 NumPy 陣列

    trunk = audio_np
    no_speech = vad.no_speech(trunk, sample_rate)

    if no_speech:
        if len(audio_np_long) <= 0:
            audio_np_long = np.array([], dtype=np.float32)
            return ""
        socketio.emit('loading', {'status': True, "audio_length": len(audio_np_long)})
        audio_np_do = audio_np_long.copy()  # 使用 copy() 方法沒問題，因為 audio_np_long 應該是 NumPy 陣列
        audio_np_long = np.array([], dtype=np.float32)  # 重置 audio_np_long 為空的 NumPy 陣列

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            sf.write(tmpfile.name, audio_np_do, sample_rate)
            audio_path = tmpfile.name

            decoded_text = ""
            previous_segment = ""
            segments, info = model.transcribe(tmpfile.name,
                                                language=language,
                                                # task="translate"
                                                )
            for segment in segments:
                if segment.text != previous_segment:
                    decoded_text += segment.text
                    previous_segment = segment.text

            text = decoded_text
            formatted_text = f"{text}"


            if formatted_text.strip() in filter_words or not formatted_text.strip():
                return ""
            
            print(formatted_text)
        os.remove(audio_path)
        return formatted_text
    
    else:
        if len(audio_np_long) == 0:
            audio_np_long = audio_np
        else:
            audio_np_long = np.concatenate((audio_np_long, audio_np))
        return ""



@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=7860, ssl_context=('ssl/chain.pem', 'ssl/key.pem'))
