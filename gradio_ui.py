import gradio as gr
import whisper
import numpy as np
import soundfile as sf
import tempfile
from datetime import datetime
import time
from vad import VAD

model = whisper.load_model("small")
audio_np_long = np.array([], dtype=np.float32)  # Initialize as empty NumPy array

def transcribe_audio(audio_data, history_state):
    history = history_state or []
    if audio_data is None:
        history.append((None, "No audio recorded!"))
        return history, history

    sample_rate, audio_np = audio_data
    global audio_np_long

    audio_np = audio_np.astype(np.float32)

    if len(audio_np_long) == 0:  # Check if audio_np_long is empty
        audio_np_long = audio_np
    else:
        audio_np_long = np.concatenate((audio_np_long, audio_np)) # Concatenate NumPy arrays

    vad = VAD()
    audio = np.frombuffer(audio_np_long, np.int16).flatten().astype(np.float32) / 32768.0
    if vad.no_speech(audio):
        print("Transcribing accumulated audio...")
        # Save accumulated audio to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            sf.write(tmpfile.name, audio_np_long, sample_rate)
            audio_path = tmpfile.name

        # Transcribe audio file using whisper
        result = model.transcribe(audio_path)
        text = result["text"]
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_text = f"[{timestamp}] {text}\n"
        if text.strip():  # Only append if text is not empty or just whitespace
            history.append((None, formatted_text))

        audio_np_long = np.array([], dtype=np.float32) # Reset as empty NumPy array
        return history, history
    else:
        print("Accumulating audio...")
        return history, history


with gr.Blocks(title="Streaming Audio Translator") as app:
    history = gr.State([]) # Initialize history as an empty list
    audio_input = gr.Audio(streaming=True, sources=["microphone"])
    output_text = gr.Chatbot()
    clear_button = gr.ClearButton([audio_input, output_text, history])
    audio_input.change(fn=transcribe_audio, inputs=[audio_input, history], outputs=[output_text, history])

app.launch(server_name="0.0.0.0", server_port=7860, share=False, ssl_keyfile="ssl/key.pem", ssl_certfile="ssl/chain.pem", ssl_verify=False)
