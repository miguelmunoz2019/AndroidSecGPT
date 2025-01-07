import os
from transformers import AutoTokenizer, AutoModel
import torch
import chromadb
from chromadb.config import Settings

persist_dir = "./chromadb_store"
chunks_folder = './chunks'

client = chromadb.PersistentClient(path=persist_dir, settings=Settings(persist_directory=persist_dir, anonymized_telemetry=False))

collection = client.create_collection("info_security_chunks")

# Tokenizador y modelo roberta
tokenizer = AutoTokenizer.from_pretrained('xlm-roberta-base')
model = AutoModel.from_pretrained('xlm-roberta-base')

# Embeddings con roberta
def generate_embeddings(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1) 
    
    return embeddings.numpy()

# Generar embedding y agregar a DB
def add_chunk_to_chromadb(chunk_id, chunk_text, collection):

    embedding = generate_embeddings(chunk_text)[0]
    embedding_list = embedding.tolist()
  
    collection.add(
        documents=[chunk_text], 
        embeddings=[embedding_list], 
        ids=[chunk_id]         
    )
    print(f"Chunk: {chunk_id}")
    
   

def count_documents_in_collection(collection):
    num_docs = collection.count()
    print(f"Total de documentos : {num_docs}")

for filename in os.listdir(chunks_folder):
    if filename.endswith(".txt"):
        file_path = os.path.join(chunks_folder, filename)
        
        # Leer el contenido del archivo de chunk
        with open(file_path, 'r', encoding='utf-8') as f:
            chunk_text = f.read()
        
        # Generar un ID Ãºnico para el chunk 
        chunk_id = filename[:-4]
        
        # Agregar el chunk y sus embeddings a ChromaDB
        add_chunk_to_chromadb(chunk_id, chunk_text, collection)
        #Contar documentos en la DB
        count_documents_in_collection(collection)



print("Proceso finalizado")
