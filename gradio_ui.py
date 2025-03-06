import gradio as gr
import whisper
import numpy as np
import soundfile as sf
import tempfile
from datetime import datetime
import time

model = whisper.load_model("tiny")

def transcribe_audio(audio_data, history_state):
    history = history_state or []
    if audio_data is None:
        history.append((None, "No audio recorded!"))
        return history, history
    
    sample_rate, audio_np = audio_data
    
    # Save audio to temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        sf.write(tmpfile.name, audio_np, sample_rate)
        audio_path = tmpfile.name
    
    # Transcribe audio file using whisper
    result = model.transcribe(audio_path)
    text = result["text"]
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted_text = f"[{timestamp}] {text}\n"
    if text.strip():  # Only append if text is not empty or just whitespace
        history.append((None, formatted_text))
    return history, history

with gr.Blocks(title="Streaming Audio Translator") as app:
    history = gr.State("")
    audio_input = gr.Audio(streaming=True, sources=["microphone"])
    output_text = gr.Chatbot() # Replace Chatbot with TextArea
    clear_button = gr.ClearButton([audio_input, output_text, history]) # Update clear button
    audio_input.change(fn=transcribe_audio, inputs=[audio_input, history], outputs=[output_text, history])
    


app.launch(server_name="0.0.0.0", server_port=7860, share=False, ssl_keyfile="ssl/key.pem", ssl_certfile="ssl/chain.pem", ssl_verify=False)