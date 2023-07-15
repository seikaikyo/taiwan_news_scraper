import os
import time
import feedparser
import requests
from html import escape
from jinja2 import Environment, FileSystemLoader

# Your RSS feeds
NEWS_FEEDS = {
    "即時": "https://news.ltn.com.tw/rss/all.xml",
    "政治": "https://news.ltn.com.tw/rss/politics.xml",
    "社會": "https://news.ltn.com.tw/rss/society.xml",
    "生活": "https://news.ltn.com.tw/rss/life.xml",
    "評論": "https://news.ltn.com.tw/rss/opinion.xml",
    "國際": "https://news.ltn.com.tw/rss/world.xml",
    "財經": "https://news.ltn.com.tw/rss/business.xml",
    "體育": "https://news.ltn.com.tw/rss/sports.xml",
    "娛樂": "https://news.ltn.com.tw/rss/entertainment.xml",
    "地方": "https://news.ltn.com.tw/rss/local.xml",
    "人物": "https://news.ltn.com.tw/rss/people.xml",
    "蒐奇": "https://news.ltn.com.tw/rss/novelty.xml",
}

# Keywords for excluding or lowering rank
EXCLUDE_KEYWORDS = {"不感興趣的關鍵詞1", "不感興趣的關鍵詞2"}
LOWER_RANK_KEYWORDS = {"降低排序的關鍵詞1", "降低排序的關鍵詞2"}

# Categories to hide
HIDE_CATEGORIES = {"不感興趣的類別"}

NEWS_PER_FEED = 5  # Maximum number of news items per feed
MAX_PARAGRAPHS = 3  # Maximum number of paragraphs to include in the summary


def is_news_item_interesting(news_item):
    """Check if a news item is interesting based on its title and description."""
    for keyword in EXCLUDE_KEYWORDS:
        if keyword in news_item['title'] or keyword in news_item['description']:
            return False
    return True


def sort_news_items(news_items):
    """Sort news items first by whether they contain lower-rank keywords, then by title."""
    def get_rank(item):
        for keyword in LOWER_RANK_KEYWORDS:
            if keyword in item['title'] or keyword in item['description']:
                return (1, item['title'])
        return (0, item['title'])

    return sorted(news_items, key=get_rank)


def fetch_news():
    """Fetch news from RSS feeds."""
    news_data = {}

    for category, feed in NEWS_FEEDS.items():
        if category in HIDE_CATEGORIES:
            continue

        news_list = []
        print(f"Fetching news from {feed}...")
        try:
            d = feedparser.parse(feed)
        except Exception as e:
            print(f"Error parsing feed {feed}: {e}")
            continue
        for entry in d.entries[:NEWS_PER_FEED]:
            news_item = {}
            news_item['link'] = entry.link
            news_item['title'] = escape(entry.title)
            if 'description' in entry:
                paragraphs = entry.description.split("\n\n")[:MAX_PARAGRAPHS]
                news_item['description'] = " ".join(paragraphs)

            if is_news_item_interesting(news_item):
                news_list.append(news_item)
        news_data[category] = sort_news_items(news_list)

    return news_data


def generate_html(news_data):
    """Generate HTML output using a Jinja2 template."""
    file_loader = FileSystemLoader('.')
    env = Environment(loader=file_loader)

    template = env.get_template('news_template.html')

    output = template.render(news=news_data)

    with open("news_output.html", "w") as f:
        f.write(output)


if __name__ == "__main__":
    news_data = fetch_news()
    generate_html(news_data)
