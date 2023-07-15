from flask import Flask, render_template
import feedparser
from flask_bootstrap import Bootstrap
from datetime import datetime
from dateutil import parser

app = Flask(__name__)
Bootstrap(app)

# RSS feeds for different categories
RSS_FEEDS = {
    '主要ニュース': 'https://www3.nhk.or.jp/rss/news/cat0.xml',
    '社会': 'https://www3.nhk.or.jp/rss/news/cat1.xml',
    '科学.医療': 'https://www3.nhk.or.jp/rss/news/cat3.xml',
    '政治': 'https://www3.nhk.or.jp/rss/news/cat4.xml',
    '経済': 'https://www3.nhk.or.jp/rss/news/cat5.xml',
    '国際': 'https://www3.nhk.or.jp/rss/news/cat6.xml',
    'スポーツ': 'https://www3.nhk.or.jp/rss/news/cat7.xml',
    '文化.エンタメ': 'https://www3.nhk.or.jp/rss/news/cat2.xml',
}

# Keywords for excluding or lowering rank
EXCLUDE_KEYWORDS = {"中國"}
LOWER_RANK_KEYWORDS = {"情熱"}

# Categories to hide
HIDE_CATEGORIES = {"スポーツ", "政治", "文化.エンタメ"}

NEWS_PER_FEED = 10  # Maximum number of news items per feed
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
            title = entry.title.lower()
            link = entry.link
            description = entry.description.lower()
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
            if any(keyword in title for keyword in LOWER_RANK_KEYWORDS):
                filtered_articles.append(filtered_article)
            else:
                # Otherwise, add it to the front
                filtered_articles.insert(0, filtered_article)

        # Limit the articles to NEWS_PER_FEED
        all_articles[category] = filtered_articles[:NEWS_PER_FEED]

    return render_template('nhk_news_template.html', articles=all_articles)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
