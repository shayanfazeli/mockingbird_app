import pyLDAvis
from flask import Blueprint, render_template, redirect
import os
from app import cache_folderpath
from app.blueprints.topic_modeling.forms import TopicModelingForm
from app.libraries.topic_modeling.utilities import get_topic_modeling_data, is_request_processed
from app.libraries.utilities.plotly import jsonify_plotly_figure
from app.libraries.io.read_write import write_pkl_gz
from app.libraries.randomization.hashing import dict_hash
topic_modeling_blueprint = Blueprint("topic_modeling", __name__)


@topic_modeling_blueprint.route('/topic_modeling', methods=['GET', 'POST'])
def topic_modeling():
    form = TopicModelingForm()
    mode = 'reset'
    graphJSON = {}
    layout = {}
    info_list = []
    lda_vis= ''

    if form.validate_on_submit():
        args = dict()
        args['support_institutions'] = form.support_institutions.data
        args['query_institutions'] = form.query_institutions.data
        args['topic_counts'] = int(form.topic_counts.data)
        args['support_min_date'] = str(form.support_min_date.data)
        args['support_max_date'] = str(form.support_max_date.data)
        args['query_step_in_days'] = int(form.query_step_in_days.data)
        args['query_min_date'] = str(form.query_min_date.data)
        args['query_max_date'] = str(form.query_max_date.data)
        if is_request_processed(**args):
            vis, fig = get_topic_modeling_data(**args)
            graphJSON, layout, info_list = jsonify_plotly_figure(fig=fig)
            mode = 'data_received'
            lda_vis = str(pyLDAvis.display(vis).data)
            return render_template("topic_modeling/palette.html",
                                   form=form, lda_vis=lda_vis, data=graphJSON, layout=layout, mode=mode,
                                   info_list=info_list)
        else:
            write_pkl_gz(args, os.path.join(cache_folderpath, 'requests', 'args',
                                            'topic_modeling_' + dict_hash(args) + '.pkl.gz'))
            return redirect('/email_notification/topic_modeling/' + dict_hash(args))

    return render_template("topic_modeling/palette.html",
                           form=form, lda_vis=lda_vis, data=graphJSON, layout=layout, mode=mode, info_list=info_list)

