## author : charlie
## date : 20220130
## edited by yanghao

import os
import math
import argparse
import numpy as np
from scipy.interpolate import interp2d
import scipy.ndimage as ndimage
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoLocator, FormatStrFormatter
from matplotlib import pylab as pylab

myparams = {
    "axes.labelsize": "10",
    "xtick.labelsize": "10",
    "ytick.labelsize": "10",
    "ytick.left": False,
    "ytick.direction": "in",
    "xtick.bottom": False,
    "xtick.direction": "in",
    "lines.linewidth": "2",
    "axes.linewidth": "1",
    "legend.fontsize": "10",
    "legend.loc": "upper right",
    "legend.fancybox": False,
    "legend.frameon": False,
    "font.family": "Arial",
    "font.size": 10,
    "figure.dpi": 600,
    "savefig.dpi": 600,
}
pylab.rcParams.update(myparams)


def readxpm(inputfile: str) -> tuple:
    """read xpm file and return all infos"""

    xpm_title, xpm_legend, xpm_type = "", "", ""
    xpm_xlabel, xpm_ylabel = "", ""
    xpm_width, xpm_height = 0, 0
    xpm_color_num, xpm_char_per_pixel = 0, 0
    chars, colors, notes, colors_rgb = [], [], [], []
    xpm_xaxis, xpm_yaxis, xpm_data = [], [], []

    ## check and read xpm file
    if not os.path.exists(inputfile):
        print("ERROR -> no {} in current directory".format(inputfile))
        exit()
    with open(inputfile, "r") as fo:
        lines = [line.strip() for line in fo.readlines()]

    ## parse content of xpm file
    flag_4_code = 0  ## means haven't detected yet
    for line in lines:
        ## finde the 4 code line and parse
        if flag_4_code == 1:  ## means this line is code4 line
            flag_4_code = 2  ## means have detected
            code4 = [int(c) for c in line.strip().strip(",").strip('"').split()]
            xpm_width, xpm_height = code4[0], code4[1]
            xpm_color_num, xpm_char_per_pixel = code4[2], code4[3]
            continue
        elif (flag_4_code == 0) and line.startswith("static char"):
            flag_4_code = 1  ## means next line is code4 line
            continue

        ## parse comments and axis parts
        if line.startswith("/* x-axis"):
            xpm_xaxis += [float(n) for n in line.strip().split()[2:-1]]
            continue
        elif line.startswith("/* y-axis"):
            xpm_yaxis += [float(n) for n in line.strip().split()[2:-1]]
            continue
        elif line.startswith("/* title"):
            xpm_title = line.strip().split('"')[1]
            continue
        elif line.startswith("/* legend"):
            xpm_legend = line.strip().split('"')[1]
            continue
        elif line.startswith("/* x-label"):
            xpm_xlabel = line.strip().split('"')[1]
            continue
        elif line.startswith("/* y-label"):
            xpm_ylabel = line.strip().split('"')[1]
            continue
        elif line.startswith("/* type"):
            xpm_type = line.strip().split('"')[1]
            continue

        items = line.strip().split()
        ## for char-color-note part
        if len(items) == 7 and items[1] == "c":
            if len(items[0].strip('"')) == xpm_char_per_pixel:
                chars.append(items[0].strip('"'))
                colors.append(items[2])
                notes.append(items[5].strip('"'))
            ## deal with blank
            if len(items[0].strip('"')) < xpm_char_per_pixel:
                print("Warning -> space in char of line : {}".format(line))
                char_item = items[0].strip('"')
                chars.append(char_item + " " * (xpm_char_per_pixel - len(char_item)))
                colors.append(items[2])
                notes.append(items[5].strip('"'))
            continue

        ## for content part
        if line.strip().startswith('"') == 1 and (
            len(line.strip().strip(",").strip('"')) == xpm_width * xpm_char_per_pixel
        ):
            xpm_data.append(line.strip().strip(",").strip('"'))

    ## check infos
    if len(chars) != len(colors) != len(notes) != xpm_color_num:
        print("Wrong -> length of chars, colors, notes != xpm_color_num")
        print(
            "chars : {}, colors : {}, notes : {}, xpm_color_num : {}".format(
                len(chars), len(colors), len(notes), xpm_color_num
            )
        )
        exit()

    if len(xpm_data) != xpm_height:
        print(
            "ERROR -> rows of data ({}) is not equal to xpm height ({}), check it !".format(
                len(xpm_data), xpm_height
            )
        )
        exit()
    if len(xpm_xaxis) != xpm_width and len(xpm_xaxis) != xpm_width + 1:
        print(
            "ERROR -> length of x-axis ({}) != xpm width ({}) or xpm width +1".format(
                len(xpm_xaxis), xpm_width
            )
        )
        exit()
    if len(xpm_yaxis) != xpm_height and len(xpm_yaxis) != xpm_height + 1:
        print(
            "ERROR -> length of y-axis ({}) != xpm height ({}) or xpm height +1".format(
                len(xpm_yaxis), xpm_height
            )
        )
        exit()

    if len(xpm_xaxis) == xpm_width + 1:
        xpm_xaxis = [
            (xpm_xaxis[i - 1] + xpm_xaxis[i]) / 2.0 for i in range(1, len(xpm_xaxis))
        ]
        print(
            "Warning -> length of x-axis is 1 more than xpm width, use intermediate value for instead. "
        )
    if len(xpm_yaxis) == xpm_height + 1:
        xpm_yaxis = [
            (xpm_yaxis[i - 1] + xpm_yaxis[i]) / 2.0 for i in range(1, len(xpm_yaxis))
        ]
        print(
            "Warning -> length of y-axis is 1 more than xpm height, use intermediate value for instead. "
        )

    ## hex color to rgb values
    for color in colors:
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        colors_rgb.append([r, g, b])

    print("Info -> all data has been read from {} successfully.".format(inputfile))

    xpm_infos = (
        xpm_title,
        xpm_legend,
        xpm_type,
        xpm_xlabel,
        xpm_ylabel,
        xpm_width,
        xpm_height,
        xpm_color_num,
        xpm_char_per_pixel,
        chars,
        colors,
        notes,
        colors_rgb,
        xpm_xaxis,
        xpm_yaxis,
        xpm_data,
    )
    return xpm_infos


def drawxpm_origin(xpmfile: str, IP: bool, outputpng: str, noshow: bool) -> None:
    """draw xpm figure by plt.imshow
    xpmfile: input xpm file
    IP : whether to interpolation
    outputpng: the name for figure output
    noshow: whether not to show figure, useful for PC without gui
    """

    ## check parameters
    if not os.path.exists(xpmfile):
        print("ERROR -> {} not in current directory".format(xpmfile))
        exit()
    if outputpng != None and os.path.exists(outputpng):
        print("ERROR -> {} already in current directory".format(outputpng))
        exit()

    (
        xpm_title,
        xpm_legend,
        xpm_type,
        xpm_xlabel,
        xpm_ylabel,
        xpm_width,
        xpm_height,
        xpm_color_num,
        xpm_char_per_pixel,
        chars,
        colors,
        notes,
        colors_rgb,
        xpm_xaxis,
        xpm_yaxis,
        xpm_data,
    ) = readxpm(xpmfile)

    ## the read order of pixels is from top to bottom
    ## but the y-axis is from bottom to top, so reverse() is important !
    xpm_yaxis.reverse()

    # visualization of xpm
    if IP == False:
        img = []
        for line in xpm_data:
            rgb_line = []
            for i in range(0, xpm_width * xpm_char_per_pixel, xpm_char_per_pixel):
                rgb_line.append(
                    colors_rgb[chars.index(line[i : i + xpm_char_per_pixel])]
                )
            img.append(rgb_line)
            img = ndimage.gaussian_filter(img,sigma=0.3)

        plt.imshow(img, aspect="auto")

    if IP == True:
        if xpm_type != "Continuous":
            print("ERROR -> Only Continuous type xpm file can interpolation")
            exit()
        ## show figure with interpolation
        imgIP = []
        for line in xpm_data:
            value_line = []
            for i in range(0, xpm_width * xpm_char_per_pixel, xpm_char_per_pixel):
                value_line.append(
                    float(notes[chars.index(line[i : i + xpm_char_per_pixel])])
                )
            imgIP.append(value_line)
            imgIP = ndimage.gaussian_filter(imgIP,sigma=0.3)
        im = plt.imshow(imgIP, cmap="coolwarm", interpolation="bilinear", aspect="auto")
        plt.colorbar(im, fraction=0.046, pad=0.04)

    ## TODO: find a better way to solve problem of ticks
    ## set the ticks
    x_tick, y_tick = 3, 3
    xpm_xticks = ["{:.1f}".format(x) for x in xpm_xaxis]
    xpm_yticks = ["{:.1f}".format(y) for y in xpm_yaxis]
    if xpm_width < 100:
        x_tick = int(xpm_width / 3)
    elif xpm_width >= 100 and xpm_width < 1000:
        x_tick = int(xpm_width / 5)
    elif xpm_width > 500:
        x_tick = int(xpm_width / 10)
    if xpm_height < 100:
        y_tick = int(xpm_height / 3)
    elif xpm_height >= 100 and xpm_height < 1000:
        y_tick = int(xpm_height / 5)
    elif xpm_height > 500:
        y_tick = int(xpm_height / 10)
    if xpm_width / xpm_height > 10:
        y_tick = int(xpm_height / 2)
    if xpm_height / xpm_width > 10:
        x_tick = int(xpm_width / 2)
    plt.tick_params(axis="both", which="major")
    plt.xticks(
        [0]
        + [w for w in range(x_tick, xpm_width - int(x_tick / 2), x_tick)]
        + [xpm_width - 1],
        [xpm_xticks[0]]
        + [xpm_xticks[w] for w in range(x_tick, xpm_width - int(x_tick / 2), x_tick)]
        + [xpm_xticks[-1]],
    )
    plt.yticks(
        [0]
        + [h for h in range(y_tick, xpm_height - int(y_tick / 2), y_tick)]
        + [xpm_height - 1],
        [xpm_yticks[0]]
        + [xpm_yticks[h] for h in range(y_tick, xpm_height - int(y_tick / 2), y_tick)]
        + [xpm_yticks[-1]],
    )

    ## set other infos in the figure
    plt.title(xpm_title)
    plt.xlabel(xpm_xlabel)
    plt.ylabel(xpm_ylabel)
    print("Legend of this xpm figure -> ", xpm_legend)
    output_filename = f"{outputpng}.png"
    if outputpng != None:
        plt.savefig(output_filename, dpi=600)
    if noshow == False:
        plt.show()


def drawxpm_newIP(xpmfile: str, IP: bool, outputpng: str, noshow: bool) -> None:
    """draw xpm figure by pcolormesh (with interpolation)
    xpmfile: input xpm file
    IP : whether to interpolation
    outputpng: the name for figure output
    noshow: whether not to show figure, useful for PC without gui
    """

    ## check parameters
    if not os.path.exists(xpmfile):
        print("ERROR -> {} not in current directory".format(xpmfile))
        exit()
    if outputpng != None and os.path.exists(outputpng):
        print("ERROR -> {} already in current directory".format(outputpng))
        exit()

    (
        xpm_title,
        xpm_legend,
        xpm_type,
        xpm_xlabel,
        xpm_ylabel,
        xpm_width,
        xpm_height,
        xpm_color_num,
        xpm_char_per_pixel,
        chars,
        colors,
        notes,
        colors_rgb,
        xpm_xaxis,
        xpm_yaxis,
        xpm_data,
    ) = readxpm(xpmfile)

    if xpm_type != "Continuous":
        print("ERROR -> Only Continuous type xpm file can interpolation")
        exit()

    xpm_yaxis.reverse()

    ## convert xpm_data to img (values)
    img = []
    for line in xpm_data:
        value_line = []
        for i in range(0, xpm_width * xpm_char_per_pixel, xpm_char_per_pixel):
            value_line.append(
                float(notes[chars.index(line[i : i + xpm_char_per_pixel])])
            )
        img.append(value_line)
    #img = ndimage.gaussian_filter(img, sigma=0.3)

    if IP == False:
        plt.pcolormesh(xpm_xaxis, xpm_yaxis, img, cmap="coolwarm", shading="auto")
    elif IP == True:
        ## interpolation
        ip_func = interp2d(xpm_xaxis, xpm_yaxis, img, kind="linear")
        x_new = np.linspace(np.min(xpm_xaxis), np.max(xpm_xaxis), 10 * len(xpm_xaxis))
        y_new = np.linspace(np.min(xpm_yaxis), np.max(xpm_yaxis), 10 * len(xpm_yaxis))
        value_new = ip_func(x_new, y_new)
        img = ndimage.gaussian_filter(value_new, sigma=0.3)
        x_new, y_new = np.meshgrid(x_new, y_new)
        ## show figure
        plt.pcolormesh(x_new, y_new, img, cmap="coolwarm", shading="auto")

    ## set ticks and other figure infos
    ax = plt.gca()
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.1f"))
    plt.colorbar()
    plt.title(xpm_title)
    plt.xlabel(xpm_xlabel)
    plt.ylabel(xpm_ylabel)
    print("Legend of this xpm figure -> ", xpm_legend)
    output_filename = f"{outputpng}_2D.png"
    if outputpng != None:
        plt.savefig(output_filename, dpi=600)
    if noshow == False:
        plt.show()


def drawxpm_3D(xpmfile: str, IP: bool, outputpng: str, noshow: bool) -> None:
    """draw xpm 3D figure (with interpolation)
    xpmfile: input xpm file
    IP : whether to interpolation
    outputpng: the name for figure output
    noshow: whether not to show figure, useful for PC without gui
    """

    ## check parameters
    if not os.path.exists(xpmfile):
        print("ERROR -> {} not in current directory".format(xpmfile))
        exit()
    if outputpng != None and os.path.exists(outputpng):
        print("ERROR -> {} already in current directory".format(outputpng))
        exit()

    (
        xpm_title,
        xpm_legend,
        xpm_type,
        xpm_xlabel,
        xpm_ylabel,
        xpm_width,
        xpm_height,
        xpm_color_num,
        xpm_char_per_pixel,
        chars,
        colors,
        notes,
        colors_rgb,
        xpm_xaxis,
        xpm_yaxis,
        xpm_data,
    ) = readxpm(xpmfile)

    if xpm_type != "Continuous":
        print("ERROR -> Only Continuous type xpm file can draw 3D figure")
        exit()

    xpm_yaxis.reverse()

    ## convert xpm_data to values
    values = []
    for line in xpm_data:
        for i in range(0, xpm_width * xpm_char_per_pixel, xpm_char_per_pixel):
            values.append(float(notes[chars.index(line[i : i + xpm_char_per_pixel])]))
    xpm_xaxis = np.array(xpm_xaxis)
    xpm_yaxis = np.array(xpm_yaxis)
    img = np.array(values)

    ## draw 3d figure
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    ## interpolation
    IP_value = 1
    if IP == False:
        IP_value = 1
    elif IP == True:
        IP_value = 12
    img = img.reshape(len(xpm_xaxis), len(xpm_yaxis))
    ip_func = interp2d(xpm_xaxis, xpm_yaxis, img, kind="linear")
    x_new = np.linspace(np.min(xpm_xaxis), np.max(xpm_xaxis), IP_value * len(xpm_xaxis))
    y_new = np.linspace(np.min(xpm_yaxis), np.max(xpm_yaxis), IP_value * len(xpm_yaxis))
    img_new = ip_func(x_new, y_new)
    x_new, y_new = np.meshgrid(x_new, y_new)
    img_new = img_new.reshape(len(x_new), len(y_new))
    # Smooth the data using a Gaussian filter
    img_smooth = gaussian_filter(img_new,sigma=0.3)

    ## show figure
    surf = ax.plot_surface(
        x_new,
        y_new,
        img_smooth,
        alpha=0.9,
        cmap="coolwarm",
        linewidth=0,
        antialiased=False,
    )
    ## set the 2d surface location
    ax.contourf(
        x_new,
        y_new,
        img_smooth,
        zdir="z",
        offset=math.floor(min(values)) - math.floor(max(values) - min(values)) / 30,
        cmap="coolwarm",
    )
    plt.title(xpm_title)
    plt.xlabel(xpm_xlabel)
    plt.ylabel(xpm_ylabel)
    plt.colorbar(surf, shrink=0.6, aspect=12)
    ## set the axis ticks and other figure infos
    ax.zaxis.set_major_locator(AutoLocator())
    ax.zaxis.set_major_formatter(FormatStrFormatter("%.1f"))
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.1f"))
    for i in range(9):
        output_filename= f"{outputpng}_3D_R{i}.png" 
        ax.view_init(elev=30, azim=45*i)
        print("Legend of this xpm figure -> ", xpm_legend)

        if outputpng != None:
            plt.savefig(output_filename, dpi=600)
        if noshow == False:
            plt.show()
    plt.close()


def get_scatter_data(xpm_infos: tuple) -> tuple:
    """convert xpm_infos into scatter data
    xpm_infos: the return of readxpm()
    """
    (
        xpm_title,
        xpm_legend,
        xpm_type,
        xpm_xlabel,
        xpm_ylabel,
        xpm_width,
        xpm_height,
        xpm_color_num,
        xpm_char_per_pixel,
        chars,
        colors,
        notes,
        colors_rgb,
        xpm_xaxis,
        xpm_yaxis,
        xpm_data,
    ) = xpm_infos

    xpm_yaxis.reverse()

    ## parse xpm_data into x, y, v
    x, y, v = [], [], []
    scatter_x, scatter_y = [], []
    # print(len(xpm_xaxis))
    # print(len(xpm_yaxis))
    for l in range(len(xpm_data)):
        for i in range(0, xpm_width * xpm_char_per_pixel, xpm_char_per_pixel):
            v.append(float(notes[chars.index(xpm_data[l][i : i + xpm_char_per_pixel])]))
            x.append(xpm_xaxis[int(i / xpm_char_per_pixel)])
            y.append(xpm_yaxis[l])

    ## parse x, y, v into scatter_x, scatter_y
    v_max = max(v)
    scatter_weight = 1
    for i in range(len(v)):
        count = round((v_max - v[i]) * scatter_weight)
        for _ in range(count):
            scatter_x.append(x[i])
            scatter_y.append(y[i])

    return scatter_x, scatter_y, x, y, v


def extract_scatter(xpm: str, outcsv: str = None) -> None:
    """extract data from xpm and save to csv"""

    if not os.path.exists(xpm):
        print("ERROR -> {} not in current directory".format(xpm))
        exit()
    if xpm[-4:] != ".xpm":
        print("ERROR -> specify a file with suffix xpm")
        exit()
    if outcsv == None:
        outcsv = xpm[:-4] + ".csv"
    if outcsv[-4:] != ".csv":
        print("ERROR -> specify a output file with suffix csv")
        exit()
    if os.path.exists(outcsv):
        print("ERROR -> {} already in current directory".format(outcsv))
        exit()

    xpm_infos = readxpm(xpm)
    if xpm_infos[2] != "Continuous":
        print("ERROR -> can not extract data from xpm whose type is not Continuous")
        exit()

    ## only x, y, v values are needed
    _, _, x, y, v = get_scatter_data(xpm_infos)
    if len(x) != len(y) != len(v):
        print("ERROR -> wrong in length of x, y, v")
        exit()
    ## write results
    with open(outcsv, "w") as fo:
        fo.write("{},{},{}\n".format("x-axis", "y-axis", "value"))
        for i in range(len(x)):
            fo.write("{:.6f},{:.6f},{:.6f}\n".format(x[i], y[i], v[i]))
    print("Info -> extract data from {} successfully".format(xpm))
    print("Info -> data are saved into {}".format(outcsv))


def combinexpm(xpm_file_list: list, outputpng: str, noshow: bool) -> None:
    """combine xpm by scatters
    xpm_file_list : a list contains all xpm file names
    outputpng : the name for figure output
    noshow: whether not to show figure, useful for PC without gui
    """

    x_list, y_list = [], []
    xpm_title, xpm_legend, xpm_xlabel, xpm_ylabel = "", "", "", ""
    for file in xpm_file_list:
        xpm_infos = readxpm(file)
        xpm_title = xpm_infos[0]
        xpm_legend = xpm_infos[1]
        xpm_xlabel = xpm_infos[3]
        xpm_ylabel = xpm_infos[4]
        if xpm_infos[2] != "Continuous":
            print("ERROR -> can not combine xpm whose type is not Continuous")
            exit()
        x, y, _, _, _ = get_scatter_data(xpm_infos)
        x_list += x
        y_list += y

    ## combine xpm
    # plt.scatter(x_list, y_list)
    # plt.show()
    heatmap, xedges, yedges = np.histogram2d(x_list, y_list, bins=800)
    heatmap = gaussian_filter(heatmap, sigma=0.3)
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    plt.imshow(heatmap.T, origin="lower", extent=extent, cmap="coolwarm")
    plt.xlim(extent[0], extent[1])
    plt.ylim(extent[2], extent[3])

    ## set ticks and other figure infos
    ax = plt.gca()
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.1f"))
    plt.title(xpm_title)
    plt.xlabel(xpm_xlabel)
    plt.ylabel(xpm_ylabel)
    print("Legend of this xpm figure -> ", xpm_legend)
    output_filename = f"{outputpng}.png"
    if outputpng != None and os.path.exists(outputpng):
        print("ERROR -> {} already in current directory".format(outputpng))
        exit()
    if outputpng != None:
        plt.savefig(output_filename, dpi=600)
    if noshow == False:
        plt.show()


def xpm2gpl(xpm: str, outgpl: str = None) -> None:
    """convert xpm file to gnuplot scripts
    xpmfile: a list contains xpm file names
    """

    ## check files
    if not os.path.exists(xpm):
        print("ERROR -> {} not in current directory".format(xpm))
        exit()
    if xpm[-4:] != ".xpm":
        print("ERROR -> specify a file with suffix xpm")
        exit()
    if outgpl == None:
        outgpl = xpm[:-4] + ".gpl"
    if os.path.exists(outgpl):
        print("ERROR -> {} already in current directory".format(outgpl))
        exit()
    outpng = xpm[:-4] + ".png"

    ## read xpm files
    (
        xpm_title,
        xpm_legend,
        xpm_type,
        xpm_xlabel,
        xpm_ylabel,
        xpm_width,
        xpm_height,
        xpm_color_num,
        xpm_char_per_pixel,
        chars,
        colors,
        notes,
        colors_rgb,
        xpm_xaxis,
        xpm_yaxis,
        xpm_data,
    ) = readxpm(xpm)

    xpm_yaxis.reverse()

    ## write gnuplot scripts
    gpl_lines = "set term png\n"
    gpl_lines += """set output "{}" \n""".format(outpng)
    gpl_lines += "unset colorbox\n"
    pal_line = "set pal defined("
    for index, color in enumerate(colors):
        pal_line += """{} "{}",""".format(index, color)
    pal_line = pal_line.strip(",") + ")"
    gpl_lines += pal_line + "\n\n"
    ## add data lines
    gpl_lines += "$data << EOD\n"
    for l in range(len(xpm_data)):
        for i in range(0, xpm_width * xpm_char_per_pixel, xpm_char_per_pixel):
            value = chars.index(xpm_data[l][i : i + xpm_char_per_pixel])
            gpl_lines += "{:.6f} {:.6f} {:.6f}\n".format(
                xpm_xaxis[int(i / xpm_char_per_pixel)], xpm_yaxis[l], value
            )
    gpl_lines += "EOD\n\n"
    ## add tail part of gpl file
    gpl_lines += "#set tmargin at screen 0.95\n"
    gpl_lines += "#set bmargin at screen 0.20\n"
    gpl_lines += "#set rmargin at screen 0.85\n"
    y_posi = 0.92
    for index, note in enumerate(notes):
        label_line = """#set label "{:10}" at screen 0.85,{:.2f} left textcolor rgb "{}"\n""".format(
            note, y_posi, colors[index]
        )
        y_posi -= 0.10
        gpl_lines += label_line
    gpl_lines += """set term pngcairo enhanced truecolor font "Arial,85" fontscale 1 linewidth 20 pointscale 5 size 10000,6000\n"""
    gpl_lines += "set tics out nomirror;\n"
    gpl_lines += "set key out reverse Left spacing 2 samplen 1/2\n"
    gpl_lines += """set title "{}"\n""".format(xpm_title)
    gpl_lines += """set xlabel "{}"; set ylabel "{}";\n""".format(
        xpm_xlabel, xpm_ylabel
    )
    gpl_lines += """plot [{:.2f}:{:.2f}] [{:.2f}:{:.2f}] $data u 1:2:3 w imag notit, \\\n""".format(
        math.floor(min(xpm_xaxis) * 10.0) / 10.0 - 0.1,
        math.ceil(max(xpm_xaxis) * 10.0) / 10.0 + 0.1,
        math.floor(min(xpm_yaxis) * 10.0) / 10.0 - 0.1,
        math.ceil(max(xpm_yaxis) * 10.0) / 10.0 + 0.1,
    )
    for index, note in enumerate(notes):
        gpl_lines += """{} w p ps 3 pt 5 lc rgb "{}" t"{}", \\\n""".format(
            math.floor(min(xpm_yaxis)) - 1, colors[index], note
        )
    gpl_lines = gpl_lines.strip("\n").strip("\\").strip().strip(",")

    ## write gpl files
    with open(outgpl, "w") as fo:
        fo.write(gpl_lines + "\n")

    print("Info -> write gnuplot scripts {} from {} successfully".format(outgpl, xpm))


def main():
    parser = argparse.ArgumentParser(description="Process xpm files generated by GMX")
    parser.add_argument("-f", "--inputfile", help="input your xpm file")
    parser.add_argument("-o", "--outputfile", help="file name to output")
    parser.add_argument(
        "-ip",
        "--interpolation",
        action="store_true",
        default=True,
        help="whether to apply interpolation (only support Continuous type xpm)",
    )
    parser.add_argument(
        "-pcm",
        "--pcolormesh",
        action="store_true",
        default=True,
        help="whether to apply pcolormesh function to draw",
    )
    parser.add_argument(
        "-3d",
        "--threeDimensions",
        action="store_true",
        default=True,
        help="whether to draw 3D figure",
    )
    parser.add_argument(
        "-ns",
        "--noshow",
        action="store_true",
        default=True,
        help="whether not to show picture, useful on computer without gui",
    )
    parser.add_argument(
        "-c",
        "--combine",
        nargs="+",
        help="specify some xpm files to combine into one figure",
    )
    parser.add_argument(
        "-e",
        "--extract",
        help="specify xpm files to extract scatter data and save to csv file",
    )
    parser.add_argument(
        "-g",
        "--gnuplot",
        help="specify xpm files to convert into gnuplot scripts (.gpl file)",
    )
    args = parser.parse_args()

    inputxpm = args.inputfile
    output = args.outputfile
    ip = args.interpolation
    noshow = args.noshow
    xpms2combine = args.combine
    pcm = args.pcolormesh
    extract_file = args.extract
    gnuplot_file = args.gnuplot
    fig_3d = args.threeDimensions

    ## check parameters and call different functions
    if inputxpm != None and xpms2combine != None:
        print("ERROR -> do not specify -f and -c at once ")
        exit()

    if xpms2combine != None:
        combinexpm(xpms2combine, output, noshow)

    if inputxpm != None:
        if fig_3d == True:
            drawxpm_3D(inputxpm, ip, output, noshow)
        if pcm == True:
            drawxpm_newIP(inputxpm, ip, output, noshow)
        elif pcm == False and fig_3d == False:
            drawxpm_origin(inputxpm, ip, output, noshow)

    if extract_file != None:
        extract_scatter(extract_file, output)

    if gnuplot_file != None:
        xpm2gpl(gnuplot_file, output)
    dirname = f"{output}_FEL"
    os.mkdir(dirname)
    os.system(f"mv *png {dirname}")
    print("Good Day !")


if __name__ == "__main__":
    main()
