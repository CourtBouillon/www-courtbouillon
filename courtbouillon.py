import os
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path

from flask import Flask, render_template
from flask_frozen import Freezer
from pygments import formatters, highlight, lexers

app = Flask(__name__, static_url_path='/static')


def list_articles():
    articles = {}
    with os.scandir(path='templates/articles') as articles_files:
        for article in articles_files:
            if article.is_file() and not article.name.startswith('_'):
                content = (
                    Path('templates/articles') / article.name).read_text()
                introduction = (
                    content.split('<header>')[1].split('</header>')[0])
                title = introduction.split('<h2>')[1].split('</h2>')[0]
                description = introduction.split('</aside>')[1]
                date = format_datetime(datetime.strptime(
                    introduction.split('datetime="')[1].split('"')[0],
                    '%Y-%m-%d'))
                article_id = article.name.split('-')[0]
                articles[article_id] = {
                    'filename': article.name.split('.html')[0],
                    'introduction': introduction.replace('h2>', 'h3>'),
                    'title': title,
                    'description': description,
                    'date': date}
    return dict(sorted(articles.items(), reverse=True))


@app.route('/')
@app.route('/<page>.html')
def page(page='index'):
    return render_template(f'{page}.html.jinja2')


@app.route('/blog.html')
@app.route('/blog/<article>.html')
def blog(article=None):
    if article is not None:
        return render_template(f'articles/{article}.html.jinja2')
    return render_template('blog.html.jinja2', articles=list_articles())


@app.route('/blog.rss')
def rss():
    return render_template('blog.rss.jinja2', articles=list_articles())


@app.template_filter()
def pygmentize(filename):
    content = (Path('templates/snippets') / filename).read_text()
    return highlight(
        content, lexers.get_lexer_for_filename(filename),
        formatters.HtmlFormatter())


@app.cli.command('freeze')
def freeze():
    Freezer(app).freeze()
