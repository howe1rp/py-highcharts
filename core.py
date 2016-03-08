import os
import re
import json
import string
import pandas as pd


PACKAGE_DIR = os.path.dirname(os.path.realpath(__file__))


class MyTemplate(string.Template):
    """
    A template class to be used in index.html
    """
    # this is what we'll look for in index.html to pop in our data
    delimiter = '@@'


def verify_data(data):
    """
    Make sure the data exists and that it's in the proper format
    :param data: the data
    :return: the data, modified if necessary
    """
    # make sure there's actually data
    try:
        assert data
    except ValueError:
        if isinstance(data, pd.DataFrame):
            assert not data.empty

    # data in list or dict format is acceptable
    if isinstance(data, list) or isinstance(data, dict):
        return data

    # extract the data if it's in a pandas DataFrame
    elif isinstance(data, pd.DataFrame):
        return data.to_dict('records')

    # unknown data type
    else:
        raise Exception('Unknown data type')


def plot(data, options=None, **kwargs):
    settings = kwargs
    chart_type = settings.get('type', 'line')
    save_file = settings.get('save', 'test.html')

    data = verify_data(data)

    if not options:
        options = {}

    if 'chart' not in options:
        options['chart'] = {}
    options['chart']['type'] = chart_type
    options['chart']['renderTo'] = 'container'

    if 'series' not in options:
        options['series'] = [{
            'data': data
        }]
    elif 'data' not in options['series'][0]:
        options['series'][0]['data'] = data

    with open(os.path.join(PACKAGE_DIR, 'index.html')) as html:
        html = MyTemplate(html.read()).substitute(
            options=format_options(options)
        )

    with open(save_file, 'w') as out_file:
        out_file.write(html)

    show_plot(html, save_file, show='inline')
    # show_plot(html, save_file)


def show_plot(html, file_name, show='tab'):
    """
    Open the chart
    :param file_name: path of the file to open
    :param show: how you want to show the plot (inline, tab)
    :return:
    """
    if show == 'inline':
        from IPython.core.display import display, HTML
        return display(HTML(html))
    else:
        import webbrowser
        print 'Opening in new tab...'
        webbrowser.open_new_tab('file://' + os.path.realpath(file_name))


def format_options(options):
    """
    Remove quotes around javascript functions.
    :param options: the options
    :return: the options with quotes around functions removed
    """
    options = json.dumps(options)
    options = re.sub(r'@@("|\')+', '', options)
    options = re.sub(r'("|\')+@@', '', options)
    return options


if __name__ == '__main__':
    df = pd.DataFrame(
        [(1, 2, 'a'), (4, 5, 'b'), (7, 8, 'c')],
        columns=['x', 'y', 'c'])

    options = {
        'title': {
            'text': 'Test'
        },

        'legend': {
            'enabled': False
        },

        # 'tooltip': {
        #     'formatter': "@@function() { var s = '<b>' + this.x + '</b></br><b>' + this.y + '</b></br><b>' + this.point.c + '</b></br>'; return s; }@@"
        # }
    }

    # plot([[1, 2], [3, 4]], options=options, type='line')
    plot(df, options=options, type='line')
    # plot([{'x': 1, 'y': 2}, {'x': 2, 'y': 4}], options=options, type='line')
    # plot('', options=options, type='line')

