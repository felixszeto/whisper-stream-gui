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
    message_id = random.randint(0, 100000) # 生成隨機消息 ID
    data['message_id'] = message_id # 將 message_id 加入 data
    audio_bytes = base64.b64decode(audio_base64)
    sample_rate = 16000  # 前端採樣率
    transcribed_text = transcribe_audio_logic((sample_rate, audio_bytes), language, message_id) # 將 language 和 message_id 傳遞給轉錄函數
    if transcribed_text:
        socketio.emit('transcription', {'text': transcribed_text, 'index': index, 'message_id': message_id})  # 返回消息索引和 message_id
    else:
        socketio.emit('loading', {'status': False, 'message_id': message_id}) # 返回 message_id

def transcribe_audio_logic(audio_data, language="en", message_id=None): # 轉錄函數接收 language 參數和 message_id
    global audio_np_long

    subtitle_keywords = ["字幕", "subtitle", "志愿者", "提供者", "by", "製作", "社群", "amara", "org"]
    thank_you_keywords = ["感謝", "謝謝", "thank you", "多謝"]
    youtube_keywords = ["小鈴鐺", "響鐘", "通知", "最新消息", "小铃铛", "開啟小鈴鐺"] # 加入 "小铃铛" 簡體中文寫法，並包含 "開啟小鈴鐺" 完整詞組

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
        socketio.emit('loading', {'status': True, "audio_length": len(audio_np_long), 'message_id': message_id}) # 傳遞 message_id
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
            processed_text = formatted_text.strip().lower() # 統一轉換為小寫方便比較

            is_filtered = False
            if not processed_text: # 過濾空字串
                is_filtered = True
            elif any(keyword in processed_text for keyword in subtitle_keywords): # 檢查字幕相關關鍵詞
                is_filtered = True
            elif any(keyword in processed_text for keyword in thank_you_keywords): # 檢查感謝語關鍵詞
                is_filtered = True
            elif any(keyword in processed_text for keyword in youtube_keywords): # 檢查 YouTube 通知關鍵詞
                is_filtered = True

            if is_filtered:
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

@app.route('/img/<path:path>')
def send_img(path):
    return send_from_directory('img', path)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=7860, ssl_context=('ssl/chain.pem', 'ssl/key.pem'))
