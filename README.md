MODELO FUNCIONAL Y DEFINITIVO ELEGIDO
🔹 Nombre del sistema: EduIA – Mentor Académico 24/7 con IA
🔹 Tipo de solución: Chatbot académico con recuperación de información basada en documentos PDF, enriquecido con embeddings semánticos y una IA generativa para respuestas personalizadas.
✅ JUSTIFICACIÓN DE LA ELECCIÓN DEL MODELO
Funcionalidad comprobada: El código fue probado exitosamente, permitiendo responder preguntas específicas sobre material educativo en formato PDF usando IA generativa local (Llama3 vía Ollama).

Simplicidad escalable: La arquitectura inicial es modular y admite escalabilidad (agregando APIs, más modelos, bases de datos, LMS, etc.).

Precisión semántica: Usa SentenceTransformer con paraphrase-multilingual-MiniLM-L12-v2, lo que permite interpretar la semántica del contenido educativo en español y otras lenguas.

Búsqueda eficiente: El índice FAISS permite recuperar rápidamente los fragmentos relevantes del contenido académico.

Respuestas relevantes: El modelo Llama3, al usar contexto, reduce el riesgo de "alucinaciones" y responde sólo según la información cargada (seguridad académica).

Alineación con la visión de EduIA: El flujo IA-embedding-contexto-documentos se ajusta perfectamente a la idea de mentoría personalizada, sin depender aún de LMS o universidades, pero compatible con ese futuro.

✅ ELEMENTOS DEL MODELO INTEGRADOS EN EL CÓDIGO
A continuación se detallan todas las conexiones, modelos, APIs y herramientas incluidas o simuladas en el código script.py que componen el MVP:

🔸 1. Extracción de contenido desde PDFs
Librería: PyPDF2

Función: extract_text_from_pdf()

Objetivo: Convertir múltiples PDFs en texto plano para ser usado como base de conocimiento.

🔸 2. Segmentación de texto en chunks
Función: split_text_into_chunks()

Parámetros ajustables: max_chunk_size=500, overlap=50

Objetivo: Permitir mejor recuperación contextual en la fase de embeddings y consulta.

🔸 3. Modelo de embeddings semánticos
Librería: sentence-transformers

Modelo utilizado: 'paraphrase-multilingual-MiniLM-L12-v2'

Función: model.encode(text_chunks)

Objetivo: Convertir texto en vectores que capturen el significado semántico del contenido.

🔸 4. Indexación semántica con FAISS
Librería: faiss

Índice: IndexFlatL2

Uso: faiss_index.add(...), luego index.search(...)

Objetivo: Buscar fragmentos más similares semánticamente al input del usuario.

🔸 5. Modelo generativo (LLM)
Interfaz: Ollama API (local)

Modelo LLM: "llama3" (deepseek/llama3 puede ajustarse)

Endpoint: http://localhost:11434/api/generate

Formato solicitud:

json
Copiar
Editar
{
  "model": "llama3",
  "prompt": "<prompt>",
  "stream": false
}
Función encargada: call_ollama_deepseek()

🔸 6. Prompt estructurado y rol del sistema
Se define a EduIA como mentor académico especializado en psicología educativa, coaching y vocación, restringido a solo usar el contenido documental.

El prompt incluye: rol del sistema + contexto relevante (chunks) + pregunta del usuario.




FLUJO DE AUTOMATIZACIÓN DEL SCRIPT.PY (DESCRIPCIÓN COMPLETA)
A continuación, el flujo funcional automatizado del script script.py:

less
Copiar
Editar
[INICIO SCRIPT]
        │
        ▼
[CARGA Y EXTRACCIÓN]
→ Se define la carpeta de PDFs.
→ Se recorre la carpeta y se extrae texto de cada PDF con PyPDF2.
→ Si falla la extracción, el programa se detiene.

        │
        ▼
[SEGMENTACIÓN EN CHUNKS]
→ El texto completo se divide en fragmentos de 500 caracteres con solapamiento.

        │
        ▼
[EMBEDDINGS]
→ Se carga el modelo de SentenceTransformer.
→ Se generan embeddings para cada fragmento.
→ Se guarda el índice FAISS (`pdf_embeddings.faiss`) y los chunks (`text_chunks.json`).

        │
        ▼
[SE INICIA EL CHATBOT]
→ `chat_with_eduaia()` solicita input del usuario en consola.

        │
        ▼
[RESPUESTA EN TIEMPO REAL]
→ Para cada pregunta:
    1. Se calcula su embedding.
    2. Se buscan los 3 chunks más relevantes usando FAISS.
    3. Se construye el prompt completo para el modelo LLM (EduIA).
    4. Se hace una llamada POST a la API local de Ollama.
    5. Se muestra la respuesta generada.

        │
        ▼
[LOOP hasta que el usuario escribe 'salir']


✅ CONCLUSIÓN
El modelo funcional y definitivo elegido es un sistema conversacional basado en recuperación aumentada por IA (RAG). La elección se justifica por su equilibrio entre robustez técnica, personalización educativa, facilidad de uso y escalabilidad futura. El código script.py implementa correctamente esta arquitectura, con todos los componentes fundamentales documentados,
