import os
import io
import re
import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
from google.genai import types
import streamlit.components.v1 as components

# CONFIGURAÇÃO DE PÁGINA BLINDADA
st.set_page_config(
    page_title="HY Risk Intelligence | HI-AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ESTILIZAÇÃO CSS PREMIUM ADAPTADA E BLINDADA (DARK MODE)
st.markdown("""
    <style>
        /* FORÇADOR GLOBAL DE FUNDO ESCURO CORPORATIVO */
        .stApp, html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #0d1117 !important;
        }
        
        /* 1. CAIXAS DE MENSAGEM DO CHAT (DARK INTEGRADO) */
        .stChatMessage {
            background-color: #161b22 !important; 
            border: 1px solid #30363d !important;  
            border-radius: 8px;
            padding: 18px;
            margin-bottom: 12px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        /* Força a cor correta do texto em todas as mensagens */
        [data-testid="stChatMessageUser"] p,
        [data-testid="stChatMessageUser"] div,
        [data-testid="stChatMessageUser"] span,
        [data-testid="stChatMessageAssistant"] p,
        [data-testid="stChatMessageAssistant"] div,
        [data-testid="stChatMessageAssistant"] span {
            color: #c9d1d9 !important; 
            font-size: 15px !important;
            line-height: 1.6 !important;
        }
        
        /* 2. PAINEL LATERAL (SIDEBAR) CONTÍNUO */
        [data-testid="stSidebar"] {
            background-color: #070a0e !important;
            border-right: 1px solid #30363d !important;
        }
        
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] span, 
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #f0f6fc !important;
        }
        
        [data-testid="stSidebar"] .stMarkdown p {
            color: #8b949e !important;
            font-size: 13px !important;
        }

        /* Ajuste fino para os textos do selectbox na sidebar ficarem brancos */
        [data-testid="stSidebar"] div[data-baseweb="select"] div {
            color: #ffffff !important;
        }
        
        /* 3. CENTRALIZAÇÃO E COR DOS TÍTULOS */
        h1, h2, h3, .stSubheader, [data-testid="stHeader"] {
            text-align: center !important;
            justify-content: center !important;
        }
        
        h1, h2, h3 {
            color: #58a6ff !important; 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            font-weight: 600 !important;
        }
        
        .stCaption {
            text-align: center !important;
            color: #8b949e !important;
            font-size: 14px !important;
        }
        
        /* 4. DESIGN DOS CARDS DE MÉTRICAS (KPIs) */
        [data-testid="stMetricValue"] {
            color: #58a6ff !important;
            font-size: 28px !important;
            font-weight: bold !important;
            text-align: center !important;
        }
        [data-testid="stMetricLabel"] {
            color: #8b949e !important;
            font-size: 12px !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            text-align: center !important;
        }
        [data-testid="stMetricDelta"] {
            justify-content: center !important;
        }
        
        /* Botões laterais modernos */
        .stButton>button {
            width: 100%;
            background-color: #21262d !important;
            color: #c9d1d9 !important;
            border: 1px solid #30363d !important;
            border-radius: 6px;
        }
        .stButton>button:hover {
            border-color: #58a6ff !important;
            color: #58a6ff !important;
        }

        /* 5. BARRA DE MENSAGENS MINIMALISTA FLUTUANTE */
        [data-testid="stChatInput"] {
            background-color: transparent !important;
            box-shadow: none !important;
            padding: 15px 0px !important;
        }
        
        [data-testid="stChatInput"] textarea {
            color: #f0f6fc !important;
            background-color: #161b22 !important;
            border: 1px solid #30363d !important;
            border-radius: 6px !important;
        }
        [data-testid="stChatInput"] textarea:focus {
            border-color: #58a6ff !important;
        }
        
        [data-testid="stChatInput"] textarea::placeholder {
            color: #484f58 !important;
        }
        
        [data-testid="stChatInput"] button {
            background-color: transparent !important;
            color: #58a6ff !important;
        }

        /* Ajuste do uploader para ficar compacto */
        .stFileUploader section {
            padding: 0.5rem 1rem !important;
            background-color: #161b22 !important;
            border: 1px dashed #30363d !important;
            border-radius: 6px !important;
        }
        .stFileUploader label {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# Prompt Base do Sistema - Foco em Risk Intelligence e Governança
BASE_PROMPT = """
Você é o "HY RISK INTELLIGENCE-AI", um assistente de inteligência artificial especialista em Segurança da Informação atuando com foco em Risk Intelligence e Governança Estratégica. Sua missão é apoiar profissionais, gestores e analistas na tomada de decisões seguras, eficientes e alinhadas ao negócio.

REGRAS DE OPERAÇÃO:
1. **Abordagem Estratégica**: Responda sempre priorizando a mitigação de riscos, governança, conformidade, arquitetura segura e melhores práticas de cibersegurança.
2. **Estrutura da Resposta**: Você OBRIGATORIAMENTE deve usar estes quatro títulos exatos, com os respectivos emojis, para estruturar sua resposta:
   * **🚨 Visão Estratégica / Análise de Risco**: Comece contextualizando o impacto do problema para o negócio ou arquitetura geral.
   * **🛠️ Planos de Ação / Mitigação**: Forneça diretrizes práticas, comandos técnicos, códigos defensivos ou políticas de segurança recomendadas. Conclua e feche todas as listas que abrir, nunca deixe tópicos numerados vazios ou incompletos no final da resposta.
   * **🔍 Justificativa Técnico-Estratégica**: Descreva detalhadamente a lógica por trás da solução sugerida, abordando riscos como roubo de sessão (Session Hijacking), vazamentos, malwares ou engenharia social, explicando o porquê de a solução mitigar o risco com eficácia.
   * **📚 Referências**: Inclua uma lista de frameworks, normas ou guias de governança internacional relevantes para o caso (como diretrizes do NIST, ISO/IEC 27001, COBIT, OWASP ou MITRE ATT&CK).
3. **Ética**: Nunca forneça metodologias ofensivas para invasão ou destruição de ativos de forma ilegal. O foco deve ser estritamente defensivo, preventivo e corporativo.
"""

# Função de Higienização (Data Masking)
def higienizar_contexto(texto):
    texto = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP_REDACTED]', texto)
    texto = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]', texto)
    texto = re.sub(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b', '[CPF_REDACTED]', texto)
    return texto

# Inicialização do Cliente GenAI
@st.cache_resource
def get_ai_client():
    api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
    if not api_key:
        st.error("Chave de API do Gemini não encontrada!")
        st.stop()
    return genai.Client(api_key=api_key)

client = get_ai_client()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Cabeçalho da Aplicação
st.title("🛡️ HY RISK INTELLIGENCE")
st.caption("Suíte Estratégica de Governança e Resposta a Incidentes de Cibersegurança")

# ---- SIDEBAR DE OPERAÇÃO ----
with st.sidebar:
    st.subheader("⚙️ Painel de Controle")
    
    modelo_selecionado = st.selectbox(
        "Selecione o Motor de IA:",
        ["gemini-2.5-flash", "gemini-2.5-pro"]
    )
    
    # 🎤 RECURSO PROFESSIONAL 1: DITADO POR VOZ INTEGRADO NA SIDEBAR
    st.markdown("**🎙️ Transcrever Fala (Voz para Texto)**")
    componente_ditado_html = """
    <button id="start-record-btn" style="width:100%; padding:10px; background-color:#21262d; color:#c9d1d9; border:1px solid #30363d; border-radius:6px; cursor:pointer; font-weight:600;">
        🎙️ Ativar Microfone
    </button>
    <p id="status-voz" style="color:#8b949e; font-size:12px; text-align:center; margin-top:5px; font-family:sans-serif;">Pronto para escutar...</p>
    
    <script>
        const btn = document.getElementById('start-record-btn');
        const status = document.getElementById('status-voz');
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.lang = 'pt-BR';
            
            btn.addEventListener('click', () => {
                recognition.start();
                status.innerText = "🎙️ Escutando fala...";
                status.style.color = "#58a6ff";
                btn.style.borderColor = "#58a6ff";
            });
            
            recognition.onresult = (event) => {
                const textResult = event.results[0][0].transcript;
                status.innerText = "Inserido com sucesso!";
                status.style.color = "#238636";
                btn.style.borderColor = "#30363d";
                
                const chatInput = window.parent.document.querySelector('[data-testid="stChatInput"] textarea');
                if (chatInput) {
                    chatInput.value = textResult;
                chatInput.dispatchEvent(new Event('input', { bubbles: true }));
            };
            
            recognition.onerror = () => {
                status.innerText = "Erro ao capturar microfone.";
                status.style.color = "#f85149";
                btn.style.borderColor = "#30363d";
            };
            recognition.onspeechend = () => { recognition.stop(); };
        } else {
            status.innerText = "Recurso indisponível neste navegador.";
            btn.disabled = true;
        }
    </script>
    """
    components.html(componente_ditado_html, height=80)
    
    st.markdown("---")
    st.markdown("**📂 Análise de Logs ou Matriz de Risco**")
    arquivo_carregado = st.file_uploader("Upload de Arquivos", type=["csv", "xlsx", "txt", "log"])
    
    contexto_arquivo = ""
    if arquivo_carregado is not None:
        try:
            if arquivo_carregado.name.endswith(".csv"):
                df = pd.read_csv(arquivo_carregado)
                contexto_arquivo = f"\n[Dados do Arquivo {arquivo_carregado.name}]:\n" + df.head(50).to_string()
                st.success("CSV anexado.")
            elif arquivo_carregado.name.endswith(".xlsx"):
                df = pd.read_excel(arquivo_carregado)
                contexto_arquivo = f"\n[Dados do Arquivo {arquivo_carregado.name}]:\n" + df.head(50).to_string()
                st.success("Excel anexado.")
            else:
                stringio = io.StringIO(arquivo_carregado.getvalue().decode("utf-8"))
                contexto_arquivo = f"\n[Conteúdo do Log {arquivo_carregado.name}]:\n" + stringio.read()[:5000]
                st.success("Log indexado.")
        except Exception as e:
            st.error(f"Erro ao processar arquivo: {e}")

    st.markdown("---")
    if st.button("🗑️ Limpar Sessão Atual"):
        st.session_state.messages = []
        st.rerun()

# ---- ÁREA DE DIÁLOGO (CHAT) ----
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de novas mensagens
if prompt_usuario := st.chat_input("Digite sua dúvida estratégica ou técnica sobre segurança..."):
    prompt_higienizado = higienizar_contexto(prompt_usuario)
    
    with st.chat_message("user"):
        st.markdown(prompt_higienizado)
    st.session_state.messages.append({"role": "user", "content": prompt_higienizado})
    
    with st.chat_message("assistant"):
        placeholder_resposta = st.empty()
        
        historico_contents = []
        for msg in st.session_state.messages[:-1]:
            historico_contents.append(
                types.Content(
                    role="user" if msg["role"] == "user" else "model",
                    parts=[types.Part.from_text(text=msg["content"])]
                )
            )
            
        input_final = prompt_higienizado
        if contexto_arquivo:
            input_final += f"\n\nAnalise também as informações contidas no seguinte arquivo corporativo:\n{contexto_arquivo}"
            
        historico_contents.append(
            types.Content(role="user", parts=[types.Part.from_text(text=input_final)])
        )
        
        configuracao_ia = types.GenerateContentConfig(
            system_instruction=BASE_PROMPT,
            temperature=0.2,
            top_p=0.95
        )
        
        if modelo_selecionado == "gemini-2.5-pro":
            configuracao_ia.thinking_config = types.ThinkingConfig(thinking_budget=1024)

        try:
            resposta_stream = client.models.generate_content_stream(
                model=modelo_selecionado,
                contents=historico_contents,
                config=configuracao_ia
            )
            
            resposta_completa = ""
            for fragmento in resposta_stream:
                resposta_completa += fragmento.text
                placeholder_resposta.markdown(resposta_completa + "▌")
                
            placeholder_resposta.markdown(resposta_completa)
            st.session_state.messages.append({"role": "assistant", "content": resposta_completa})
            
            # 🔊 RECURSO PROFESSIONAL 2: TEXTO PARA VOZ (FALA DA IA)
            texto_limpo = re.sub(r'[*#`_\-🚨🛠️🔍📚]', '', resposta_completa).replace('"', '\\"').replace('\n', ' ')
            
            componente_audio_html = f"""
            <script>
                if ('speechSynthesis' in window) {{
                    window.speechSynthesis.cancel();
                    const msg = new SpeechSynthesisUtterance("{texto_limpo}");
                    msg.lang = "pt-BR";
                    msg.rate = 1.1; // Ritmo ágil corporativo
                    window.speechSynthesis.speak(msg);
                }}
            </script>
            """
            components.html(componente_audio_html, height=0, width=0)
            
        except Exception as e:
            st.error(f"Falha na comunicação com o motor do HY-AI: {e}")

# ---- EXPORTAÇÃO DE RELATÓRIOS ----
if st.session_state.messages:
    st.markdown("---")
    buffer_relatorio = io.BytesIO()
    conteudo_texto = "==================================================\n"
    conteudo_texto += "       HY RISK INTELLIGENCE - REPORT (RI-AI)       \n"
    conteudo_texto += "    Mapeamento estrategico e blindagem de ativos  \n"
    conteudo_texto += "==================================================\n\n"
    
    for idx, msg in enumerate(st.session_state.messages, 1):
        autor = "USUARIO" if msg["role"] == "user" else "HY-AI"
        conteudo_texto += f"[{idx}] {autor}:\n{msg['content']}\n"
        conteudo_texto += "-"*50 + "\n"
        
    buffer_relatorio.write(conteudo_texto.encode("utf-8"))
    buffer_relatorio.seek(0)
    
    st.download_button(
        label="📥 Exportar Relatório de Governança (.TXT)",
        data=buffer_relatorio,
        file_name="hy_risk_intelligence_report.txt",
        mime="text/plain"
    )
