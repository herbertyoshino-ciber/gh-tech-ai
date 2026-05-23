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

    # Estilização CSS para garantir contraste perfeito no chat, na barra lateral e na caixa de entrada
st.markdown("""
    <style>
        /* 1. CAIXAS DE MENSAGEM DO CHAT */
        .stChatMessage {
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
        }
        
        /* CORREÇÃO DO CONTEXTO ENVIADO (MENSAGEM DO USUÁRIO) */
        /* Força as letras dentro da caixinha clara do usuário a ficarem escuras para dar leitura */
        [data-testid="stChatMessageUser"] p,
        [data-testid="stChatMessageUser"] div,
        [data-testid="stChatMessageUser"] span {
            color: #161b22 !important; 
            font-size: 16px !important;
        }
        
        /* MENSAGEM DA IA (ASSISTENTE) */
        /* Garante que o texto da IA fique legível no fundo padrão */
        [data-testid="stChatMessageAssistant"] p,
        [data-testid="stChatMessageAssistant"] div,
        [data-testid="stChatMessageAssistant"] span {
            color: #161b22 !important;
            font-size: 16px !important;
        }
        
        /* 2. PAINEL LATERAL (SIDEBAR) - MANTIDO ESCURO E NITIDO */
        [data-testid="stSidebar"] {
            background-color: #0d1117 !important; /* Fundo grafite escuro */
            border-right: 2px solid #00d2ff;       /* Linha vertical azul ciano */
        }
        
        /* Força todas as letras da Sidebar a ficarem brancas e visíveis */
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] span, 
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #ffffff !important;
        }
        
        /* Ajuste fino de alto contraste para textos menores na barra lateral */
        [data-testid="stSidebar"] .stMarkdown p {
            color: #f8f9fa !important;
            font-size: 14px !important;
        }
        
        /* 3. TÍTULOS DO SISTEMA */
        h1, h2, h3 {
            color: #00d2ff !important; /* Títulos em Azul Ciano brilhante */
            font-family: 'Courier New', Courier, monospace;
        }
        
        /* Botões laterais ocupando toda a largura útil */
        .stButton>button {
            width: 100%;
        }

        /* 4. REMOÇÃO DA TARJA PRETA NA CAIXA DE PERGUNTA */
        /* Remove a cor de fundo preta, restaura o padrão claro e coloca o texto escuro */
        [data-testid="stChatInput"] textarea {
            color: #161b22 !important;
            background-color: #ffffff !important;
            border: 1px solid #d3d3d3 !important;
            box-shadow: none !important;
        }
        
        /* Ajusta o texto temporário (Placeholder) para um tom cinza legível no fundo branco */
        [data-testid="stChatInput"] textarea::placeholder {
            color: #6e7681 !important;
        }
    </style>
""", unsafe_allow_html=True)






# Prompt Base do Sistema - Foco em Segurança de Forma Estratégica
BASE_PROMPT = """
Você é o "HY RI-AI", um assistente de inteligência artificial especialista em Segurança da Informação atuando com foco em Risk Intelligence e Governança Estratégica. Sua missão é apoiar profissionais, gestores e analistas na tomada de decisões seguras, eficientes e alinhadas ao negócio.

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

    # ... (código anterior da barra lateral)
    st.markdown("---")
    
    # 🚨 ISSO FOI ADICIONADO/ALTERADO:
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

# Fluxo principal do chat
if prompt := st.chat_input("Digite sua dúvida estratégica ou técnica sobre segurança..."):
    if not client:
        st.warning("⚠️ Operação bloqueada. Insira sua API Key na barra lateral para liberar o terminal.")
        st.stop()
        
    # Anexa logs se houver
    if arquivo_log:
        conteudo_log = arquivo_log.read().decode("utf-8")
        prompt_completo = f"CONTEXTO DO LOG ENVIADO:\n```\n{conteudo_log}\n```\n\nPERGUNTA DO USUÁRIO:\n{prompt}"
    else:
        prompt_completo = prompt

    # Salva a pergunta do usuário no histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Exibe imediatamente a mensagem na tela
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Monta o histórico estruturado para a nova API do Gemini
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
        
    # Gera a resposta do assistente
    with st.chat_message("assistant"):
        with st.spinner("🕵️‍♂️ Analisando vetores de risco e gerando resposta corporativa..."):
            try:
                contexto_categoria = f"\nO usuário selecionou a categoria específica: [{categoria}]. Conecte sua análise técnica estrategicamente a este escopo de inteligência de riscos corporativos."
                prompt_final = BASE_PROMPT + contexto_categoria
                
                config = types.GenerateContentConfig(
                    system_instruction=prompt_final,
                    temperature=0.4,
                    max_output_tokens=2048
                )
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=history_contents,
                    config=config
                )
                
                ai_resposta = response.text
                st.markdown(ai_resposta)
                
                # Salva a resposta da IA no histórico
                st.session_state.messages.append({"role": "assistant", "content": ai_resposta})
                
                # CORREÇÃO: Força a atualização correta da página para renderizar o botão de PDF imediatamente
                st.fragment(st.rerun())
                
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


