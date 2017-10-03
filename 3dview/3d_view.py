import plotly.graph_objs as go
import plotly.offline as offline
offline.init_notebook_mode()

import numpy as np
import sys

def view_3d(filename):
    data = np.genfromtxt(fname=filename, dtype=float, delimiter=',', skip_header=5)
    data = np.delete(data, [0,1], 1)

    x, y, z = np.random.multivariate_normal(np.array([0, 0, 0]), np.eye(3), int(data.shape[1]/3)).transpose()
    for row in data:
        count = 0
        tmp = 0
        while count < len(row):
            x[tmp] = row[count]
            y[tmp] = row[count + 1]
            z[tmp] = row[count + 2]
            tmp += 1
            count += 3

        trace1 = go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode='markers',
            marker=dict(
                size=12,
                line=dict(
                    color='rgba(217, 217, 217, 0.14)',
                    width=0.5
                ),
                opacity=0.8
            )
        )
        break

    data = [trace1]
    layout = go.Layout(
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0
        )
    )
    fig = go.Figure(data=data, layout=layout)
    offline.iplot(fig, filename='simple-3d-scatter')

    return True

if __name__ == '__main__':
    arg = sys.argv
    if len(arg) != 2:
        print ("argument error:python 3d_view.py filename")
    else:
        if view_3d(arg[1]):
            print("finished")
        else:
            print("An error was occurred")