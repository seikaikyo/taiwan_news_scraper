# Taiwan and Japan News Scraper

![Preview](templates/preview.png)
![Preview](templates/nhk_preview.png)

This program collects and aggregates news from various Taiwanese and Japanese news RSS feeds. It enables users to filter news based on specific keywords, adjust the display order of news items, and limit the number of news items displayed per feed. In addition, users can hide news from categories they are not interested in. For any news description that exceeds a height of 300px, it is truncated and a "See More" link is provided for the full description.

## Usage

1. Install the requirements by running `pip install Flask feedparser BeautifulSoup Flask-Bootstrap`.
2. Run `python news_scraper.py`.
3. Open your web browser and go to `http://localhost:5000`.

## Configuration

You can modify the RSS feeds, exclusion keywords, lower-rank keywords, and hide categories in the news_scraper.py file.

# 台湾・日本ニューススクレーパー

このプログラムは、様々な台湾と日本のニュース RSS フィードからニュースを収集し、集約します。ユーザーは、特定のキーワードに基づいてニュースをフィルタリングし、ニュース項目の表示順序を調整し、フィードごとに表示されるニュース項目の数を制限することができます。さらに、ユーザーは興味のないカテゴリーのニュースを非表示にすることができます。また、高さが 300px を超えるニュースの説明は切り捨てられ、「詳細を見る」のリンクが全文の説明のために提供されます。

## 使用方法

1. `pip install Flask feedparser BeautifulSoup Flask-Bootstrap` を実行して、必要なパッケージをインストールします
2. `python news_scraper.py`を実行します。
3. ウェブブラウザを開き、`http://localhost:5000` にアクセスします。

## 設定

`news_scraper.py` ファイルで、RSS フィード、除外キーワード、ランクを下げるキーワード、隠すカテゴリーを変更することができます。

# 台灣新聞擷取器與日本新聞擷取器

此程式從各種台灣與日本新聞 RSS 饋送中收集並聚合新聞。它允許使用者根據特定的關鍵詞過濾新聞、調整新聞項目的顯示順序、並限制每個饋送顯示的新聞項目數量。此外，使用者可以隱藏他們不感興趣的類別的新聞。對於任何超過 300px 高度的新聞描述，它會被截斷，並提供一個 "查看更多" 的連結以供完整描述。

## 使用方法

1. 透過執行 `pip install Flask feedparser BeautifulSoup Flask-Bootstrap` 安裝所需的套件。
2. 執行`python news_scraper.py`
3. 在網頁瀏覽器中打開 `http://localhost:5000`.

## 配置

您可以在 `news_scraper.py` 文件中修改 RSS 饋送、排除關鍵詞、降低排名的關鍵詞和隱藏類別。
