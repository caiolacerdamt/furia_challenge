import streamlit as st
from app.firebase.auth_config import auth
from app.firebase.firebase_admin import db_firebase
from datetime import datetime, date
from itertools import cycle
from utils.utils import validar_cpf

class TelaBase:
    def render(self):
        raise NotImplementedError()

class TelaLogin(TelaBase):
    def render(self):
        st.markdown("<h2 style='text-align: center;'>Bem-vindo de volta 👋</h2>", unsafe_allow_html=True)
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
        st.subheader("Nos conte mais sobre você, gênio!")

        nickname = st.text_input("Qual seu nick?", key="onb_nick")
        cpf = st.text_input("Qual seu CPF?", key="onb_cpf")
        data_nascimento = st.date_input("Data de nascimento", key="onb_datanascimento", min_value=date(1900, 1, 1), max_value=date.today())
        genero = st.selectbox("Qual seu gênero?", options=["Masculino", "Feminino", "Outro", "Prefiro não dizer."])

        st.markdown("### 🎮 Quais jogos você acompanha? ###")

        jogos_ref = db_firebase.collection("jogos")
        jogos_doc = list(jogos_ref.stream())

        if "jogos_selecionados" not in st.session_state:
            st.session_state.jogos_selecionados = []

        colunas = st.columns(3)
        col_cycle = cycle(colunas)

        for jogo_doc in jogos_doc:
            jogo_id = jogo_doc.id
            selecionado = jogo_id in st.session_state.jogos_selecionados

            col = next(col_cycle)
            with col:
                if st.button(f"{'✅' if selecionado else '➕'} {jogo_id.capitalize()}", key=f"btn_{jogo_id}"):

                    if selecionado:
                        st.session_state.jogos_selecionados.remove(jogo_id)
                    else:
                        st.session_state.jogos_selecionados.append(jogo_id)
                    st.rerun()

        if st.button("Enviar", key="btn_onb_enviar"):
            if not nickname or not cpf or not genero or not data_nascimento:
                st.warning("Por favor, preencha todos os campos.")
                return

            if not validar_cpf(cpf):
                st.warning("CPF inválido. Verifique e tente novamente.")
                return

            usuarios_ref = db_firebase.collection("usuarios").stream()
            apelido_ja_usado = False

            for usuario_doc in usuarios_ref:
                dados = usuario_doc.to_dict()
                if dados.get("nickname", "").strip().lower() == nickname.strip().lower():
                    apelido_ja_usado = True
                    break

            if apelido_ja_usado:
                st.warning("Esse nick já está em uso. Por favor, escolha outro.")
                return

            try:
                usuario_id = st.session_state.user_uid
                db_firebase.collection("usuarios").document(usuario_id).update({
                    "jogos_acompanhados": st.session_state.jogos_selecionados,
                    "nickname": nickname,
                    "cpf": cpf,
                    "data_nascimento": data_nascimento.isoformat(),
                    "genero": genero,
                    "onboarding_completo": True
                })
                st.session_state.nickname = nickname
                st.success("Onboarding concluído!")
                st.session_state.onboarding_pendente = False
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar escolhas: {e}")
