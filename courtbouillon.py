import re
import textwrap
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path

from flask import Flask, Response, render_template
from flask_frozen import Freezer
from pygments import formatters, highlight, lexers

app = Flask(__name__)
TEMPLATES = Path(app.root_path) / app.template_folder
TAGS = {
    'release': 'Release',
    'life-of-courtbouillon': 'Life of Courtbouillon',
    'opinion': 'Opinion',
    'technique': 'Technique',
}

def list_articles():
    articles_path = TEMPLATES / 'articles'
    if not articles_path.is_dir():
        return {}

    articles = {}
    for article in articles_path.iterdir():
        if not article.is_file() or article.name.startswith('_'):
            continue
        content = (articles_path / article.name).read_text()
        header = re.search('<header>(.*)</header>', content, re.S)[1]
        title = re.search('<h1>(.*)</h1>', header, re.S)[1]
        description = re.search('</aside>(.*)', header, re.S)[1]
        date_string = re.search('datetime="(.*?)"', header)[1]
        tags = re.findall("tag='(.*?)'", header)
        image = None
        if match := re.search('<img .*src="(.*?)"', content):
            image = match[1]
            if image.startswith('{'):
                image = re.search("filename='(.*?)'", image)[1]
        date = datetime.strptime(date_string, '%Y-%m-%d')
        rss_date = format_datetime(date)
        article_date = date.strftime('%B %d, %Y')
        article_id = article.name.split('-')[0]
        articles[article_id] = {
            'filename': article.name.split('.html')[0],
            'title': title,
            'description': description,
            'rss_date': rss_date,
            'article_date': article_date,
            'date': date,
            'image': image,
            'article_tags': tags,
        }

    return dict(sorted(articles.items(), reverse=True))


@app.route('/blog-articles/')
@app.route('/blog-articles/<int:year>/')
@app.route('/blog-articles/<tag>/')
@app.route('/blog/<article>/')
def blog(article=None, year=None, tag=None):
    if article is not None:
        article_object = list_articles()[article.split('-')[0]]
        template = f'articles/{article}.html.jinja2'
        return render_template(template, page='article', tags=TAGS, **article_object)
    articles = list_articles()
    all_years = {article['date'].year for article in articles.values()}
    if tag:
        articles = {
            key: article for key, article in articles.items()
            if tag in article['article_tags']}
    else:
        if year:
            years = {year}
        else:
            now = datetime.now()
            years = {now.year, now.year - 1} if now.month <= 6 else {now.year}
        articles = {
            key: article for key, article in articles.items()
            if article['date'].year in years}
    return render_template(
        'blog.html.jinja2', articles=articles, tags=TAGS, years=all_years)


@app.route('/')
@app.route('/<path:page>/')
def page(page='index'):
    return render_template(f'{page}.html.jinja2', page=page)


@app.route('/blog.rss')
def rss():
    rss = render_template('blog.rss.jinja2', articles=list_articles(), tags=TAGS)
    return Response(rss, mimetype='application/rss+xml')


@app.route('/robots.txt')
def robots():
    return Response('User-agent: *\nDisallow:', mimetype='text/plain')


@app.template_filter()
def pygmentize(filename):
    content = (TEMPLATES / 'snippets' / filename).read_text()
    lexer = lexers.get_lexer_for_filename(filename)
    return highlight(content, lexer, formatters.HtmlFormatter(linenos=True))


@app.template_filter()
def pygmentize_string(string, extension):
    lexer = lexers.get_lexer_by_name(extension)
    return highlight(string, lexer, formatters.HtmlFormatter(linenos=True))


@app.template_filter()
def dedent(string):
    return textwrap.dedent(string)


freezer = Freezer(app)

@app.cli.command('freeze')
def freeze():
    freezer.freeze()


@freezer.register_generator
def page():
    yield {'page': 'message'}
