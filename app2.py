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

"<script>",
            f"const text = {spoken_text_json};",
            f"const autoRead = {auto_read_json};",
            'const speakButton = document.getElementById("hy-speak");',
            'const stopButton = document.getElementById("hy-stop");',
            "function speakHyAnswer(){",
            'if (!("speechSynthesis" in window) || !text) return;',
            "window.speechSynthesis.cancel();",
            "const utterance = new SpeechSynthesisUtterance(text);",
            'utterance.lang = "pt-BR";',
            "utterance.rate = 1;",
            "utterance.pitch = 1;",
            "window.speechSynthesis.speak(utterance);",
            "}",
            'speakButton.addEventListener("click", speakHyAnswer);',
            "stopButton.addEventListener('click', () => window.speechSynthesis.cancel());",
            "if (autoRead) { setTimeout(speakHyAnswer, 500); }",
            "</script>",
        ]
    )
    components.html(html, height=58)


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
