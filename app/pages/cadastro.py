import streamlit as st
from app.firebase.auth_config import auth, db
from datetime import datetime 
import time

def tela_login():
    st.subheader("Login")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        try:
            user = auth.sign_in_with_email_and_password(email, senha)
            uid = user["localId"]
            id_token = user["idToken"]

            dados_usuario = db.child("usuarios").child(uid).get(id_token).val()
            nome = dados_usuario.get("nome", "Usuário") if dados_usuario else "Usuário"
            email_confirmado = auth.get_account_info(user["idToken"])["users"][0]["emailVerified"]

            if not email_confirmado:
                st.error("Por favor, confirme seu e-mail antes de fazer login.")

                if st.button("Reenviar e-mail de confirmação"):
                    auth.send_email_verification(user["idToken"])
                    st.success("E-mail de confirmação enviado.")
                return
            
            else:
                st.session_state.usuario_cadastrado = True
                st.session_state.user_email = email
                st.session_state.user_nome = nome
                st.session_state.confirmando_email = False

                st.success("Login realizado com sucesso!")
                st.rerun()
        except Exception as e:
            st.error("Error ao fazer login. Verifique suas credenciais.")
            #st.error(e)
    
    if st.button("Esqueci minha senha"):
        st.session_state.recuperar_senha = True
        st.rerun()

def tela_cadastro():
    st.subheader("Cadastro")
    nome = st.text_input("Nome")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Cadastrar"):
        try:
            user = auth.create_user_with_email_and_password(email, senha)
            uid = user['localId']
            data = {
                "nome": nome,
                "email": email,
                "data_cadastro": datetime.now().isoformat()
            }
            db.child("usuarios").child(uid).set(data)

            auth.send_email_verification(user["idToken"])

            st.success("Cadastro realizado com sucesso! Por favor, verifique seu e-mail para confirmar.")
            st.session_state.usuario_cadastrado = False
            st.session_state.user_email = email
            st.session_state.user_nome = nome
            st.session_state.recuperar_senha = False
            st.session_state.confirmando_email = True
            st.rerun()

        except Exception as e:
            if 'EMAIL_EXISTS' in str(e):
                st.error("Esse email já está em uso. Tente outro.")
            else:
                st.error("Erro ao cadastrar. Tente novamente mais tarde.")
                st.error(e)

def tela_recuperar_senha():
    st.subheader("Recuperar senha")
    email = st.text_input("Digite seu email")

    if st.button("Enviar email de recuperação"):
        if email:
            try:
                auth.send_password_reset_email(email)
                st.success("Um e-mail foi enviado para redefinir a sua senha.")
            except Exception as e:
                erro_str = str(e)
                if "EMAIL_NOT_FOUND" in erro_str:
                    st.error("Esse e-mail não está cadastrado.")
                else:
                    st.error("Erro ao enviar o e-mail de recuperação.")
                    st.error(erro_str)
        else:
            st.error("Insira seu email corretamente.")

    if st.button("Fazer Login"):
        st.session_state.recuperar_senha = False
        st.rerun()

def tela_confirmacao_email():
    st.subheader("Verifique seu e-mail")
    st.info("Um e-mail de confirmação foi enviado. Verifique sua caixa de entrada (e spam também).")

    if st.button("Já confirmei meu e-mail, fazer login"):
        st.session_state.recuperar_senha = False
        st.session_state.confirmando_email = False
        st.rerun()