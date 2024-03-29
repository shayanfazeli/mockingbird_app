from flask import Blueprint, render_template, redirect
import os
from app import cache_folderpath
from app.blueprints.word_cloud.forms import WordCloudForm
from app.libraries.utilities.plotly import jsonify_plotly_figure
from app.libraries.word_clouds.utilities import get_word_cloud_data, is_request_processed
from app.libraries.io.read_write import write_pkl_gz
from app.libraries.randomization.hashing import dict_hash

word_clouds_blueprint = Blueprint("word_clouds", __name__)


# @word_clouds_blueprint.route('/word_clouds', methods=['GET', 'POST'])
# def word_clouds():
#     form = WordCloudForm()
#     mode = 'reset'
#     graphJSONs = {}
#     layouts = {}
#     info_lists = []
#     timespans = []
#     num_word_clouds=0
#
#     if form.validate_on_submit():
#         args = dict()
#         args['query_institutions'] = form.query_institutions.data
#         args['query_step_in_days'] = int(form.query_step_in_days.data)
#         args['query_min_date'] = str(form.query_min_date.data)
#         args['query_max_date'] = str(form.query_max_date.data)
#         args['max_word_count'] = int(form.max_word_count.data)
#         figs, timespans = get_word_cloud_data(**args)
#         graphJSONs = []
#         layouts = []
#         info_lists = []
#         for fig in figs:
#             graphJSON, layout, info_list = jsonify_plotly_figure(fig=fig)
#             graphJSONs.append(graphJSON)
#             layouts.append(layout)
#             info_lists.append(info_list)
#         mode = 'data_received'
#         num_word_clouds = len(graphJSONs)
#
#     return render_template("word_cloud/palette.html",
#                            form=form, data=graphJSONs, layouts=layouts, mode=mode, info_lists=info_lists, timespans=timespans, num_word_clouds=num_word_clouds)





# - with queue
@word_clouds_blueprint.route('/word_clouds', methods=['GET', 'POST'])
def word_clouds():
    form = WordCloudForm()
    mode = 'reset'
    graphJSONs = {}
    layouts = {}
    info_lists = []
    timespans = []
    num_word_clouds=0

    if form.validate_on_submit():
        args = dict()
        args['query_institutions'] = form.query_institutions.data
        args['query_step_in_days'] = int(form.query_step_in_days.data)
        args['query_min_date'] = str(form.query_min_date.data)
        args['query_max_date'] = str(form.query_max_date.data)
        args['max_word_count'] = int(form.max_word_count.data)
        if is_request_processed(**args):
            figs, timespans = get_word_cloud_data(**args)
            graphJSONs = []
            layouts = []
            info_lists = []
            for fig in figs:
                graphJSON, layout, info_list = jsonify_plotly_figure(fig=fig)
                graphJSONs.append(graphJSON)
                layouts.append(layout)
                info_lists.append(info_list)
            mode = 'data_received'
            num_word_clouds = len(graphJSONs)
            return render_template("word_cloud/palette.html",
                                   form=form, data=graphJSONs, layouts=layouts, mode=mode, info_lists=info_lists,
                                   timespans=timespans, num_word_clouds=num_word_clouds)
        else:
            write_pkl_gz(args, os.path.join(cache_folderpath, 'requests', 'args', 'word_cloud_' + dict_hash(args) + '.pkl.gz'))
            return redirect('/email_notification/word_cloud/' + dict_hash(args))
    return render_template("word_cloud/palette.html",
                           form=form, data=graphJSONs, layouts=layouts, mode=mode, info_lists=info_lists, timespans=timespans, num_word_clouds=num_word_clouds)
