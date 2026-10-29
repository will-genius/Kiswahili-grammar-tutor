## Teacher Assistant Cbot 

## What the Bot Does
It is an interactive, bilingual (English & Kiswahili) AI-powered educational assistant designed for the Competency-Based Curriculum (CBC). It bridges language barriers by allowing students and educators to query curriculum content, dictionaries, and learning resources either via **text input** or **voice recording**, complete with RAG (Retrieval-Augmented Generation) source grounding and bilingual audio-text responses.

##  Who It Is For
* **Students:** Looking for curriculum-aligned explanations and tutoring in both Swahili and English.
* **Educators & Teachers:** Needing quick cross-referencing against CBC teaching documents and resources.
* **Edge/Resource-Constrained Environments:** Optimized to run locally or containerized using lightweight embedding pipelines and fast transcription models.

---

##  Setup Instructions & Configuration

### Prerequisites
* [Docker Desktop](https://www.docker.com/) installed and running with WSL2 backend.
* A valid [Groq API Key](https://console.groq.com/) (for high-speed LLM inference and Whisper speech-to-text transcription).

## Running the Application via Docker
Clone the repository and navigate to the project root directory:
cd path/to/Think-Reseller
Build and start the containerized services using Docker Compose:
docker compose up --build

## Access the application in your browser:

* **Streamlit Frontend UI**: http://localhost:8501

* **FastAPI Backend Docs**: http://localhost:8000/docs

## Example Usage
To demonstrate the bot, you can test these sample prompts or workflows:

* **Text Query** : 
    Ufahamu ni nini?
    Taja hatua zinazofuatiliwa katika kufahamu.
    Andika udogo na ukubwa wa majina haya: Mbwa, Wanawake, Kiti, Nyoka, Ng'ombe.
    kiambishi ni nini
    more sample questions in the exercises.json file containing all the exercises that 
    were in the book used to build the kb

* **Voice Input Flow**:

Select "Ongea na Sauti (Voice)" from the sidebar.

Click the microphone recording button, speak your question in English or Swahili, and click stop.

The app will transcribe your audio via Groq Whisper, display the transcription, query the vector store, and return the tutor's response.

## Known Limitations & Testing Status
## What is Complete:

Bilingual text and voice chat routing.

FastAPI backend integration with Groq Whisper and ChromaDB vector retrieval.

Streamlit frontend layout with session state chat history and source grounding card expanders.

Full Docker containerization configuration.

## What is Still Rough:

Audio playback latency depends on network speed when reaching cloud-hosted transcription APIs.

Edge deployment resource footprints on low-spec local machines require tuning.

## What Needs Testing:

Stress testing concurrent multi-user voice transcriptions under heavy container loads.

Cross-browser microphone permission handling and audio sample rate conversions. 