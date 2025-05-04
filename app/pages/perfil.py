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
            with st.form("form_edicao_perfil"):
                st.markdown("### Atualize seus dados")
                st.markdown("#### Avatar")
                avatar_file = st.file_uploader("Selecione uma imagem (png/jpg)", type=["png","jpg","jpeg"])
                if "avatar_bytes" in st.session_state:
                    st.image(st.session_state["avatar_bytes"], width=100, caption="Preview")

                nome = st.text_input("Nome", value=dados.get("nome", ""))
                #email = st.text_input("E-mail", value=dados.get("email", ""))
                nickname = st.text_input("Nickname", value=dados.get("nickname", ""))
                cpf = st.text_input("CPF", value=dados.get("cpf", ""))
                data_nasc = st.date_input("Data de nascimento",
                                         value=(dados.get("data_nascimento") and datetime.fromisoformat(dados["data_nascimento"]).date()) or date.today())
                genero = st.selectbox("Gênero",
                                      ["Masculino", "Feminino", "Outro", "Prefiro não dizer"],
                                      index=["Masculino","Feminino","Outro","Prefiro não dizer"].index(dados.get("genero"))
                                      if dados.get("genero") in ["Masculino","Feminino","Outro","Prefiro não dizer"] else 0)
                pais = st.selectbox("País", PAISES,
                                     index=PAISES.index(dados.get("pais")) if dados.get("pais") in PAISES else 0)
                telefone = st.text_input("Telefone (somente números)", value=dados.get("telefone", ""))
                
                jogos_salvos = dados.get("jogos_acompanhados", [])
                jogos_doc = [doc.id for doc in db_firebase.collection("jogos").stream()]
                jogos_label = [j.capitalize() for j in jogos_doc]
                jogos_selecionados = st.multiselect(
                    "🎮 Quais jogos você acompanha?",
                    options=jogos_label,
                    default=[j.capitalize() for j in jogos_salvos],
                    key="onb_jogos"
                )

                players_salvos = dados.get("players_favoritos", [])
                apelidos_doc = db_firebase.collection("apelidos").document("lista").get()
                apelidos_dict = apelidos_doc.to_dict() if apelidos_doc.exists else {}
                apelidos = sorted(apelidos_dict.values())
                players_selecionados = st.multiselect(
                    "👤 Quais são seus players favoritos?",
                    options=apelidos,
                    default=players_salvos,
                    key="onb_players"
                )

                if st.form_submit_button("Salvar alterações", use_container_width=True):
                    if not nome  or not nickname:
                        st.warning("Preencha nome e nickname.")
                        st.stop()
                    if not validar_cpf(cpf):
                        st.warning("CPF inválido.")
                        st.stop()
                    if not telefone.isdigit() or not (10 <= len(telefone) <= 11):
                        st.warning("Telefone deve ter 10 ou 11 dígitos numéricos.")
                        st.stop()
                    if pais == "Selecione um país":
                        st.warning("Selecione um país válido.")
                        st.stop()
                    for u in db_firebase.collection("usuarios").stream():
                        ud = u.to_dict()
                        if u.id != uid and ud.get("nickname", "").lower() == nickname.lower():
                            st.warning("Nickname já em uso.")
                            st.stop()

                    update_data = {
                        "nome": nome.strip(),
                        #"email": email.strip(),
                        "nickname": nickname.strip(),
                        "cpf": cpf.strip(),
                        "data_nascimento": data_nasc.isoformat(),
                        "genero": genero,
                        "pais": pais,
                        "telefone": telefone.strip(),
                        "jogos_acompanhados": [j.lower() for j in jogos_selecionados],
                        "players_favoritos": players_selecionados
                    }
                    if avatar_file:
                        bytes_img = avatar_file.read()
                        encoded = base64.b64encode(bytes_img).decode("utf-8")
                        update_data["avatar_url"] = upload_to_imgur(encoded, data_type="base64")

                    usuario_ref.update(update_data)
                    st.success("Perfil atualizado com sucesso!")
                    st.session_state.edit_mode = False
                    st.rerun()

            if st.button("❌ Cancelar edição", use_container_width=True):
                st.session_state.edit_mode = False
                st.rerun()
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
