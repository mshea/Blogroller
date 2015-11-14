# This script will take in a number of RSS feeds and
# aggregate them into a single list sorted by date.
# This is the sourcecode that powers the website
# http://dndblogs.com.
# This source code is released under a creative commons
# attribution, non-commercial, share alike license.
# Please attribute it to Mike Shea with the URL
# http://mikeshea.net.
#
# This script requires the feedparser and PyRSS2Gen
# modules. I have included both of these modules in the
# Github repository.


import feedparser
import PyRSS2Gen
from string import Template
import time
import datetime
import unicodedata
import re

feed_list = [
"http://feeds.com/index.atom",
"http://feeds.com/index.atom",
"http://feeds.com/index.atom",
"http://feeds.com/index.atom",
,
]

rssoutputfile = "/path/to/your/rss/output/index.xml"
htmloutputfile = "/path/to/your/html/output/index.html"
errorfile = "/path/to/your/errors/errors.txt"

## Edit below with your own HTML output.
html_header_template = Template("""<!DOCTYPE html>
<html>
<head>
<title>D&D Blogs: Dungeons and Dragons blog articles from across the web.</title>
<link rel="stylesheet" type="text/css" href="style.css">
<link rel="alternate" type="application/rss+xml" title="DnDBlogs" href="index.xml">
<meta name="viewport" content="user-scalable=yes, width=device-width" />
</head>
<body>
<div class="container">
<header>
<h1>D&D Blogs</h1>
<p>Latest Dungeons and Dragons articles from across the web. Last updated on $currenttime.</p>
</header>
<section>
$itemhtmlblocks
</section>
<aside>
<p><a href="http://twitter.com/dndblogs">twitter</a> - <a href="http://4eblogs.com/index.xml">rss</a></p>
<h2>Blog List</h2>
<ul>
$bloglist
</ul>
<p>Want to get your site on DnDBlogs? Write useful D&amp;D focused articles weekly for two months and then <a href="mailto:mike@mikeshea.net">send me a note</a>.</p>
<h2>Support This Site!</h2>
<ul>
<li><a href="http://slyflourish.com/book">Dungeon Master Tips</a>
<li><a href="http://slyflourish.com/lazydm">The Lazy Dungeon Master</a>
<li><a href="https://www.amazon.com/Dungeons-Dragons-Starter-Set-Fundamentals/dp/0786965592/ref=as_sl_pc_ss_til?tag=slyflourish-20&linkCode=w01&linkId=GCSMYQB22BV5VWEK&creativeASIN=0786965592">D&D Starter Set</a>
<li><a href="https://www.amazon.com/Players-Handbook-Dungeons-Dragons-Wizards/dp/0786965606/ref=as_sl_pc_ss_til?tag=slyflourish-20&linkCode=w01&linkId=BRA3KRG36IN5H3YC&creativeASIN=0786965606">D&D Player's Handbook</a>
<li><a href="https://www.amazon.com/Monster-Manual-Core-Rulebook-Wizards/dp/0786965614/ref=as_sl_pc_ss_til?tag=slyflourish-20&linkCode=w01&linkId=3IOCHKLMVDQGHXG4&creativeASIN=0786965614">D&D Monster Manual</a>
<li><a href="https://www.amazon.com/Dungeon-Masters-Guide-Core-Rulebook/dp/0786965622/ref=as_sl_pc_ss_til?tag=slyflourish-20&linkCode=w01&linkId=5UQGH4F76XZIJEU2&creativeASIN=0786965622">D&D Dungeon Master's Guide</a>
<li><a href="https://www.amazon.com/Princes-Apocalypse-D-Accessory/dp/0786965789/ref=as_sl_pc_ss_til?tag=slyflourish-20&linkCode=w01&linkId=CF3Z5JECJQLAXLVD&creativeASIN=0786965789">Princes of the Apocalypse</a>
<li><a href="https://www.amazon.com/13th-Age-RPG-Core-Book/dp/190898340X/ref=as_sl_pc_ss_til?tag=slyflourish-20&linkCode=w01&linkId=Y6T7MYBU2KTFI2JO&creativeASIN=190898340X">13th Age Core Book</a>
<li><a href="https://www.amazon.com/Evil-Hat-Productions-Fate-Accelerated/dp/1613170475/ref=as_sl_pc_ss_til?tag=slyflourish-20&linkCode=w01&linkId=IJM45MGO4Q6LKL27&creativeASIN=1613170475">Fate Accelerated</a>
<li><a href="https://www.amazon.com/Pathfinder-Flip-Mat-Basic-Terrain-Multi-Pack/dp/1601255578/ref=as_sl_pc_ss_til?tag=slyflourish-20&linkCode=w01&linkId=3RFYCPBFLK5IGOOT&creativeASIN=1601255578">Pathfinder Flip Mats</a>
<li><a href="http://www.shareasale.com/r.cfm?B=752497&U=1142287&M=60247&urllink=">105 Dice Pack</a>
</ul>
</aside>
<footer></footer>
</div>""")

html_item_template = Template("""<article>
<h2><a href="$item_url">$item_title</a></h2>
<p>Posted $item_date: $item_summary - <a href="$item_url">more</a></p>
</article>
""")

html_links_template = Template("""<li><a href="$sitelink">$sitetitle</a>\n""")


def clean_summary(summary):
	return re.sub("<[^>]+>|\S{20}|\n|\r", "", summary)


def parse_feed(feed):
	print "Fetching " + feed
	feed_data = feedparser.parse(feed)
	items = []
	try:
		site_info = [feed_data.feed.title, feed_data.feed.link]
		error = ""
	except:
		error = "Feed " + feed + " failed to validate."
		return "", items, error
	for item in feed_data.entries:
		item.title = feed_data.feed.title + ": " + item.title
		items.append(item)
	return site_info, items, error


def aggregate_items(feed_list):
	total_items = []
	total_site_info = []
	errors = []
	for feed in feed_list:
		site_info, items, error = parse_feed(feed)
		total_site_info.append(site_info)
		errors.append(error)
		for item in items:
			total_items.append([item.published_parsed, item])
	total_items.sort()
	total_items.reverse()
	total_items = [item[1] for item in total_items]
	return total_site_info, total_items, errors


def generate_html(items, site_info, htmloutputfile):
	items_html_block = ""
	site_info_html_block = ""
	currenttime = time.strftime("%d %b %Y %I:%m %p", time.localtime(time.time()))
	for item in items:
		try:
			summary = clean_summary(item.summary)[0:250]
		except:
			summary = ""
		items_html_block += html_item_template.substitute(
			item_url = item.link,
			item_title = item.title,
			item_date = time.strftime("%d %b %Y",items[0].published_parsed),
			item_summary = summary
			)
	for site_data in site_info:
		site_info_html_block += html_links_template.substitute(
			sitetitle = site_data[0],
			sitelink = site_data[1]
			)
	html_output = html_header_template.substitute(
		itemhtmlblocks = items_html_block,
		bloglist = site_info_html_block,
		currenttime = currenttime
		)

	with open(htmloutputfile, "w") as outputfile:
		outputfile.write(html_output.encode('ascii','ignore'))


def generate_xml(items, rssoutputfile):
	rss_items = []
	for item in items:
		rss_date = datetime.datetime.fromtimestamp(time.mktime(item.published_parsed))
		try:
			summary = clean_summary(item.summary)[0:250]
		except:
			summary = ""
		rss_items.extend([(PyRSS2Gen.RSSItem(
							title = item.title,
							link = item.link,
							description=summary,
							guid = item.link,
							pubDate = rss_date
							))])
	rss = PyRSS2Gen.RSS2 (
		title = "DnDBlogs.com",
		link = "http://dndblogs.com",
		description = "New posts from the top Dungeons and Dragons blogs.",
		lastBuildDate = datetime.datetime.now(),
		items = rss_items
	)
	rss.write_xml(open(rssoutputfile, "w"))


def main():
	site_info, items, errors = aggregate_items(feed_list)
	generate_html(items[0:30], site_info, htmloutputfile)
	generate_xml(items[0:30], rssoutputfile)
	with open(errorfile,"w") as f:
		f.write("\n".join(errors))


if __name__ == "__main__":
    main()