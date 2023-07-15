from flask import Flask, render_template
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
EXCLUDE_KEYWORDS_TAIWAN = {"中國", "中英對照讀新聞", "中職", "民眾黨", "濕身", "郭台銘",
                           "廖大乙", "侯友宜", "中醫", "民俗", "證券行情表", "證券表格",
                           "浪浪", "環保團體", "自由說新聞", "官我什麼事", "謠言終結站",
                           "飆股幕後", "首長早餐會", "王力宏", "Makiyo", "弦子", "吳鳳",
                           "彭佳慧", "MLB", "金廈", "如懿傳", "黃國昌", "館長", "李玟",
                           "亞錦", "張秀卿", "股市", "柯志恩", "周子瑜", "聯賽", "游淑慧",
                           "王世堅", "高嘉瑜", "林心如", "柯文哲", "亞運", "男籃", "演藝圈",
                           "高虹安", "選秀", "TIME", "盧秀燕", "韓國瑜",
                           "朱立倫", "馬英九", "素食", "小甜甜", "TikTok", "戴愛玲", "何志偉",
                           "客家", "日職", "539", "國際油價", "黃金", "盧廣仲", "大愛", "全裸",
                           "裸奔", "詐騙", "捐血", "小巨蛋", "陳奕迅"}
LOWER_RANK_KEYWORDS_TAIWAN = {"羨慕", "熱情"}

# Categories to hide
HIDE_CATEGORIES_TAIWAN = {"政治", "娛樂", "體育", "地方", "評論", "蒐奇"}

# Keywords for excluding or lowering rank
EXCLUDE_KEYWORDS_JAPAN = {"中國"}
LOWER_RANK_KEYWORDS_JAPAN = {"情熱"}

# Categories to hide
HIDE_CATEGORIES_JAPAN = {"スポーツ", "政治", "文化.エンタメ"}

NEWS_PER_FEED = 20  # Maximum number of news items per feed
MAX_PARAGRAPHS = 3  # Maximum number of paragraphs to include in the summary


def trim_description(description, max_lines=10, width=80):
    """Trim the description to a certain number of lines."""
    lines = textwrap.wrap(description, width=width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    return ' '.join(lines)


def get_news(RSS_FEEDS, EXCLUDE_KEYWORDS, LOWER_RANK_KEYWORDS, HIDE_CATEGORIES):
    all_articles = {}
    seen_articles = set()  # Track seen articles

    for category, url in RSS_FEEDS.items():
        # Skip categories that we want to hide
        if category in HIDE_CATEGORIES:
            continue

        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries:
            # Skip articles that contain excluded keywords in title or description
            if any(keyword in entry.title for keyword in EXCLUDE_KEYWORDS) or \
                    any(keyword in entry.description for keyword in EXCLUDE_KEYWORDS):
                continue

            title = entry.title
            link = entry.link
            description = trim_description(entry.description)
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

            articles.append({
                'title': title,
                'link': link,
                'description': description,
                'published_time': formatted_published_time
            })

        # Sort the articles by published time from new to old
        articles.sort(
            key=lambda article: article['published_time'], reverse=True)

        # Limit the articles to NEWS_PER_FEED
        all_articles[category] = articles[:NEWS_PER_FEED]
    return all_articles


@app.route('/')
def news():
    all_articles_taiwan = get_news(
        RSS_FEEDS_TAIWAN, EXCLUDE_KEYWORDS_TAIWAN, LOWER_RANK_KEYWORDS_TAIWAN, HIDE_CATEGORIES_TAIWAN)
    all_articles_japan = get_news(
        RSS_FEEDS_JAPAN, EXCLUDE_KEYWORDS_JAPAN, LOWER_RANK_KEYWORDS_JAPAN, HIDE_CATEGORIES_JAPAN)
    return render_template('news_template.html', taiwan_articles=all_articles_taiwan, japan_articles=all_articles_japan)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
