import streamlit as st
import base64
from datetime import datetime, date
from app.firebase.firebase_admin import db_firebase
from app.firebase.auth_config import db, auth
from app.utils.utils import upload_to_imgur, validar_cpf 
from app.utils.constants import DEFAULT_AVATAR, PAISES

class TelaBase:
    def render(self):
        raise NotImplementedError()

class TelaPerfil(TelaBase):
    def render(self):
        if 'confirm_delete' not in st.session_state:
            st.session_state.confirm_delete = False

        if 'user' not in st.session_state:
            st.warning("Por favor, faça login para acessar o seu perfil.")
            return

        uid = st.session_state.user["uid"]
        usuario_ref = db_firebase.collection("usuarios").document(uid)
        usuario = usuario_ref.get()
        if not usuario.exists:
            st.error("Erro ao carregar os dados do usuário.")
            return

        dados = usuario.to_dict()

        st.markdown("""
            <style>
                .profile-card { background: linear-gradient(135deg, #1e2228, #2a2e36); border-radius: 16px; padding: 24px; box-shadow: 0 8px 16px rgba(0,0,0,0.3); max-width: 800px; margin: auto; color: #c9d1d9; font-family: 'Segoe UI', sans-serif; }
                .profile-header { text-align: center; margin-bottom: 24px; }
                .profile-header h2 { margin: 0; font-size: 2.5rem; color: #58a6ff; }
                .profile-details { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }
                .detail-item { background: #161b22; padding: 12px; border-radius: 8px; text-align: center; }
                .detail-item b { color: #58a6ff; }
                .badges-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 12px; }
                .badge { padding: 8px 16px; border-radius: 16px; font-weight: 600; background: #0d1117; border: 1px solid #30363d;}
            </style>
        """, unsafe_allow_html=True)

        if 'edit_mode' not in st.session_state:
            st.session_state.edit_mode = False

        if st.session_state.edit_mode:
            # edição omitida para focar na exclusão
            return

        avatar_url = dados.get("avatar_url", DEFAULT_AVATAR)
        st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
        st.markdown("<div class='profile-header'><h2>Meu Perfil 👤</h2></div>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='text-align:center; margin: 0 auto 24px auto;'>"
            f"<img src='{avatar_url}' alt='Avatar' style='border-radius:50%; width:150px; height:150px; object-fit:cover;'/>"
            f"</div>",
            unsafe_allow_html=True
        )
        st.markdown("<div class='profile-details'>", unsafe_allow_html=True)
        for label, key in [("Nome", 'nome'), ("E-mail", 'email'), ("Nickname", 'nickname'), ("CPF", 'cpf'),
                            ("Data de Nascimento", 'data_nascimento'), ("Gênero", 'genero'), ("País", 'pais'), ("Telefone", 'telefone')]:
            valor = dados.get(key, "-")
            st.markdown(f"<div class='detail-item'><b>{label}:</b><br>{valor}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        jogos = dados.get("jogos_acompanhados", [])
        if jogos:
            st.markdown("<h3 style='text-align:center; color:#58a6ff;'>🎮 Jogos que você acompanha</h3>", unsafe_allow_html=True)
            badges = "".join([f"<div class='badge'>{jogo.capitalize()}</div>" for jogo in jogos])
            st.markdown(f"<div class='badges-container'>{badges}</div>", unsafe_allow_html=True)
        players = dados.get("players_favoritos", [])
        if players:
            st.markdown("<h3 style='text-align:center; color:#58a6ff;'>🏆 Jogadores Favoritos</h3>", unsafe_allow_html=True)
            badges_p = "".join([f"<div class='badge'>{p.capitalize()}</div>" for p in players])
            st.markdown(f"<div class='badges-container'>{badges_p}</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ Editar perfil", use_container_width=True):
                st.session_state.edit_mode = True
                st.rerun()
        with col2:
            if st.button("🗑️ Excluir perfil", use_container_width=True, key="delete_button"):
                st.session_state.confirm_delete = True
                st.rerun()

        if st.session_state.get("confirm_delete"):
            st.warning("Você tem certeza que deseja excluir seu perfil? Essa ação é irreversível.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Cancelar", key="cancel_excluir", use_container_width=True):
                    st.session_state.confirm_delete = False
                    st.rerun()
            with col2:
                if st.button("Confirmar exclusão", key="confirm_excluir", use_container_width=True):
                    try:
                        db_firebase.collection("usuarios").document(uid).delete()

                        posts = db_firebase.collection("posts").where("user_id", "==", uid).stream()
                        for post in posts:
                            post.reference.delete()

                        auth.delete_user_account(st.session_state.user_token)

                        st.success("Perfil excluído com sucesso.")
                        st.session_state.clear()
                        st.rerun()

                    except Exception as e:
                        st.error(f"Erro ao excluir perfil: {e}")
