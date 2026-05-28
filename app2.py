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
