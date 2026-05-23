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

# Estilização CSS para garantir contraste e letras super nítidas
st.markdown("""
    <style>
        /* 1. CAIXAS DE MENSAGEM DO CHAT */
        .stChatMessage {
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
        }
        
        /* 2. PAINEL LATERAL (SIDEBAR) */
        [data-testid="stSidebar"] {
            background-color: #0d1117 !important; /* Fundo grafite escuro */
            border-right: 2px solid #00d2ff;       /* Linha vertical azul ciano */
        }
        
        /* FORÇA TODAS AS LETRAS DA SIDEBAR A FICAREM BRANCAS E VISÍVEIS */
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] span, 
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #ffffff !important;
        }
        
        /* Ajuste fino de alto contraste para textos menores ou explicativos na barra lateral */
        [data-testid="stSidebar"] .stMarkdown p {
            color: #f8f9fa !important; /* Branco fosco de alta leitura */
            font-size: 14px !important;
        }
        
        /* 3. CORPO PRINCIPAL (TEXTOS DO CHAT) */
        /* Garante que o texto digitado por você e as respostas da IA tenham excelente leitura */
        .stMarkdown p, .stChatMessage p {
            color: #ffffff !important; /* Altere para #000000 se o seu Streamlit estiver em modo claro por padrão */
            font-size: 16px !important;
        }
        
        /* 4. TÍTULOS DO SISTEMA */
        h1, h2, h3 {
            color: #00d2ff !important; /* Títulos em Azul Ciano brilhante */
            font-family: 'Courier New', Courier, monospace;
        }
        
        /* Botões laterais ocupando toda a largura útil */
        .stButton>button {
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)


# Prompt Base do Sistema - Foco em Segurança de Forma Estratégica
BASE_PROMPT = """
Você é o "GH Tech AI", um assistente de inteligência artificial especialista em Segurança da Informação atuando de forma estratégica. Sua missão é apoiar profissionais, gestores e analistas na tomada de decisões seguras, eficientes e alinhadas ao negócio.

REGRAS DE OPERAÇÃO:
1. **Abordagem Estratégica**: Responda sempre priorizando a mitigação de riscos, governança, conformidade, arquitetura segura e melhores práticas de cibersegurança.
2. **Estrutura da Resposta**: Sempre formate suas respostas da seguinte maneira:
   * **🚨 Visão Estratégica / Análise de Risco**: Comece contextualizando o impacto do problema para o negócio ou arquitetura geral.
   * **🛠️ Planos de Ação / Mitigação**: Forneça diretrizes práticas, comandos técnicos, códigos defensivos ou políticas de segurança recomendadas.
   * **🔍 Justificativa Técnico-Estratégica**: Descreva a lógica por trás da solução sugerida e o porquê dela mitigar o risco com eficácia para o negócio.
   * **📚 Frameworks de Referência**: Ao final, inclua uma seção chamada "📚 Referências Recomendadas" citando padrões de mercado reconhecidos (como diretrizes do NIST, ISO 27001, COBIT, regras da OWASP, mapeamentos do MITRE ATT&CK ou leis como LGPD/GDPR).
3. **Ética**: Nunca forneça metodologias ofensivas para invasão ou destruição de ativos de forma ilegal. O foco deve ser estritamente defensivo, preventivo e corporativo.
"""

# Inicializa as variáveis no session_state do Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = []

# Função para gerar um relatório em PDF/Texto formatado
def gerar_relatorio_estrategico(historico):
    pdf_buffer = io.BytesIO()
    conteudo = "==================================================\n"
    conteudo += "        GH TECH AI - RELATÓRIO ESTRATÉGICO        \n"
    conteudo += "         Segurança de forma estratégica          \n"
    conteudo += "==================================================\n\n"
    
    for idx, msg in enumerate(historico, 1):
        autor = "USUÁRIO" if msg["role"] == "user" else "GH TECH AI"
        conteudo += f"[{idx}] {autor}:\n"
        conteudo += f"{msg['content']}\n"
        conteudo += "-" * 50 + "\n\n"
        
    conteudo += "==================================================\n"
    conteudo += "Fim do relatório. GH Tech AI - Proteção e Negócio.\n"
    
    pdf_buffer.write(conteudo.encode('utf-8'))
    pdf_buffer.seek(0)
    return pdf_buffer

# Painel Lateral (Sidebar)
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #00d2ff !important;'>🛡️ HY RI-AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Mapeamento estratégico e blindagem de ativos</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Campo para chave de API
    gemini_api_key = st.text_input(
        "Chave de Acesso (API Key Gemini)",
        type="password",
        help="Gere sua chave gratuitamente no painel: https://google.com"
    )
    
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
    
    # GERADOR DE RELATÓRIO PDF (Só exibe se houver mensagens no chat)
    if st.session_state.messages:
        st.markdown("### 📄 Exportar Dados")
        dados_pdf = gerar_relatorio_estrategico(st.session_state.messages)
        st.download_button(
            label="📥 Baixar Relatório Estratégico (.pdf)",
            data=dados_pdf,
            file_name="relatorio_gh_tech_ai.pdf",
            mime="application/pdf"
        )
        st.markdown("---")
    
    # Botão para limpar histórico do chat
    if st.button("🗑️ Limpar Histórico do Terminal", type="secondary"):
        st.session_state.messages = []
        st.rerun()

# Título principal da interface
st.markdown("<h1>🛡️ HY RI-AI <span style='font-size: 18px; color: #8b949e;'>v3.5</span></h1>", unsafe_allow_html=True)
st.subheader("Mapeamento estratégico e blindagem de ativos 💻")

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

# Inicialização do cliente Google GenAI
if gemini_api_key:
    try:
        client = genai.Client(api_key=gemini_api_key)
    except Exception as e:
        st.sidebar.error(f"Falha de autenticação: {e}")
        st.stop()
elif st.session_state.messages:
    st.warning("⚠️ Autenticação necessária. Insira sua API Key do Gemini no painel lateral para interagir.")

# Fluxo principal do chat
if prompt := st.chat_input("Digite sua dúvida estratégica ou técnica sobre segurança..."):
    if not client:
        st.warning("⚠️ Operação bloqueada. Insira sua API Key na barra lateral para liberar o terminal.")
        st.stop()
        
    # Se houver um arquivo de log, lê e anexa o conteúdo à pergunta do usuário
    if arquivo_log:
        conteudo_log = arquivo_log.read().decode("utf-8")
        prompt_completo = f"CONTEXTO DO LOG ENVIADO:\n```\n{conteudo_log}\n```\n\nPERGUNTA DO USUÁRIO:\n{prompt}"
    else:
        prompt_completo = prompt

    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Monta o histórico estruturado exigido pela biblioteca google-genai
    history_contents = []
    for msg in st.session_state.messages[:-1]: # Adiciona o histórico antigo normal
        role_mapping = "model" if msg["role"] == "assistant" else "user"
        history_contents.append(
            types.Content(
                role=role_mapping,
                parts=[types.Part.from_text(text=msg["content"])]
            )
        )
    # Adiciona a última mensagem contendo o log expandido se houver
    history_contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt_completo)]
        )
    )
        
    with st.chat_message("assistant"):
        with st.spinner("🕵️‍♂️ Avaliando riscos e gerando resposta estratégica..."):
            try:
                # Modifica o prompt do sistema dinamicamente baseado na categoria escolhida
                contexto_categoria = f"\nO usuário selecionou a categoria específica: [{categoria}]. Conecte sua análise técnica estrategicamente a este escopo corporativo."
                prompt_final = BASE_PROMPT + contexto_categoria
                
                config = types.GenerateContentConfig(
                    system_instruction=prompt_final,
                    temperature=0.4,
                    max_output_tokens=2048
                )
                
                # Dispara a requisição para o modelo oficial do Gemini
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=history_contents,
                    config=config
                )
                
                ai_resposta = response.text
                st.markdown(ai_resposta)
                
                st.session_state.messages.append({"role": "assistant", "content": ai_resposta})
                st.rerun()
                
            except Exception as e:
                st.error(f"Erro na comunicação com o core da IA: {e}")

# Rodapé
st.markdown(
    """
    <div style="text-align: center; color: #8b949e; font-size: 12px;">
        <hr style="border-color: #21262d;">
        <p>🔒 HY Risk Intelligence (HY RI-AI) — Mapeamento estratégico e blindagem de ativos. Todos os direitos reservados.</p>
    </div>
    """,
    unsafe_allow_html=True
)

