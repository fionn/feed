feed
----

Make RSS and Atom feeds for static websites.

The `Feed` class takes a URL and grabs all the `main.ul.li` elements. Assuming they contain `a`s, it gets the link and checks for publishing time and a snippet and turns this into a feed.

The point is to be able to quickly generate (and regenerate) feeds without thinking about it.

Basic usage could look something like the example below.

```python
from feed import Feed

def main() -> None:
    url = "https://example.com/blog/"

    feed_kwargs = {"title": "Some Blog",
                   "url": url,
                   "name": "My name",
                   "email": "blog@example.com",
                   "generator": "generator name",
                   "generator_version": "0.1.2.3",
                   "logo": "https://example.com/logo.png",
                   "icon": "https://example.com/icon.png",
                   "description": "Blog blog",
                   "language": "en"
                  }

    feed = Feed(**feed_kwargs)
    feed.add_from_blog(url)

    print(feed.atom().decode())
    print(feed.rss().decode())

    feed.atom_file()
    feed.rss_file()

if __name__ == "__main__":
    main()
```
