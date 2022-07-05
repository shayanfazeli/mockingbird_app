from flask import Blueprint, render_template

from app.blueprints.word_frequency.forms import WordFrequencyForm
from app.libraries.utilities.plotly import jsonify_plotly_figure
from app.libraries.word_frequency.utilities import get_word_frequency_data

word_frequencies_blueprint = Blueprint("word_frequencies", __name__)


@word_frequencies_blueprint.route('/word_frequencies', methods=['GET', 'POST'])
def word_frequencies():
    form = WordFrequencyForm()
    mode = 'reset'
    graphJSON = {}
    layout = {}
    info_list = []

    if form.validate_on_submit():
        args = dict()
        args['query_institutions'] = form.query_institutions.data
        args['query_step_in_days'] = int(form.query_step_in_days.data)
        args['query_min_date'] = str(form.query_min_date.data)
        args['query_max_date'] = str(form.query_max_date.data)
        args['query_terms'] = [e.lower().strip() for e in form.query_terms.data.split(',')]
        fig = get_word_frequency_data(**args)
        graphJSON, layout, info_list = jsonify_plotly_figure(fig=fig)
        mode = 'data_received'

    return render_template("word_frequency/palette.html",
                           form=form, data=graphJSON, layout=layout, mode=mode, info_list=info_list)

