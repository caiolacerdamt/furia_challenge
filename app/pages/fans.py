import streamlit as st
from app.firebase.firebase_admin import db_firebase

class TelaBase:
    def render(self):
        raise NotImplementedError()

class InstagramPostsRenderer(TelaBase):
    def __init__(self, max_posts=12):
        self.db = db_firebase
        self.collection_path = "instagram_posts/furiagg/posts"
        self.max_posts = max_posts

    def fetch_posts_from_firestore(self):
        posts_ref = self.db.collection(self.collection_path)
        posts = posts_ref.stream()
        post_list = []
        for post in posts:
            data = post.to_dict()
            data['id'] = post.id
            post_list.append(data)

        sorted_posts = sorted(post_list, key=lambda x: x.get('timestamp', 0), reverse=True)
        return sorted_posts[: self.max_posts]

    def render(self):
        posts = self.fetch_posts_from_firestore()
        if not posts:
            st.info("Nenhum post recente encontrado.")
            return
        st.markdown("<h2 style='color:#f9f3f3;'>✨ Destaques do Instagram ✨</h2>", unsafe_allow_html=True)
        st.markdown(
            "<div style='margin-bottom:20px;'>"
            "<a href='https://www.instagram.com/furiagg/' target='_blank' "
            "style='display:inline-block; background:#262730; color:#fff; padding:10px 20px; "
            "border-radius:8px; font-weight:bold; text-decoration:none;'>"
            "📸 Siga a FURIA no Instagram</a>"
            "</div>", unsafe_allow_html=True
        )

        st.markdown("""
            <style>
                .card-container {
                    background: #1f2228;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 6px 12px rgba(0,0,0,0.3);
                    transition: transform 0.2s;
                }
                .card-container:hover {
                    transform: scale(1.03);
                }
                .card-image {
                    width: 100%;
                    height: 0;
                    padding-bottom: 100%; /* Aspect ratio 1:1 */
                    position: relative;
                }
                .card-image img {
                    position: absolute;
                    top: 0; left: 0;
                    width: 100%; height: 100%;
                    object-fit: cover;
                }
                .card-overlay {
                    position: absolute;
                    bottom: 0;
                    width: 100%;
                    padding: 8px;
                    background: linear-gradient(0deg, rgba(0,0,0,0.85), transparent);
                    color: #fff;
                    font-size: 16px;
                    font-weight: 600;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
                    max-height: 70%;
                    overflow: hidden;
                }
                .card-link a {
                    color: #3897f0;
                    font-weight: bold;
                    text-decoration: none;
                }
            </style>
        """, unsafe_allow_html=True)

        cols_per_row = 4
        for i in range(0, len(posts), cols_per_row):
            cols = st.columns(cols_per_row)
            for col, post in zip(cols, posts[i:i+cols_per_row]):
                caption = post.get('caption', '')

                col.markdown(f"""
                    <div class="card-container">
                        <div class="card-image">
                            <img src="{post['image_url']}" alt="Post Instagram" />
                            <div class="card-overlay">{caption[:100] + ('...' if len(caption) > 100 else '')}</div>
                        </div>
                        <div class="card-link" style="padding:12px 8px; background:#111418;">
                            <a href="{post['post_url']}" target="_blank">🔗 Ver no Instagram</a>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

