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
