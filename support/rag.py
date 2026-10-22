
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
import os
from pypdf import PdfReader

# Initialize ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")

embedding_fn = DefaultEmbeddingFunction()

collection = client.get_or_create_collection(
    name="arocode_docs",
    embedding_function=embedding_fn
)


def chunk_text(text, chunk_size=500, overlap=80):
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        current_chunk = []
        current_size = 0
        end = start

        while end < len(words):
            word = words[end]
            added_size = len(word) + (1 if current_chunk else 0)

            if current_size + added_size > chunk_size and current_chunk:
                break

            current_chunk.append(word)
            current_size += added_size
            end += 1

        chunks.append(" ".join(current_chunk))

        if end >= len(words):
            break

        # Move back to retain some context between chunks
        next_start = end
        overlap_size = 0

        while next_start > start and overlap_size < overlap:
            next_start -= 1
            overlap_size += len(words[next_start]) + 1

        start = max(start + 1, next_start)

    return chunks


def load_documents():
    docs_path = "support/documents/"

    if not os.path.isdir(docs_path):
        print(f"Documents folder not found: {docs_path}")
        return

    documents = []
    ids = []
    metadatas = []

    for filename in os.listdir(docs_path):
        if not filename.lower().endswith(".pdf"):
            continue

        filepath = os.path.join(docs_path, filename)

        try:
            reader = PdfReader(filepath)
            raw_text = "\n".join(
                page.extract_text() or ""
                for page in reader.pages
            ).strip()

            if not raw_text:
                print(f"No extractable text: {filename}")
                continue

            chunks = chunk_text(raw_text)

            for i, chunk in enumerate(chunks):
                documents.append(chunk)
                ids.append(f"{filename}_{i}")
                metadatas.append({
                    "source": filename,
                    "chunk": i
                })

        except Exception as exc:
            print(f"Error reading {filename}: {exc}")

    if documents:
        collection.upsert(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )

    print(f"Processed {len(documents)} chunks into ChromaDB")


def search_knowledge_base(query):
    if collection.count() == 0:
        return "No company documents have been indexed yet."

    results = collection.query(
        query_texts=[query],
        n_results=min(3, collection.count())
    )

    matched_chunks = results["documents"][0]

    if not matched_chunks:
        return "No relevant information found in company documents."

    return "\n\n".join(matched_chunks)