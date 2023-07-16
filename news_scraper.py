from flask import Flask, render_template, request
import feedparser
from flask_bootstrap import Bootstrap
from datetime import datetime
from dateutil import parser
import textwrap

app = Flask(__name__)
Bootstrap(app)

# RSS feeds for different categories
RSS_FEEDS_TAIWAN = {
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
}  # Taiwan RSS feeds

RSS_FEEDS_JAPAN = {
    '主要ニュース': 'https://www3.nhk.or.jp/rss/news/cat0.xml',
    '社会': 'https://www3.nhk.or.jp/rss/news/cat1.xml',
    '科学.医療': 'https://www3.nhk.or.jp/rss/news/cat3.xml',
    '政治': 'https://www3.nhk.or.jp/rss/news/cat4.xml',
    '経済': 'https://www3.nhk.or.jp/rss/news/cat5.xml',
    '国際': 'https://www3.nhk.or.jp/rss/news/cat6.xml',
    'スポーツ': 'https://www3.nhk.or.jp/rss/news/cat7.xml',
    '文化.エンタメ': 'https://www3.nhk.or.jp/rss/news/cat2.xml',
}  # Japan RSS feeds

# Keywords for excluding or lowering rank
EXCLUDE_KEYWORDS_TAIWAN = {"中國", "中英對照讀新聞", "中職", "民眾黨", "濕身", "郭台銘"}
LOWER_RANK_KEYWORDS_TAIWAN = {"羨慕", "熱情"}

# Categories to hide
HIDE_CATEGORIES_TAIWAN = {"政治", "娛樂", "體育", "地方", "評論", "蒐奇"}

# Keywords for excluding or lowering rank
EXCLUDE_KEYWORDS_JAPAN = {"中國"}
LOWER_RANK_KEYWORDS_JAPAN = {"情熱"}

# Categories to hide
HIDE_CATEGORIES_JAPAN = {"スポーツ", "政治", "文化.エンタメ"}

NEWS_PER_FEED = 10  # Maximum number of news items per feed
MAX_PARAGRAPHS = 3  # Maximum number of paragraphs to include in the summary


class NewsSource:
    def __init__(self, feeds, exclude_keywords, lower_rank_keywords, hide_categories, max_paragraphs=3, width=80):
        self.feeds = feeds
        self.exclude_keywords = exclude_keywords
        self.lower_rank_keywords = lower_rank_keywords
        self.hide_categories = hide_categories
        self.max_paragraphs = max_paragraphs
        self.width = width
        self.seen_articles = set()  # Track seen articles

    def get_news(self):
        articles = {}
        for category, url in self.feeds.items():
            if category not in self.hide_categories:
                articles[category] = self._parse_feed(url)
        return articles

    # ... Rest of your methods ...

    def _parse_feed(self, url):
        try:
            feed = feedparser.parse(url)
            return self._process_entries(feed.entries)
        except Exception as e:
            print(f"Failed to parse feed from {url}. Error: {e}")
            return []

    def _process_entries(self, entries):
        articles = []
        for entry in entries:
            # Skip articles that contain excluded keywords in title or description
            if any(keyword in entry.title for keyword in self.exclude_keywords) or \
                    any(keyword in entry.description for keyword in self.exclude_keywords):
                continue

            title = entry.title
            link = entry.link
            description = self.trim_description(entry.description)
            pub_date = parser.parse(entry.published)
            rank = 1 if any(keyword in title for keyword in self.lower_rank_keywords) or \
                any(keyword in description for keyword in self.lower_rank_keywords) else 0

            # Skip if we've already seen this article
            if (title, pub_date) in self.seen_articles:
                continue
            self.seen_articles.add((title, pub_date))

            articles.append({
                'title': title,
                'link': link,
                'description': description,
                'pub_date': pub_date,
                'rank': rank,
            })

        return sorted(articles, key=lambda x: (x['rank'], x['pub_date']), reverse=True)[:NEWS_PER_FEED]

    def trim_description(self, description):
        paragraphs = description.split('\n')
        trimmed = "\n".join(textwrap.fill(p, self.width)
                            for p in paragraphs[:self.max_paragraphs])
        return trimmed


news_source_taiwan = NewsSource(
    RSS_FEEDS_TAIWAN, EXCLUDE_KEYWORDS_TAIWAN, LOWER_RANK_KEYWORDS_TAIWAN, HIDE_CATEGORIES_TAIWAN)
news_source_japan = NewsSource(
    RSS_FEEDS_JAPAN, EXCLUDE_KEYWORDS_JAPAN, LOWER_RANK_KEYWORDS_JAPAN, HIDE_CATEGORIES_JAPAN)


@app.route("/")
def home():
    # Default to 300 seconds (5 minutes)
    refresh_interval = request.args.get(
        'refresh_interval', default=300, type=int)
    all_articles_taiwan = news_source_taiwan.get_news()
    all_articles_japan = news_source_japan.get_news()
    return render_template('news_template.html', taiwan_articles=all_articles_taiwan, japan_articles=all_articles_japan, refresh_interval=refresh_interval)


@app.route("/taiwan")
def taiwan_news():
    news = news_source_taiwan.get_news()
    return render_template('taiwan_news_template.html', news=news, title='Taiwan')


@app.route("/japan")
def japan_news():
    news = news_source_japan.get_news()
    return render_template('nhk_news_template.html', news=news, title='Japan')


if __name__ == "__main__":
    app.run(port=5000, debug=True)
