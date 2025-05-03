import streamlit as st
import streamlit.components.v1 as components
from app.firebase.firebase_admin import db_firebase
from datetime import datetime
import base64
import os
import textwrap
from app.utils.constants import LINKS_FURIA
import math

class TelaBase:
    def render(self):
        raise NotImplementedError()
    
class SocialLinksRenderer:
    def render(self):
        st.markdown("### 🌍 Todas as Redes Sociais da FURIA")

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

class TweetsRenderer:
    def __init__(
        self,
        profile_image_path: str = 'static/furia_logo.png',
        max_tweets: int = 12,
        collection_path: str = 'twitter_posts/furiagg/posts'
    ):
        self.db = db_firebase
        self.collection_path = collection_path
        self.max_tweets = max_tweets
        self.profile_image_b64 = self._load_image_base64(profile_image_path)

    def _load_image_base64(self, path: str) -> str:
        try:
            with open(path, 'rb') as img_file:
                b64 = base64.b64encode(img_file.read()).decode()
            return f"data:image/png;base64,{b64}"
        except Exception:
            return ''

    def fetch_tweets(self) -> list:
        if not self.db or not self.collection_path:
            return []
        posts = self.db.collection(self.collection_path).stream()
        tweets = []
        for post in posts:
            data = post.to_dict()
            data['id'] = post.id
            tweets.append(data)
        tweets.sort(key=lambda x: x.get('date', 0), reverse=True)
        return tweets[:self.max_tweets]

    def render_card(self, tweet: dict) -> str:
        ts = tweet.get('date')
        tweet_url = tweet.get('url', '')
        dt = None
        if isinstance(ts, (int, float)):
            dt = datetime.fromtimestamp(ts)
        elif isinstance(ts, datetime):
            dt = ts
        elif isinstance(ts, str):
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            except ValueError:
                dt = None

        time_str = dt.strftime('%I:%M %p · %b %d, %Y').lstrip('0') if dt else str(ts)
        content = tweet.get('content', '').replace('<', '&lt;').replace('>', '&gt;')

        return textwrap.dedent(f"""
        <div class="tweet-card">
          <div class="tweet-header">
            <img src="{self.profile_image_b64}" class="profile-img"/>
            <div>
              <a href="{tweet_url}" target="_blank" class="handle">@furiagg</a>
            </div>
            <span class="timestamp">{time_str}</span>
          </div>
          <div class="tweet-content">
            <p>{content}</p>
          </div>
        </div>
        """)

    def render(self):
        st.markdown(
            "<h2 style='color:#f9f3f3; margin-bottom:16px;'>✨ Destaques do X ✨</h2>",
            unsafe_allow_html=True
        )

        tweets = self.fetch_tweets()

        if not tweets:
            st.info("Nenhum tweet recente encontrado.")
            return

        cards_html = "".join(self.render_card(t) for t in tweets)
        html = f"""
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600&display=swap');

          .tweet-grid,
          .tweet-card,
          .tweet-header,
          .tweet-header *,
          .tweet-content,
          .tweet-content p {{
            font-family: 'Source Sans Pro', sans-serif;
          }}

          .tweet-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 24px;
            padding: 0;
            margin: 0;
          }}
          .tweet-card {{
            background-color: #1e1e29;
            padding: 16px;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            box-sizing: border-box;
          }}
          .tweet-header {{
            display: flex;
            align-items: center;
            margin-bottom: 12px;
          }}
          .profile-img {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-right: 12px;
          }}
          .handle {{
            color: #4f8ef7;
            margin-left: 4px;
            text-decoration: none;
            font-weight: 600;
          }}
          .handle:hover {{ text-decoration: underline; }}
          .timestamp {{
            margin-left: auto;
            font-size: 0.75rem;
            color: #8899a6;
          }}
          .tweet-content p {{
            margin: 0;
            font-size: 0.9rem;
            line-height: 1.4;
            color: #d1d5db;
          }}
        </style>
        <div class="tweet-grid">
          {cards_html}
        </div>
        """

        cols_per_row = 3
        num_rows = math.ceil(len(tweets) / cols_per_row)
        approx_row_height = 350 
        total_height = num_rows * approx_row_height

        components.html(
            html,
            height=total_height,
            scrolling=False
        )











