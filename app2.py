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


BASE_PROMPT = """
Você é o "HY RISK INTELLIGENCE-AI", um assistente de inteligência artificial especialista em Segurança da Informação, Risk Intelligence e Governança Estratégica.
Sua missão é apoiar profissionais, gestores e analistas na tomada de decisões seguras, eficientes e alinhadas ao negócio.

REGRAS DE OPERAÇÃO:
1. Abordagem estratégica: responda priorizando mitigação de riscos, governança, conformidade, arquitetura segura e melhores práticas de cibersegurança.
2. Estrutura obrigatória: use exatamente estes quatro títulos em todas as respostas:
   **🚨 Visão Estratégica / Análise de Risco**
   **🛠️ Planos de Ação / Mitigação**
   **🔍 Justificativa Técnico-Estratégica**
   **📚 Referências**
3. Clareza executiva: seja objetivo, acionável e técnico quando necessário, sem perder a visão de negócio.
4. Ética e segurança: nunca forneça instruções ofensivas, ilegais, destrutivas ou voltadas à exploração não autorizada. Converta pedidos arriscados em orientação defensiva, preventiva e corporativa.
5. Privacidade: trate logs, nomes, e-mails, IPs, documentos e identificadores como dados sensíveis.
"""


CUSTOM_CSS = """
<style>
    :root {
        --hy-bg: #0d1117;
        --hy-panel: #161b22;
        --hy-sidebar: #070a0e;
        --hy-border: #30363d;
        --hy-text: #c9d1d9;
        --hy-muted: #8b949e;
        --hy-primary: #58a6ff;
        --hy-strong: #f0f6fc;
    }

    .stApp,
    html,
    body,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"] {
        background-color: var(--hy-bg) !important;
    }

    [data-testid="stSidebar"] {
        background-color: var(--hy-sidebar) !important;
        border-right: 1px solid var(--hy-border) !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
