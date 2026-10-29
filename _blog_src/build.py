#!/usr/bin/env python3
"""Builds the blog from _blog_src/posts.json and one body file per post.
Run from the repo root:  python3 _blog_src/build.py
Writes: blog/index.html, blog/<slug>/index.html, blog/feed.xml, sitemap.xml,
        and redirect stubs under writing/ for the old URLs."""
import json, html, re, datetime, pathlib
from email.utils import format_datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "_blog_src"
SITE = "https://salma71.github.io"
AUTHOR = "Salma Elmasry"
# Email subscribe: paste the form action URL from your email service here.
# Leave empty to show the RSS link only.
SUBSCRIBE_ACTION = ""
SUBSCRIBE_FIELD = "email"
MEDIUM = "https://salmaeng71.medium.com/"
OLD_SLUGS = ["governed-ai-analyst"]

posts = json.loads((SRC / "posts.json").read_text())
posts.sort(key=lambda p: p["date"], reverse=True)
e = html.escape

def d(p): return datetime.date.fromisoformat(p["date"])
def pretty(p): return d(p).strftime("%B %Y")
def body(p): return (SRC / f'{p["slug"]}.html').read_text()
def minutes(p): return max(1, round(len(re.sub(r"<[^>]+>", " ", body(p)).split()) / 220))
def url(p): return f"/blog/{p['slug']}/"

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
 '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
 '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wdth,wght@12..96,75..100,400..800&amp;family=Source+Serif+4:opsz,wght@8..60,400..700&amp;display=swap">\n'
 '<link rel="stylesheet" href="/blog/blog.css">\n'
 '<link rel="alternate" type="application/rss+xml" title="Blog by Salma Elmasry" href="/blog/feed.xml">')

HEADER = '''<a class="skip" href="#main">Skip to content</a>
<div class="page">
  <header class="bar">
    <a class="name" href="/">Salma Elmasry</a>
    <nav aria-label="Primary">
      <a href="/#work">Work</a>
      <a href="/#experience">Experience</a>
      <a href="/blog/" aria-current="page">Blog</a>
      <a href="/#contact">Contact</a>
    </nav>
  </header>
</div>'''
FOOTER = '<footer>&copy; 2026 Salma Elmasry &middot; <a href="/blog/feed.xml">RSS</a></footer>'

def subscribe(compact=False):
    if SUBSCRIBE_ACTION:
        form = (f'<form class="sub-form" action="{e(SUBSCRIBE_ACTION)}" method="post" target="_blank">'
                f'<label for="sub-email{"-c" if compact else ""}">Email address</label>'
                f'<div class="sub-row"><input id="sub-email{"-c" if compact else ""}" type="email" name="{SUBSCRIBE_FIELD}" required autocomplete="email" placeholder="you@example.com">'
                '<button type="submit">Subscribe</button></div></form>')
        note = 'New posts by email. No other mail, and you can leave any time.'
    else:
        form = ''
        note = 'Follow new posts with any feed reader.'
    return (f'<section class="sub" aria-labelledby="sub-h{"-c" if compact else ""}">'
            f'<h2 id="sub-h{"-c" if compact else ""}">Get new posts</h2><p>{note}</p>{form}'
            '<p class="sub-alt"><a href="/blog/feed.xml">RSS feed</a></p></section>')

def related(cur):
    others = [p for p in posts if p["slug"] != cur["slug"]]
    shared = lambda p: len(set(p["tags"]) & set(cur["tags"]))
    others.sort(key=lambda p: (shared(p), p["date"]), reverse=True)
    others = others[:4]
    if others:
        items = "".join(f'<li><a href="{url(p)}">{e(p["title"])}</a><span>{pretty(p)}</span></li>' for p in others)
        inner = f'<ul>{items}</ul>'
    else:
        inner = (f'<p>More posts are on the way. Older technical notes are on '
                 f'<a href="{MEDIUM}" rel="me noopener">Medium</a>.</p>')
    return f'<aside class="side" aria-labelledby="rel-h"><h2 id="rel-h">Related posts</h2>{inner}</aside>'

def write(path, text):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)

def head(title, desc, canon, og_type="website", extra=""):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(title.replace(' | ' + AUTHOR, ''))}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
{extra}{FONTS}
</head>'''

# ---- posts
for p in posts:
    canon = SITE + url(p)
    ld = json.dumps({
        "@context": "https://schema.org", "@type": "BlogPosting",
        "headline": p["title"], "description": p["description"],
        "datePublished": p["date"], "dateModified": p["date"],
        "keywords": ", ".join(p["tags"]),
        "author": {"@type": "Person", "name": AUTHOR, "url": SITE + "/"},
        "mainEntityOfPage": canon, "image": SITE + "/og-image.png",
        "isPartOf": {"@type": "Blog", "name": "Blog by " + AUTHOR, "url": SITE + "/blog/"}
    }, indent=2)
    extra = (f'<meta name="author" content="{AUTHOR}">\n'
             f'<meta property="article:author" content="{AUTHOR}">\n'
             f'<meta property="article:published_time" content="{p["date"]}">\n'
             f'<script type="application/ld+json">\n{ld}\n</script>\n')
    tags = "".join(f'<li>{e(t)}</li>' for t in p["tags"])
    page = f'''{head(p["title"] + " | " + AUTHOR, p["description"], canon, "article", extra)}
<body>
{HEADER}
<div class="post-wrap">
<main id="main" class="post-main">
<article>
  <p class="crumb"><a href="/blog/">Blog</a></p>
  <h1>{e(p["title"])}</h1>
  <p class="dek">{e(p["dek"])}</p>
  <p class="meta">{AUTHOR} &middot; <time datetime="{p["date"]}">{pretty(p)}</time> &middot; {minutes(p)} min read</p>
  <ul class="tags" aria-label="Topics">{tags}</ul>

{body(p)}

  <p class="back"><a href="/blog/">All posts</a></p>
</article>
<div class="sub-bottom">{subscribe(True)}</div>
</main>
<div class="side-col">
{related(p)}
{subscribe()}
</div>
</div>
{FOOTER}
</body>
</html>
'''
    write(f"blog/{p['slug']}/index.html", page)

# ---- index
rows = "".join(f'''    <li>
      <a class="t" href="{url(p)}">{e(p["title"])}</a>
      <p>{e(p["dek"])}</p>
      <div class="d">{pretty(p)} &middot; {minutes(p)} min read</div>
    </li>
''' for p in posts)
idx = f'''{head("Blog | " + AUTHOR, "Posts by Salma Elmasry on data platforms, governed AI analytics, and the cost of running a warehouse.", SITE + "/blog/")}
<body>
{HEADER}
<main id="main" class="narrow">
  <h1>Blog</h1>
  <p class="dek">Notes on data platforms, governed AI analytics, and what a warehouse costs to run.</p>
  <ul class="list">
{rows}  </ul>
  <p class="more">Older technical notes are on <a href="{MEDIUM}" rel="me noopener">Medium</a>.</p>
  {subscribe()}
</main>
{FOOTER}
</body>
</html>
'''
write("blog/index.html", idx)

# ---- feed
now = format_datetime(datetime.datetime.now(datetime.timezone.utc))
items = ""
for p in posts:
    pub = format_datetime(datetime.datetime.combine(d(p), datetime.time(12), datetime.timezone.utc))
    items += (f'<item><title>{e(p["title"])}</title><link>{SITE}{url(p)}</link>'
              f'<guid isPermaLink="true">{SITE}{url(p)}</guid><pubDate>{pub}</pubDate>'
              f'<description>{e(p["description"])}</description></item>\n')
write("blog/feed.xml", f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<title>Blog by {AUTHOR}</title><link>{SITE}/blog/</link>
<description>Notes on data platforms, governed AI analytics, and what a warehouse costs to run.</description>
<language>en-us</language><lastBuildDate>{now}</lastBuildDate>
{items}</channel></rss>
''')

# ---- sitemap
latest = posts[0]["date"]
urls = [(SITE + "/", latest, "1.0"), (SITE + "/blog/", latest, "0.7")] + \
       [(SITE + url(p), p["date"], "0.8") for p in posts]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      "".join(f'  <url><loc>{u}</loc><lastmod>{m}</lastmod><priority>{pr}</priority></url>\n' for u, m, pr in urls) + '</urlset>\n')

# ---- old /writing/ URLs -> new
def stub(old, new):
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Moved | {AUTHOR}</title>
<link rel="canonical" href="{SITE}{new}"><meta http-equiv="refresh" content="0; url={new}">
<meta name="robots" content="noindex"></head>
<body><p>This page moved to <a href="{new}">{SITE}{new}</a>.</p></body></html>
'''
write("writing/index.html", stub("/writing/", "/blog/"))
for s in OLD_SLUGS:
    write(f"writing/{s}/index.html", stub(f"/writing/{s}/", f"/blog/{s}/"))
print("built", len(posts), "post(s)")
