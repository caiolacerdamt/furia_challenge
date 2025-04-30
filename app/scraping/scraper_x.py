from playwright.sync_api import sync_playwright
from app.firebase.firebase_admin import db_firebase
from utils.utils import upload_to_imgur
from dotenv import load_dotenv
import os
import time

load_dotenv()

class TwitterScraper:
    def __init__(self, user_handle: str):
        self.user_handle = user_handle
        self.db = db_firebase

    def fetch_tweets(self, max_tweets: int = 8):
        tweets_data = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(f"https://twitter.com/{self.user_handle}")
            time.sleep(5)

            for _ in range(3):
                page.mouse.wheel(0, 3000)
                time.sleep(2)

            tweets = page.locator("article").all()[:max_tweets]

            for tweet in tweets:
                try:
                    content = tweet.locator("div[lang]").inner_text()
                    time_element = tweet.locator("time")
                    date = time_element.get_attribute("datetime")

                    tweet_href = time_element.locator("xpath=ancestor::a").get_attribute("href")
                    tweet_url = f"https://twitter.com{tweet_href}" if tweet_href else ""
                    
                    image_urls = [
                        img.get_attribute("src")
                        for img in tweet.locator("img").all()
                        if img.get_attribute("src") and (
                            "pbs.twimg.com/media" in img.get_attribute("src") or
                            "pbs.twimg.com/ext_tw_video_thumb" in img.get_attribute("src")
                        )
                    ]

                    tweets_data.append({
                        "content": content,
                        "date": date,
                        "image_urls": image_urls,
                        "url": tweet_url
                    })

                except Exception as e:
                    print("Erro ao extrair tweet:", e)

            browser.close()

        return tweets_data

    def save_to_firebase(self, tweets):
        path = "twitter_posts/furiagg/posts"
        collection_ref = self.db.collection(path)

        for index, tweet in enumerate(tweets):
            try:
                imgur_urls = [upload_to_imgur(url) for url in tweet["image_urls"]]
            except Exception as e:
                print(f"Erro ao fazer upload das imagens do tweet {index}: {e}")
                imgur_urls = []

            post_data = {
                "content": tweet.get("content", ""),
                "date": tweet.get("date", ""),
                "imgur_images": imgur_urls,
                "url": tweet.get("url", "")
            }

            collection_ref.document(str(index)).set(post_data)

        print(f"Salvo {len(tweets)} tweets no Firebase com sucesso!")

if __name__ == "__main__":
    scraper = TwitterScraper(user_handle="FURIA")
    tweets = scraper.fetch_tweets(max_tweets=8)
    scraper.save_to_firebase(tweets)
