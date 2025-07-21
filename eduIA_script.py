# Ejemplo básico con PyPDF2 (puedes adaptar para multiples PDFs o pdfminer.six)
import PyPDF2
import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import re
import json
import requests

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text()
    except Exception as e:
        print(f"Error al extraer texto de {pdf_path}: {e}")
        return None
    return text

def split_text_into_chunks(text, max_chunk_size=500, overlap=50):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = []
    current_len = 0

    for sentence in sentences:
        if current_len + len(sentence) + 1 <= max_chunk_size:
            current_chunk.append(sentence)
            current_len += len(sentence) + 1
        else:
            chunks.append(" ".join(current_chunk))
            overlap_size = int(len(current_chunk) * overlap / max_chunk_size)
            current_chunk = current_chunk[-overlap_size:] if current_chunk and overlap_size > 0 else []
            current_chunk.append(sentence)
            current_len = sum(len(s) + 1 for s in current_chunk)
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def call_ollama_deepseek(prompt, model_name="llama3"): # Aquí ya está cambiado a llama3
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json()['response']
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con Ollama: {e}")
        return "Lo siento, no pude conectar con el modelo DeepSeek."
    except KeyError:
        print("Respuesta inesperada de Ollama.")
        return "Lo siento, hubo un problema al procesar la respuesta."

def get_relevant_chunks(user_query, model, index, text_chunks, k=3):
    query_embedding = model.encode([user_query])
    D, I = index.search(np.array(query_embedding).astype('float32'), k)
    relevant_texts = [text_chunks[i] for i in I[0]]
    return relevant_texts

# --- LÓGICA PRINCIPAL PARA CARGA Y PROCESAMIENTO DE DOCUMENTOS ---

# Ruta de la carpeta donde están TODOS tus PDFs
pdf_folder_path = "C:/Users/difow/Desktop/eduIA"

all_extracted_text = ""
for filename in os.listdir(pdf_folder_path):
    if filename.endswith(".pdf"):
        current_pdf_path = os.path.join(pdf_folder_path, filename)
        print(f"Procesando: {current_pdf_path}")
        text_from_current_pdf = extract_text_from_pdf(current_pdf_path)
        if text_from_current_pdf:
            all_extracted_text += text_from_current_pdf + "\n\n"

if not all_extracted_text.strip():
    print("No se encontró texto en ningún PDF o hubo errores en la extracción. El chatbot no tendrá información.")
    exit()

# Dividir todo el texto combinado en chunks
text_chunks = split_text_into_chunks(all_extracted_text)
print(f"Dividido en {len(text_chunks)} chunks.")

# Cargar el modelo de embeddings
model_embeddings = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2') # Cambié el nombre para mayor claridad
print("Modelo de embeddings cargado.")

# Generar embeddings
chunk_embeddings = model_embeddings.encode(text_chunks, show_progress_bar=True)
print(f"Generados {len(chunk_embeddings)} embeddings.")

# Crear un índice FAISS para búsqueda eficiente
dimension = chunk_embeddings.shape[1]
faiss_index = faiss.IndexFlatL2(dimension) # Cambié el nombre para mayor claridad
faiss_index.add(np.array(chunk_embeddings).astype('float32'))

# Guardar el índice y los chunks para usarlos después
faiss.write_index(faiss_index, "pdf_embeddings.faiss")
with open("../../../Downloads/text_chunks.json", "w", encoding="utf-8") as f:
    json.dump(text_chunks, f, ensure_ascii=False, indent=4)

print("Embeddings y chunks guardados.")

# --- FUNCIÓN PRINCIPAL DEL CHATBOT ---

# ¡CAMBIO AQUÍ! La función ahora acepta model_embeddings, faiss_index y text_chunks como parámetros
def chat_with_eduaia(model_embeddings, faiss_index, text_chunks):
    print("Bienvenido a EduIA. ¡Hazme una pregunta!")
    print("Escribe 'salir' para terminar.")

    while True:
        user_query = input("Tú: ")
        if user_query.lower() == 'salir':
            print("EduIA: ¡Hasta pronto!")
            break

        # 1. Obtener chunks relevantes del PDF
        # Se usan los parámetros pasados a la función
        relevant_chunks = get_relevant_chunks(user_query, model_embeddings, faiss_index, text_chunks, k=3)

        # 2. Construir el prompt para Llama3 (o el modelo que estés usando)
        context = "\n\n".join(relevant_chunks)
        system_prompt = (
            "Eres EduIA, un mentor y asistente académico impulsado por Inteligencia Artificial. "
            "Tu propósito principal es guiar y apoyar a estudiantes universitarios en aspectos clave como la psicología educativa, "
            "el coaching académico (incluyendo técnicas de estudio, gestión del tiempo, etc.), y la orientación profesional. "
            "**Tu misión es proporcionar asesoramiento y recursos basados *exclusivamente* en la información detallada en el contexto proporcionado.** "
            "No te desvíes de esta información. Si una pregunta está fuera del contexto o no puedes responderla con la información dada, "
            "indica claramente que no tienes esa información y sugiere consultar a un profesional humano si aplica."
            "Mantén un tono empático, de apoyo y profesional, como un mentor experimentado."
        )
        full_prompt = f"{system_prompt}\n\nContexto:\n{context}\n\nPregunta del usuario: {user_query}\n\nRespuesta de EduIA:"

        # 3. Llamar a Ollama con el prompt y el contexto
        ai_response = call_ollama_deepseek(full_prompt) # Esta función ya usa "llama3"
        print(f"EduIA: {ai_response}")

# Para iniciar el chatbot, pasa las variables que acabas de cargar/generar
# ¡CAMBIO AQUÍ! Se pasan los argumentos a la función
chat_with_eduaia(model_embeddings, faiss_index, text_chunks)