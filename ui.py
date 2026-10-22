import streamlit as st
import requests

# FastAPI Backend URL
FASTAPI_URL = "http://127.0.0.1:8000/api/chat/message"

st.set_page_config(
    page_title="Swahili & English Educational Tutor",
    page_icon="",
    layout="centered"
)

# App Header
st.title(" Mwalimu Msaidizi (AI Tutor)")
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
            with st.expander(" View Curriculum Grounding Source"):
                for idx, doc in enumerate(message["context"]):
                    st.markdown(f"**Source {idx+1}:** {doc['metadata'].get('topic_title')} ({doc['metadata'].get('source_file')})")
                    st.text(doc['content'][:300] + "...")

# Handle Voice Input Mode in Sidebar or Container
active_query = None
audio_bytes = None

if input_mode == " Ongea na Sauti (Voice)":
    st.sidebar.markdown("---")
    st.sidebar.subheader("Rekodi Sauti Yako")
    st.sidebar.caption("Bonyeza kitufe cha mic kuanza kurekodi swali lako.")
    
    # Native Streamlit audio input widget
    audio_file = st.audio_input("Record your question (Swahili / English)")
    
    if audio_file:
        audio_bytes = audio_file.getvalue()
        active_query = "[Voice Message Sent by Student]"

# Handle Text Input Mode
else:
    active_query = st.chat_input("Uliza swali lako hapa / Type your question here...")

# Process Student Query (whether Text or Voice)
if active_query:
    
    # 1. Append and display student message
    msg_payload = {"role": "user", "content": active_query}
    if audio_bytes:
        msg_payload["audio"] = audio_bytes
        
    st.session_state.messages.append(msg_payload)
    
    with st.chat_message("user"):
        st.markdown(active_query)
        if audio_bytes:
            st.audio(audio_bytes)

    # 2. Query FastAPI Backend
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        retrieved_context = []

        try:
            # If it's audio, we can pass text description or hook up audio bytes. 
            # For this MVP text bridge, if voice is used, we send a prompt placeholder or transcribe.
            query_text = "Nieleze kuhusu masomo yangu" if audio_bytes else active_query
            
            payload = {"message": query_text}
            response = requests.post(FASTAPI_URL, json=payload)
            
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

        # 3. Save Assistant Response and Context to Session State
        st.session_state.messages.append({
            "role": "assistant", 
            "content": full_response,
            "context": retrieved_context
        })
        
        # Display grounding sources if available
        if retrieved_context:
            with st.expander(" View Curriculum Grounding Source"):
                for idx, doc in enumerate(retrieved_context):
                    st.markdown(f"**Source {idx+1}:** {doc['metadata'].get('topic_title')} ({doc['metadata'].get('source_file')})")
                    st.text(doc['content'][:300] + "...")


# to run streamlit run ui.py