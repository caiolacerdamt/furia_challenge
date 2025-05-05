import streamlit as st
from app.firebase.auth_config import auth
from app.firebase.firebase_admin import db_firebase
from datetime import datetime, date
from itertools import cycle
from app.utils.utils import validar_cpf, upload_to_imgur
from app.utils.constants import DEFAULT_AVATAR, PAISES
import base64

class TelaBase:
    def render(self):
        raise NotImplementedError()

class TelaLogin(TelaBase):
    def render(self):
        st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)
        st.write("")
        
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            with st.container(border=True):
                st.write("")
                email = st.text_input("📧 E-mail", key="login_email")
                senha = st.text_input("🔒 Senha", type="password", key="login_senha")
                st.write("")
                
                col_login = st.columns(2)
                with col_login[0]:
                    if st.button("Entrar 🚀", key="btn_login", use_container_width=True):
                        self._login(email, senha)
                with col_login[1]:
                    if st.button("Esqueci a senha", key="btn_forgot", use_container_width=True):
                        st.session_state.recuperar_senha = True
                        st.rerun()

                st.divider()

                if st.button("🆕 Não tem conta? Cadastre-se", key="btn_login_go_cadastro", use_container_width=True):
                    st.session_state.pagina_acesso = "Cadastro"
                    st.rerun()

    def _login(self, email, senha):
        try:
            user = auth.sign_in_with_email_and_password(email, senha)
            uid = user["localId"]
            id_token = user["idToken"]
            st.session_state.user = {
                "uid": uid,
                "email": email,
                "token": id_token
            }
            user_doc = db_firebase.collection("usuarios").document(uid).get()
            dados_usuario = user_doc.to_dict()
            
            avatar_url = dados_usuario.get("avatar_url", DEFAULT_AVATAR)

            nome = dados_usuario.get("nome", "Usuário") if dados_usuario else "Usuário"
            email_confirmado = auth.get_account_info(id_token)["users"][0]["emailVerified"]

            if not email_confirmado:
                st.error("Por favor, confirme seu e-mail antes de fazer login.")
                if st.button("Reenviar e-mail de confirmação", key="btn_resent"):
                    auth.send_email_verification(id_token)
                    st.success("E-mail de confirmação enviado.")
                return

            onboarding_completo = dados_usuario.get("onboarding_completo", False)
            st.session_state.user_email = email
            st.session_state.user_nome = nome
            st.session_state.avatar_url = avatar_url
            st.session_state.user_uid = uid
            st.session_state.user_token = id_token
            st.session_state.nickname = dados_usuario.get("nickname", nome)
            st.session_state.usuario_cadastrado = True
            st.session_state.confirmando_email = False
            st.session_state.onboarding_pendente = not onboarding_completo

            if onboarding_completo:
                st.success("Login realizado com sucesso!")

            st.rerun()
        except Exception:
            st.error("Erro ao fazer login. Verifique suas credenciais.")

class TelaCadastro(TelaBase):
    def render(self):
        st.markdown("<h2 style='text-align: center;'>Crie sua conta 🚀</h2>", unsafe_allow_html=True)
        st.write("")
        
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            with st.container(border=True):
                st.write("")
                nome = st.text_input("👤 Nome completo", key="cad_nome")
                email = st.text_input("📧 E-mail", key="cad_email")
                senha = st.text_input("🔒 Senha", type="password", key="cad_senha")
                senha_confirmacao = st.text_input("🔒 Confirme sua senha", type="password", key="cad_senha_confirmacao")
                st.write("")
                
                if st.button("Cadastrar ✨", key="btn_cadastrar", use_container_width=True):
                    self._cadastrar(nome, email, senha, senha_confirmacao)

                st.divider()

                if st.button("🔑 Já tem conta? Fazer login", key="btn_go_login", use_container_width=True):
                    st.session_state.pagina_acesso = "Login"
                    st.rerun()
        
        
    def _cadastrar(self, nome, email, senha, senha_confirmacao):
        if senha != senha_confirmacao:
            st.error("As senhas não coincidem. Tente novamente.")
            return
            
        try:
            user = auth.create_user_with_email_and_password(email, senha)
            uid = user["localId"]
            data = {
                "nome": nome,
                "email": email,
                "data_cadastro": datetime.now().isoformat(),
                "onboarding_completo": False
            }

            db_firebase.collection("usuarios").document(uid).set(data)
            auth.send_email_verification(user["idToken"])
            st.success("Cadastro realizado! Verifique seu e-mail para ativar sua conta.")
            st.session_state.usuario_cadastrado = False
            st.session_state.user_email = email
            st.session_state.user_nome = nome
            st.session_state.recuperar_senha = False
            st.session_state.confirmando_email = True
            st.rerun()
        except Exception as e:
            if "EMAIL_EXISTS" in str(e):
                st.error("Esse email já está em uso. Tente outro ou faça login.")
            else:
                st.error("Error ao cadastrar. Tente novamente mais tarde.")

class TelaRecuperarSenha(TelaBase):
    def render(self):
        st.subheader("Recuperar senha")
        email = st.text_input("Digite seu email", key="rec_email")
        if st.button("Enviar email de recuperação", key="btn_envio_rec"):
            if email:
                try:
                    auth.send_password_reset_email(email)
                    st.success("E-mail enviado para redefinir sua senha.")
                except Exception as e:
                    if "EMAIL_NOT_FOUND" in str(e):
                        st.error("Esse e-mail não está cadastrado.")
                    else:
                        st.error("Erro ao enviar o e-mail de recuperação.")
            else:
                st.error("Insira seu email corretamente.")
        if st.button("Fazer Login", key="btn_voltar_login"):
            st.session_state.recuperar_senha = False
            st.rerun()


class TelaConfirmacaoEmail(TelaBase):
    def render(self):
        st.subheader("Verifique seu e-mail")
        st.info("Um e-mail de confirmação foi enviado. Verifique sua caixa de entrada.")
        if st.button("Já confirmei meu e-mail, fazer login", key="btn_confirma_email"):
            st.session_state.confirmando_email = False
            st.session_state.pagina_acesso = "Login"
            st.rerun()

class TelaOnboarding(TelaBase):

    def render(self):
        st.header("📋 Conte um pouco sobre você — prometo que é rápido!")

        img_src = st.session_state.get("avatar_b64", DEFAULT_AVATAR)
        st.markdown(
            f'<div style="text-align:center;">'
            f'<img src="{img_src}" style="border-radius:50%; '
            f'width:150px; height:150px; object-fit:cover; '
            f'border:4px solid #444;"/>'
            f'</div>',
            unsafe_allow_html=True
        )

        image_file = st.file_uploader(
            "Envie sua nova foto",
            type=["png", "jpg", "jpeg"],
            key="onb_avatar"
        )

        if image_file is not None:
            prev_name = st.session_state.get("avatar_name")
            if image_file.name != prev_name:
                img_bytes = image_file.read()
                b64 = base64.b64encode(img_bytes).decode("utf-8")
                st.session_state["avatar_b64"]   = f"data:image/png;base64,{b64}"
                st.session_state["avatar_bytes"] = img_bytes
                st.session_state["avatar_name"]  = image_file.name
                st.rerun()

        st.markdown("---")

        with st.form("onboarding_form"):
            nickname = st.text_input("Qual seu nick?", key="onb_nick")

            pais = st.selectbox(
                "Selecione seu país",
                options=PAISES,
                index=0,
                key="onb_pais"
            )

            telefone = st.text_input(
                "Telefone (somente números)",
                placeholder="61987654321",
                key="onb_telefone"
            )

            cpf = st.text_input("Qual seu CPF?", key="onb_cpf")

            data_nasc = st.date_input(
                "Data de nascimento",
                key="onb_datanascimento",
                min_value=date(1900, 1, 1),
                max_value=date.today()
            )

            genero = st.selectbox(
                "Qual seu gênero?",
                ["Masculino", "Feminino", "Outro", "Prefiro não dizer."],
                key="onb_genero"
            )

            jogos_docs = [doc.id for doc in db_firebase.collection("jogos").stream()]
            jogos_label = [j.capitalize() for j in jogos_docs]
            selecionados = st.multiselect(
                "🎮 Quais jogos você acompanha?",
                options=jogos_label,
                key="onb_jogos"
            )

            try:
                apelidos_doc = db_firebase.collection("apelidos").document("lista").get()
                apelidos_dict = apelidos_doc.to_dict() if apelidos_doc.exists else {}
                apelidos = sorted(apelidos_dict.values())
            except Exception as e:
                st.error(f"Erro ao buscar os jogadores favoritos: {e}")
                apelidos = []
            
            players_favoritos = st.multiselect(
                "👤 Quais são seus players favoritos?",
                options=apelidos,
                key="onb_players"
            )

            enviar = st.form_submit_button("Enviar")


        if enviar:
            if not (nickname and cpf and data_nasc and genero and selecionados):
                st.warning("Preencha todos os campos e selecione ao menos um jogo.")
                return
            
            if pais == "Selecione um país":
                st.warning("Por favor, selecione seu país")
                return
            
            if not telefone:
                st.warning("Adicione seu número.")
                return
            elif not telefone.isdigit() or not (10 <= len(telefone) <=11):
                st.error("Informe apenas números.")
                return

            if not validar_cpf(cpf):
                st.warning("CPF inválido.")
                return

            for usuario in db_firebase.collection("usuarios").stream():
                if usuario.to_dict().get("nickname", "").strip().lower() == nickname.strip().lower():
                    st.warning("Esse nick já está em uso. Escolha outro, por favor.")
                    return
                
            avatar_url = DEFAULT_AVATAR

            if st.session_state.get("avatar_bytes"):
                try:
                    encoded = base64.b64encode(st.session_state["avatar_bytes"]).decode("utf-8")
                    avatar_url = upload_to_imgur(encoded, data_type="base64")
                    del st.session_state["avatar_bytes"]
                except Exception as e:
                    st.error(f"Falha ao enviar imagem: {e}")
                    return

            try:
                usuario_id = st.session_state.user_uid
                data = {
                    "avatar_url": avatar_url,
                    "nickname": nickname.strip(),
                    "pais": pais,
                    "telefone": telefone,
                    "cpf": cpf.strip(),
                    "data_nascimento": data_nasc.isoformat(),
                    "genero": genero,
                    "jogos_acompanhados": [
                        jogos_docs[jogos_label.index(j)] for j in selecionados
                    ],
                    "players_favoritos": players_favoritos,
                    "onboarding_completo": True
                }

                db_firebase.collection("usuarios").document(usuario_id).update(data)

                st.session_state.nickname = nickname.strip()
                st.session_state.avatar_url = avatar_url
                st.success("Onboarding concluído com sucesso! 🎉")
                st.session_state.onboarding_pendente = False
                st.rerun()

            except Exception as e:
                st.error(f"Erro ao salvar dados: {e}")