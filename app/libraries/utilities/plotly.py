import json
import plotly.utils
import plotly_express as px


def jsonify_plotly_figure(fig):
    info_list = []
    graphJSON = json.dumps(fig.data, cls=plotly.utils.PlotlyJSONEncoder)
    layout = json.dumps(fig.layout, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON, layout, info_list
