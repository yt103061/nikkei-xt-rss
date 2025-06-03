#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import re
import json
import logging
import datetime
import requests
import hashlib
from pathlib import Path
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 定数
BASE_URL = "https://xtrend.nikkei.com/"
LOGIN_URL = "https://xtrend.nikkei.com/auth/login/"
ARTICLES_DIR = Path(__file__).parent.parent / "data" / "articles"
IMAGES_DIR = Path(__file__).parent.parent / "data" / "images"
DOCS_DIR = Path(__file__).parent.parent / "docs"

# 日付フォーマット
DATE_FORMAT = "%Y.%m.%d"
RSS_DATE_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"

class NikkeiXTrendScraper:
    def __init__(self, headless=True):
        """
        日経クロストレンドスクレイパーの初期化
        
        Args:
            headless (bool): ヘッドレスモードで実行するかどうか
        """
        self.setup_dirs()
        self.driver = self.setup_browser(headless)
        self.articles_data = []
        
    def setup_dirs(self):
        """必要なディレクトリを作成"""
        ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        
    def setup_browser(self, headless=True):
        """
        Seleniumブラウザを設定
        
        Args:
            headless (bool): ヘッドレスモードで実行するかどうか
            
        Returns:
            webdriver: 設定されたWebDriverインスタンス
        """
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)
        return driver
    
    def login(self, username, password):
        """
        日経クロストレンドにログイン
        
        Args:
            username (str): ログイン用ユーザー名/メールアドレス
            password (str): ログイン用パスワード
            
        Returns:
            bool: ログイン成功したかどうか
        """
        try:
            logger.info("ログイン処理を開始します")
            self.driver.get(LOGIN_URL)
            
            # ログインフォームが表示されるまで待機
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "LA7010Form01:LA7010Email"))
            )
            
            # ユーザー名とパスワードを入力
            self.driver.find_element(By.ID, "LA7010Form01:LA7010Email").send_keys(username)
            self.driver.find_element(By.ID, "LA7010Form01:LA7010Password").send_keys(password)
            
            # ログインボタンをクリック
            self.driver.find_element(By.ID, "LA7010Form01:LA7010Login").click()
            
            # ログイン成功の確認（トップページにリダイレクトされるか、ログイン後の要素が表示されるか）
            WebDriverWait(self.driver, 10).until(
                EC.url_contains("xtrend.nikkei.com")
            )
            
            logger.info("ログインに成功しました")
            return True
            
        except Exception as e:
            logger.error(f"ログイン中にエラーが発生しました: {e}")
            return False
    
    def get_yesterday_articles(self):
        """
        昨日公開された記事のURLとタイトルを取得
        
        Returns:
            list: 記事情報のリスト（辞書形式）
        """
        logger.info("昨日公開された記事を検索します")
        
        # トップページにアクセス
        self.driver.get(BASE_URL)
        
        # 昨日の日付を取得（日本時間）
        jst_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        yesterday = jst_now - datetime.timedelta(days=1)
        yesterday_str = yesterday.strftime(DATE_FORMAT)
        logger.info(f"検索対象日: {yesterday_str}")
        
        # ページ内の記事リンクを取得
        articles = []
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        # 記事リンクを探索
        article_links = soup.find_all('a', href=True)
        
        for link in article_links:
            href = link.get('href')
            # 記事URLのパターンに一致するか確認
            if href and re.match(r'/atcl/contents/', href):
                # 完全なURLを構築
                article_url = urljoin(BASE_URL, href)
                
                # タイトルを取得（リンクのテキストまたは親要素内のタイトル要素）
                title = link.get_text(strip=True)
                if not title:
                    title_elem = link.find('h2') or link.find('h3') or link.find('h4')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                
                if title and len(title) > 5:  # 有効なタイトルのみ追加
                    article_id = self.generate_article_id(article_url)
                    articles.append({
                        'id': article_id,
                        'url': article_url,
                        'title': title,
                        'date': yesterday_str
                    })
        
        logger.info(f"{len(articles)}件の記事候補を見つけました")
        
        # 重複を除去
        unique_articles = []
        seen_urls = set()
        
        for article in articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        logger.info(f"重複除去後: {len(unique_articles)}件の記事")
        return unique_articles
    
    def generate_article_id(self, url):
        """URLからユニークなIDを生成"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def fetch_article_content(self, article):
        """
        記事の全文と画像を取得
        
        Args:
            article (dict): 記事情報
            
        Returns:
            dict: 更新された記事情報
        """
        url = article['url']
        logger.info(f"記事「{article['title']}」の内容を取得します: {url}")
        
        try:
            # 記事ページにアクセス
            self.driver.get(url)
            
            # 「続き」ボタンがあれば全てクリック
            self.click_all_continue_buttons()
            
            # 記事本文を取得
            content = self.extract_article_content()
            
            # 記事内の画像をダウンロード
            images = self.download_article_images(article['id'])
            
            # 記事情報を更新
            article['content'] = content
            article['images'] = images
            
            # Markdown形式で保存
            self.save_article_as_markdown(article)
            
            return article
            
        except Exception as e:
            logger.error(f"記事「{article['title']}」の取得中にエラーが発生しました: {e}")
            article['error'] = str(e)
            return article
    
    def click_all_continue_buttons(self):
        """記事ページ内の「続き」ボタンを全てクリック"""
        try:
            # 「続き」ボタンを探して全てクリック
            continue_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), '続き')]")
            
            if continue_buttons:
                logger.info(f"{len(continue_buttons)}個の「続き」ボタンを見つけました")
                
                for i, button in enumerate(continue_buttons):
                    try:
                        # ボタンが表示されるまでスクロール
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(1)  # スクロール後少し待機
                        
                        # ボタンをクリック
                        button.click()
                        logger.info(f"「続き」ボタン {i+1}/{len(continue_buttons)} をクリックしました")
                        time.sleep(2)  # コンテンツ読み込み待機
                    except Exception as e:
                        logger.warning(f"ボタン {i+1} のクリックに失敗しました: {e}")
            else:
                logger.info("「続き」ボタンは見つかりませんでした")
                
            # 他の可能性のあるボタンも探す
            other_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), '続きを見る')]")
            if other_buttons:
                logger.info(f"{len(other_buttons)}個の「続きを見る」ボタンを見つけました")
                for i, button in enumerate(other_buttons):
                    try:
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(1)
                        button.click()
                        logger.info(f"「続きを見る」ボタン {i+1}/{len(other_buttons)} をクリックしました")
                        time.sleep(2)
                    except Exception as e:
                        logger.warning(f"「続きを見る」ボタン {i+1} のクリックに失敗しました: {e}")
                        
        except Exception as e:
            logger.error(f"「続き」ボタンの処理中にエラーが発生しました: {e}")
    
    def extract_article_content(self):
        """
        記事本文を抽出
        
        Returns:
            dict: 記事コンテンツ情報
        """
        # ページが完全に読み込まれるまで少し待機
        time.sleep(3)
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        # 記事タイトル
        title_elem = soup.find('h1')
        title = title_elem.get_text(strip=True) if title_elem else "タイトルなし"
        
        # 公開日
        date_elem = soup.find('time') or soup.find(class_=lambda c: c and 'date' in c.lower())
        publish_date = None
        if date_elem:
            date_text = date_elem.get_text(strip=True)
            # 日付形式を抽出（YYYY.MM.DD または YYYY年MM月DD日）
            date_match = re.search(r'(\d{4})[\.年](\d{1,2})[\.月](\d{1,2})', date_text)
            if date_match:
                year, month, day = date_match.groups()
                publish_date = f"{year}.{month.zfill(2)}.{day.zfill(2)}"
        
        # カテゴリ
        category_elem = soup.find(class_=lambda c: c and ('category' in c.lower() or 'cat' in c.lower()))
        category = category_elem.get_text(strip=True) if category_elem else None
        
        # 記事本文
        # 複数の可能性のあるセレクタを試す
        content_selectors = [
            'article', 
            '.article-body', 
            '.article-content',
            'main',
            '#article-body',
            '.content'
        ]
        
        content_elem = None
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem and len(content_elem.get_text(strip=True)) > 100:
                break
        
        # コンテンツ要素が見つからない場合は、本文らしき段落を全て取得
        if not content_elem:
            paragraphs = soup.find_all('p')
            content_text = "\n\n".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])
        else:
            # 不要な要素を除去（ナビゲーション、広告、関連記事など）
            for elem in content_elem.select('.ad, .advertisement, .related, .share, .social, nav, footer, .footer'):
                elem.decompose()
            
            # 本文テキストを取得
            paragraphs = content_elem.find_all('p')
            if paragraphs:
                content_text = "\n\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
            else:
                content_text = content_elem.get_text(strip=True)
        
        # 著者情報
        author_elem = soup.find(class_=lambda c: c and 'author' in c.lower())
        author = author_elem.get_text(strip=True) if author_elem else "日経クロストレンド"
        
        return {
            'title': title,
            'publish_date': publish_date,
            'category': category,
            'content_text': content_text,
            'author': author
        }
    
    def download_article_images(self, article_id):
        """
        記事内の画像をダウンロード
        
        Args:
            article_id (str): 記事ID
            
        Returns:
            list: ダウンロードした画像情報のリスト
        """
        images = []
        
        try:
            # 記事ページ内の画像要素を取得
            img_elements = self.driver.find_elements(By.TAG_NAME, "img")
            
            # 記事ID用のディレクトリを作成
            article_img_dir = IMAGES_DIR / article_id
            article_img_dir.mkdir(exist_ok=True)
            
            for i, img in enumerate(img_elements):
                try:
                    # 画像URLを取得
                    img_url = img.get_attribute("src")
                    
                    # 有効なURLかつ広告やアイコンでない場合のみ処理
                    if img_url and not self.is_ad_or_icon_image(img_url, img):
                        # 画像ファイル名を生成
                        img_filename = f"{i+1}_{Path(urlparse(img_url).path).name}"
                        if not img_filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                            img_filename += '.jpg'
                        
                        img_path = article_img_dir / img_filename
                        
                        # 画像をダウンロード
                        response = requests.get(img_url, stream=True)
                        if response.status_code == 200:
                            with open(img_path, 'wb') as f:
                                for chunk in response.iter_content(1024):
                                    f.write(chunk)
                            
                            # 画像情報を記録
                            alt_text = img.get_attribute("alt") or ""
                            images.append({
                                'filename': img_filename,
                                'path': str(img_path.relative_to(Path(__file__).parent.parent)),
                                'alt': alt_text
                            })
                            logger.info(f"画像をダウンロードしました: {img_filename}")
                except Exception as e:
                    logger.warning(f"画像 {i+1} のダウンロード中にエラーが発生しました: {e}")
            
            logger.info(f"{len(images)}個の画像をダウンロードしました")
            return images
            
        except Exception as e:
            logger.error(f"画像ダウンロード処理中にエラーが発生しました: {e}")
            return images
    
    def is_ad_or_icon_image(self, img_url, img_element):
        """広告やアイコン画像かどうかを判定"""
        # URLに基づく判定
        if any(keyword in img_url.lower() for keyword in ['ad', 'advertisement', 'banner', 'icon', 'logo', 'button']):
            return True
        
        # サイズに基づく判定（小さすぎる画像はアイコンの可能性）
        try:
            width = img_element.get_attribute("width")
            height = img_element.get_attribute("height")
            if width and height:
                if int(width) < 100 or int(height) < 100:
                    return True
        except:
            pass
        
        return False
    
    def save_article_as_markdown(self, article):
        """
        記事をMarkdown形式で保存
        
        Args:
            article (dict): 記事情報
        """
        article_id = article['id']
        content = article['content']
        images = article.get('images', [])
        
        # Markdownファイルのパス
        md_file = ARTICLES_DIR / f"{article_id}.md"
        
        # Markdownコンテンツを構築
        md_content = f"# {content['title']}\n\n"
        
        if content.get('publish_date'):
            md_content += f"**公開日**: {content['publish_date']}\n\n"
        
        if content.get('category'):
            md_content += f"**カテゴリ**: {content['category']}\n\n"
        
        # 本文
        md_content += content['content_text'] + "\n\n"
        
        # 画像があれば追加
        if images:
            md_content += "## 画像\n\n"
            for img in images:
                md_content += f"![{img['alt']}](/{img['path']})\n\n"
        
        # 著者情報
        if content.get('author'):
            md_content += f"**著者**: {content['author']}\n\n"
        
        # 元記事URL
        md_content += f"**元記事**: [{article['url']}]({article['url']})\n"
        
        # ファイルに保存
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logger.info(f"記事をMarkdown形式で保存しました: {md_file}")
    
    def generate_rss(self):
        """RSSフィードを生成"""
        from generate_rss import generate_rss_feed
        generate_rss_feed()
    
    def close(self):
        """ブラウザを閉じる"""
        if self.driver:
            self.driver.quit()
            logger.info("ブラウザを閉じました")

def main():
    """メイン処理"""
    # 環境変数からログイン情報を取得
    username = os.environ.get('NIKKEI_USERNAME')
    password = os.environ.get('NIKKEI_PASSWORD')
    
    if not username or not password:
        logger.error("環境変数 NIKKEI_USERNAME または NIKKEI_PASSWORD が設定されていません")
        return 1
    
    scraper = None
    try:
        # スクレイパーを初期化
        scraper = NikkeiXTrendScraper(headless=True)
        
        # ログイン
        if not scraper.login(username, password):
            logger.error("ログインに失敗しました")
            return 1
        
        # 昨日公開された記事を取得
        articles = scraper.get_yesterday_articles()
        
        if not articles:
            logger.warning("昨日公開された記事は見つかりませんでした")
            return 0
        
        # 各記事の内容を取得
        for article in articles:
            scraper.fetch_article_content(article)
            time.sleep(2)  # サーバー負荷軽減のため少し待機
        
        # 記事データを保存
        with open(Path(__file__).parent.parent / "data" / "articles_data.json", 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        # RSSフィードを生成
        scraper.generate_rss()
        
        logger.info("処理が完了しました")
        return 0
        
    except Exception as e:
        logger.error(f"処理中にエラーが発生しました: {e}")
        return 1
        
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    exit(main())
