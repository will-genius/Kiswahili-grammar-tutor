import os
import re
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

def parse_markdown_file(filepath):
    """
    Slices a markdown file into smaller chunks based on YAML frontmatter.
    Returns a list of Document objects.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    # Regex to find all blocks starting with --- metadata --- followed by content
    # It stops capturing content when it hits the next --- block or the end of the file.
    pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n(.*?)(?=(?:^---\s*\n)|\Z)', re.MULTILINE | re.DOTALL)
    
    documents = []
    
    for match in pattern.finditer(text):
        frontmatter = match.group(1)
        content = match.group(2).strip()
        
        metadata = {}
        # Parse the key: value pairs in the frontmatter
        for line in frontmatter.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip().strip('"').strip("'")
                
        # Keep track of the source file
        metadata['source_file'] = os.path.basename(filepath)
        
        sub_sections = re.split(r'\n(?=## )', content)
        
        for sub_section in sub_sections:
            if sub_section.strip():
                # Append each tiny chunk as its own document
                documents.append(Document(page_content=sub_section.strip(), metadata=metadata.copy()))
        
    return documents

def main():
    print("Loading embedding model (BAAI/bge-m3)...")
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")

    persist_dir = "./chromadb_grammar_kb"
    print(f"Initializing ChromaDB at {persist_dir}...")
    vector_store = Chroma(
        collection_name="swahili_grammar_kb",
        embedding_function=embeddings,
        persist_directory=persist_dir 
    )

    kb_directory = os.path.join("data", "knowledge_base")
    all_documents = []
    
    if not os.path.exists(kb_directory):
        print(f"Error: Directory {kb_directory} does not exist.")
        return

    for filename in os.listdir(kb_directory):
        if filename.endswith(".md"):
            filepath = os.path.join(kb_directory, filename)
            # This now returns a LIST of chunked documents per file
            chunks = parse_markdown_file(filepath)
            all_documents.extend(chunks)
            print(f"Chunked {filename} into {len(chunks)} pieces.")

    if all_documents:
        print(f"Inserting {len(all_documents)} precise chunks into ChromaDB...")
        vector_store.add_documents(all_documents)
        print(" Knowledge Base successfully populated with chunked data!")
    else:
        print("No markdown files found to process.")

if __name__ == "__main__":
    main()