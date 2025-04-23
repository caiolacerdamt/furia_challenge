import streamlit as st
from app.firebase.auth_config import auth, db
from datetime import datetime 

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

            st.session_state.usuario_cadastrado = True
            st.session_state.user_email = email
            st.session_state.user_nome = nome

            st.success("Login realizado com sucesso!")
            st.rerun()
        except Exception as e:
            st.error("Error ao fazer login. Verifique suas credenciais.")
            st.error(e)

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
            st.success("Cadastro realizado com sucesso!")
            st.session_state.usuario_cadastrado = True
            st.session_state.user_email = email
            st.session_state.user_nome = nome
            st.rerun()
        except Exception as e:
            if 'EMAIL_EXISTS' in str(e):
                st.error("Esse email já está em uso. Tente outro.")
            else:
                st.error("Erro ao cadastrar. Tente novamente mais tarde.")
                st.error(e)