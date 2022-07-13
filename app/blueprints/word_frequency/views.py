from flask import Blueprint, render_template, redirect
import os
from app import cache_folderpath
from app.blueprints.word_frequency.forms import WordFrequencyForm
from app.libraries.utilities.plotly import jsonify_plotly_figure
from app.libraries.word_frequency.utilities import get_word_frequency_data, is_request_processed
from app.libraries.io.read_write import write_pkl_gz
from app.libraries.randomization.hashing import dict_hash
word_frequencies_blueprint = Blueprint("word_frequencies", __name__)


# @word_frequencies_blueprint.route('/word_frequencies', methods=['GET', 'POST'])
# def word_frequencies():
#     form = WordFrequencyForm()
#     mode = 'reset'
#     graphJSON = {}
#     layout = {}
#     info_list = []
#
#     if form.validate_on_submit():
#         args = dict()
#         args['query_institutions'] = form.query_institutions.data
#         args['query_step_in_days'] = int(form.query_step_in_days.data)
#         args['query_min_date'] = str(form.query_min_date.data)
#         args['query_max_date'] = str(form.query_max_date.data)
#         args['query_terms'] = [e.lower().strip() for e in form.query_terms.data.split(',')]
#         fig = get_word_frequency_data(**args)
#         graphJSON, layout, info_list = jsonify_plotly_figure(fig=fig)
#         mode = 'data_received'
#
#     return render_template("word_frequency/palette.html",
#                            form=form, data=graphJSON, layout=layout, mode=mode, info_list=info_list)


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
        if is_request_processed(**args):
            fig = get_word_frequency_data(**args)
            graphJSON, layout, info_list = jsonify_plotly_figure(fig=fig)
            mode = 'data_received'
            return render_template("word_frequency/palette.html",
                                   form=form, data=graphJSON, layout=layout, mode=mode, info_list=info_list)
        else:
            write_pkl_gz(args, os.path.join(cache_folderpath, 'requests', 'args',
                                            'word_frequency_' + dict_hash(args) + '.pkl.gz'))
            return redirect('/email_notification/word_frequency/' + dict_hash(args))

    return render_template("word_frequency/palette.html",
                           form=form, data=graphJSON, layout=layout, mode=mode, info_list=info_list)
