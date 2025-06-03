#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from pathlib import Path

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 定数
DOCS_DIR = Path(__file__).parent.parent / "docs"

def create_sample_index():
    """サンプルのindex.htmlを作成"""
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
    
    <div class="article">
        <h2><a href="https://xtrend.nikkei.com/atcl/contents/casestudy/00012/00187/">日本生命「強すぎる営業部隊」　法人・個人の壁なし、職域攻略の妙</a></h2>
        <div class="date">2025/06/03</div>
        <div class="description">日本生命保険相互会社。その原動力となっているのが、約4万7000人もの人でモンモス体制を築く「強い営業組織」だ。いわゆる個人や企業と対面する営業職員の「フロント」部と、商品企画や社員教育、営業支援を行う「ミドル・バック」部の間の連携が、まるで潤滑油のように循環しやすい企業カルチャーが、ここ数年で定着したことが大きい。</div>
        <a href="https://xtrend.nikkei.com/atcl/contents/casestudy/00012/00187/">続きを読む</a>
    </div>
    
    <div class="footer">
        <p>このRSSフィードは非公式なものです。コンテンツの著作権は日経BP社に帰属します。</p>
        <p>&copy; 2025 Nikkei Business Publications, Inc. All Rights Reserved.</p>
    </div>
</body>
</html>
"""
    
    index_file = DOCS_DIR / "index.html"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    logger.info(f"サンプルのindex.htmlを作成しました: {index_file}")

def create_sample_feed():
    """サンプルのfeed.xmlを作成"""
    xml = """<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/">
<channel>
  <title>日経クロストレンド 最新記事</title>
  <link>https://xtrend.nikkei.com/</link>
  <description>日経クロストレンドの最新記事を配信するRSSフィード</description>
  <language>ja</language>
  <lastBuildDate>Tue, 03 Jun 2025 01:00:00 GMT</lastBuildDate>
  <generator>Nikkei XTrend RSS Generator</generator>
  
  <item>
    <title>日本生命「強すぎる営業部隊」　法人・個人の壁なし、職域攻略の妙</title>
    <link>https://xtrend.nikkei.com/atcl/contents/casestudy/00012/00187/</link>
    <description>日本生命保険相互会社。その原動力となっているのが、約4万7000人もの人でモンモス体制を築く「強い営業組織」だ。いわゆる個人や企業と対面する営業職員の「フロント」部と、商品企画や社員教育、営業支援を行う「ミドル・バック」部の間の連携が、まるで潤滑油のように循環しやすい企業カルチャーが、ここ数年で定着したことが大きい。</description>
    <content:encoded><![CDATA[
<h1>日本生命「強すぎる営業部隊」　法人・個人の壁なし、職域攻略の妙</h1>

<p><strong>公開日</strong>: 2025.06.03</p>

<p><strong>カテゴリ</strong>: ヒットを支える「断トツ営業戦略」</p>

<p>日本生命保険相互会社。その原動力となっているのが、約4万7000人もの人でモンモス体制を築く「強い営業組織」だ。</p>

<p>いわゆる個人や企業と対面する営業職員の「フロント」部と、商品企画や社員教育、営業支援を行う「ミドル・バック」部の間の連携が、まるで潤滑油のように循環しやすい企業カルチャーが、ここ数年で定着したことが大きい。しかも、リーテイル部門とホールセール部門のそれぞれで、改革が進んだのだ。</p>

<p>「例えば、リーテイルとホールセールの連携が進む中で、リーテイル部門側には、ホールセールのカウンターパートナー役となる組織として法人職域業務部という組織があり、そこがミドル・バックの窓口となる。そして最終的に、リーテイル部門のフロント側営業職員がどう動くべきかのプランに落とし込んでいる」（鈴木氏）</p>

<p>営業支援を目的に、営業推進部や営業企画部といった組織を置くのは珍しいことではない。ただ日本生命保険の場合、複雑な意思決定プロセスが円滑に進むように役割分担がより細分化され、しかも全体最適化されて機能するのが特徴だ。</p>

<p>例えるなら、アメーバに近いかもしれない。大きくなるために分裂を繰り返して、それぞれが自律的に動きながら、全体としては1つの細胞として同じ意思を共有する。必要であれば再び結合することもある。よく似ているだろう。</p>

<p>その思いが、新規事業開発の推進力につながったのです。</p>

<p>どこでも、誰でも、簡単に</p>

<p><strong>著者</strong>: 日経クロストレンド</p>

<p><strong>元記事</strong>: <a href="https://xtrend.nikkei.com/atcl/contents/casestudy/00012/00187/">https://xtrend.nikkei.com/atcl/contents/casestudy/00012/00187/</a></p>
    ]]></content:encoded>
    <pubDate>Mon, 03 Jun 2025 00:00:00 GMT</pubDate>
    <dc:creator>日経クロストレンド</dc:creator>
    <guid>https://xtrend.nikkei.com/atcl/contents/casestudy/00012/00187/</guid>
  </item>
  
</channel>
</rss>
"""
    
    feed_file = DOCS_DIR / "feed.xml"
    with open(feed_file, 'w', encoding='utf-8') as f:
        f.write(xml)
    
    logger.info(f"サンプルのfeed.xmlを作成しました: {feed_file}")

def main():
    """メイン処理"""
    try:
        # docsディレクトリが存在することを確認
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        
        # サンプルファイルを作成
        create_sample_index()
        create_sample_feed()
        
        logger.info("サンプルファイルの作成が完了しました")
        return 0
        
    except Exception as e:
        logger.error(f"サンプルファイル作成中にエラーが発生しました: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
