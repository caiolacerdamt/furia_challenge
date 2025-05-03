import streamlit as st
from app.firebase.firebase_admin import db_firebase, storage
from firebase_admin import firestore
from datetime import datetime
from app.utils.constants import DEFAULT_AVATAR

class TelaBase:
    def render(self):
        raise NotImplementedError()

class HomePage(TelaBase):
    def set_post(self, user_id, content):
        tweet_ref = db_firebase.collection("posts").document()
        tweet_ref.set({
            "user_id": user_id,
            "content": content,
            "timestamp": datetime.now(),
            "likes": 0,
            "liked_by": [],
        })
    
    def get_posts(self):
        posts = db_firebase.collection("posts").order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
        posts_list = list(posts)
        return posts_list
    
    def toggle_like(self, post_id, user_uid, liked_by):
        post_ref = db_firebase.collection("posts").document(post_id)
        if user_uid in liked_by:
            post_ref.update({
                "likes": firestore.Increment(-1),
                "liked_by": firestore.ArrayRemove([user_uid])
            })
        else:
            post_ref.update({
                "likes": firestore.Increment(1),
                "liked_by": firestore.ArrayUnion([user_uid])
            })
        
    def delete_post(self, post_id):
        try:
            post_ref = db_firebase.collection("posts").document(post_id)
            post_ref.delete()
            st.success("Post excluído com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Error ao tentar excluir o post")

    def get_avatar_url(self, user_id):
        try:
            usuario_ref = db_firebase.collection("usuarios").document(user_id)
            usuario = usuario_ref.get()

            if usuario.exists:
                dados_usuario = usuario.to_dict()
                avatar_url = dados_usuario.get("avatar_url")
                return avatar_url
            else:
                return None
        except Exception as e:
            st.error(f"Error ao carregar o avatar: {e}")
            return None

    def render(self):
        if "user" not in st.session_state or not st.session_state.get("usuario_cadastrado", False):
            st.warning("Por favor, faça o login antes de postar.")
            st.session_state.usuario_cadastrado = False
            st.rerun()
            return
        
        user_uid = st.session_state.get("user", {}).get("uid", "")
        
        usuario_ref = db_firebase.collection("usuarios").document(user_uid)
        usuario = usuario_ref.get()

        if usuario.exists:
            dados_usuario = usuario.to_dict()
            nickname = dados_usuario.get("nickname", "Nickname não disponível")
        else:
            st.error("Usuário não encontrado!")
            return

        st.title("🔥 Comunidade FURIA")

        if "tweet_content" not in st.session_state:
            st.session_state["tweet_content"] = ""

        with st.form("post_form"):
            tweet_content = st.text_area("Fala como se sente, furioso!", key="tweet_content", max_chars=500)
            
            submitted = st.form_submit_button("Post")
            if submitted and tweet_content.strip(): 
                try:
                    self.set_post(user_uid, tweet_content)
                    st.success("Postado!")
                except Exception as e:
                    st.error(f"Error ao postar. Por favor, tente novamente. {e}")

        st.subheader("🚀 Feed da rapaziada")

        posts = self.get_posts()

        if not posts:
            st.warning("Ainda não há posts por aqui. Seja o primeiro a postar algo!")

        with st.spinner("Carregando posts..."):
            cols = st.columns(2) 
            for i, post in enumerate(posts):
                post_data = post.to_dict()
                post_id = post.id
                liked_by = post_data.get("liked_by", [])
                is_liked = user_uid in liked_by
                try:
                    author_nickname = nickname if post_data["user_id"] == user_uid else "Usuário"
                    avatar_url = self.get_avatar_url(post_data["user_id"])

                    post_time = post_data["timestamp"].strftime('%d/%m/%Y %H:%M')

                    col = cols[i % 2]
                    with col:
                        with st.container():
                            liked_text = "💔 Descurtir" if is_liked else "❤️ Curtir"
                            is_author = post_data["user_id"] == user_uid

                            if avatar_url:
                                st.markdown(f"""
                                    <div style="
                                        background-color: #262730;
                                        padding: 15px;
                                        border-radius: 12px;
                                        margin-bottom: 20px;
                                        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
                                        display: flex;
                                        flex-direction: column;
                                        justify-content: flex-start;
                                        min-height: 250px; /* Garante que todos os posts tenham uma altura mínima */
                                        max-height: 600px; /* Limita a altura máxima */
                                        overflow-y: auto; /* Rolagem quando o conteúdo for muito grande */
                                    ">
                                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                                            <img src="{avatar_url}" alt="Avatar" style="width: 40px; height: 40px; border-radius: 50%; margin-right: 10px;">
                                            <h4 style="color:white;">{author_nickname}</h4>
                                        </div>
                                        <p style='color:gray; margin-bottom: 10px;'>📅 {post_time}</p>
                                        <p style="color:white; word-wrap: break-word; flex-grow: 1; margin-bottom: 10px;">
                                            {post_data['content']}
                                        </p>
                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                                            <p style="color:white; font-weight: bold;">❤️ {post_data['likes']} curtidas</p>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                avatar_url = DEFAULT_AVATAR

                            col1, col2 = st.columns([2, 1])
                            with col1:
                                if st.button(liked_text, key=f"like_{post_id}", help="Clique para curtir/descurtir", use_container_width=True):
                                    self.toggle_like(post_id, user_uid, liked_by)
                                    st.rerun()

                            with col2:
                                if is_author:
                                    if st.button("❌ Excluir", key=f"delete_{post_id}", help="Clique para excluir o post", use_container_width=True):
                                        self.delete_post(post_id)

                            st.markdown("---")
                except Exception as e:
                        st.error(f"Error ao carregar posts. Estamos trabalhando para corrigir isso.")
