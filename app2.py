import io
import json
import re
from dataclasses import dataclass

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types

try:
    from streamlit_mic_recorder import speech_to_text
except ImportError:
    speech_to_text = None


APP_TITLE = "HY Risk Intelligence | HI-AI"
APP_VERSION = "v6.0"
PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-2.0-flash"
MAX_LOG_CHARS = 30_000


@dataclass(frozen=True)
class RiskMetric:
    label: str
    value: str
    delta: str


RISK_METRICS = [
    RiskMetric("Análises Efetuadas", "dynamic", "SOC Ativo"),
    RiskMetric("Controles de GRC", "NIST / ISO", "Mapeados"),
    RiskMetric("Status de Conformidade", "98.4%", "+1.2% este mês"),
    RiskMetric("Nível de Resiliência", "Alta", "Foco Preventivo"),
]


ANALYSIS_SCOPES = [
    "Geral / Sem Filtro",
    "Análise de Logs e Incidentes",
    "Governança Corporativa e Riscos (GRC)",
    "Gestão de Incidentes e Continuidade (BCP/DRP)",
    "Segurança em Aplicações Web (OWASP)",
    "Criptografia e Proteção de Dados",
    "Segurança de Redes e Firewalls",
    "Conformidade e Privacidade (LGPD/GDPR)",
    "Pentest e Defesa Ativa (Blue/Red Team)",
]


BASE_PROMPT = "\n".join(
    [
        'Você é o "HY RISK INTELLIGENCE-AI", um assistente de inteligência artificial especialista em Segurança da Informação, Risk Intelligence e Governança Estratégica.',
        "Sua missão é apoiar profissionais, gestores e analistas na tomada de decisões seguras, eficientes e alinhadas ao negócio.",
        "",
        "REGRAS DE OPERAÇÃO:",
        "1. Abordagem estratégica: responda priorizando mitigação de riscos, governança, conformidade, arquitetura segura e melhores práticas de cibersegurança.",
        "2. Estrutura obrigatória: use exatamente estes quatro títulos em todas as respostas:",
        "   **🚨 Visão Estratégica / Análise de Risco**",
        "   **🛠️ Planos de Ação / Mitigação**",
        "   **🔍 Justificativa Técnico-Estratégica**",
        "   **📚 Referências**",
        "3. Clareza executiva: seja objetivo, acionável e técnico quando necessário, sem perder a visão de negócio.",
        "4. Ética e segurança: nunca forneça instruções ofensivas, ilegais, destrutivas ou voltadas à exploração não autorizada. Converta pedidos arriscados em orientação defensiva, preventiva e corporativa.",
        "5. Privacidade: trate logs, nomes, e-mails, IPs, documentos e identificadores como dados sensíveis.",
    ]
)


CUSTOM_CSS = "\n".join(
    [
        "<style>",
        ":root{--hy-bg:#0d1117;--hy-panel:#161b22;--hy-sidebar:#070a0e;--hy-border:#30363d;--hy-text:#c9d1d9;--hy-muted:#8b949e;--hy-primary:#58a6ff;--hy-strong:#f0f6fc;}",
        ".stApp,html,body,[data-testid='stAppViewContainer'],[data-testid='stHeader']{background-color:var(--hy-bg)!important;}",
        "[data-testid='stSidebar']{background-color:var(--hy-sidebar)!important;border-right:1px solid var(--hy-border)!important;}",
        "[data-testid='stSidebar'] p,[data-testid='stSidebar'] label,[data-testid='stSidebar'] span,[data-testid='stSidebar'] div,[data-testid='stSidebar'] h1,[data-testid='stSidebar'] h2,[data-testid='stSidebar'] h3{color:var(--hy-strong)!important;}",
        "[data-testid='stSidebar'] .stMarkdown p{color:var(--hy-muted)!important;font-size:13px!important;}",
        "[data-testid='stSidebar'] div[data-baseweb='select'] div{color:#fff!important;}",
        "h1,h2,h3,.stSubheader{color:var(--hy-primary)!important;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;font-weight:650!important;letter-spacing:0!important;text-align:center!important;}",
        ".stCaption{color:var(--hy-muted)!important;font-size:14px!important;text-align:center!important;}",
        ".stChatMessage{background-color:var(--hy-panel)!important;border:1px solid var(--hy-border)!important;border-radius:8px!important;box-shadow:0 4px 12px rgba(0,0,0,.16);margin-bottom:12px!important;padding:18px!important;}",
        "[data-testid='stChatMessageUser'] p,[data-testid='stChatMessageUser'] div,[data-testid='stChatMessageUser'] span,[data-testid='stChatMessageAssistant'] p,[data-testid='stChatMessageAssistant'] div,[data-testid='stChatMessageAssistant'] span{color:var(--hy-text)!important;font-size:15px!important;line-height:1.6!important;}",
        "[data-testid='stMetricValue']{color:var(--hy-primary)!important;font-size:28px!important;font-weight:700!important;text-align:center!important;}",
        "[data-testid='stMetricLabel']{color:var(--hy-muted)!important;font-size:12px!important;letter-spacing:1px!important;text-align:center!important;text-transform:uppercase!important;}",
        "[data-testid='stMetricDelta']{justify-content:center!important;}",
        ".stButton>button,.stDownloadButton>button{width:100%;background-color:#21262d!important;border:1px solid var(--hy-border)!important;border-radius:6px!important;color:var(--hy-text)!important;}",
        ".stButton>button:hover,.stDownloadButton>button:hover{border-color:var(--hy-primary)!important;color:var(--hy-primary)!important;}",
        "[data-testid='stChatInput']{background-color:transparent!important;box-shadow:none!important;padding:15px 0!important;}",
        "[data-testid='stChatInput'] textarea{background-color:var(--hy-panel)!important;border:1px solid var(--hy-border)!important;border-radius:6px!important;color:var(--hy-strong)!important;}",
        "[data-testid='stChatInput'] textarea:focus{border-color:var(--hy-primary)!important;}",
        "[data-testid='stChatInput'] textarea::placeholder{color:#6e7681!important;}",
        ".stFileUploader section{background-color:var(--hy-panel)!important;border:1px dashed var(--hy-border)!important;border-radius:6px!important;padding:.5rem 1rem!important;}",
        ".stFileUploader label{display:none!important;}",
        "</style>",
    ]
)


def configure_page() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def initialize_state() -> None:
    defaults = {
        "messages": [],
        "arquivo_log_dados": None,
        "last_uploaded_file": None,
        "voice_transcript": "",
        "auto_read_answers": False,
  }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def sanitize_context(text: str) -> str:
    replacements = {
        r"\b\d{1,3}(?:\.\d{1,3}){3}\b": "[IP_REDACTED]",
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b": "[EMAIL_REDACTED]",
        r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b": "[CPF_REDACTED]",
        r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b": "[CNPJ_REDACTED]",
        r"\b(?:\d[ -]*?){13,19}\b": "[CARD_REDACTED]",
    }

    sanitized = text
    for pattern, replacement in replacements.items():
        sanitized = re.sub(pattern, replacement, sanitized)

    return sanitized[:MAX_LOG_CHARS]
    

def get_api_key() -> str:
    return st.secrets.get("GEMINI_API_KEY", "").strip()


@st.cache_resource(show_spinner=False)
def get_genai_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def build_system_prompt(scope: str) -> str:
    return (
        f"{BASE_PROMPT}\n\n"
        f"ESCOPO SELECIONADO PELO USUÁRIO: [{scope}]. "
        "Conecte a análise a esse escopo de inteligência de riscos corporativos."
    )


def build_history_contents(current_prompt: str) -> list[types.Content]:
    contents = []

    for message in st.session_state.messages[:-1]:
        role = "model" if message["role"] == "assistant" else "user"
        part = types.Part.from_text(text=message["content"])
        contents.append(types.Content(role=role, parts=[part]))

    current_part = types.Part.from_text(text=current_prompt)
    contents.append(types.Content(role="user", parts=[current_part]))
    return contents


def generate_ai_response(client: genai.Client, contents: list[types.Content], system_prompt: str) -> str:
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.3,
        max_output_tokens=4096,
    )

    try:
        response = client.models.generate_content(
            model=PRIMARY_MODEL,
            contents=contents,
            config=config,
        )
    except Exception as primary_error:
        error_text = str(primary_error)
        quota_error = "429" in error_text or "RESOURCE_EXHAUSTED" in error_text

        if not quota_error:
                       raise RuntimeError(f"Erro técnico no core da IA: {primary_error}") from primary_error

        response = client.models.generate_content(
            model=FALLBACK_MODEL,
            contents=contents,
            config=config,
        )

    if not response.text:
        raise RuntimeError("A IA retornou uma resposta vazia. Tente reenviar a pergunta.")

    return response.text


def generate_strategic_report(history: list[dict[str, str]]) -> io.BytesIO:
    report = [
        "=" * 58,
        "HY RISK INTELLIGENCE - REPORT (RI-AI)",
        "Mapeamento estratégico e blindagem de ativos",
        "=" * 58,
        "",
    ]

    for index, message in enumerate(history, 1):
        author = "USUÁRIO" if message["role"] == "user" else "HY-AI"
        report.extend(
            [
                f"[{index}] {author}:",
                message["content"],
                "-" * 58,
                "",
            ]
        )

    report.extend(
        [
            "=" * 58,
            "Fim do relatório. HY Risk Intelligence - Proteção e Negócio.",
        ]
    )

    buffer = io.BytesIO()
    buffer.write("\n".join(report).encode("utf-8"))
    buffer.seek(0)
    return buffer


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown("<h1>🛡️ HY-AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'>Mapeamento estratégico e blindagem de ativos</p>", unsafe_allow_html=True)
        st.markdown("---")

        st.markdown("### 🔍 Escopo de Análise")
        scope = st.selectbox("Selecione o foco do problema:", ANALYSIS_SCOPES)

        st.markdown("---")
        st.markdown("### 🔊 Voz")
        st.session_state.auto_read_answers = st.checkbox(
            "Ler respostas automaticamente",
            value=st.session_state.auto_read_answers,
            help="Usa a voz nativa do navegador para ler a última resposta da IA.",
        )

        if st.session_state.messages:
            st.markdown("---")
            st.markdown("### 📄 Exportar Dados")
            st.download_button(
                label="📥 Baixar Relatório Estratégico",
                              data=generate_strategic_report(st.session_state.messages),
                file_name="relatorio_hy_risk_intelligence.txt",
                mime="text/plain",
                key="download_report_btn",
            )

        st.markdown("---")
        if st.button("🗑️ Limpar Histórico", type="secondary"):
            st.session_state.messages = []
            st.session_state.arquivo_log_dados = None
            st.session_state.last_uploaded_file = None
            st.rerun()

    return scope


def render_header() -> None:
    st.markdown(
        f"<h1>🛡️ HY-AI <span style='font-size:18px;color:#8b949e;'>{APP_VERSION}</span></h1>",
        unsafe_allow_html=True,
    )
    st.subheader("Mapeamento estratégico e blindagem de ativos 💻")


def render_metrics() -> None:
    columns = st.columns(4)

    total_user_messages = len(
        [
            message
            for message in st.session_state.messages
            if message["role"] == "user"
        ]
    )

    for column, metric in zip(columns, RISK_METRICS):
        if metric.value == "dynamic":
            value = str(total_user_messages)
        else:
            value = metric.value

        with column:
            st.metric(
                label=metric.label,
                value=value,
                delta=metric.delta,
            )


def render_risk_dashboard() -> None:
    chart_column, guide_column = st.columns([2, 1])

    with chart_column:
        radar_data = pd.DataFrame(
            {
                "r": [4, 5, 3, 4, 5],
                "theta": [
                    "Conformidade",
                    "Segurança de Dados",
                    "Gestão de Crise",
                    "Arquitetura de Redes",
                    "Resposta a Incidentes",
                ],
            }
        )

        fig = px.line_polar(
            radar_data,
            r="r",
            theta="theta",
            line_close=True,
            range_r=[0, 5],
            title="🛡️ Índice de Maturidade de Risco Operacional",
        )

        fig.update_traces(fill="toself", line_color="#58a6ff")
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin={"l": 20, "r": 20, "t": 40, "b": 20},
            height=320,
        )

        st.plotly_chart(fig, use_container_width=True)

    with guide_column:
        st.markdown(
            "<p style='font-weight:700;color:#58a6ff;margin-bottom:5px;'>🔍 Guia Rápido de Governança</p>",
            unsafe_allow_html=True,
        )

        with st.expander("🚨 Prazo Notificação ANPD"):
            st.write(
                "Pela LGPD, incidentes de segurança relevantes envolvendo dados pessoais devem ser comunicados "
                "à ANPD e aos titulares em prazo razoável, conforme risco e impacto aos titulares."
            )

        with st.expander("🛠️ O que compõe RTO e RPO?"):
            st.write(
                "RTO é o tempo máximo tolerável para restabelecer um serviço. "
                "RPO é o limite máximo aceitável de perda de dados após uma falha."
            )


def render_chat_history():
    chat_container = st.container()

    with chat_container:
        for index, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == "assistant":
                    st.feedback("thumbs", key=f"feedback_{index}")

    return chat_container


def render_log_uploader() -> None:
    uploaded_file = st.file_uploader(
        "Anexar log",
        type=["txt", "log"],
        label_visibility="collapsed",
    )

    if not uploaded_file:
        return

    uploaded_file.seek(0)
    raw_text = uploaded_file.read().decode("utf-8", errors="replace")
    st.session_state.arquivo_log_dados = sanitize_context(raw_text)
    st.session_state.last_uploaded_file = uploaded_file.name

    st.markdown(
        f"<p style='color:#58a6ff;font-size:12px;margin-top:-10px;margin-bottom:10px;'>"
        f"📎 Arquivo carregado e higienizado: <b>{uploaded_file.name}</b></p>",
        unsafe_allow_html=True,
    )


def get_last_assistant_answer() -> str:
       for message in reversed(st.session_state.messages):
        if message["role"] == "assistant":
            return message["content"]
    return ""


def render_text_to_speech_controls() -> None:
    answer = get_last_assistant_answer()
    if not answer:
        return

    spoken_text = re.sub(r"[*_`#>\[\]()]", "", answer)
    spoken_text_json = json.dumps(spoken_text)
    auto_read_json = json.dumps(bool(st.session_state.auto_read_answers))
    html = (
        '<button onclick="speakHyAnswer()" style="background:#21262d;color:#c9d1d9;border:1px solid #30363d;border-radius:6px;padding:8px 12px;cursor:pointer;margin-right:8px;">🔊 Ouvir última resposta</button>'
        '<button onclick="window.speechSynthesis.cancel()" style="background:#21262d;color:#c9d1d9;border:1px solid #30363d;border-radius:6px;padding:8px 12px;cursor:pointer;">⏹️ Parar</button>'
        "<script>"
        f"const hyText={spoken_text_json};"
        f"const hyAutoRead={auto_read_json};"
        "function speakHyAnswer(){if(!('speechSynthesis' in window)||!hyText)return;window.speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(hyText);u.lang='pt-BR';u.rate=1;u.pitch=1;window.speechSynthesis.speak(u);}"
        "if(hyAutoRead){setTimeout(speakHyAnswer,500);}"
        "</script>"
    )
    components.html(html, height=48)


def render_voice_input() -> str:
    st.markdown("#### 🎙️ Entrada por voz")

    if speech_to_text is None:
        st.info(
            "Para ativar o microfone, adicione `streamlit-mic-recorder` ao requirements.txt "
            "e publique novamente no GitHub/Streamlit Cloud."
        )
        return ""

    transcript = speech_to_text(
        language="pt-BR",
        start_prompt="🎙️ Gravar pergunta",
        stop_prompt="⏹️ Parar gravação",
        just_once=True,
        use_container_width=True,
        key="hy_voice_to_text",
    )

    if transcript:
        st.session_state.voice_transcript = transcript

    if not st.session_state.voice_transcript:
        return ""

    edited_transcript = st.text_area(
        "Texto reconhecido",
        value=st.session_state.voice_transcript,
        height=90,
        key="voice_transcript_editor",
    )

    if st.button("Enviar transcrição para análise", type="primary"):
        st.session_state.voice_transcript = ""
        return edited_transcript.strip()

    return ""

def build_user_prompt(prompt: str) -> str:
    if not st.session_state.arquivo_log_dados:
        return prompt

return (
    "CONTEXTO DO LOG ENVIADO (HIGIENIZADO):\n"
    f"```\n{st.session_state.arquivo_log_dados}\n```\n\n"
    f"PERGUNTA DO USUÁRIO:\n{prompt}"
)


def handle_chat_prompt(chat_container, scope: str, client: genai.Client, voice_prompt: str = "") -> None:
    prompt = voice_prompt or st.chat_input("Digite sua dúvida estratégica ou técnica sobre segurança...")
    if not prompt:
        return

complete_prompt = build_user_prompt(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analisando vetores de risco e gerando resposta corporativa..."):
                try:
                    contents = build_history_contents(complete_prompt)
                    answer = generate_ai_response(client, contents, build_system_prompt(scope))
                except Exception as error:
                    st.error(str(error))
                    return

st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.toast("Análise de riscos concluída!", icon="🛡️")
                st.rerun()


def render_footer() -> None:
    footer = "\n".join(
        [
            '<div style="text-align:center;color:#8b949e;font-size:12px;margin-top:50px;">',
            '<hr style="border-color:#21262d;">',
            "<p>🔒 HY Risk Intelligence (HY RI-AI) - Mapeamento estratégico e blindagem de ativos. Todos os direitos reservados.</p>",
            "</div>",
        ]
    )
    st.markdown(footer, unsafe_allow_html=True)


def main() -> None:
    configure_page()
    initialize_state()

api_key = get_api_key()
    if not api_key:
        st.warning("⚠️ Chave ausente nos Secrets do Streamlit Cloud. Configure GEMINI_API_KEY para iniciar a IA.")
        st.stop()

    scope = render_sidebar()
    client = get_genai_client(api_key)

    render_header()
    render_metrics()
    st.markdown("---")
    render_risk_dashboard()
    st.markdown("---")
  chat_container = render_chat_history()
    render_text_to_speech_controls()
    st.markdown("<br><br>", unsafe_allow_html=True)
    render_log_uploader()
    voice_prompt = render_voice_input()
    handle_chat_prompt(chat_container, scope, client, voice_prompt)
    render_footer()


if __name__ == "__main__":
    main()
