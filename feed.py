import datetime
from typing import Union, List
import textwrap
import requests
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup, Tag

class Blog:

    def __init__(self, url: str) -> None:
        self.url = url
        self._html = self._get(url)
        self._soup = BeautifulSoup(self._html, features="lxml")
        self.articles = self._articles()
        self.title = self._soup.title.string

    @staticmethod
    def _get(url: str) -> bytes:
        response = requests.get(url)
        response.raise_for_status()
        return response.content

    def _articles(self) -> List["Article"]:
        articles = []
        for element in self._soup.main.ul.find_all("li"):
            article_url = self.url + element.a.get("href")
            articles.append(Article(element.a.string, article_url))
        return articles

class Article:

    JOINERY = "\n" + " " * 6

    def __init__(self, title: str, url: str) -> None:
        self.url = url
        self.title = title
        self._html = self._get(url)
        self._soup = BeautifulSoup(self._html, features="lxml")
        self.snippet = self._soup.body.article.p.text.strip() + " […]"

    @staticmethod
    def _get(url: str) -> bytes:
        response = requests.get(url)
        response.raise_for_status()
        return response.content

    @staticmethod
    def _content_wrapper(tag: Tag) -> str:
        wrapper = textwrap.TextWrapper(width=80, break_long_words=False,
                                       break_on_hyphens=False)
        if tag.name in {"pre", "code"}:
            return str(tag)
        lines = [Article.JOINERY.join(wrapper.wrap(line))
                 for line in str(tag).splitlines()]
        return Article.JOINERY.join(lines)

    @property
    def date(self) -> Union[datetime.datetime, None]:
        try:
            soup_time = self._soup.time.get("datetime")
        except AttributeError:
            return None
        date = datetime.datetime.fromisoformat(soup_time)
        return date.replace(tzinfo=datetime.timezone.utc)

    @property
    def description(self) -> Union[None, str]:
        try:
            return self._soup.find(attrs={"name": "description"}).get("content")
        except AttributeError:
            return None

    @property
    def content(self) -> str:
        content = []
        initial_p = self._soup.body.article.find("p")
        content.append(self._content_wrapper(initial_p))
        for tag in initial_p.next_siblings:
            if isinstance(tag, Tag) \
               and tag.name not in {"link", "script", "object"}:
                content.append(self._content_wrapper(tag))
        return self.JOINERY.join(content) + self.JOINERY

class Feed:

    def __init__(self, url: str, name: str, email: str, title: str = None,
                 generator: str = None, generator_version: str = None,
                 logo: str = None, icon: str = None, description: str = None,
                 language: str = None) -> None:
        self.name = name
        self.email = email

        self.fg = FeedGenerator()
        self.fg.id(url + "feed.atom")
        self.fg.link(href=url + "feed.xml", rel="self")
        self.fg.link(href=url, rel="alternate")
        self.fg.author(name=name, email=email)
        self.fg.contributor(name=name, email=email)
        self.fg.managingEditor(email)
        self.fg.webMaster(email)

        self.fg.title(title)
        self.fg.generator(generator=generator, version=generator_version)
        self.fg.logo(logo)
        self.fg.icon(icon)
        self.fg.description(description)
        self.fg.language(language)

    def add(self, article: Article) -> None:
        feed_entry = self.fg.add_entry()
        feed_entry.id(article.url)
        feed_entry.title(article.title)
        feed_entry.link(href=article.url)
        feed_entry.guid(guid=article.url, permalink=True)
        feed_entry.author(name=self.name, email=self.email)
        feed_entry.summary(article.description or article.snippet)
        feed_entry.content(content=article.content, type="CDATA")
        feed_entry.published(article.date)
        if article.date:
            feed_entry.published(article.date)
            feed_entry.updated(article.date)
        else:
            epoch = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
            feed_entry.published(epoch)
            feed_entry.updated(epoch)

    def add_from_blog(self, url: str) -> None:
        blog = Blog(url)
        if not self.fg.title():
            self.fg.title(blog.title)
        for article in blog.articles:
            self.add(article)

    def atom(self) -> bytes:
        return self.fg.atom_str(pretty=True)

    def rss(self) -> bytes:
        return self.fg.rss_str(pretty=True)

    def atom_file(self, filename: str = "feed.atom") -> None:
        self.fg.atom_file(filename, pretty=True)

    def rss_file(self, filename: str = "feed.xml") -> None:
        self.fg.rss_file(filename, pretty=True)
