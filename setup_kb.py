from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# STEP 1: Initialize the Multilingual Embedding Model
# We use BAAI/bge-m3 because it is heavily optimized for multilingual retrieval.
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")

# STEP 2: Initialize the Persistent Vector Store
# This creates a local folder to store the vectors on disk.
vector_store = Chroma(
    collection_name="swahili_grammar_kb",
    embedding_function=embeddings,
    persist_directory="./chromadb_grammar_kb" 
)

# STEP 3: Define the Validated Knowledge Base (KB) Entries
# The architecture requires specific metadata tags for pedagogical filtering.
initial_rules = [
    Document(
        page_content="The m-/wa- noun class is used for people. Singular uses m- (mtoto), plural uses wa- (watoto).",
        metadata={
            "rule_id": "rule_m_wa_01",
            "morphology_class": "m-/wa-",
            "cbc_topic": "Noun Classes (Ngeli)",
            "explanation_sw": "Ngeli ya m-/wa- hutumika kwa majina ya watu. Umoja ni m- na wingi ni wa-.",
            "explanation_en": "The m-/wa- class is for people. Singular takes m-, plural takes wa-.",
            "example_error": "Watoto anasoma",
            "example_correction": "Watoto wanasoma"
        }
    ),
    Document(
        page_content="Present tense marker is -na-. Example: ninasoma (I am reading).",
        metadata={
            "rule_id": "rule_tense_na_01",
            "morphology_class": "tense_marker",
            "cbc_topic": "Tenses (Nyakati)",
            "explanation_sw": "Wakati uliopo hutumia kiambishi -na-. Mfano: ninasoma.",
            "explanation_en": "The present tense uses the marker -na-. Example: ninasoma (I am reading).",
            "example_error": "Mimi kusoma sasa",
            "example_correction": "Mimi ninasoma sasa"
        }
    )
]

# STEP 4: Add the documents to the database
vector_store.add_documents(initial_rules)
print(f"Successfully loaded {len(initial_rules)} rules into the persistent ChromaDB.")