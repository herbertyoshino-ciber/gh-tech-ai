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
    page_title="HY Risk Intelligence | -AI",
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

# Inicializa a variável do arquivo no session state para evitar NameError
if "arquivo_log_dados" not in st.session_state:
    st.session_state.arquivo_log_dados = None

# Painel Lateral (Sidebar)
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #58a6ff !important;'>🛡️ HY RI-AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Mapeamento estratégico e blindagem de ativos</p>", unsafe_allow_html=True)
    st.markdown("---")
    
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
    
    if st.button("🗑️ Limpar Histórico do Terminal", type="secondary"):
        st.session_state.messages = []
        st.session_state.arquivo_log_dados = None
        st.rerun()

# --- FIM DO BLOCO DA SIDEBAR ---

# Título principal da interface
st.markdown("<h1>🛡️ HY RI-AI <span style='font-size: 18px; color: #8b949e;'>v5.0</span></h1>", unsafe_allow_html=True)
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

# 📊 DASHBOARD GRÁFICO DE VETORES DE RISCO (PLOTLY) E GUIA DE CONSULTA
col_chart, col_faq = st.columns([2, 1])

with col_chart:
    # Dados de modelagem para o gráfico de radar corporativo
    dados_radar = pd.DataFrame(dict(
        r=[4, 5, 3, 4, 5],
        theta=['Conformidade', 'Segurança de Dados', 'Gestão de Crise', 'Arquitetura de Redes', 'Resposta a Incidentes']
    ))
    
    fig = px.line_polar(
        dados_radar, 
        r='r', 
        theta='theta', 
        line_close=True, 
        range_r=[0, 5], 
        title="🛡️ Índice de Maturidade de Risco Operacional"
    )
    fig.update_traces(fill='toself', line_color='#58a6ff')
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20),
        height=320
    )
    st.plotly_chart(fig, use_container_width=True)

with col_faq:
    # Título da seção de consulta rápida
    st.markdown("<p style='font-weight:bold; color:#58a6ff; margin-bottom:5px;'>🔍 Guia Rápido de Governança</p>", unsafe_allow_html=True)
    
    # 🚨 LINHAS CORRIGIDAS: Mudado de st.accordion para st.expander (O componente correto do Streamlit)
    with st.expander("🚨 Prazo Notificação ANPD"):
        st.write("Sob a ótica da LGPD, incidentes graves que envolvam dados pessoais devem ser comunicados à ANPD e aos titulares em prazo razoável (geralmente interpretado pelo mercado como até 2 dias úteis).")
        
    with st.expander("🛠️ O que compõe RTO e RPO?"):
        st.write("RTO (Recovery Time Objective) é o tempo máximo tolerável para restabelecer um sistema após uma falha. RPO (Recovery Point Objective) define a quantidade máxima de dados tolerada para perda.")

st.markdown("---")

# CONTAINER DE HISTÓRICO DO CHAT
chat_container = st.container()

with chat_container:
    for index, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                st.feedback("thumbs", key=f"fb_{index}")

client = None

# Inicialização do cliente Google GenAI
if gemini_api_key:
    try:
        client = genai.Client(api_key=gemini_api_key)
    except Exception as e:
        st.error(f"Falha técnica na inicialização da chave secreta: {e}")
        st.stop()
else:
    st.warning("⚠️ Chave ausente nos Secrets do Streamlit Cloud.")
    st.stop()

# --- ÁREA DE INPUT DISCRETA NO FINAL ---
st.markdown("<br><br>", unsafe_allow_html=True)

arquivo_log = st.file_uploader(
    "Discreto", 
    type=["txt", "log"],
    label_visibility="collapsed"
)

if arquivo_log:
    st.session_state.arquivo_log_dados = arquivo_log
    st.markdown(f"<p style='color:#58a6ff; font-size:12px; margin-top:-10px; margin-bottom:10px;'>📎 Arquivo carregado: <b>{arquivo_log.name}</b></p>", unsafe_allow_html=True)

# Fluxo principal do chat
if prompt := st.chat_input("Digite sua dúvida estratégica ou técnica sobre segurança..."):
    if st.session_state.arquivo_log_dados:
        conteudo_puro = st.session_state.arquivo_log_dados.read().decode("utf-8")
        conteudo_higienizado = higienizar_contexto(conteudo_puro)
        prompt_completo = f"CONTEXTO DO LOG ENVIADO (HIGIENIZADO):\n```\n{conteudo_higienizado}\n```\n\nPERGUNTA DO USUÁRIO:\n{prompt}"
    else:
        prompt_completo = prompt

    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)
        
    # 🚨 ESSAS LINHAS ABAIXO PRECISAM ESTAR AQUI PARA DEFINIR O HISTÓRICO:
    history_contents = []
    for msg in st.session_state.messages[:-1]:
        role_mapping = "model" if msg["role"] == "assistant" else "user"
        history_contents.append(
            types.Content(role=role_mapping, parts=[types.Part.from_text(text=msg["content"])]))
    history_contents.append(
        types.Content(role="user", parts=[types.Part.from_text(text=prompt_completo)]))
        
    # Bloco de geração de resposta com o Fallback ativo
    with chat_container:
        with st.chat_message("assistant"):
            with st.spinner("🕵️‍♂️ Analisando vetores de risco e gerando resposta corporativa..."):
                try:
                    contexto_categoria = f"\nO usuário selecionou a categoria específica: [{categoria}]. Conecte sua análise técnica estrategicamente a este escopo de inteligência de riscos corporativos."
                    prompt_final = BASE_PROMPT + contexto_categoria
                    
                    # Tentativa 1: Modelo Principal (2.0)
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

                except Exception as e_principal:
                    # Se o modelo 2.5 estourar a cota (Erro 429), tenta o modelo 2.0 automaticamente
                    if "429" in str(e_principal) or "RESOURCE_EXHAUSTED" in str(e_principal):
                        try:
                            config = types.GenerateContentConfig(
                                system_instruction=prompt_final,
                                temperature=0.3,
                                max_output_tokens=4096 
                            )
                            response = client.models.generate_content(
                                model='gemini-2.0-flash',
                                contents=history_contents,
                                config=config
                            )
                            ai_resposta = response.text
                        except Exception as e_fallback:
                            st.warning("""
                                ⏳ **Fila de Espera GRC Ativa**
                                
                                O volume de requisições simultâneas excedeu a cota diária global do servidor do Google. 
                                Por favor, **Tente Novamente mais tarde!! ** e clique em enviar novamente para reprocessar o terminal.
                            """)
                            st.stop()
                    else:
                        st.error(f"Erro técnico no core da IA: {e_principal}")
                        st.stop()

                try:
                    st.markdown(ai_resposta)
                    st.session_state.messages.append({"role": "assistant", "content": ai_resposta})
                    st.toast("Análise de riscos concluída!", icon="🛡️")
                    st.rerun()
                except Exception as e_interface:
                    st.error(f"Erro na renderização da interface: {e_interface}")

# Rodapé
st.markdown(
    """
    <div style="text-align: center; color: #8b949e; font-size: 12px; margin-top: 50px;">
        <hr style="border-color: #21262d;">
        <p>🔒 HY Risk Intelligence (HY RI-AI) — Mapeamento estratégico e blindagem de ativos. Todos os direitos reservados.</p>
    </div>
    """,
    unsafe_allow_html=True
)

       

     
                
