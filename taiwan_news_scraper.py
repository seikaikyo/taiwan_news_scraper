from flask import Flask, render_template
import feedparser
from bs4 import BeautifulSoup
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

# RSS feeds for different categories
RSS_FEEDS = {
    '國際': 'https://news.ltn.com.tw/rss/world.xml',
    '生活': 'https://news.ltn.com.tw/rss/life.xml',
    '財經': 'https://news.ltn.com.tw/rss/business.xml',
    '即時': 'https://news.ltn.com.tw/rss/all.xml',
    '政治': 'https://news.ltn.com.tw/rss/politics.xml',
    '社會': 'https://news.ltn.com.tw/rss/society.xml',
    '評論': 'https://news.ltn.com.tw/rss/opinion.xml',
    '體育': 'https://news.ltn.com.tw/rss/sports.xml',
    '娛樂': 'https://news.ltn.com.tw/rss/entertainment.xml',
    '地方': 'https://news.ltn.com.tw/rss/local.xml',
    '蒐奇': 'https://news.ltn.com.tw/rss/novelty.xml'
}

# Keywords for excluding or lowering rank
EXCLUDE_KEYWORDS = {"中國", "中英對照讀新聞", "中職",
                    "民眾黨", "濕身", "郭台銘", "廖大乙", "侯友宜", "中醫", "民俗", "證券行情表", "證券表格", "浪浪", "環保團體", "自由說新聞", "官我什麼事", "謠言終結站", "飆股幕後", "首長早餐會"}
LOWER_RANK_KEYWORDS = {"降低排序的關鍵詞1", "降低排序的關鍵詞2"}

# Categories to hide
HIDE_CATEGORIES = {"即時", "政治", "娛樂", "體育", "地方", "評論"}

NEWS_PER_FEED = 30  # Maximum number of news items per feed
MAX_PARAGRAPHS = 2  # Maximum number of paragraphs to include in the summary


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

            filtered_article = {
                'title': article.get('title', ''),
                'link': article.get('link', ''),
                'description': description
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
