import os
import io
import streamlit as st
from google import genai
from google.genai import types

# Configuração da página com foco em Governança e Segurança Estratégica
st.set_page_config(
    page_title="HY Risk Intelligence | RI-AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded" 

)
# Estilização CSS para centralização de títulos, contraste e barra de mensagem minimalista

 # Estilização CSS Premium Unificada com Forçador de Modo Escuro Absoluto
st.markdown("""
    <style>
        /* FORÇADOR DE MODO ESCURO ABSOLUTO - PINTA A TELA TODA DE PRETO */
        .stApp, html, body, [data-testid="stAppViewContainer"] {
            background-color: #0d1117 !important;
            color: #c9d1d9 !important;
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

        /* Correção para o seletor da categoria na sidebar */
        [data-testid="stSidebar"] div[data-baseweb="select"] div {
            color: #ffffff !important;
            background-color: #161b22 !important;
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
    </style>
""", unsafe_allow_html=True)








# Prompt Base do Sistema - Foco em Segurança de Forma Estratégica
BASE_PROMPT = """
Você é o "HY RISK INTELLIGENCE-AI", um assistente de inteligência artificial especialista em Segurança da Informação atuando com foco em Risk Intelligence e Governança Estratégica. Sua missão é apoiar profissionais, gestores e analistas na tomada de decisões seguras, eficientes e alinhadas ao negócio.

REGRAS DE OPERAÇÃO:
1. **Abordagem Estratégica**: Responda sempre priorizando a mitigação de riscos, governança, conformidade, arquitetura segura e melhores práticas de cibersegurança.
2. **Estrutura da Resposta**: Você OBRIGATORIAMENTE deve usar estes quatro títulos exatos, com os respectivos emojis, para estruturar sua resposta:
   * **🚨 Visão Estratégica / Análise de Risco**: Comece contextualizando o impacto do problema para o negócio ou arquitetura geral.
   * **🛠️ Planos de Ação / Mitigação**: Forneça diretrizes práticas, comandos técnicos, códigos defensivos ou políticas de segurança recomendadas.
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
    conteudo += "       HY RISK INTELIGENCE - REPORT (RI-AI)     \n"
    conteudo += "   Mapeamento estratégico e blindagem de ativos          \n"
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

# Painel Lateral (Sidebar)
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #00d2ff !important;'>🛡️ HY RI-AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Mapeamento estratégico e blindagem de ativos</p>", unsafe_allow_html=True)
    st.markdown("---")
    
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

    # NOVO: UPLOAD DE ARQUIVOS DE LOG
    st.markdown("### 📁 Analisador de Logs")
    arquivo_log = st.file_uploader(
        "Envie um arquivo de log (.txt ou .log):", 
        type=["txt", "log"],
        help="O conteúdo será adicionado como contexto para a IA."
    )
    
    st.markdown("---")
    
    if st.session_state.messages:
        st.markdown("### 📄 Exportar Dados")
        dados_pdf = gerar_relatorio_estrategico(st.session_state.messages)
        st.download_button(
            label="📥 Baixar Relatório Estratégico (.pdf)",
            data=dados_pdf,
            file_name="relatorio_hy_risk_intelligence.pdf",
            mime="application/pdf",
            key="download_pdf_btn"  # <-- Esta chave garante a estabilidade do botão
        )
        st.markdown("---")
    
    # Botão para limpar histórico do chat
    if st.button("🗑️ Limpar Histórico do Terminal", type="secondary"):
        st.session_state.messages = []
        st.rerun()


# Título principal da interface
st.markdown("<h1>🛡️ HY RI-AI <span style='font-size: 18px; color: #8b949e;'>v3.5</span></h1>", unsafe_allow_html=True)
st.subheader("Mapeamento estratégico e blindagem de ativos 💻")

# 📊 PAINEL DE INDICADORES EXECUTIVOS (KPIs)
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

# Inicialização do cliente Google GenAI utilizando a chave secreta de fundo
if gemini_api_key:
    try:
        client = genai.Client(api_key=gemini_api_key)
    except Exception as e:
        st.error(f"Falha técnica na inicialização da chave secreta: {e}")
        st.stop()
else:
    st.warning("⚠️ Chave ausente nos Secrets do Streamlit Cloud. Verifique as configurações do painel da nuvem.")
    st.stop()

# Fluxo principal do chat

   
              
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
        
    # Anexa logs se houver
    if arquivo_log:
        conteudo_log = arquivo_log.read().decode("utf-8")
        prompt_completo = f"CONTEXTO DO LOG ENVIADO:\n```\n{conteudo_log}\n```\n\nPERGUNTA DO USUÁRIO:\n{prompt}"
    else:
        prompt_completo = prompt

    # 1. Adiciona a pergunta do usuário e exibe na tela
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # 2. Monta o histórico estruturado para a API do Gemini
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
        
    # 3. Gera e exibe a resposta do assistente (IA)
    with st.chat_message("assistant"):
        with st.spinner("🕵️‍♂️ Analisando vetores de risco e gerando resposta corporativa..."):
            try:
                contexto_categoria = f"\nO usuário selecionou a categoria específica: [{categoria}]. Conecte sua análise técnica estrategicamente a este escopo de inteligência de riscos corporativos."
                prompt_final = BASE_PROMPT + contexto_categoria
                
                config = types.GenerateContentConfig(
                    system_instruction=prompt_final,
                    temperature=0.3,
                    max_output_tokens=4096 
                )
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=history_contents,
                    config=config
                )
                
                ai_resposta = response.text
                st.markdown(ai_resposta)
                
                # 4. Salva a resposta da IA no histórico
                st.session_state.messages.append({"role": "assistant", "content": ai_resposta})
                
                # 🚨 CORREÇÃO CRUCIAL: Removido o st.rerun() daqui para impedir que o Streamlit
                # corte a renderização do texto pela metade.
                
            except Exception as e:
                st.error(f"Erro na comunicação com o core da IA: {e}")

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

