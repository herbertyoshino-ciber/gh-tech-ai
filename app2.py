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

# Estilização CSS para caixas de mensagem com interior totalmente branco
st.markdown("""
    <style>
        /* 1. CONFIGURAÇÃO GERAL DAS CAIXAS DE MENSAGEM (USUÁRIO E IA) */
        .stChatMessage {
            background-color: #ffffff !important; /* Interior todo branco */
            border: 1px solid #d3d3d3 !important;  /* Borda cinza clara para dar acabamento */
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
        }
        
        /* COR DAS LETRAS DENTRO DO CHAT (USUÁRIO) */
        [data-testid="stChatMessageUser"] p,
        [data-testid="stChatMessageUser"] div,
        [data-testid="stChatMessageUser"] span {
            color: #161b22 !important; /* Letras escuras para contraste no fundo branco */
            font-size: 16px !important;
        }
        
        /* COR DAS LETRAS DENTRO DO CHAT (IA / ASSISTENTE) */
        [data-testid="stChatMessageAssistant"] p,
        [data-testid="stChatMessageAssistant"] div,
        [data-testid="stChatMessageAssistant"] span {
            color: #161b22 !important; /* Letras também escuras para o fundo branco */
            font-size: 16px !important;
        }
        
        /* 2. PAINEL LATERAL (SIDEBAR) - MANTIDO ESCURO PARA IDENTIDADE VISUAL */
        [data-testid="stSidebar"] {
            background-color: #0d1117 !important;
            border-right: 2px solid #00d2ff;
        }
        
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] span, 
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #ffffff !important;
        }
        
        [data-testid="stSidebar"] .stMarkdown p {
            color: #f8f9fa !important;
            font-size: 14px !important;
        }
        
        /* 3. TÍTULOS DO SISTEMA */
        h1, h2, h3 {
            color: #00d2ff !important;
            font-family: 'Courier New', Courier, monospace;
        }
        
        .stButton>button {
            width: 100%;
        }

        /* 4. CAIXA DE PERGUNTA (INPUT) TAMBÉM INTEGRADA EM BRANCO */
        [data-testid="stChatInput"] textarea {
            color: #161b22 !important;
            background-color: #ffffff !important;
            border: 1px solid #d3d3d3 !important;
            box-shadow: none !important;
        }
        
        [data-testid="stChatInput"] textarea::placeholder {
            color: #6e7681 !important;
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

