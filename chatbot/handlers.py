import streamlit as st
from app.firebase.firebase_admin import db_firebase
from chatbot.scraping_twitch import check_if_live
from datetime import datetime
import base64
from utils.constants import DEFAULT_AVATAR, STREAMERS_FURIA, LINKS_FURIA


def initialize_state():
    if "chatbot_messages" not in st.session_state:
        st.session_state.update({
            "chatbot_messages": [],
            "chatbot_step": "inicio",
            "chatbot_selected_game": None,
            "chatbot_selected_team": None,
            "chatbot_prompted_game": False,
            "chatbot_prompted_team": False
        })


def render_history():
    try:
        user_uid = st.session_state.get("user", {}).get("uid", "")
        usuario_ref = db_firebase.collection("usuarios").document(user_uid)
        usuario = usuario_ref.get()
        avatar_url = usuario.to_dict().get("avatar_url", DEFAULT_AVATAR) if usuario.exists else DEFAULT_AVATAR
    except Exception:
        avatar_url = DEFAULT_AVATAR

    for msg in st.session_state["chatbot_messages"]:
        avatar = 'static/furia_logo.png' if msg["role"] == "assistant" else avatar_url
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
    if not user:
        return
    add_message("user", user)
    add_message("assistant", (
        "**Fala, furioso(a)!** 👋\n\n"
        "Eu sou o seu **contato inteligente da FURIA** e estou aqui para te ajudar!\n\n"
        "O que você deseja saber hoje? 🤔\n\n"
        "Aqui estão algumas opções do que posso fazer para você:\n"
        "- ⚽ **Elenco dos times**\n"
        "- 📅 **Calendário de jogos**\n"
        "- 📺 **Streamers ao vivo**\n"
        "- 🛒 **Loja FURIA**\n\n"
        "- 🌍 **Redes Sociais da FURIA**\n\n"
        "**Fique à vontade para escolher o que quiser, guerreiro(a)!** 😎"
    ))
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
        if st.button("🔗 Redes Sociais da FURIA", use_container_width=True):
            add_message("user", "Redes Sociais da FURIA")
            add_message("assistant", "🌐 Chegou a hora de se conectar com a tropa!\n\n"    
                        "Siga a FURIA nas redes sociais e fique por dentro de todas as novidades, bastidores, conteúdos exclusivos e muito mais. 👊🐾")
            st.session_state["chatbot_step"] = "redes_sociais"
            st.rerun()
    with col2:
        if st.button("📺 Ver streamers online", use_container_width=True):
            add_message("user", "Ver streamers online")
            add_message("assistant", "Buscando streamers online...")
            st.session_state["chatbot_step"] = "loading_streamers"
            st.rerun()
        if st.button("🛒 Loja da FURIA", use_container_width=True):
            add_message("user", "Loja da FURIA")
            add_message("assistant", "Confira os produtos da FURIA na loja: [furia.gg](https://www.furia.gg/)")
            st.session_state["chatbot_step"] = "fim"
            st.rerun()


def step_loading_streamers():
    try:
        live = check_if_live(STREAMERS_FURIA)
        if live:
            st.markdown("### 🔴 Streamers da FURIA ao vivo agora!")
            for s in live:
                st.markdown(f"""
                    <div style='background-color:#1e1e1e; padding:16px; border-radius:12px; margin-bottom:10px'>
                        <a href='https://twitch.tv/{s}' target='_blank' style='color:#fafafa; font-size:18px; font-weight:bold; text-decoration:none;'>
                            🎮 <span style='color:#9146FF'>{s}</span> está em live agora! Clique aqui para assistir!
                        </a>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Nenhum streamer da FURIA está ao vivo no momento.")
    except Exception as e:
        st.error(f"Erro ao verificar status dos streamers: {e}")
    step_fim()


def step_list_games():
    if not st.session_state.get("chatbot_prompted_game", False):
        add_message("assistant", "🎮 Escolha um dos jogos abaixo para ver os times da FURIA:")
        st.session_state["chatbot_prompted_game"] = True
        st.rerun()
    jogos = [doc.id for doc in db_firebase.collection("jogos").list_documents()]
    st.markdown("### 🎮 Jogos disponíveis")
    for i in range(0, len(jogos), 3):
        cols = st.columns(3)
        for idx, jogo in enumerate(jogos[i:i+3]):
            if cols[idx].button(jogo, use_container_width=True):
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
    st.markdown(f"### 🛡️ Times em **{jogo}**")
    for i in range(0, len(times), 3):
        cols = st.columns(3)
        for idx, team in enumerate(times[i:i+3]):
            if cols[idx].button(team, use_container_width=True):
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
    players = [d.to_dict() for d in db_firebase.collection("jogos").document(jogo).collection("times").document(team).collection("jogadores").stream()]
    if players:
        texto = f"### 👥 Elenco de **{team}** em {jogo}\n\n"
        texto += "\n".join(f"- **{p.get('apelido', p.get('nome','?'))}** — {p.get('função','—')}" for p in players)
    else:
        texto = f"⚠️ Não encontrei jogadores para {team}."
    add_message("assistant", texto)
    st.session_state["chatbot_step"] = "fim"
    st.rerun()


def step_calendar():
    try:
        eventos = [doc.to_dict() for doc in db_firebase.collection("calendario").stream()]
        if not eventos:
            add_message("assistant", "Nenhum jogo agendado por enquanto.")
        else:
            eventos.sort(key=lambda e: datetime.strptime(f"{e['data']} {e['hora']}", "%d/%m/%Y %Hh%M"))
            texto = "📅 **Próximos Jogos:**\n\n"
            for ev in eventos:
                texto += f"- **{ev['data']} às {ev['hora']}** — {ev['evento_nome']} ({ev['jogo']})\n"
            add_message("assistant", texto)
    except Exception as e:
        add_message("assistant", f"Erro ao carregar o calendário: {e}")
    st.session_state["chatbot_step"] = "fim"
    st.rerun()

def step_redes_sociais():
    st.markdown("### 🌍 Redes Sociais da FURIA")

    redes = list(LINKS_FURIA.items())
    col1, col2 = st.columns(2)

    for i, (name, url) in enumerate(redes):
        try:
            with open(f"static/{name}.png", "rb") as img_file:
                b64_img = base64.b64encode(img_file.read()).decode()
        except Exception:
            b64_img = "" 

        bloco_html = f"""
            <div style='background-color:#1e1e1e; padding:16px; border-radius:12px; margin-bottom:15px'>
                <a href='{url}' target='_blank' style='color:#fafafa; text-decoration:none; display:flex; align-items:center; gap:16px;'>
                    <img src='data:image/png;base64,{b64_img}' width='32' height='32' style='border-radius:8px;' />
                    <span style='font-size:18px; font-weight:bold; color:#9146FF;'>{name.capitalize()}</span>
                </a>
            </div>
        """

        if i % 2 == 0:
            col1.markdown(bloco_html, unsafe_allow_html=True)
        else:
            col2.markdown(bloco_html, unsafe_allow_html=True)

    step_fim()


def step_fim():
    col1, col2 = st.columns(2)
    if col1.button("🔙 Voltar ao menu", use_container_width=True):
        reset_chat()
        add_message("assistant", "Olá! Tudo bem? O que deseja agora?")
        st.session_state["chatbot_step"] = "menu"
        st.rerun()
    if col2.button("❌ Encerrar chat", use_container_width=True):
        reset_chat()
        st.session_state["chatbot_step"] = "inicio"
        st.rerun()
