import os
import openai
from dotenv import load_dotenv
from duckduckgo_search import DDGS

load_dotenv()

# Initialize OpenAI client (DeepSeek Compatible)
api_key = os.getenv("DEEPSEEK_API_KEY") # Prioritize DeepSeek
if not api_key:
    api_key = os.getenv("OPENAI_API_KEY")
    BASE_URL = None
    MODEL_NAME = "gpt-3.5-turbo"
else:
    BASE_URL = "https://api.deepseek.com"
    MODEL_NAME = "deepseek-chat"

client = openai.OpenAI(api_key=api_key, base_url=BASE_URL)

SYSTEM_PROMPT = """
Eres 'IuristaTech AI', un asistente legal virtual experto en derecho colombiano.
Tu objetivo es orientar a usuarios (principalmente Pymes y personas naturales) en tres áreas clave:
1. Derecho Laboral y Seguridad Social via Ministerio de Trabajo.
2. Derecho Inmobiliario y Arrendamientos via Ley 820 de 2003.
3. Derecho Migratorio via Cancillería y Migración Colombia.

Directrices:
- Responde de manera profesional, empática y concisa.
- Cita siempre la normativa aplicable (Leyes, Decretos, Sentencias C-XXX).
- Si detectas riesgos legales graves (demanda inminente, vencimiento de términos), advierte al usuario con un emoji de alerta ⚠️.
- Si la consulta está fuera de tus 3 áreas de especialidad, infórmalo amablemente y sugiere contactar a un abogado humano.
- No inventes leyes. Si no sabes, di que necesitas verificar la información.
- Estructura tus respuestas con viñetas o negritas para facilitar la lectura.

4. Redacción de Documentos:
- Si el usuario solicita un contrato, derecho de petición o carta, NO lo generes de inmediato si faltan datos.
- Actúa como un abogado meticuloso: Pregunta los detalles necesarios (Nombres, Cédulas, Fechas, Valores, Cláusulas especiales) antes de redactar.
- Una vez tengas la información, genera el documento completo en formato Markdown, usando bloques de código o formato claro para copiar y pegar.

Al final de tu respuesta, clasifica internamente el "estado" de la consulta en una de estas categorías:
- 'analyzing': Consulta normal informativa o entrevista inicial.
- 'risk': Se detecta un riesgo legal o urgencia.
- 'document': El usuario solicita un documento y tú lo estás entregando o redactando.

IMPORTANTE: Genera siempre 2 o 3 "Acciones Sugeridas" cortas para que el usuario continúe la conversación.
Usa el formato estricto: [ACCION: Título de la acción] al final del texto.
Ejemplos:
[ACCION: Redactar Contrato]
[ACCION: Ver Ley 820]
[ACCION: Contactar Abogado]
"""

def search_web(query):
    """Realiza una búsqueda web rápida para obtener contexto actualizado."""
    try:
        results = DDGS().text(f"colombia derecho legal {query}", max_results=3)
        if not results:
            return ""
        
        search_ctx = "\n\n--- RESULTADOS DE BÚSQUEDA WEB (USAR SOLO SI ES RELEVANTE) ---\n"
        for r in results:
            search_ctx += f"- {r['title']}: {r['body']} (Fuente: {r['href']})\n"
        return search_ctx
    except Exception as e:
        print(f"Error searching web: {e}")
        return ""

def generate_response(message, conversation_id=None, document_context=None):
    try:
        if not api_key or "placeholder" in api_key:
            return {
                "text": "Error de configuración: No se ha detectado una API Key válida (DeepSeek/OpenAI). Por favor, configure las variables de entorno.",
                "status": "risk"
            }

        detailed_system_prompt = SYSTEM_PROMPT

        # 0. Inject uploaded document context
        if document_context:
            doc_name = document_context.get('filename', 'Documento')
            doc_text = document_context.get('text', '')
            if doc_text:
                detailed_system_prompt += f"""

--- DOCUMENTO CARGADO POR EL USUARIO: "{doc_name}" ---
{doc_text[:15000]}
--- FIN DEL DOCUMENTO ---

INSTRUCCIÓN CRÍTICA SOBRE EL DOCUMENTO:
- El usuario ha cargado este documento para tu análisis.
- DEBES leer, comprender y analizar el contenido del documento.
- Proporciona un resumen, identifica puntos clave legales, riesgos potenciales y criterios jurídicos relevantes.
- Si el usuario hace preguntas sobre el documento, responde basándote en su contenido.
- Cita secciones específicas del documento cuando sea relevante.
"""

        # 0. Fetch Knowledge Base Context
        try:
            from models import KnowledgeBase
            docs = KnowledgeBase.query.all()
            if docs:
                context_text = "\n\n".join([f"--- DOCUMENTO REFERENCIA: {d.title} ---\n{d.content[:5000]}..." for d in docs]) # Limit to 5k chars per doc
                detailed_system_prompt += f"\n\n5. BASE DE CONOCIMIENTO (FUENTE PRIMARIA Y OBLIGATORIA):\n{context_text}\n\nINSTRUCCIÓN CRÍTICA: La respuesta DEBE basarse principalmente en los documentos anteriores. Si la información está en estos documentos, úsala y cítala explícitamente. Ignora tu conocimiento general si contradice estos documentos."
        except Exception as e:
            print(f"Error loading knowledge base: {e}")

        # 1. Perform Web Search for current query
        search_context = search_web(message)
        if search_context:
            detailed_system_prompt += search_context + "\nInstrucción: Usa la información de búsqueda web para complementar tu respuesta, especialmente para leyes recientes o datos actualizados."

        detailed_system_prompt += "\n\nINSTRUCCIÓN DE SÍNTESIS: Para responder, DEBES integrar estas tres fuentes:\n1. TUS ARCHIVOS (Base de Conocimiento): Prioridad máxima para datos específicos del usuario.\n2. BÚSQUEDA WEB: Úsala para actualizar leyes o confirmar hechos recientes.\n3. TU CONOCIMIENTO: Úsalo para explicar conceptos, dar estructura y sentido legal.\n\nCombina todo para dar la respuesta más completa y precisa posible."

        messages_payload = [{"role": "system", "content": detailed_system_prompt}]
        
        if conversation_id:
            from models import Message
            # Fetch last 10 messages
            past_messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at.desc()).limit(10).all()
            past_messages.reverse()
             
            for msg in past_messages:
                role = "assistant" if msg.sender_role == "assistant" else "user"
                messages_payload.append({"role": role, "content": msg.content})

        # Append current user message
        messages_payload.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model=MODEL_NAME, 
            messages=messages_payload,
            temperature=0.3, # Low temperature for factual accuracy
        )

        ai_text = response.choices[0].message.content
        
        # Parse Suggested Actions
        import re
        suggested_actions = []
        # Regex to find [ACCION: ...]
        actions_found = re.findall(r'\[ACCION: (.*?)\]', ai_text)
        if actions_found:
            suggested_actions = actions_found
            # Remove actions from text to keep it clean
            ai_text = re.sub(r'\[ACCION: .*?\]', '', ai_text).strip()

        status = 'analyzing'
        if '⚠️' in ai_text or 'riesgo' in ai_text.lower():
            status = 'risk'
        elif 'contrato' in ai_text.lower() or 'documento' in ai_text.lower():
            status = 'document'
            
        return {"text": ai_text, "status": status, "suggested_actions": suggested_actions}

    except Exception as e:
        print(f"OpenAI Error: {e}")
        if "insufficient_quota" in str(e) or "429" in str(e):
            return {
                "text": "⚠️ **Aviso de Sistema**: El servicio de IA está temporalmente saturado (Cuota Excedida). \n\n" + 
                        "Sin embargo, puedo orientarle con información general: \n" +
                        "Para temas laborales, consulte el Código Sustantivo del Trabajo. \n" +
                        "Para temas inmobiliarios, la Ley 820 de 2003. \n" +
                        "Le sugiero contactar directamente a nuestros abogados humanos.",
                "status": "risk"
            }
            
        return {
            "text": "Lo siento, estoy experimentando dificultades técnicas para procesar tu consulta legal en este momento. Por favor, intenta de nuevo más tarde.",
            "status": "analyzing"
        }
