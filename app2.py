import os
import io
import re
import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
from google.genai import types

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

# ==========================================
# SOLUÇÃO DO ERRO 503: INICIALIZAÇÃO DA SDK COM RETRY
# ==========================================
# O parâmetro max_retries força a SDK a tentar novamente usando backoff exponencial automático
@st.cache_resource
def inicializar_cliente_ia():
    return genai.Client() # Remove as http_options daqui

client = inicializar_cliente_ia()


# Função de Higienização (Data Masking)
def higienizar_contexto(texto):
    texto = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP_REDACTED]', texto)
    texto = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]', texto)
    texto = re.sub(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b', '[CPF_REDACTED]', texto)
    return texto

# Inicializa as variáveis no session_state do Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = []

# Função para gerar um relatório em PDF/Texto formatado
def gerar_relatorio_estrategico(historico):
    conteudo = "==================================================\n"
    conteudo += "       HY RISK INTELLIGENCE - REPORT (RI-AI)       \n"
    conteudo += "    Mapeamento estratégico e blindagem de ativos  \n"
    conteudo += "==================================================\n\n"
    
    for idx, msg in enumerate(historico, 1):
        autor = "USUÁRIO" if msg["role"] == "user" else "HY-AI"
        conteudo += f"[{idx}] {autor}:\n"
        conteudo += f"{msg['content']}\n\n"
    return conteudo

# INTERFACE GRÁFICA DO STREAMLIT
st.title("🛡️ HY Risk Intelligence AI")
st.caption("Governança Corporativa e Análise de Riscos Estratégicos Baseada em Dados")

# Exibição do Histórico do Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Colado na margem esquerda (Sem espaços antes)
if user_input := st.chat_input("Insira sua análise, log ou cenário de risco corporativo..."):
    # 4 Espaços (1 Tab) antes destas linhas:
    texto_higienizado = higienizar_contexto(user_input)
    st.session_state.messages.append({"role": "user", "content": texto_higienizado})
    
    with st.chat_message("user"):
        # 8 Espaços (2 Tabs) antes desta linha:
        st.write(texto_higienizado)

    with st.chat_message("assistant"):
        # 8 Espaços (2 Tabs) antes destas linhas:
        placeholder = st.empty()
        placeholder.markdown("*Analisando arquitetura e calculando riscos de conformidade...*")
        
        historico_api = [{"role": "user", "parts": [BASE_PROMPT]}]
        
        for m in st.session_state.messages:
            # 12 Espaços (3 Tabs) antes destas duas linhas abaixo (Onde dava o erro):
            role_api = "user" if m["role"] == "user" else "model"
            historico_api.append({"role": role_api, "parts": [m["content"]]})
            
        try:
            # 12 Espaços (3 Tabs) antes do bloco de envio:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=historico_api
            )
            resposta_ia = response.text
            placeholder.markdown(resposta_ia)
            st.session_state.messages.append({"role": "assistant", "content": resposta_ia})
            
        except Exception as e:
            # 12 Espaços (3 Tabs) antes do tratamento de erro:
            erro_msg = (
                "⚠️ **Erro de Conexão com o Core da IA (503)**: O servidor do modelo está enfrentando um pico massivo "
                "de acessos neste momento. As tentativas de reconexão automática foram esgotadas. Por favor, "
                "aguarde alguns instantes e envie a mensagem novamente."
            )
            placeholder.error(erro_msg)
            print(f"[HY-AI LOG ERROR]: {str(e)}")


# ==========================================
# SIDEBAR DE CONTROLE E EXPORTAÇÃO
# ==========================================
with st.sidebar:
    st.markdown("### 📊 Painel de Governança")
    st.markdown("Utilize este espaço para auditar as conversas atuais e exportar artefatos de conformidade.")
    
    if st.session_state.messages:
        # Botão para baixar relatório do chat atual
        relatorio_txt = gerar_relatorio_estrategico(st.session_state.messages)
        st.download_button(
            label="📥 Exportar Relatório de Risco",
            data=relatorio_txt,
            file_name="hy_risk_intelligence_report.txt",
            mime="text/plain"
        )
        
        # Botão para limpar a sessão
        if st.button("🗑️ Limpar Sessão do Chat"):
            st.session_state.messages = []
            st.rerun()
