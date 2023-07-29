from flask import Flask, render_template, request, redirect
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
    '国際': 'https://www3.nhk.or.jp/rss/news/cat6.xml',
    '社会': 'https://www3.nhk.or.jp/rss/news/cat1.xml',
    '科学.医療': 'https://www3.nhk.or.jp/rss/news/cat3.xml',
    '文化.エンタメ': 'https://www3.nhk.or.jp/rss/news/cat2.xml',
    '経済': 'https://www3.nhk.or.jp/rss/news/cat5.xml',
    '政治': 'https://www3.nhk.or.jp/rss/news/cat4.xml',
    'スポーツ': 'https://www3.nhk.or.jp/rss/news/cat7.xml',
}  # Japan RSS feeds

# Keywords for excluding or lowering rank
EXCLUDE_KEYWORDS_TAIWAN = {"中國", "中英", "中職", "民眾", "濕身", "台銘", "盈餘", "足球", "志祥",
                           "性侵", "友宜", "中醫", "民俗", "行情", "證券", "虧損", "跌停", "潮牌",
                           "浪浪", "環保", "自由", "謠言", "搶購", "團隊", "國寶", "漲停", "股價",
                           "飆股", "首長", "力宏", "弦子", "吳鳳", "豪門", "節氣", "最美", "股民",
                           "佳慧", "MLB", "金廈", "如懿", "國昌", "館長", "李玟", "嗆聲", "心聲",
                           "亞錦", "秀卿", "股市", "志恩", "子瑜", "聯賽", "淑慧", "彩妝", "幫派",
                           "世堅", "嘉瑜", "心如", "文哲", "亞運", "男籃", "演藝", "高球", "角頭",
                           "虹安", "選秀", "TIME", "秀燕", "國瑜", "MiLB", "漲停", "男神", "微博",
                           "立倫", "英九", "素食", "甜甜", "TikTok", "愛玲", "志偉", "冠軍", "韓劇",
                           "客家", "日職", "539", "油價", "黃金", "廣仲", "大愛", "全裸", "開獎",
                           "裸奔", "詐騙", "捐血", "巨蛋", "奕迅", "導演", "金馬", "豪宅", "退休",
                           "黑吃", "部落", "配息", "除息", "女神", "個展", "職棒", "裸照", "股神",
                           "綠帽", "芭比", "女星", "偶像", "酒後", "OPPO", "男團", "五月", "八點",
                           "圍棋", "女團", "參選", "戲劇", "網友", "搭訕", "主題", "影帝", "恐",
                           "動產", "貸款", "晶圓", "香港", "媒體", "免職", "性別", "開盤", "拌麵",
                           "鹹粥", "重點", "遶境", "港星", "仙", "指數", "暑假", "花博", "哈林",
                           "謊報", "音樂", "分屍", "基進", "盤", "車禍", "小三", "生殖", "高粱",
                           "失蹤", "異動", "占用", "萬安", "凍結", "被騙", "泰達", "攀", "惡煞",
                           "砸車", "酒駕", "告別", "人魚", "身材", "T1", "吸金", "神明", "復燃",
                           "疏導", "宮廟", "遶境", "改槍", "通緝", "家暴", "平等", "LGBT", "吸毒",
                           "販毒", "風華", "溫網", "名譽", "玉女", "娛樂", "能量", "熱銷", "三創",
                           "啟智", "慢飛", "美貌", "氣質", "售價", "入門", "創作", "韓團", "認愛",
                           "NBA", "慈善", "行善", "性平", "內褲", "清涼", "拍攝", "宗憲", "單曲",
                           "櫃買", "人民", "明星", "投資", "球王", "球后", "路透", "錦標", "房價",
                           "強勢", "法拍", "藝人", "歌手", "誘餌", "主持", "主播", "興櫃", "猥褻",
                           "記者", "拍賣", "外資", "羽球", "人為", "性騷", "挑釁", "國民黨", "搜救"
                           "登山", "粉絲", "男友", "爆料", "匿名", "黃牛", "房貸", "利率", "墨鏡",
                           "師鐸", "薪酬", "網美", "毒犯", "定裝", "廣告", "處置", "擲筊", "標售",
                           "價值", "養眼", "球團", "匯率", "訂單", "疑似", "爆發", "操作", "股票",
                           "命喪", "升息", "都更", "糾紛", "獨攀", "暴哭", "碰撞", "棒", "女孩",
                           "善政", "專輯", "仲介", "需求", "盜領", "預告", "劇場", "影集", "萌"}
LOWER_RANK_KEYWORDS_TAIWAN = {"羨慕", "熱情", }

# Categories to hide
HIDE_CATEGORIES_TAIWAN = {"政治", "娛樂", "體育", "地方", "評論", "蒐奇"}

# Keywords for excluding or lowering rank
EXCLUDE_KEYWORDS_JAPAN = {"中國"}
LOWER_RANK_KEYWORDS_JAPAN = {"情熱"}

# Categories to hide
HIDE_CATEGORIES_JAPAN = {""}

NEWS_PER_FEED = 15  # Maximum number of news items per feed
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
            published_time = parser.parse(
                entry.published).strftime('%Y-%m-%d %H:%M:%S')
            rank = 1 if any(keyword in title for keyword in self.lower_rank_keywords) or \
                any(keyword in description for keyword in self.lower_rank_keywords) else 0

            # Skip if we've already seen this article
            if (title, published_time) in self.seen_articles:
                continue
            self.seen_articles.add((title, published_time))

            articles.append({
                'title': title,
                'link': link,
                'description': description,
                'published_time': published_time,
                'rank': rank,
            })

        return sorted(articles, key=lambda x: (x['rank'], x['published_time']), reverse=True)[:NEWS_PER_FEED]

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
        'refresh_interval', default=3600, type=int)
    all_articles_taiwan = news_source_taiwan.get_news()
    all_articles_japan = news_source_japan.get_news()
    return render_template('news_template.html', taiwan_articles=all_articles_taiwan, japan_articles=all_articles_japan, refresh_interval=refresh_interval)


@app.route("/refresh")
def refresh_news():
    # Get the news
    news_source_taiwan.get_news()
    news_source_japan.get_news()
    # Redirect to the home page
    return redirect("/", code=302)


@app.route("/taiwan")
def taiwan_news():
    news = news_source_taiwan.get_news()
    return render_template('taiwan_news_template.html', news=news, title='Taiwan')


@app.route("/japan")
def japan_news():
    news = news_source_japan.get_news()
    return render_template('nhk_news_template.html', news=news, title='Japan')


if __name__ == "__main__":
    app.run(port=5000, debug=False)
