feed
----

Make RSS and Atom feeds for static websites.

The `feed.Feed` class takes a URL and grabs all the `main.ul.li` elements. Assuming they contain `a`s, it gets the link and checks for content and metadata, like publishing time and description, and turns this into a feed. It exposes methods for producing `feed.xml` and `feed.atom` files.

The point is to be able to quickly generate (and regenerate) feeds without thinking about it.

For basic usage, see [`example.py`](example.py).

