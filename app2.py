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
        .stApp, html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #0d1117 !important;
        }
        .stChatMessage {
            background-color: #161b22 !important; 
            border: 1px solid #30363d !important;  
            border-radius: 8px;
            padding: 18px;
            margin-bottom: 12px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15);
        }
        [data-testid="stChatMessageUser"] p, [data-testid="stChatMessageUser"] div, [data-testid="stChatMessageUser"] span,
        [data-testid="stChatMessageAssistant"] p, [data-testid="stChatMessageAssistant"] div, [data-testid="stChatMessageAssistant"] span {
            color: #c9d1d9 !important; 
            font-size: 15px !important;
            line-height: 1.6 !important;
        }
        [data-testid="stSidebar"] {
            background-color: #070a0e !important;
            border-right: 1px solid #30363d !important;
        }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: #f0f6fc !important;
        }
        [data-testid="stSidebar"] .stMarkdown p {
            color: #8b949e !important;
            font-size: 13px !important;
        }
        [data-testid="stSidebar"] div[data-baseweb="select"] div {
            color: #ffffff !important;
        }
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
        
        /* BARRA DE MENSAGENS MINIMALISTA ADAPTADA PARA O MICROFONE */
        [data-testid="stChatInput"] {
            background-color: transparent !important;
            box-shadow: none !important;
            padding: 15px 0px !important;
            position: relative;
        }
        [data-testid="stChatInput"] textarea {
            color: #f0f6fc !important;
            background-color: #161b22 !important;
            border: 1px solid #30363d !important;
            border-radius: 24px !important; /* Bordas arredondadas iguaizinhas à sua imagem */
            padding-right: 85px !important; /* Espaço para o microfone e botão de enviar */
            padding-left: 20px !important;
        }
        [data-testid="stChatInput"] textarea:focus {
            border-color: #58a6ff !important;
        }
        [data-testid="stChatInput"] textarea::placeholder {
            color: #8b949e !important;
        }
        [data-testid="stChatInput"] button {
            background-color: transparent !important;
            color: #58a6ff !important;
            right: 15px !important;
        }
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
   * **🔍 Justificativa Técnico-Estratégica**: Descreva detalhadamente a lógica por trás della solução sugerida, abordando riscos como roubo de sessão (Session Hijacking), vazamentos, malwares ou engenharia social, explicando o porquê de a solução mitigar o risco com eficácia.
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

# 1. ESTA LINHA DEVE VIR ANTES DE TUDO: Captura o texto do chat
if prompt_usuario := st.chat_input("Pergunte o que quiser..."):
    
    # 2. Aqui a variável é criada corretamente
    prompt_higienizado = higienizar_contexto(prompt_usuario)
    
    # Exibe a mensagem do usuário na tela
    with st.chat_message("user"):
        st.markdown(prompt_higienizado)
    st.session_state.messages.append({"role": "user", "content": prompt_higienizado})
    
    # Abre o container do assistente
    with st.chat_message("assistant"):
        placeholder_resposta = st.empty()
        
        # Reconstrói o histórico
        historico_contents = []
        for msg in st.session_state.messages[:-1]:
            historico_contents.append(
                types.Content(
                    role="user" if msg["role"] == "user" else "model",
                    parts=[types.Part.from_text(text=msg["content"])]
                )
            )
            
        # 3. AGORA SIM: Usa a variável 'prompt_higienizado' com segurança (Identado dentro do IF)
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
            
            # 🔊 TEXTO PARA VOZ (FALA DA IA)
            texto_limpo = re.sub(r'[*#`_\-🚨🛠️🔍📚]', '', resposta_completa).replace('"', '\\"').replace('\n', ' ')
            
            componente_audio_html = f"""
            <script>
                if ('speechSynthesis' in window) {{
                    window.speechSynthesis.cancel();
                    const msg = new SpeechSynthesisUtterance("{texto_limpo}");
                    msg.lang = "pt-BR";
                    msg.rate = 1.1;
                    window.speechSynthesis.speak(msg);
                }}
            </script>
            """
            components.html(componente_audio_html, height=0, width=0)
            
        except Exception as e:
            st.error(f"Falha na comunicação com o motor do HY-AI: {e}")


# 🎙️ EMBUTIDOR DO MICROFONE DENTRO DA CAIXA DE CHAT (Injeção de Elemento UI)
componente_microfone_embutido = """
<script>
    function injetarMicrofone() {
        // Encontra o container de input do chat do Streamlit na janela principal
        const chatContainer = window.parent.document.querySelector('[data-testid="stChatInput"]');
        const textarea = window.parent.document.querySelector('[data-testid="stChatInput"] textarea');
        
        if (chatContainer && textarea && !window.parent.document.getElementById('mic-embutido-btn')) {
            // Cria o botão do microfone estilizado e posicionado exatamente dentro da caixa
            const micBtn = window.parent.document.createElement('button');
            micBtn.id = 'mic-embutido-btn';
            micBtn.innerHTML = '🎤';
            micBtn.style.position = 'absolute';
            micBtn.style.right = '55px'; /* Fica ao lado esquerdo do botão nativo de enviar */
            micBtn.style.top = '50%';
            micBtn.style.transform = 'translateY(-50%)';
            micBtn.style.background = 'none';
            micBtn.style.border = 'none';
            micBtn.style.fontSize = '18px';
            micBtn.style.cursor = 'pointer';
            micBtn.style.zIndex = '999';
            micBtn.title = 'Ditado por voz';
            
            // Configura o reconhecimento de voz nativo do navegador
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (SpeechRecognition) {
                const recognition = new SpeechRecognition();
                recognition.lang = 'pt-BR';
                
                micBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    recognition.start();
                    micBtn.innerHTML = '🛑';
                    textarea.placeholder = "Escutando... fale agora.";
                });
                
                recognition.onresult = (event) => {
                    const textoDitado = event.results[0][0].transcript;
                    textarea.value = textoDitado;
                    textarea.dispatchEvent(new Event('input', { bubbles: true }));
                    micBtn.innerHTML = '🎤';
                    textarea.placeholder = "Pergunte o que quiser...";
                };
                
                recognition.onerror = () => {
                    micBtn.innerHTML = '🎤';
                    textarea.placeholder = "Erro ao escutar. Tente de novo.";
                };
                
                recognition.onspeechend = () => {
                    recognition.stop();
                    micBtn.innerHTML = '🎤';
                };
            } else {
                micBtn.style.display = 'none';
            }
            
            chatContainer.appendChild(micBtn);
        }
    }
    // Roda repetidamente para garantir a persistência caso o Streamlit recarregue a UI
    setInterval(injetarMicrofone, 1000);
</script>
"""
components.html(componente_microfone_embutido, height=0, width=0)


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
