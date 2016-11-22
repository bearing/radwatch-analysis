import csv
import numpy as np
import datetime
import matplotlib.pyplot as plt

metacols = 3
color_scheme = ['#00B2A5', '#D9661F', '#00B0DA', '#FDB515', '#ED4E33',
                '#2D637F', '#9DAD33', '#53626F', '#EE1F60', '#6C3302',
                '#C2B9A7', '#CFDD45', '#003262']
color_map = {'k40': 8, 'bi214': 5, 'tl208': 7, 'cs137': 10, 'cs134': 9}
isotope_key = ['k40', 'bi214', 'tl208', 'cs137', 'cs134']
color_scheme = np.asarray([color_scheme[color_map[key]]
                           for key in isotope_key])


def parse_time(date):
    """
    parse_time formats the date given into the format month-day-year.
    """
    if ('-' in date):
        return ''
    date_list = date.split('/')
    return_list = []
    for item in date_list:
        return_list.append(int(item))
    return datetime.datetime(year=2000+return_list[2], month=return_list[0],
                             day=return_list[1])


def unique_sample_names(sample_names):
    """
    unique_sample_names takes a given list of sample names and returns a list
    of all the unique names in the list
    """
    ret = []
    for name in sample_names:
        if name not in ret:
            ret.append(name)
    return ret


def combine_measurements(sample_array, sample_names,
                         sample_dates):
    """
    combine_measurements acquires all the samples with the same name and
    their corresponding information and combines it into one sample
    that's representative of the group. It returns sample information that
    contains the name of the sample group, the average of the group data and
    uncertainty, and the dates of the three most recent samples.
    """
    u_sample_names = unique_sample_names(sample_names)
    u_sample_array = []
    u_sample_names_ret = []
    for u_name in u_sample_names:
        lst = []
        row = 0
        u_sample_dates = []
        for name in sample_names:
            if(u_name == name):
                lst.append(sample_array[row, :])
                if sample_dates[row] == '':
                    continue
                u_sample_dates.append(sample_dates[row])
            row += 1

        u_sample_dates = np.sort(u_sample_dates)
        if len(u_sample_dates):
            u_sample_dates_ = '('+str(len(u_sample_dates))+')'
        else:
            u_sample_dates_ = '('+str(1)+')'

        for date in u_sample_dates[-3:]:
            u_sample_dates_ += "\n"+date.strftime('%m-%d-%y')
        lst = np.asarray(lst)
        u_sample_array.append(np.mean(lst, axis=0))
        u_sample_names_ret.append(u_name + u_sample_dates_)

    return np.asarray(u_sample_array), u_sample_names_ret


def create_barerror_plot(csv_file, title, log=True):
    """
    create_barerror_plot reads a csv file and takes a title input and prepares
    the information from the csv file for generating a bar plot. This
    preparation includes cleaning the sample names of the UCB title and simply
    showing the sample type.
    """
    sample_list = []
    name_list = []
    date_list = []
    header = []
    with open(csv_file) as csvfile:
        parser = csv.reader(csvfile)
        header = parser.__next__()
        dictparser = csv.DictReader(csvfile, header)
        for row in dictparser:
            tmp_list = []
            if 'recal' in row[header[0]]:
                # Remove recal from name
                label = str(row[header[0]][7:-6])
            else:
                label = str(row[header[0]][7:])
            name_list.append(label)
            date_list.append(parse_time(row[header[1]]))
            for ind in range(metacols, 2 * len(isotope_key) + 2, 2):
                    tmp_list.extend([float(row[header[ind]]),
                                     float(row[header[ind+1]])])
            sample_list.append(tmp_list)
    sample_list = np.asarray(sample_list)
    legend_key = []
    sample_list, name_list = combine_measurements(sample_array=sample_list,
                                                  sample_names=name_list,
                                                  sample_dates=date_list)
    data = np.zeros((len(name_list), int(sample_list.shape[1] / 2.)))
    error = np.zeros((len(name_list), int(sample_list.shape[1] / 2.)))
    loop = 0
    # Create data and error lists for simple bar graph assembly
    for item in range(0, sample_list.shape[1], 2):
        legend_key.append(header[metacols + item])
        data[:, loop] = sample_list[:, item]
        error[:, loop] = sample_list[:, item + 1]
        loop += 1
    ax, fig = generate_barerror_logy(sample_names=name_list, data=data,
                                     error=error, legend_key=legend_key,
                                     title=title, log=log)


def generate_barerror_logy(sample_names, data, error, legend_key, title,
                           log=True):
    """
    generate_barerror_logy generates a bar graph with error bars. Bars are
    are generated on a log plot with arrows indicating a detection limit and
    bars representing a concentration value.
    """
    number_samples = len(sample_names)
    index = np.arange(0.5, number_samples, dtype=np.float64)
    width = float(0.15)
    fig, ax = plt.subplots()

    axis = []
    mins = np.amin(data[np.nonzero(data)])
    for sample in range(0, len(legend_key)):
        error_color = []
        for i in range(len(data[:, sample])):
            # Determine whether to present a bar or detection limit
            if data[:, sample][i] <= error[:, sample][i]:
                data[:, sample][i] = 0
                error_color.append(color_scheme[sample])
            else:
                error_color.append('black')
        args = np.zeros((0))
        left_edge = index + float(width) * float(sample)
        if np.amin(data[:, sample]) == 0:
            args = np.where(data[:, sample] == 0)
            data[args, sample] += 1e-2
            draw_arrows(axes=ax, xlocs=(left_edge + 0.5 * float(width))[args],
                        ylocs=error[args, sample], color=color_scheme[sample])
        for pos, val, err, color in zip(left_edge, data[:, sample],
                                        error[:, sample], error_color):
            ax.errorbar(pos + 0.075, val, err, color=color)
        axis.append(ax.bar(left=left_edge, height=tuple(data[:, sample]),
                    width=width, color=color_scheme[sample],
                    edgecolor="none", log=log))
    ylims = ax.get_ylim()
    upper_mult = 1
    if log:
        upper_mult = 10
    ax.set_ylim([mins / 10, upper_mult * ylims[1]])
    ax.set_xticks(index + float(len(legend_key)) / 2. * width)
    ax.set_xticklabels(sample_names)
    ax.tick_params(axis='x', color='w')
    ax.legend([a[0] for a in axis], legend_key, loc='upper left')
    ax.annotate('', xy=(0.88, 0.8999), xycoords='axes fraction',
                xytext=(0.88, 0.9), textcoords='axes fraction',
                arrowprops=dict(edgecolor='k', facecolor='k',
                arrowstyle='-|>'))
    ax.annotate('Detection Limit', xy=(0.888, 0.905), xytext=(0.888, 0.905),
                textcoords='axes fraction', ha='left', va='center')
    ax.set_title(title)
    ax.set_ylabel('Specific Activity' + legend_key[0].split(' ')[1])
    plt.gcf().subplots_adjust(bottom=0.15, left=0.05, right=0.95)
    plt.show()
    return ax, fig


def draw_arrows(axes, xlocs, ylocs, color):
    """
    draw_arrows places arrow hats for measurement detection limits to
    distinguish them from regular error bars.
    """
    num_els = len(xlocs)
    if num_els == 0:
        return
    if len(ylocs.shape) > 1:
        ylocs = np.squeeze(ylocs, axis=(0,))
    for index in range(0, num_els):
        dy = 1e-10
        axes.annotate("", xy=(xlocs[index], ylocs[index] - dy),
                      xycoords='data', xytext=(xlocs[index], ylocs[index]),
                      textcoords='data', arrowprops=dict(edgecolor=color,
                      facecolor=color, arrowstyle="-|>"))
    return

create_barerror_plot('Sampling_Table.csv', 'Sample Summary')
