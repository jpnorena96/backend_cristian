import os
import openai
from dotenv import load_dotenv

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
"""

def generate_response(message, conversation_id=None):
    try:
        if not api_key or "placeholder" in api_key:
            return {
                "text": "Error de configuración: No se ha detectado una API Key válida (DeepSeek/OpenAI). Por favor, configure las variables de entorno.",
                "status": "risk"
            }

        # Build message history
        # 0. Fetch Knowledge Base Context
        try:
            from models import KnowledgeBase
            docs = KnowledgeBase.query.all()
            if docs:
                context_text = "\n\n".join([f"--- DOCUMENTO REFERENCIA: {d.title} ---\n{d.content[:5000]}..." for d in docs]) # Limit to 5k chars per doc to avoid token overflow
                
                # Append context instructions to system prompt
                detailed_system_prompt = SYSTEM_PROMPT + f"\n\n5. BASE DE CONOCIMIENTO (USAR PARA RESPUESTAS):\n{context_text}\n\nInstrucción: Si la consulta del usuario se relaciona con alguno de los documentos anteriores, ÚSALOS como base principal para tu respuesta o redacción."
            else:
                detailed_system_prompt = SYSTEM_PROMPT
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            detailed_system_prompt = SYSTEM_PROMPT

        messages_payload = [{"role": "system", "content": detailed_system_prompt}]
        
        if conversation_id:
            from models import Message
            # Fetch last 10 messages to maintain context without exceeding token limits
            # Import db inside function to avoid circular imports if necessary, 
            # or rely on the fact that models are available if app context is active
            
            # Simple query: last 10 messages for this conversation, ordered by time
            # Note: We need to filter out system messages if any, or just take user/assistant
            past_messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at.desc()).limit(10).all()
            
            # Reorder to chronological for the LLM
            past_messages.reverse()
             
            for msg in past_messages:
                # Map role 'assistant'/'user'. Ensure we don't accidently include system errors as context if stored
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
        
        # Simple heuristic to determine status based on keywords in AI response or user input
        #Ideally, we would ask the LLM to output JSON with status, but text is fine for now.
        status = 'analyzing'
        if '⚠️' in ai_text or 'riesgo' in ai_text.lower():
            status = 'risk'
        elif 'contrato' in ai_text.lower() or 'documento' in ai_text.lower():
            status = 'document'
            
        return {"text": ai_text, "status": status}

    except Exception as e:
        print(f"OpenAI Error: {e}")
        # Fallback to hardcoded responses if OpenAI fails (Quota or Network)
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
