import datetime
from typing import Union, List
import requests
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup

class Blog:

    def __init__(self: Blog, url: str) -> None:
        self.url = url
        self._html = self._get(url)
        self._soup = BeautifulSoup(self._html, features="lxml")
        self.articles = self._articles()

    @staticmethod
    def _get(url: str) -> bytes:
        response = requests.get(url)
        response.raise_for_status()
        return response.content

    def _articles(self: Blog) -> List[Article]:
        articles = []
        for element in self._soup.main.ul.find_all("li"):
            article_url = self.url + element.a.get("href")
            articles.append(Article(element.a.string, article_url))
        return articles

class Article:

    def __init__(self: Article, title: str, url: str) -> None:
        self.url = url
        self.title = title
        self._html = self._get(url)
        self._soup = BeautifulSoup(self._html, features="lxml")
        self.description = self._soup.article.p.text.strip() + "…"

    @staticmethod
    def _get(url: str) -> bytes:
        response = requests.get(url)
        response.raise_for_status()
        return response.content

    @property
    def date(self: Article) -> Union[datetime.datetime, None]:
        try:
            date = [int(x) for x in self._soup.time.get("datetime").split("-")]
            return datetime.datetime(*date, tzinfo=datetime.timezone(datetime.timedelta()))
        except AttributeError:
            return None

class Feed:

    def __init__(self: Feed, title: str, url: str, name: str, email: str,
                 generator: str, generator_version: str, logo: str, icon: str,
                 description: str, language: str) -> None:
        self.name = name
        self.email = email
        self.fg = FeedGenerator()
        self.fg.title(title)
        self.fg.id(url + "feed.atom")
        self.fg.author(name=name, email=email)
        self.fg.managingEditor(email)
        self.fg.webMaster(email)
        self.fg.contributor(name=name, email=email)
        self.fg.generator(generator=generator, version=generator_version)
        self.fg.link(href=url + "feed.xml", rel="self")
        self.fg.link(href=url, rel="alternate")
        self.fg.logo(logo)
        self.fg.icon(icon)
        self.fg.description(description)
        self.fg.language(language)

    def add(self: Feed, article: Article) -> None:
        feed_entry = self.fg.add_entry()
        feed_entry.id(article.url)
        feed_entry.title(article.title)
        feed_entry.link(href=article.url)
        feed_entry.guid(guid=article.url, permalink=True)
        feed_entry.author(name=self.name, email=self.email)
        feed_entry.summary(article.description)
        feed_entry.published(article.date)
        if article.date:
            feed_entry.updated(article.date)
        else:
            utc = datetime.timezone(datetime.timedelta())
            epoch = datetime.datetime(1970, 1, 1, tzinfo=utc)
            feed_entry.updated(epoch)

    def add_from_blog(self: Feed, url: str) -> None:
        blog = Blog(url)
        for article in blog.articles:
            self.add(article)

    def atom(self: Feed) -> bytes:
        return self.fg.atom_str(pretty=True)

    def rss(self: Feed) -> bytes:
        return self.fg.rss_str(pretty=True)

    def atom_file(self: Feed, filename: str = "feed.atom") -> None:
        self.fg.atom_file(filename)

    def rss_file(self: Feed, filename: str = "feed.xml") -> None:
        self.fg.rss_file(filename)
