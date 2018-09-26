#!/usr/bin/env python3

from feed import Feed

def main() -> None:
    url = "https://www.example.com/blog/"

    feed_kwargs = {"url": url,
                   "name": "Fionn",
                   "email": "email@example.com",
                   "generator": "generator-name",
                   "generator_version": "0.1.2.3",
                   "logo": "https://www.example.com/logo.png",
                   "icon": "https://www.example.com/icon.png",
                   "description": "Blog blog",
                   "language": "en"
                  }

    feed = Feed(**feed_kwargs)
    feed.add_from_blog(url)

    # Print the Atom feed to stdout
    print(feed.atom().decode())
    # Print the RSS feed to stdout
    print(feed.rss().decode())

    # Produce feed.xml, feed.atom
    feed.atom_file()
    feed.rss_file()

if __name__ == "__main__":
    main()
