from flask import Flask, render_template
import feedparser
from flask_bootstrap import Bootstrap
from datetime import datetime
from dateutil import parser

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
                    "王世堅", "高嘉瑜", "林心如", "柯文哲", "亞運", "男籃", "演藝圈",
                    "高虹安", "選秀", "TIME", "攻蛋", "台北巨蛋", "盧秀燕", "韓國瑜",
                    "朱立倫", "馬英九", "素食", "小甜甜", "TikTok", "戴愛玲", "何志偉", "客家"}
LOWER_RANK_KEYWORDS = {"羨慕", "詐騙", "熱情"}

# Categories to hide
HIDE_CATEGORIES = {"政治", "娛樂", "體育", "地方", "評論", "蒐奇"}

NEWS_PER_FEED = 30  # Maximum number of news items per feed
MAX_PARAGRAPHS = 3  # Maximum number of paragraphs to include in the summary


@app.route('/')
def get_news():
    all_articles = {}
    seen_articles = set()  # Track seen articles

    for category, url in RSS_FEEDS.items():
        # Skip categories that we want to hide
        if category in HIDE_CATEGORIES:
            continue

        feed = feedparser.parse(url)
        filtered_articles = []
        for entry in feed.entries:
            # Skip articles that contain excluded keywords
            if any(keyword in entry.title for keyword in EXCLUDE_KEYWORDS):
                continue

            title = entry.title
            link = entry.link
            description = entry.description
            published_time = entry.published
            # Get the published time of the article
            published_time = parser.parse(entry.published)

            formatted_published_time = published_time.strftime(
                '%Y-%m-%d %H:%M:%S')

            # Generate unique ID for the article
            article_id = hash((title, description))
            if article_id in seen_articles:  # Skip if the article has been seen before
                continue
            seen_articles.add(article_id)

            filtered_article = {
                'title': title,
                'link': link,
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

    return render_template('news_template.html', articles=all_articles)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
