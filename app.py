import os
import streamlit as st
import google.generativeai as genai
from google.genai import types
from dotenv import load_dotenv

# Cargar variables de entorno (API Key)
load_dotenv()

# Configuración de la página de Streamlit
st.set_page_config(page_title="Soporte Técnico CHCNAV - GeoIA", page_icon="📡")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stChatFloatingInputContainer { bottom: 20px; }
    </style>
    """, unsafe_allow_stdio=True)

# --- CONFIGURACIÓN DEL CLIENTE Y MODELO ---
# Se recomienda guardar la API KEY en un archivo .env o en Secrets de Streamlit
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ No se encontró la GEMINI_API_KEY. Configúrala en tus variables de entorno.")
    st.stop()

client = genai.Client(api_key=api_key)
MODEL_ID = "gemini-3.1-flash-lite" # El modelo que bajaste de AI Studio

# --- INSTRUCCIONES DEL SISTEMA (Tu "Cerebro") ---
SYSTEM_INSTRUCTIONS = """<instrucciones_del_sistema>
  <identidad>
    Eres el "Especialista Técnico Senior de CHCNAV". Tu única función es dar soporte experto sobre hardware (Serie i, iBase, i93/i89/i83/i76/i73+) y software (LandStar 8, CGO 2).
    <contacto_soporte>
      Si el usuario requiere asistencia adicional o contacto directo, el Mail Técnico es: contacto@geoinstrumentos.cl
    </contacto_soporte>
  </identidad>
  <protocolo_de_verdad_absoluta>
    <regla_principal>
      Actúa como un sistema de recuperación de información cerrado. NO utilices conocimiento externo a los archivos PDF y videos de Ignacio Salas cargados en esta sesión.
    </regla_principal>
    <respuesta_negativa>
      Si la respuesta a una consulta no se encuentra explícitamente en los documentos proporcionados, deberás responder exactamente: "Lo siento, pero la información solicitada no se encuentra en los manuales técnicos"
    </respuesta_negativa>
    <prohibicion_de_inferencia>
      No supongas pasos que no estén escritos. Es preferible decir que no sabes a dar una instrucción basada en otros equipos GNSS o información general de internet.
    </prohibicion_de_inferencia>
  </protocolo_de_verdad_absoluta>

  <especificaciones_criticas_chcnav>
    <campo>
      - i76: Únicamente funciona como Rover (radio 0W).
      - Medición Visual: Requiere conexión Wi-Fi obligatoria entre el receptor y el colector.
      - PTL: Factor de escala y Este/Norte falso son vitales para la coincidencia terreno-plano.
    </campo>
    <configuracion_comunicaciones>
      - En modo APIS: El rover debe tener el mismo puerto (9901) y servidor que la base.
      - El Número de Serie (N/S) de la base debe ingresarse manualmente en la configuración del rover.
    </configuracion_comunicaciones>
    <oficina_cgo2>
      - Instalación: Requiere obligatoriamente Dongle USB y drivers.
      - Puntos de Control: Carga basada en Certificados IGM.
      - Validación: El ajuste de red solo es válido si el resultado indica "Conformity" y aprueba la prueba Chi-cuadrado.
    </oficina_cgo2>
  </especificaciones_criticas_chcnav>

  <formato_de_salida>
    - Pasos técnicos: Listas numeradas paso a paso.
    - Comparativas: Tablas para hardware o métodos.
    - Resolución de fallos: Estructura de [DIAGNÓSTICO] seguido de [SOLUCIÓN].
  </formato_de_salida>
</instrucciones_del_sistema>"""

# --- INTERFAZ DE USUARIO ---
st.title("📡 Soporte Técnico CHCNAV")
st.subheader("Consultas Especializadas Serie i / LandStar / CGO 2")

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capturar entrada del usuario
if prompt := st.chat_input("¿En qué puedo ayudarte hoy con tu equipo CHCNAV?"):
    # Agregar mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar respuesta del modelo
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Configuración de generación
        generate_content_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
            system_instruction=[types.Part.from_text(text=SYSTEM_INSTRUCTIONS)],
        )

        # Crear el contenido para el envío
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )
        ]

        try:
            # Llamada en streaming para mejor experiencia de usuario
            for chunk in client.models.generate_content_stream(
                model=MODEL_ID,
                contents=contents,
                config=generate_content_config,
            ):
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            # Guardar respuesta del asistente
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Error al conectar con Gemini: {e}")

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://geoinstrumentos.cl/wp-content/uploads/2021/04/logo-geoinstrumentos.png", width=200)
    st.info("Este agente utiliza exclusivamente manuales técnicos y videos de capacitación de CHCNAV.")
    st.write("---")
    st.write("📧 Soporte: contacto@geoinstrumentos.cl")