import streamlit as st
from app.firebase.firebase_admin import db_firebase
from app.firebase.auth_config import auth

class TelaBase:
    def render(self):
        raise NotImplementedError()

class TelaPerfil(TelaBase):
    def render(self):
        if 'user' not in st.session_state:
            st.warning("Por favor, faça login para acessar o seu perfil.")
            return

        uid = st.session_state.user["uid"]
        usuario_ref = db_firebase.collection("usuarios").document(uid)
        usuario = usuario_ref.get()

        if usuario.exists:
            dados_usuario = usuario.to_dict()
            nome = dados_usuario.get("nome", "Nome não disponível")
            email = dados_usuario.get("email", "E-mail não disponível")
            nickname = dados_usuario.get("nickname", "Nickname não disponível")
            cpf = dados_usuario.get("cpf", "CPF não disponível")
            data_nascimento = dados_usuario.get("data_nascimento", "Data de nascimento não disponível")
            genero = dados_usuario.get("genero", "Gênero não disponível")
            pais = dados_usuario.get("pais", "País não disponível")
            numero = dados_usuario.get("numero", "Número não disponível")
            avatar_url = dados_usuario.get("avatar_url", "https://via.placeholder.com/150")
            jogos_acompanhados = dados_usuario.get("jogos_acompanhados", [])
            players_favoritos = dados_usuario.get("players_favoritos", [])

            st.markdown("""
                <style>
                    body {
                        background-color: #0d1117;
                        color: #c9d1d9;
                        text-align: center;
                    }
                    .perfil-container {
                        background-color: #161b22;
                        padding: 2rem;
                        border-radius: 12px;
                        margin-bottom: 2rem;
                        display: inline-block;
                        text-align: left;
                    }
                    .perfil-title {
                        font-size: 32px;
                        font-weight: 700;
                        margin-bottom: 1.5rem;
                        color: #fff;
                    }
                    .perfil-item {
                        font-size: 18px;
                        margin-bottom: 0.8rem;
                    }
                    .avatar {
                        border-radius: 50%;
                        width: 120px;
                        height: 120px;
                        border: 3px solid #58a6ff;
                        margin: 0 auto 1rem;
                    }
                    .badges-container {
                        display: flex;
                        flex-wrap: wrap;
                        justify-content: center;
                        padding: 10px;
                    }
                    .badge {
                        display: inline-block;
                        padding: 14px 24px;
                        margin: 8px;
                        font-size: 16px;
                        font-weight: 600;
                        color: #58a6ff;
                        background: linear-gradient(145deg, #161b22, #0d1117);
                        border: 1px solid #30363d;
                        border-radius: 12px;
                    }
                    .section-title {
                        font-size: 32px;
                        color: #fff;
                        margin-top: 30px;
                        text-align: center;
                        margin-bottom: 0.8rem;
                    }
                    .flex-row {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 1rem;
                    }
                    .flex-column {
                        display: flex;
                        flex-direction: column;
                    }
                </style>
            """, unsafe_allow_html=True)

            st.markdown("<div class='perfil-title'>Meu Perfil 👤</div>", unsafe_allow_html=True)

            st.markdown(f"<img src='{avatar_url}' alt='Avatar' class='avatar'>", unsafe_allow_html=True)

            st.markdown("<div class='perfil-container'>", unsafe_allow_html=True)

            st.markdown(f"<div class='perfil-item'>👤 <b>Nome:</b> {nome}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='perfil-item'>📧 <b>E-mail:</b> {email}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='perfil-item'>🏷️ <b>Nickname:</b> {nickname}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='perfil-item'>🆔 <b>CPF:</b> {cpf}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='perfil-item'>🎂 <b>Data de Nascimento:</b> {data_nascimento}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='perfil-item'>⚧️ <b>Gênero:</b> {genero}</div>", unsafe_allow_html=True)

            st.markdown(f"<div class='perfil-item'>🌍 <b>País:</b> {pais}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='perfil-item'>🔢 <b>Número:</b> {numero}</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            if jogos_acompanhados:
                st.markdown("<div class='section-title'>🎮 Jogos que você acompanha</div>", unsafe_allow_html=True)
                st.markdown("<div class='perfil-container'>", unsafe_allow_html=True)
                badges_html = "<div class='badges-container'>"
                for jogo in jogos_acompanhados:
                    badges_html += f"<div class='badge'>{jogo.capitalize()}</div>"
                badges_html += "</div>"
                st.markdown(badges_html, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='section-title'>Você ainda não acompanha nenhum jogo.</div>", unsafe_allow_html=True)

            if players_favoritos:
                st.markdown("<div class='section-title'>🏆 Jogadores Favoritos</div>", unsafe_allow_html=True)
                st.markdown("<div class='perfil-container'>", unsafe_allow_html=True)
                badges_html = "<div class='badges-container'>"
                for player in players_favoritos:
                    badges_html += f"<div class='badge'>{player.capitalize()}</div>"
                badges_html += "</div>"
                st.markdown(badges_html, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='section-title'>Você ainda não tem jogadores favoritos.</div>", unsafe_allow_html=True)

        else:
            st.error("Erro ao carregar os dados do usuário.")
