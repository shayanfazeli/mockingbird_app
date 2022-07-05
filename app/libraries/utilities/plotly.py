import json
import plotly.utils
import plotly_express as px


def jsonify_plotly_figure(fig):
    """
    Preparation of the plotly figure for jsonification to work in Jinja2.

    Parameters
    ----------
    fig: `plotly.graph_objects.Figure`, required
        The plotly figure to jsonify.

    Returns
    -------
    The jsonified plotly figure data
    """
    info_list = []
    graphJSON = json.dumps(fig.data, cls=plotly.utils.PlotlyJSONEncoder)
    layout = json.dumps(fig.layout, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON, layout, info_list
