from flask import Flask, render_template, url_for, request
from data import queries
import math
from dotenv import load_dotenv

from data.init_db import init_db, create_schema

load_dotenv()
app = Flask('codecool_series')
SHOWS_PER_PAGE = 15
SHOWN_PAGE_NUMBERS = 5  # should be odd to have a symmetry in pagination


@app.route('/')
def index():
    shows = queries.get_shows()
    return render_template('index.html', shows=shows)


@app.route('/design')
def design():
    return render_template('design.html')


@app.route('/shows/')
@app.route('/shows/<int:page_number>')
@app.route('/shows/most-rated/')
@app.route('/shows/most-rated/<int:page_number>')
@app.route('/shows/order-by-<order_by>/')
@app.route('/shows/order-by-<order_by>-<order>/')
@app.route('/shows/order-by-<order_by>/<int:page_number>')
@app.route('/shows/order-by-<order_by>-<order>/<int:page_number>')
def shows(page_number=1, order_by="rating", order="DESC"):
    count = queries.get_show_count()
    pages_count = math.ceil(count[0]['count'] / SHOWS_PER_PAGE)
    shows = queries.get_shows_limited(order_by, order, SHOWS_PER_PAGE, (page_number - 1) * SHOWS_PER_PAGE)

    shown_pages_start = int(page_number - ((SHOWN_PAGE_NUMBERS - 1) / 2))
    shown_pages_end = int(page_number + ((SHOWN_PAGE_NUMBERS - 1) / 2))
    if shown_pages_start < 1:
        shown_pages_start = 1
        shown_pages_end = SHOWN_PAGE_NUMBERS
    elif shown_pages_end > pages_count:
        shown_pages_start = pages_count - SHOWN_PAGE_NUMBERS + 1
        shown_pages_end = pages_count

    return render_template(
        'shows.html',
        shows=shows,
        pages_count=pages_count,
        page_number=page_number,
        shown_pages_start=shown_pages_start,
        shown_pages_end=shown_pages_end,
        order_by=order_by,
        order=order
    )


@app.route('/show/<int:id>/')
def show(id):
    show = queries.get_show(id)
    characters = queries.get_show_characters(id, 3)
    seasons = queries.get_show_seasons(id)

    # format character names
    show['characters_str'] = \
        ', '.join([character['name'] for character in characters])

    # getting trailer id from URL to embed video
    show['trailer_id'] = \
        show['trailer'][show['trailer'].find('=') + 1:] if show['trailer'] else ''

    # format runtime
    hours, minutes = divmod(show['runtime'], 60)
    runtime_str = (str(hours) + 'h ' if hours else '') + (str(minutes) + 'min' if minutes else '')
    show['runtime_str'] = runtime_str

    return render_template('show.html', show=show, seasons=seasons)


@app.route('/show/<int:id>/actors')
def show_actors(id):
    show = queries.get_show(id)
    actors = queries.get_show_characters(id, 100)
    return render_template('actors.html', show=show, actors=actors)


@app.route('/actor/<int:id>/', methods=['GET', 'POST'])
def actor_form(id):
    if request.method == "POST":
        name = request.form['name']
        queries.update_actor(id, name)
    actor = queries.get_actor(id)
    return render_template('actor.html', actor=actor)


def main():
    app.run(debug=False)


'''
1. Create a page, together with a new route /shows/{show_id}/actors, that shows the actors names from the show with the 
   played character name, sorted by actor name.

2. Add a button with text “Shorten first name” at the end of the page, after clicking this button, without page reload, 
   change displayed actors' real names to contain the first letter of first name, then dot and surname afterwards. 
   Example: Anthony Daniels should be changed to A. Daniels

3. Add a link to the actor name that will open a new page with a form that will enable to change the actor name. After 
   submitting the form the name should be changed in the database.
'''

if __name__ == '__main__':
    main()
