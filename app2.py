import os
import io
import streamlit as st
from google import genai
from google.genai import types

# CONFIGURAÇÃO DE PÁGINA BLINDADA
st.set_page_config(
    page_title="HY Risk Intelligence | RI-AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialize o cliente corretamente antes de usá-lo
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"Erro ao inicializar a API Key do Gemini: {e}. Verifique seus Secrets.")

with st.sidebar:
    st.title("🔵 HY RI-AI")
    st.caption("Mapeamento estratégico e blindagem de ativos")
    
    st.write("---")
    st.subheader("🌐 Escopo de Análise")
    foco_problema = st.selectbox(
        label="Selecione o foco do problema:",
        options=["Geral / Sem Filtro", "Infraestrutura", "Aplicações Web", "Políticas de GRC"]
    )
    
    st.write("---")
    
    st.subheader("📂 Analisador de Logs")
    uploaded_file = st.file_uploader("Upload de arquivo de log", type=["txt", "log", "csv"], label_visibility="collapsed")
    if uploaded_file:
        st.success("Log carregado com sucesso!")
        st.title("📊 PAINEL DE INDICADORES EXECUTIVOS (KPIs)")

# Criação das 4 colunas de métricas superiores
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="ANÁLISES EFETUADAS", value="0")
    st.info("⬆️ SOC Ativo")

with col2:
    st.metric(label="CONTROLES DE GRC", value="NIST / ISO")
    st.success("⬆️ Mapeados")
    with col3:
    st.metric(label="STATUS DE CONFORMIDADE", value="98.4%", delta="+1.2% este mês")
    st.success("⬆️ Foco Preventivo")

with col4:
    st.metric(label="NÍVEL DE RESILIÊNCIA", value="Alta")
    st.success("⬆️ Seguro")

st.write("---")
st.write("Consulte vulnerabilidades, analise riscos de arquitetura e otimize suas defesas corporativas.")
# Garante que as mensagens não sumam quando a página recarregar
if "messages" not in st.session_state:
    st.session_state.messages = []

# Desenha na tela todas as mensagens salvas na memória
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # CAIXA DE ENTRADA DO CHAT (BOTÃO INFERIOR)
# ---------------------------------------------------------
if prompt := st.chat_input("Digite sua dúvida estratégica ou técnica sobre segurança..."):
    
    # 1. Mostra imediatamente a pergunta do usuário na tela
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 2. Salva a pergunta do usuário no histórico
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. Bloco de resposta do assistente (IA)
    with st.chat_message("assistant"):
         message_placeholder = st.empty()
        
        try:
            # Envia o prompt estruturado com contexto de segurança para o Gemini
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Você é o especialista HY RI-AI focado em mapeamento estratégico e blindagem de ativos de segurança. Responda a seguinte dúvida técnica de forma direta: {prompt}"
            )
            
            resposta_ia = response.text
             # Exibe o texto retornado no balão do assistente
            message_placeholder.markdown(resposta_ia)
            
            # 4. Salva a resposta do assistente no histórico
            st.session_state.messages.append({"role": "assistant", "content": resposta_ia})
            
        except Exception as e:
            st.error(f"Erro ao processar resposta com a API Gemini: {e}")
            
# Estilização CSS Premium para transformar a plataforma em uma interface executiva (Dark Theme Unificado)
st.markdown("""
    <style>
        /* 1. UNIFICAÇÃO DO FUNDO DO APLICATIVO (DARK MODE CORPORATIVO) */
        .stApp {
            background-color: #0d1117 !important;
        }
        
        /* 2. CAIXAS DE MENSAGEM DO CHAT (ESTILO DASHBOARD PREMIUM) */
        .stChatMessage {
            background-color: #161b22 !important; /* Cinza escuro integrado ao fundo */
            border: 1px solid #21262d !important;  /* Borda sutil */
            border-radius: 8px;
            padding: 18px;
            margin-bottom: 12px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        /* Força as letras do chat (usuário e IA) a ficarem brancas e limpas sobre o fundo escuro */
        [data-testid="stChatMessageUser"] p,
        [data-testid="stChatMessageUser"] div,
        [data-testid="stChatMessageUser"] span,
        [data-testid="stChatMessageAssistant"] p,
        [data-testid="stChatMessageAssistant"] div,
        [data-testid="stChatMessageAssistant"] span {
            color: #c9d1d9 !important; /* Branco acinzentado confortável para leitura */
            font-size: 15px !important;
            line-height: 1.6 !important;
        }
        
        /* 3. PAINEL LATERAL (SIDEBAR) CONTÍNUO */
        [data-testid="stSidebar"] {
            background-color: #070a0e !important; /* Levemente mais escuro que o fundo principal */
            border-right: 1px solid #21262d !important;
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
                
        /* 4. CENTRALIZAÇÃO E COR DOS TÍTULOS */
        h1, h2, h3, .stSubheader, [data-testid="stHeader"] {
            text-align: center !important;
            justify-content: center !important;
        }
        
        h1, h2, h3 {
            color: #58a6ff !important; /* Azul ciano corporativo suave, menos agressivo aos olhos */
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            font-weight: 600 !important;
        }
        
        .stCaption {
            text-align: center !important;
            color: #8b949e !important;
            font-size: 14px !important;
        }
        
        /* 5. DESIGN DOS CARDS DE MÉTRICAS (KPIs) */
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

        /* 6. BARRA DE MENSAGENS MINIMALISTA FLUTUANTE */
        [data-testid="stChatInput"] {
            background-color: transparent !important;
            box-shadow: none !important;
            padding: 5px 0px !important;
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
         /* Ajuste do uploader para ficar mais discreto e compacto */
        .stFileUploader section {
            padding: 0.5rem 1rem !important;
            background-color: #161b22 !important;
            border: 1px dashed #30363d !important;
            border-radius: 6px !important;
        }
        .stFileUploader label {
            display: none !important; /* Esconde o título gigante do uploader */
        }
    </style>
""", unsafe_allow_html=True)


# Prompt Base do Sistema - Foco em Risk Intelligence e Governança
BASE_PROMPT = """
Você é o "HY RI-AI", um assistente de inteligência artificial especialista em Segurança da Informação atuando com foco em Risk Intelligence e Governança Estratégica. Sua missão é apoiar profissionais, gestores e analistas na tomada de decisões seguras, eficientes e alinhadas ao negócio.

REGRAS DE OPERAÇÃO:
1. **Abordagem Estratégica**: Responda sempre priorizando a mitigação de riscos, governança, conformidade, arquitetura segura e melhores práticas de cibersegurança.
2. **Estrutura da Resposta**: Você OBRIGATORIAMENTE deve usar estes quatro títulos exatos, com os respectivos emojis, para estruturar sua resposta:
   * **🚨 Visão Estratégica / Análise de Risco**: Comece contextualizando o impacto do problema para o negócio ou arquitetura geral.
   * **🛠️ Planos de Ação / Mitigação**: Forneça diretrizes práticas, comandos técnicos, códigos defensivos ou políticas de segurança recomendadas. Conclua e feche todas as listas que abrir, nunca deixe tópicos numerados vazios ou incompletos no final da resposta.
   * **🔍 Justificativa Técnico-Estratégica**: Descreva detalhadamente a lógica por trás da solução sugerida, abordando riscos como roubo de sessão (Session Hijacking), vazamentos, malwares ou engenharia social, explicando o porquê de a solução mitigar o risco com eficácia.
   * **📚 Referências**: Inclua uma lista de frameworks, normas ou guias de governança internacional relevantes para o caso (como diretrizes do NIST, ISO/IEC 27001, COBIT, OWASP ou MITRE ATT&CK).
3. **Ética**: Nunca forneça metodologias ofensivas para invasão ou destruição de ativos de forma ilegal. O foco deve ser estritamente defensivo, preventivo e corporativo.
"""

# Inicializa as variáveis no session_state do Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = []

# Função para gerar um relatório em PDF/Texto formatado
def gerar_relatorio_estrategico(historico):
    pdf_buffer = io.BytesIO()
    conteudo = "==================================================\n"
    conteudo += "       HY RISK INTELLIGENCE - REPORT (RI-AI)       \n"
    conteudo += "    Mapeamento estratégico e blindagem de ativos  \n"
    conteudo += "==================================================\n\n"
    
    for idx, msg in enumerate(historico, 1):
        autor = "USUÁRIO" if msg["role"] == "user" else "HY RI-AI"
        conteudo += f"[{idx}] {autor}:\n"
        conteudo += f"{msg['content']}\n"
        conteudo += "-" * 50 + "\n\n"
        
    conteudo += "==================================================\n"
    conteudo += "Fim do relatório. HY Risk Intelligence - Proteção e Negócio.\n"
    
    pdf_buffer.write(conteudo.encode('utf-8'))
    pdf_buffer.seek(0)
    return pdf_buffer

# CARREGAMENTO SILENCIOSO DA CHAVE (SECRETS)
gemini_api_key = st.secrets.get("GEMINI_API_KEY", "")
  
    # Filtro expandido com categorias de segurança e governança corporativa
    st.markdown("### 🔍 Escopo de Análise")
    categoria = st.selectbox(
        "Selecione o foco do problema:",
        [
            "Geral / Sem Filtro", 
            "Análise de Logs e Incidentes",
            "Governança Corporativa e Riscos (GRC)",
            "Gestão de Incidentes e Continuidade (BCP/DRP)",
            "Segurança em Aplicações Web (OWASP)", 
            "Criptografia e Proteção de Dados", 
            "Segurança de Redes e Firewalls", 
            "Conformidade e Privacidade (LGPD/GDPR)",
            "Pentest e Defesa Ativa (Blue/Red Team)"
        ]
    )
    
    st.markdown("---")

   
    # Renderizador do Botão de Exportar PDF
    if st.session_state.messages:
        st.markdown("### 📄 Exportar Dados")
        dados_pdf = gerar_relatorio_estrategico(st.session_state.messages)
        st.download_button(
            label="📥 Baixar Relatório Estratégico (.pdf)",
            data=dados_pdf,
            file_name="relatorio_hy_risk_intelligence.pdf",
            mime="application/pdf",
            key="download_pdf_btn"
        )
        st.markdown("---")
    
    # Botão para limpar histórico do chat
    if st.button("🗑️ Limpar Histórico do Terminal", type="secondary"):
        st.session_state.messages = []
        st.rerun()

# Título principal da interface
st.markdown("<h1>🛡️ HY RI-AI <span style='font-size: 18px; color: #8b949e;'>v4.0</span></h1>", unsafe_allow_html=True)
st.subheader("Mapeamento estratégico e blindagem de ativos 💻")

# O Python não entende o emoji solto no código

st.title("📊 PAINEL DE INDICADORES EXECUTIVOS (KPIs)")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Análises Efetuadas", value=len([m for m in st.session_state.messages if m["role"] == "user"]), delta="SOC Ativo")
with col2:
    st.metric(label="Controles de GRC", value="NIST / ISO", delta="Mapeados")
with col3:
    st.metric(label="Status de Conformidade", value="98.4%", delta="+1.2% este mês")
with col4:
    st.metric(label="Nível de Resiliência", value="Alta", delta="Foco Preventivo")

st.markdown("---")
# Exibe aviso de contexto ativo
if arquivo_log:
    st.success(f"📎 Arquivo **{arquivo_log.name}** carregado com sucesso como contexto.")
elif categoria != "Geral / Sem Filtro":
    st.caption(f"Filtro ativo: **{categoria}**")
else:
    st.caption("Consulte vulnerabilidades, analise riscos de arquitetura e otimize suas defesas corporativas.")

# Exibe mensagens anteriores cadastradas no histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

client = None
# Fluxo principal do chat
if prompt := st.chat_input("Digite sua dúvida estratégica ou técnica sobre segurança..."):
    # Anexa logs se houver
    if arquivo_log:
        conteudo_log = arquivo_log.read().decode("utf-8")
        prompt_completo = f"CONTEXTO DO LOG ENVIADO:\n```\n{conteudo_log}\n```\n\nPERGUNTA DO USUÁRIO:\n{prompt}"
    else:
        prompt_completo = prompt

    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

 # Histórico estruturado
    history_contents = []
    for msg in st.session_state.messages[:-1]:
        role_mapping = "model" if msg["role"] == "assistant" else "user"
        history_contents.append(
            types.Content(
                role=role_mapping,
                parts=[types.Part.from_text(text=msg["content"])]
            )
        )
    history_contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt_completo)]
        )
    )
# Rodapé da página
st.markdown(
    """
    <div style="text-align: center; color: #8b949e; font-size: 12px;">
        <hr style="border-color: #21262d;">
        <p>🔒 HY Risk Intelligence (HY RI-AI) — Mapeamento estratégico e blindagem de ativos. Todos os direitos reservados.</p>
    </div>
    """,
    unsafe_allow_html=True
)
