import matplotlib
matplotlib.use('Agg') # run matploblib on main threads
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import urllib.parse
import io
import base64
import numpy as np
import math

def gaussian(bins, sigma, mu):
    return 1/(sigma*np.sqrt(2*np.pi))*np.exp(-(bins - mu)**2/(2*sigma**2))

def create_pie_chart(plot_title, slices, labels):

    img = io.BytesIO()
    fig, ax1 = plt.subplots()
    ax1.pie(slices, labels = labels, startangle = 90, autopct='%1.1f%%', wedgeprops = {'ec': 'black'})
    ax1.set_title(plot_title)


    plt.savefig(img, format='png')
    img.seek(0)
    plot_data = urllib.parse.quote(base64.b64encode(img.read()).decode())
    return plot_data

def create_comparative_bar_chart(title, data_1, label_1, data_2, label_2, x_labels, xaxis_label):

    img = io.BytesIO()
    x = np.arange(len(x_labels))
    width = 0.25

    fig, ax1 = plt.subplots()
    ax1.bar(x - width/2, data_1, width = width, label = label_1, edgecolor= 'black')
    ax1.bar(x + width/2, data_2, width = width, label = label_2, edgecolor= 'black')
    ax1.legend()
    ax1.set_title(title)
    ax1.set_xticks(x)
    ax1.set_xticklabels(x_labels)
    ax1.set_xlabel(xaxis_label)
    ax1.set_ylabel('Achievement (%)')


    plt.savefig(img, format='png')
    img.seek(0)
    plot_data = urllib.parse.quote(base64.b64encode(img.read()).decode())
    return plot_data

def create_distribution_plot(data, sd, mean, title, is_personal, x_value):

    img = io.BytesIO()
    bins = [x*5 for x in range(21)]
    fig_dist, (ax0, ax1, ax2) = plt.subplots(nrows = 3, ncols = 1)

    if is_personal == True:
        x = [x_value]
        y = [1] #arbitrary choice for now
        ax2.plot(x,y,'or', 'ro', ms = 20)

    x = np.linspace(0, 100, 100)
    ax0.plot(x, gaussian(x, sd, mean))
    ax0.set_title(title)
    ax0.set_xlim([0,105])
    ax0.grid(True)
    ax0.set_yticks([])
    ax0.set_ylabel('Normal Distribution')

    ax1.hist(data, bins = bins, weights = np.ones(len(data))/len(data), edgecolor = 'black')
    ax1.yaxis.set_major_formatter(PercentFormatter(1))
    ax1.set_ylabel('Ratio of Students')
    ax1.grid(True)
    ax1.set_xlim([0,105])
    ax1.set_xticks([x*5 for x in range(21)])

    ax2.boxplot(data, vert = False, whis = [0,100], showfliers = False)
    ax2.set_xlabel('Achievement (%)')
    ax2.grid(True)
    ax2.set_xlim([0,105])
    ax2.set_yticks([])

    plt.savefig(img, format='png')
    img.seek(0)
    plot_data = urllib.parse.quote(base64.b64encode(img.read()).decode())
    return plot_data
