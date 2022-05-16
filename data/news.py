import feedparser
import investpy
import datetime as dt

def get_forex_news():

    NewsFeed = feedparser.parse("https://th.investing.com/rss/news_1.rss")

    forex_news = []
    for idx, news in enumerate(NewsFeed.entries):

        forex_news.append( {"id": idx + 1, "topic": news['title'], "published": news['published'], "link": news['link'], "image_url": news['links'][0]['href']} )

    return forex_news

# define day interval
day_interval_past = 3
day_interval_future = 7

def get_economic_calendar(symbol):

    day_now = dt.datetime.now()
    day_past = (day_now - dt.timedelta(days=day_interval_past)).strftime("%d/%m/%Y")
    day_future = (day_now + dt.timedelta(days=day_interval_future)).strftime("%d/%m/%Y")

    economic_news = investpy.news.economic_calendar(from_date=str(day_past), to_date=str(day_future))
    economic_news = economic_news[(economic_news['currency'] == symbol.split("/")[0]) | (economic_news['currency'] == symbol.split("/")[1])][["date", "time", "currency", "importance", "event", "actual", "forecast", "previous"]]
    economic_news = economic_news.reset_index(drop=True)
    economic_news_json = economic_news.to_json(orient='records')

    return economic_news_json