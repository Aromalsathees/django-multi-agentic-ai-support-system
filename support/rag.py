import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
import os
from pypdf import PdfReader



# initialize chromadb client
client = chromadb.PersistentClient(path="./chroma_db")

embedding_fn = DefaultEmbeddingFunction()

# get or create collection - just like table in regular db
collection = client.get_or_create_collection(
    name="coolbreeze_docs",
    embedding_function=embedding_fn
)


def chunk_text(text, chunk_size=500): 
    # current_chunk = [I willl earn python] --> I will learn python
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0

    for word in words:
        current_chunk.append(word)
        current_size += len(word) + 1

        if current_size >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_size = 0

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
        

def load_documents():
    docs_path = "support/documents/"

    documents = []
    ids = []

    for filename in os.listdir(docs_path):
        if filename.endswith(".pdf"):
            # filepath: support/documents/refund_policy.pdf
            filepath = os.path.join(docs_path, filename)
            reader = PdfReader(filepath)
            
            raw_text = ""
            for page in reader.pages:
                raw_text += page.extract_text()

            chunks = chunk_text(raw_text, chunk_size=500)

            for i, chunk in enumerate(chunks):
                documents.append(chunk)
                ids.append(f"{filename}_{i}")

    if documents:
        collection.add(documents=documents, ids=ids)

    print(f"Loaded {len(documents)} chunks into ChromaDB")
    
        

def search_knowledge_base(query):
    results = collection.query(query_texts=[query], n_results=3)
    print("DEBUG RESULTS:", results["documents"])
    if not results["documents"][0]:
        return "No relevant information found in company documents."
    
    matched_chunks = results["documents"][0]
    return "\n\n".join(matched_chunks)


"""
matched_chunks = [
    "Refund requests must be submitted within 30 days of delivery.",
    "Approved refunds are processed within 7 to 10 business days.",
    "Products purchased during sales are eligible for exchange only."
]


Refund requests must be submitted within 30 days of delivery.

Approved refunds are processed within 7 to 10 business days.

Products purchased during sales are eligible for exchange only.

"""