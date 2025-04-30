import streamlit as st
from app.firebase.firebase_admin import db_firebase
from datetime import datetime
import base64
import textwrap

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

        if dt:
            raw = dt.strftime('%I:%M %p · %b %d, %Y')
            time_str = raw.lstrip('0')
        else:
            time_str = str(ts)


        raw = f"""
        <div class="tweet-card">
          <div class="tweet-header">
            <img src="{self.profile_image_b64}" class="profile-img"/>
            <div>
              <strong>FURIA GG</strong> <span class="handle">@furiagg</span><br>
              <a href="{tweet_url}" target="_blank" class="timestamp">{time_str} 🔗</a>
            </div>
          </div>
          <div class="tweet-content">
            <p>{tweet.get('content','')}</p>
          </div>
        </div>
        """
        return textwrap.dedent(raw)

    def render(self):
        st.markdown("<h2 style='color:#f9f3f3;'>✨ Destaques do X✨</h2>", unsafe_allow_html=True)
        st.markdown(
            "<div style='margin-bottom:20px;'>"
            "<a href='https://x.com/furia' target='_blank' "
            "style='display:inline-block; background:#262730; color:#fff; padding:10px 20px; "
            "border-radius:8px; font-weight:bold; text-decoration:none;'>"
            "📸 Siga a FURIA no X</a>"
            "</div>", unsafe_allow_html=True
        )

        tweets = self.fetch_tweets()
        tweets.pop(3)

        if not tweets:
            st.info("Nenhum tweet recente encontrado.")
            return

        css = textwrap.dedent("""
        <style>
        .tweet-grid {
          display: flex;
          flex-wrap: wrap;
          gap: 16px;
        }
        .tweet-card {
          height: 220px;
          box-sizing: border-box;
          padding: 16px;
          border: 1px solid #e1e8ed;
          border-radius: 8px;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          background-color: #262730;
        }
        .tweet-header {
          display: flex;
          align-items: center;
          margin-bottom: 8px;
        }
        .profile-img {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          margin-right: 12px;
        }
        .handle, .timestamp {
          color: #657786;
        }
        .timestamp {
          font-size: 0.9em;
          text-decoration: none;
        }
        .timestamp:hover {
          text-decoration: underline;
        }
        .tweet-content p {
          margin: 0;
          font-size: 1rem;
          line-height: 1.4;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        </style>
        """)
        st.markdown(css, unsafe_allow_html=True)

        columns = st.columns(3)
        for i, tweet in enumerate(tweets):
            col = columns[i % 3]
            with col:
                card_html = self.render_card(tweet)
                st.markdown(card_html, unsafe_allow_html=True)









