from datetime import datetime
from email.utils import format_datetime
from pathlib import Path

from flask import Flask, Response, render_template
from flask_frozen import Freezer
from pygments import formatters, highlight, lexers

app = Flask(__name__)
TEMPLATES = Path(app.root_path) / app.template_folder


def list_articles():
    articles_path = TEMPLATES / 'articles'
    if not articles_path.is_dir():
        return {}

    articles = {}
    for article in articles_path.iterdir():
        if not article.is_file() or article.name.startswith('_'):
            continue
        content = (articles_path / article.name).read_text()
        introduction = content.split('<header>')[1].split('</header>')[0]
        title = introduction.split('<h2>')[1].split('</h2>')[0]
        description = introduction.split('</aside>')[1]
        date_string = introduction.split('datetime="')[1].split('"')[0]
        date = format_datetime(datetime.strptime(date_string, '%Y-%m-%d'))
        article_id = article.name.split('-')[0]
        articles[article_id] = {
            'filename': article.name.split('.html')[0],
            'introduction': introduction.replace('h2>', 'h3>'),
            'title': title,
            'description': description,
            'date': date,
        }

    return dict(sorted(articles.items(), reverse=True))


@app.route('/blog-articles/')
@app.route('/blog/<article>/')
def blog(article=None):
    if article is not None:
        article_object = list_articles()[article.split('-')[0]]
        template = f'articles/{article}.html.jinja2'
        return render_template(template, page='article', **article_object)
    return render_template('blog.html.jinja2', articles=list_articles())


@app.route('/')
@app.route('/<path:page>/')
def page(page='index'):
    return render_template(f'{page}.html.jinja2', page=page)


@app.route('/blog.rss')
def rss():
    rss = render_template('blog.rss.jinja2', articles=list_articles())
    return Response(rss, mimetype='application/rss+xml')


@app.route('/robots.txt')
def robots():
    return Response('User-agent: *\nDisallow:', mimetype='text/plain')


@app.template_filter()
def pygmentize(filename):
    content = (TEMPLATES / 'snippets' / filename).read_text()
    lexer = lexers.get_lexer_for_filename(filename)
    return highlight(content, lexer, formatters.HtmlFormatter())


@app.cli.command('freeze')
def freeze():
    Freezer(app).freeze()
