import streamlit as st
from app.firebase.firebase_admin import db_firebase
from chatbot.scraping_twitch import check_if_live
from datetime import datetime

def initialize_state():
    if "chatbot_messages" not in st.session_state:
        st.session_state.update({
            "chatbot_messages": [],
            "chatbot_step": "inicio",
            "chatbot_selected_game": None,
            "chatbot_selected_team": None,
        })

def render_history():
    try:
        user_uid = st.session_state.get("user", {}).get("uid", "")
        usuario_ref = db_firebase.collection("usuarios").document(user_uid)
        usuario = usuario_ref.get()

        if usuario.exists:
            dados_usuario = usuario.to_dict()
            avatar_url = dados_usuario.get("avatar_url")
        else:
            avatar_url = "https://i.imgur.com/2tjbfjU.png"
    except Exception as e:
        avatar_url = "https://i.imgur.com/2tjbfjU.png"

    for msg in st.session_state["chatbot_messages"]:
        avatar = (
            'static/furia_logo.png' if msg["role"] == "assistant"
            else avatar_url
        )
        st.chat_message(msg["role"], avatar=avatar).write(msg["content"])

def add_message(role, content):
    st.session_state["chatbot_messages"].append({"role": role, "content": content})

def reset_chat():
    st.session_state.update({
        "chatbot_messages": [],
        "chatbot_step": "inicio",
        "chatbot_selected_game": None,
        "chatbot_selected_team": None,
        "chatbot_prompted_game": False,
        "chatbot_prompted_team": False
    })

def step_inicio():
    user = st.chat_input("Digite algo para iniciar o chat")
    if user:
        add_message("user", user)
        add_message("assistant", """
        **Fala, furioso(a)!** 👋

        Eu sou o seu **contato inteligente da FURIA** e estou aqui para te ajudar! 

        O que você deseja saber hoje? 🤔

        Aqui estão algumas opções do que posso fazer para você:

        - ⚽ **Elenco dos times**: Saiba quem são os jogadores da FURIA.
        - 📅 **Calendário de jogos**: Fique por dentro dos próximos eventos da FURIA.
        - 📺 **Streamers ao vivo**: Veja quem da FURIA está transmitindo ao vivo! 
        - 🛒 **Loja FURIA**: Não perca os produtos exclusivos da nossa loja!

        **Fique à vontade para escolher o que quiser, guerreiro(a)!** 😎

        """)
        st.session_state["chatbot_step"] = "menu"
        st.rerun()

def step_menu():
    col1, col2 = st.columns(2)
    with col1:
        if st.button("ℹ️ Informações sobre time", use_container_width=True):
            add_message("user", "Informações sobre time")
            st.session_state["chatbot_step"] = "list_games"
            st.rerun()
        if st.button("📅 Calendário de jogos", use_container_width=True):
            add_message("user", "Calendário de jogos")
            add_message("assistant", "Buscando jogos agendados…")
            st.session_state["chatbot_step"] = "calendar"
            st.rerun()
    with col2:
        if st.button("📺 Ver streamers online", use_container_width=True):
            add_message("user", "Ver streamers online")
            add_message("assistant", "Buscando streamers online...")
            st.session_state["chatbot_step"] = "loading_streamers"
            st.rerun()
        if st.button("🛒 Loja da FURIA", use_container_width=True):
            add_message("user", "Loja da FURIA")
            add_message("assistant", "Você pode conferir os produtos da FURIA na loja: [https://www.furia.gg/](https://www.furia.gg/)")
            st.session_state["chatbot_step"] = "fim"
            st.rerun()

def step_loading_streamers():
    streamers = [
        'gafallen', 'brino', 'mount', 'paulanobre', 'sofiaespanha', 'xarola_',
        'otsukaxd', 'mwzera', 'jxmo', 'furiatv', 'fittipaldibrothers', 'breezefps',
        'immadness', 'gabssf', 'pokizgames', 'kscerato', 'ikee', 'chelok1ng',
        'qckval', 'raf1nhafps', 'crisguedes', 'yuurih', 'khalil_fps', 'vaxlon', 'daaygamer_',
        'rafaelmoraesgm', 'yanxnz_', 'herdszz', 'havocfps1', 'ablej', 'izaa', 'xeratricky',
        'luanlealx', 'ivdmaluco', 'igoorctg', 'omanelzin_'
    ]

    try:
        live = check_if_live(streamers)
        if live:
            st.markdown("### 🔴 Streamers da FURIA ao vivo agora!")
            for s in live:
                st.markdown(f"""
                    <div style="background-color:#1e1e1e; padding:16px; border-radius:12px; margin-bottom:10px">
                        <a href="https://twitch.tv/{s}" target="_blank" style="color:#fafafa; font-size:18px; font-weight:bold; text-decoration:none;">
                            🎮 <span style="color:#9146FF">{s}</span> está em live agora! Clique aqui para assistir!
                        </a>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("⚠️ Nenhum streamer da FURIA está ao vivo no momento.")
    except Exception as e:
        st.markdown(f"❌ Erro ao verificar status dos streamers: {e}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔙 Voltar ao menu", use_container_width=True):
            reset_chat()
            add_message("assistant", "Olá! Tudo bem? O que deseja agora?")
            st.session_state["chatbot_step"] = "menu"
            st.rerun()
    with col2:
        if st.button("❌ Encerrar chat", use_container_width=True):
            reset_chat()
            st.session_state["chatbot_step"] = "inicio"
            st.rerun()


def step_list_games():
    if not st.session_state.get("chatbot_prompted_game", False):
        add_message("assistant", "🎮 Escolha um dos jogos abaixo para ver os times da FURIA:")
        st.session_state["chatbot_prompted_game"] = True
        st.rerun()

    jogos = [doc.id for doc in db_firebase.collection("jogos").list_documents()]
    
    with st.container():
        st.markdown("### 🎮 Jogos disponíveis")
        for i in range(0, len(jogos), 3):
            cols = st.columns(3)
            for idx, jogo in enumerate(jogos[i:i+3]):
                with cols[idx]:
                    if st.button(jogo, use_container_width=True):
                        add_message("user", jogo)
                        add_message("assistant", f"Carregando times de {jogo}…")
                        st.session_state.update({
                            "chatbot_selected_game": jogo,
                            "chatbot_step": "list_teams",
                            "chatbot_prompted_game": False
                        })
                        st.rerun()

def step_list_teams():
    jogo = st.session_state["chatbot_selected_game"]
    doc = db_firebase.collection("jogos").document(jogo).get()
    data = doc.to_dict() or {}
    times = data.get("times") or [d.id for d in db_firebase.collection("jogos").document(jogo).collection("times").list_documents()]

    if not st.session_state.get("chatbot_prompted_team", False):
        add_message("assistant", f"🛡️ Escolha um time de **{jogo}**:")
        st.session_state["chatbot_prompted_team"] = True
        st.rerun()

    with st.container():
        st.markdown(f"### 🛡️ Times em **{jogo}**")
        for i in range(0, len(times), 3):
            cols = st.columns(3)
            for idx, team in enumerate(times[i:i+3]):
                with cols[idx]:
                    if st.button(team, use_container_width=True):
                        add_message("user", team)
                        add_message("assistant", f"Buscando jogadores de {team}…")
                        st.session_state.update({
                            "chatbot_selected_team": team,
                            "chatbot_step": "list_players",
                            "chatbot_prompted_team": False
                        })
                        st.rerun()

def step_list_players():
    jogo = st.session_state["chatbot_selected_game"]
    team = st.session_state["chatbot_selected_team"]
    players = [
        d.to_dict()
        for d in db_firebase
        .collection("jogos").document(jogo)
        .collection("times").document(team)
        .collection("jogadores").stream()
    ]

    if players:
        texto = f"### 👥 Elenco de **{team}** em {jogo}\n\n"
        texto += "\n".join(
            f"- **{p.get('apelido', p.get('nome','?'))}** — {p.get('função','—')}" for p in players
        )
    else:
        texto = f"⚠️ Não encontrei jogadores para {team}."

    add_message("assistant", texto)
    st.session_state["chatbot_step"] = "fim"
    st.rerun()

def step_calendar():
    try:
        docs = db_firebase.collection("calendario").stream()
        eventos = [doc.to_dict() for doc in docs]

        if not eventos:
            add_message("assistant", "Nenhum jogo agendado por enquanto.")
        else:
            def evento_datetime(e):
                try:
                    return datetime.strptime(f"{e.get('data', '')} {e.get('hora', '')}", "%d/%m/%Y %Hh%M")
                except:
                    return datetime.max 

            eventos.sort(key=evento_datetime)

            texto = "📅 **Próximos Jogos:**\n\n"
            for evento in eventos:
                data = evento.get("data", "?")
                hora = evento.get("hora", "?")
                nome = evento.get("evento_nome", "?")
                jogo = evento.get("jogo", "?")

                texto += f"- **{data} às {hora}** — {nome} ({jogo})\n"
            
            add_message("assistant", texto)
    except Exception as e:
        add_message("assistant", f"Erro ao carregar o calendário: {e}")
    
    st.session_state["chatbot_step"] = "fim"
    st.rerun()

def step_fim():
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔙 Voltar ao menu", use_container_width=True):
            reset_chat()
            add_message("assistant", "Olá! Tudo bem? O que deseja agora?")
            st.session_state["chatbot_step"] = "menu"
            st.rerun()
    with col2:
        if st.button("❌ Encerrar chat", use_container_width=True):
            reset_chat()
            st.session_state["chatbot_step"] = "inicio"
            st.rerun()
