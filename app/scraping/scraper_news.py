from playwright.sync_api import sync_playwright
from app.firebase.firebase_admin import db_firebase
import requests
from dotenv import load_dotenv
import os
from utils.utils import upload_to_imgur

load_dotenv()

api_token = os.getenv("APIFY_API_TOKEN")
dataset_id = os.getenv("DATASET_ID")

class InstagramApifyScraper:
    def __init__(self, dataset_id: str, api_token: str):
        self.dataset_id = dataset_id
        self.api_token = api_token
        self.db = db_firebase
        self.task_url = f"https://api.apify.com/v2/datasets/{self.dataset_id}/items?token={self.api_token}"

    def fetch_posts(self, max_posts: int = 6):
        res = requests.get(self.task_url)
        res.raise_for_status()
        data = res.json()
        posts = data
        return posts

    def save_to_firebase(self, posts):
        path = "instagram_posts/furiagg/posts"
        collection_ref = self.db.collection(path)

        for index, post in enumerate(posts):
            try:
                imgur_url = upload_to_imgur(post.get("displayUrl", ""))
            except Exception as e:
                print(f"Erro ao fazer upload da imagem {index}: {e}")
                imgur_url = None

            post_data = {
                "caption": post.get("caption", ""),
                "image_url": imgur_url,
                "post_url": post.get("url"),
                "timestamp": post.get("timestamp")
            }

            collection_ref.document(str(index)).set(post_data)

        print(f"Salvo {len(posts)} posts no Firebase com sucesso!")

if __name__ == "__main__":

    scraper = InstagramApifyScraper(dataset_id=dataset_id, api_token=api_token)
    posts = scraper.fetch_posts(max_posts=6)
    scraper.save_to_firebase(posts)
