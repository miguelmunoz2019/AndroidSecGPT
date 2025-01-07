import openai
from transformers import AutoTokenizer, AutoModel
import torch
import chromadb
from chromadb.config import Settings




openai.api_key = input("Por favor, ingrese su OpenAI API key: ")
print("Seleccione la opción con la version del modelo XLM-RoBERTa que desea utilizar: ")
print("1. xlm-roberta-base")
print("2. xlm-roberta-large")

xlm_type = input("")
print(xlm_type)

if xlm_type == '1':
    model_name = 'xlm-roberta-base'
elif xlm_type == '2':
    model_name = 'xlm-roberta-Large'
else:
    print("Opcion invalida.")
    exit(1)

print("Seleccione la opción con la version del modelo GPT que desea utilizar: ")
print("1. GPT-3.5")
print("2. GPT-4.0")
gpt_type = input("")


print(gpt_type)
if gpt_type == '1':
    gptmodel_name = 'gpt-3.5-turbo'
elif gpt_type == '2':
    gptmodel_name = 'gpt-4-turbo'
else:
    print("Opcion invalida.")
    exit(1)

print("Seleccione el metodo para realizar preguntas que desea: ")
print("1. Una pregunta directamente en consola")
print("2. Multiples preguntas directamente en consola")
print("3. Multiples preguntas en el documento .xlsx")
questionType = input("")



print("Comienza proceso usando: "+model_name +" y "+gptmodel_name)

# Configuración de ChromaDB (directorio de persistencia)
persist_dir = ""
collection_name = ""
if model_name=="xlm-roberta-base": 
    persist_dir = "./chromadb_store"
    collection_name = "info_security_chunks"
elif model_name=="xlm-roberta-Large":
    persist_dir = "./chromadb_storeL"
    collection_name = "info_security_chunksL"
client = chromadb.PersistentClient(path=persist_dir, settings=Settings(persist_directory=persist_dir, anonymized_telemetry=False))
print("ChromaDB funcionando")

# Cargar la colección
try:
    collection = client.get_collection(collection_name)
    print(f"Colección '{collection_name}' cargada exitosamente.")
except chromadb.errors.InvalidCollectionException:
    print(f"Error: La colección '{collection_name}' no existe. Asegúrate de haberla cargado correctamente.")
    exit(1)  

# Cargar el tokenizador y el modelo XLM-RoBERTa
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Función para generar embeddings con XLM-RoBERTa
def generate_embeddings(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).numpy()

# Paso 2: Generación de la respuesta hipotética (HyDE)
def generate_hypothetical_response(query_text):
    response = openai.ChatCompletion.create(
        model=gptmodel_name,
        messages=[{"role": "user", "content": query_text}],
        max_tokens=2500,
        temperature=0.5
    )
    hypothetical_answer = response['choices'][0]['message']['content'].strip()
    return hypothetical_answer

# Paso 3: Convertir la respuesta hipotética en un embedding
def get_hypothetical_embedding(hypothetical_answer):
    embedding = generate_embeddings(hypothetical_answer)[0]
    return embedding


# Paso 4: Recuperar los chunks más cercanos en ChromaDB usando el embedding
def get_relevant_chunks(hypothetical_embedding, collection, top_n=30):
    results = collection.query(
        query_embeddings=[hypothetical_embedding.tolist()],
        n_results=top_n
    )
    documents = [doc[0] for doc in results["documents"]]
    ids = results["ids"]
    return documents, ids

# Paso 5: Generar la respuesta final usando la pregunta original y los chunks de contexto
def generate_final_response(query_text, relevant_chunks):
    context = " ".join(relevant_chunks)
    prompt = f"""
    ```{context}```
    'Question--- {query_text}---
    From the support information that you are provided, delimited by triple backticks,
    extract the relevant information based on the asked question delimited by triple quotes.
    If there are any specific vulnerabilities, security measures, or technical details mentioned in the question,
    try to locate them in the provided information. Then, using these relevant details and any specific information you extracted,
    answer the question in a detailed manner. Provide further explanations and elaborations on the information where necessary.
    The answer must not include special characters such as /, ”,---, “‘ etc. If the question cannot be answered with only the
    provided information, simply write "I don’t know."
    Once you have formulated your answer, revise it following these steps:
    1. Verify your answer and remove any references to the "provided information." For example, if your answer states:
       "Based on the information provided, it appears that ...", replace it with "It appears that ".
       Refer to the information as your own expertise in Android security.
       Do not mention the words “provided information” or “given information” under any circumstances.
    2. If the context delimited by triple backticks is empty or if your answer implies that
       you cannot respond based on the given information, simply state “I don’t know.”
    3. Remove from your answer any advice that suggests consulting an external resource; assume the role of an authoritative source on security.
    """
    response = openai.ChatCompletion.create(
        model= gptmodel_name,
        messages=[
            {"role": "system", "content": "You are an expert in in information security in android."},
            {"role": "user", "content":prompt}
        ],
        max_tokens=2500,
        temperature=0.5
    )
    final_response = response['choices'][0]['message']['content'].strip()
    return final_response

def completeProcess(query_text):
    
    # Ejecutar el paso 2
    hypothetical_answer = generate_hypothetical_response(query_text)
     # Ejecutar el paso 3
    hypothetical_embedding = get_hypothetical_embedding(hypothetical_answer)
    # Ejecutar el Paso 4
    top_n = 30
    relevant_chunks, chunk_ids = get_relevant_chunks(hypothetical_embedding, collection, top_n=top_n)

    # Ejecutar el Paso 5
    return generate_final_response(query_text, relevant_chunks), relevant_chunks, hypothetical_answer

def save_answers_to_excel(file_path, questions, answers,context,hypothetic):
    df = pd.read_excel(file_path)
    df['Generated Answer'] = answers
    df['Hypothetic Answer'] = hypothetic
    df['Used Context'] = context
    df.to_excel(file_path, index=False)
    
# Guardar la respuesta final en un archivo txt
def save_response_to_file(query_text, final_response, file_path="AndroidSecGPTAnswer.txt"):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"Pregunta del usuario:\n{query_text}\n\n")
        f.write(f"Respuesta final generada:\n{final_response}\n\n")

if questionType == '1':  
    query_text = input("Por favor, ingrese su pregunta: ").strip()
    final_response=completeProcess(query_text)
    print("Respuesta final generada:")
    print(final_response)
    document_path = "AndroidSecGPTAnswer.txt"
    save_response_to_file(query_text, final_response, document_path)
    print(f"La respuesta ha sido guardada en {document_path}.")
    

elif questionType == '2': 
    while True:
        query_text = input("Ingrese su pregunta (o escriba 'salir' para terminar): ").strip()
        if query_text.lower() == 'salir':
            break
        final_response=completeProcess(query_text)
        print("Respuesta final generada:")
        print(final_response)
        document_path = "AndroidSecGPTAnswer.txt"
        save_response_to_file(query_text, final_response, document_path)

        print(f"La respuesta ha sido guardada en {document_path}.")

elif questionType == '3': 
    import pandas as pd
    excel_file = "questions.xlsx"
    df = pd.read_excel(excel_file)
    answers = []
    context = []
    hypothetic = []
    for query_text in df['Questions']:
        final_response, relevant_chunks, hypothetical_answer=completeProcess(query_text)
        answers.append(final_response)
        context.append(relevant_chunks)
        hypothetic.append(hypothetical_answer)
    save_answers_to_excel(excel_file, df['Questions'], answers,context,hypothetic)
    print("Respuestas guardadas en el archivo Excel.")



