import plotly.plotly as py
import plotly.offline as offline
import plotly.graph_objs as go
import numpy as np

class Plot(object):

    def __init__(self, plot_data):
        self.name = plot_data['name']
        self.x = plot_data['x']
        self.y = plot_data['y']
        self.plot_type = plot_data['plot_type']
        self.text = plot_data['text']
        self.title = plot_data['title']
        self.filename = plot_data['filename']

        self.data = []

    def bar(self, x, y, text=None):
        self.data.append(go.Bar(x = x,
                                y = y,
                                text = text,
        ))


    def scatter(self, x, y, text):
        self.data.append(go.Scatter(
            x = x,
            y = y,
            mode = 'lines+markers',
            name = text,
        ))


    def plot(self):
        py.plot({'data': self.data,
                 'layout': {'title': self.title,
                            'font': dict(size=16)}},
                filename=self.filename,
        )


    def plot_offline(self):
        offline.plot({'data': self.data,
                      'layout': {'title': self.title,
                                 'font': dict(size=16)}},
                     filename=self.filename,
        )
