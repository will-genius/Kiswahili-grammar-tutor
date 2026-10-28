import os
import streamlit as st
import requests
from audio_recorder_streamlit import audio_recorder

# FastAPI Backend URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
FASTAPI_TEXT_URL = f"{BACKEND_URL.rstrip('/')}/api/chat/message"
FASTAPI_VOICE_URL = f"{BACKEND_URL.rstrip('/')}/api/chat/voice"

st.set_page_config(
    page_title="Swahili & English Educational Tutor",
    page_icon="🎓",
    layout="centered"
)

# App Header
st.title("🎓 Mwalimu Msaidizi (AI Tutor)")
st.caption("Bilingual Swahili & English CBC Curriculum Assistant (Optimized for Edge)")

# Sidebar for Input Mode Selection
input_mode = st.sidebar.radio("Chagua Njia ya Kuwasiliana / Input Mode:", ["Andika Ujumbe (Text)", "🎤 Ongea na Sauti (Voice)"])

# Initialize Chat History in Streamlit Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior chat messages on re-run
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "audio" in message and message["audio"]:
            st.audio(message["audio"])
        if "context" in message and message["context"]:
            with st.expander("View Curriculum Grounding Source"):
                for idx, doc in enumerate(message["context"]):
                    st.markdown(f"**Source {idx+1}:** {doc['metadata'].get('topic_title')} ({doc['metadata'].get('source_file')})")
                    st.text(doc['content'][:300] + "...")

active_query = None
audio_bytes = None

# --- VOICE INPUT MODE (Main Panel) ---
if input_mode == "🎤 Ongea na Sauti (Voice)":
    st.markdown("---")
    st.subheader("🎙️ Voice Recording Studio")
    st.info("Click the microphone button below to start recording your question. Click it again to stop, and your audio will process automatically!")
    
    # Clean dedicated audio recorder component
    audio_bytes = audio_recorder(
        text="Click to record",
        recording_color="#e8b62c",
        neutral_color="#4f8bf9",
        icon_size="3x"
    )
    
    if audio_bytes:
        active_query = "[Voice Message Sent by Student]"

# --- TEXT INPUT MODE ---
else:
    active_query = st.chat_input("Uliza swali lako hapa / Type your question here...")

# Process Student Query (whether Text or Voice)
if active_query:
    
    # Append and display student message
    msg_payload = {"role": "user", "content": active_query}
    if audio_bytes:
        msg_payload["audio"] = audio_bytes
        
    st.session_state.messages.append(msg_payload)
    
    with st.chat_message("user"):
        if audio_bytes:
            st.markdown("🎙️ *[Voice Audio Prompt]*")
            st.audio(audio_bytes)
        else:
            st.markdown(active_query)

    # Query FastAPI Backend
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        retrieved_context = []

        try:
            if audio_bytes:
                message_placeholder.markdown("Transcribing audio with Groq Whisper & querying RAG tutor...")
                files = {"file": ("voice_query.wav", audio_bytes, "audio/wav")}
                response = requests.post(FASTAPI_VOICE_URL, files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success":
                        transcribed = data.get("transcribed_query", "")
                        full_response = data.get("tutor_response", "Samahani, hakuna jibu lililopatikana.")
                        retrieved_context = data.get("retrieved_context_used", [])
                        
                        message_placeholder.markdown(f"**Transcribed Text:** *{transcribed}*\n\n---\n\n{full_response}")
                    else:
                        full_response = "Samahani, usindikaji wa sauti umeshindikana."
                        message_placeholder.markdown(full_response)
                else:
                    full_response = f"Server Error ({response.status_code})"
                    message_placeholder.markdown(full_response)
            else:
                payload = {"message": active_query}
                response = requests.post(FASTAPI_TEXT_URL, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    full_response = data.get("tutor_response", "Samahani, hakuna jibu lililopatikana.")
                    retrieved_context = data.get("retrieved_context_used", [])
                    message_placeholder.markdown(full_response)
                else:
                    full_response = f" Server Error ({response.status_code})"
                    message_placeholder.markdown(full_response)
                
        except requests.exceptions.RequestException as e:
            full_response = f" Connection Error: Is FastAPI running? Details: {e}"
            message_placeholder.markdown(full_response)

        # Save Assistant Response and Context to Session State
        st.session_state.messages.append({
            "role": "assistant", 
            "content": full_response,
            "context": retrieved_context
        })
        
        # Display grounding sources if available
        if retrieved_context:
            with st.expander("View Curriculum Grounding Source"):
                for idx, doc in enumerate(retrieved_context):
                    st.markdown(f"**Source {idx+1}:** {doc['metadata'].get('topic_title')} ({doc['metadata'].get('source_file')})")
                    st.text(doc['content'][:300] + "...")