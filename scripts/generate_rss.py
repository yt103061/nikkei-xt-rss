#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import logging
import datetime
import re
from pathlib import Path
from xml.sax.saxutils import escape

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 定数
ARTICLES_DIR = Path(__file__).parent.parent / "data" / "articles"
IMAGES_DIR = Path(__file__).parent.parent / "data" / "images"
DOCS_DIR = Path(__file__).parent.parent / "docs"
RSS_FILE = DOCS_DIR / "feed.xml"
INDEX_FILE = DOCS_DIR / "index.html"

# 日付フォーマット
RSS_DATE_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"

def generate_rss_feed():
    """RSSフィードを生成"""
    logger.info("RSSフィード生成を開始します")
    
    try:
        # 記事データを読み込み
        articles_data_file = Path(__file__).parent.parent / "data" / "articles_data.json"
        if not articles_data_file.exists():
            logger.error("記事データファイルが見つかりません")
            return False
        
        with open(articles_data_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        # 記事を日付順にソート（新しい順）
        articles.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        # RSSフィードのXMLを構築
        rss_xml = generate_rss_xml(articles)
        
        # RSSファイルに保存
        with open(RSS_FILE, 'w', encoding='utf-8') as f:
            f.write(rss_xml)
        
        # インデックスページも生成
        generate_index_html(articles)
        
        logger.info(f"RSSフィードを生成しました: {RSS_FILE}")
        return True
        
    except Exception as e:
        logger.error(f"RSSフィード生成中にエラーが発生しました: {e}")
        return False

def generate_rss_xml(articles):
    """
    記事リストからRSS XMLを生成
    
    Args:
        articles (list): 記事情報のリスト
        
    Returns:
        str: RSS XML文字列
    """
    # 現在時刻（GMT）
    now = datetime.datetime.now(datetime.timezone.utc)
    build_date = now.strftime(RSS_DATE_FORMAT)
    
    # RSSヘッダー
    rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/">
<channel>
  <title>日経クロストレンド 最新記事</title>
  <link>https://xtrend.nikkei.com/</link>
  <description>日経クロストレンドの最新記事を配信するRSSフィード</description>
  <language>ja</language>
  <lastBuildDate>{build_date}</lastBuildDate>
  <generator>Nikkei XTrend RSS Generator</generator>
"""
    
    # 記事アイテム
    for article in articles:
        # エラーがある記事はスキップ
        if 'error' in article:
            continue
        
        # 記事のMarkdownファイルを読み込み
        md_file = ARTICLES_DIR / f"{article['id']}.md"
        if not md_file.exists():
            continue
        
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # 公開日をRSS形式に変換
        pub_date = ""
        if 'date' in article:
            try:
                date_parts = article['date'].split('.')
                if len(date_parts) == 3:
                    year, month, day = date_parts
                    dt = datetime.datetime(int(year), int(month), int(day), tzinfo=datetime.timezone.utc)
                    pub_date = dt.strftime(RSS_DATE_FORMAT)
            except Exception as e:
                logger.warning(f"日付変換エラー: {e}")
                pub_date = now.strftime(RSS_DATE_FORMAT)
        else:
            pub_date = now.strftime(RSS_DATE_FORMAT)
        
        # 記事内容をHTML形式に変換
        content_html = markdown_to_html(md_content, article)
        
        # 記事の説明（先頭の数行）
        description = extract_description(md_content)
        
        # 著者情報
        author_match = re.search(r'\*\*著者\*\*: (.*)', md_content)
        author = author_match.group(1) if author_match else "日経クロストレンド"
        
        # RSSアイテムを追加
        rss += f"""  
  <item>
    <title>{escape(article['title'])}</title>
    <link>{escape(article['url'])}</link>
    <description>{escape(description)}</description>
    <content:encoded><![CDATA[
{content_html}
    ]]></content:encoded>
    <pubDate>{pub_date}</pubDate>
    <dc:creator>{escape(author)}</dc:creator>
    <guid>{escape(article['url'])}</guid>
  </item>
"""
    
    # RSSフッター
    rss += """  
</channel>
</rss>"""
    
    return rss

def markdown_to_html(md_content, article):
    """
    Markdown形式の記事をHTML形式に変換
    
    Args:
        md_content (str): Markdown形式の記事内容
        article (dict): 記事情報
        
    Returns:
        str: HTML形式の記事内容
    """
    # 簡易的なMarkdown→HTML変換
    # 実際のプロジェクトではmarkdown2やmistune等のライブラリを使うことを推奨
    
    # タイトル（H1）
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', md_content, flags=re.MULTILINE)
    
    # 見出し（H2）
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    
    # 太字
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    
    # 段落
    paragraphs = []
    for line in html.split('\n\n'):
        line = line.strip()
        if line and not line.startswith('<h') and not line.startswith('!['):
            paragraphs.append(f'<p>{line}</p>')
        else:
            paragraphs.append(line)
    
    html = '\n\n'.join(paragraphs)
    
    # 画像
    def replace_image(match):
        alt_text = match.group(1)
        image_path = match.group(2)
        
        # 相対パスを絶対URLに変換（GitHub Pages用）
        if image_path.startswith('/'):
            image_path = image_path[1:]  # 先頭の/を削除
        
        # GitHub Pagesのベースパス
        repo_name = "nikkei-xt-rss"  # リポジトリ名
        base_url = f"https://USERNAME.github.io/{repo_name}"  # USERNAME部分は後で置き換え
        
        image_url = f"{base_url}/{image_path}"
        
        return f'<img src="{image_url}" alt="{alt_text}" />'
    
    html = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_image, html)
    
    # リンク
    html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)
    
    return html

def extract_description(md_content):
    """
    Markdown形式の記事から説明文（先頭の数行）を抽出
    
    Args:
        md_content (str): Markdown形式の記事内容
        
    Returns:
        str: 説明文
    """
    # タイトル行を除外
    content_without_title = re.sub(r'^# .*?$', '', md_content, flags=re.MULTILINE).strip()
    
    # メタデータ行（**公開日**など）を除外
    content_without_meta = re.sub(r'^\*\*.*?\*\*:.*?$', '', content_without_title, flags=re.MULTILINE).strip()
    
    # 先頭の段落を抽出
    paragraphs = content_without_meta.split('\n\n')
    for p in paragraphs:
        p = p.strip()
        if p and len(p) > 10 and not p.startswith('!['):
            # 150文字程度に制限
            if len(p) > 150:
                return p[:147] + '...'
            return p
    
    return "日経クロストレンドの記事"

def generate_index_html(articles):
    """
    記事リストからインデックスHTMLを生成
    
    Args:
        articles (list): 記事情報のリスト
    """
    html = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>日経クロストレンド RSS</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #c00;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .article {
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }
        .article h2 {
            margin-bottom: 5px;
        }
        .article .date {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        .article .description {
            margin-bottom: 10px;
        }
        .article a {
            color: #c00;
            text-decoration: none;
        }
        .article a:hover {
            text-decoration: underline;
        }
        .footer {
            margin-top: 30px;
            color: #666;
            font-size: 0.9em;
        }
        .rss-link {
            display: inline-block;
            margin-top: 20px;
            padding: 10px 15px;
            background-color: #f60;
            color: white;
            border-radius: 4px;
            text-decoration: none;
        }
        .rss-link:hover {
            background-color: #e50;
        }
    </style>
</head>
<body>
    <h1>日経クロストレンド RSS</h1>
    <p>日経クロストレンドの最新記事を配信するRSSフィードです。</p>
    <a href="feed.xml" class="rss-link">RSSフィードを購読</a>
    
    <h2>最新記事</h2>
"""
    
    # 記事リスト
    for article in articles:
        # エラーがある記事はスキップ
        if 'error' in article:
            continue
        
        # 記事のMarkdownファイルを読み込み
        md_file = ARTICLES_DIR / f"{article['id']}.md"
        if not md_file.exists():
            continue
        
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # 説明文を抽出
        description = extract_description(md_content)
        
        # 日付
        date_display = article.get('date', '').replace('.', '/')
        
        html += f"""
    <div class="article">
        <h2><a href="{escape(article['url'])}">{escape(article['title'])}</a></h2>
        <div class="date">{date_display}</div>
        <div class="description">{escape(description)}</div>
        <a href="{escape(article['url'])}">続きを読む</a>
    </div>
"""
    
    # フッター
    current_year = datetime.datetime.now().year
    html += f"""
    <div class="footer">
        <p>このRSSフィードは非公式なものです。コンテンツの著作権は日経BP社に帰属します。</p>
        <p>&copy; {current_year} Nikkei Business Publications, Inc. All Rights Reserved.</p>
    </div>
</body>
</html>
"""
    
    # ファイルに保存
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    
    logger.info(f"インデックスHTMLを生成しました: {INDEX_FILE}")

if __name__ == "__main__":
    generate_rss_feed()
