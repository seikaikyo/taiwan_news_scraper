from flask import Flask, render_template
import feedparser
from bs4 import BeautifulSoup
from flask_bootstrap import Bootstrap
from datetime import datetime

app = Flask(__name__)
Bootstrap(app)

# RSS feeds for different categories
RSS_FEEDS = {
    '即時': 'https://news.ltn.com.tw/rss/all.xml',
    '國際': 'https://news.ltn.com.tw/rss/world.xml',
    '財經': 'https://news.ltn.com.tw/rss/business.xml',
    '生活': 'https://news.ltn.com.tw/rss/life.xml',
    '社會': 'https://news.ltn.com.tw/rss/society.xml',
    '地方': 'https://news.ltn.com.tw/rss/local.xml',
    '蒐奇': 'https://news.ltn.com.tw/rss/novelty.xml',
    '娛樂': 'https://news.ltn.com.tw/rss/entertainment.xml',
    '評論': 'https://news.ltn.com.tw/rss/opinion.xml',
    '政治': 'https://news.ltn.com.tw/rss/politics.xml',
    '體育': 'https://news.ltn.com.tw/rss/sports.xml'
}

# Keywords for excluding or lowering rank
EXCLUDE_KEYWORDS = {"中國", "中英對照讀新聞", "中職", "民眾黨", "濕身", "郭台銘",
                    "廖大乙", "侯友宜", "中醫", "民俗", "證券行情表", "證券表格",
                    "浪浪", "環保團體", "自由說新聞", "官我什麼事", "謠言終結站",
                    "飆股幕後", "首長早餐會", "王力宏", "Makiyo", "弦子", "吳鳳",
                    "彭佳慧", "MLB", "金廈", "如懿傳", "黃國昌", "館長", "李玟",
                    "亞錦", "張秀卿", "股市", "柯志恩", "周子瑜", "聯賽", "游淑慧",
                    "王世堅", "高嘉瑜", "林心如", "柯文哲", "亞運", "男籃", "演藝圈"}
LOWER_RANK_KEYWORDS = {"降低排序的關鍵詞1", "降低排序的關鍵詞2"}

# Categories to hide
HIDE_CATEGORIES = {"政治", "娛樂", "體育", "地方", "評論", "蒐奇"}

NEWS_PER_FEED = 30  # Maximum number of news items per feed
MAX_PARAGRAPHS = 3  # Maximum number of paragraphs to include in the summary


@app.route('/')
def get_news():
    all_articles = {}
    for category, url in RSS_FEEDS.items():
        # Skip categories that we want to hide
        if category in HIDE_CATEGORIES:
            continue

        feed = feedparser.parse(url)
        filtered_articles = []
        for article in feed['entries']:
            # Skip articles that contain excluded keywords
            if any(keyword in article.title for keyword in EXCLUDE_KEYWORDS):
                continue

            # Parse description HTML with BeautifulSoup
            soup = BeautifulSoup(article.get('summary', ''), 'html.parser')

            # Limit the description to the first MAX_PARAGRAPHS paragraphs
            description = '\n'.join(str(p)
                                    for p in soup.find_all('p')[:MAX_PARAGRAPHS])

            # Get the published time of the article
            published_time = datetime.strptime(article.get(
                'published', ''), '%a, %d %b %Y %H:%M:%S %z')
            formatted_published_time = published_time.strftime(
                '%Y-%m-%d %H:%M')

            filtered_article = {
                'title': article.get('title', ''),
                'link': article.get('link', ''),
                'description': description,
                'published_time': formatted_published_time
            }

            # If the article contains a lower-rank keyword, add it to the end
            if any(keyword in filtered_article['title'] for keyword in LOWER_RANK_KEYWORDS):
                filtered_articles.append(filtered_article)
            else:
                # Otherwise, add it to the front
                filtered_articles.insert(0, filtered_article)

        # Limit the articles to NEWS_PER_FEED
        all_articles[category] = filtered_articles[:NEWS_PER_FEED]

    # Sort the articles by published time in descending order
    for category, articles in all_articles.items():
        all_articles[category] = sorted(articles, key=lambda x: datetime.strptime(
            x['published_time'], '%Y-%m-%d %H:%M'), reverse=True)

    return render_template('news_template.html', articles=all_articles)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
