from tkinter.colorchooser import *
from matplotlib import colors
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter.colorchooser import *
from tkinter import *
from collections import defaultdict
import glob, os
import pandas as pd
import numpy as np

from coords_canvas_SDC import Coords_canvas_SDC
class Curve_overview_SDC(Frame):
    def __init__(self, master, data, master_ax, xrange_Value):
        super().__init__(master)
        self.pack()
        inf = Label(self, font= ('courier', 14))
        inf.pack(side = 'top')

        f = Frame(self)
        f.pack()

        fig = Figure(figsize=(8, 8))
        self.canvas = FigureCanvasTkAgg(fig, master=f)  # A tk.DrawingArea.
        self.ax = fig.add_subplot(111)
        self.canvas.get_tk_widget().pack()
        toolbar = NavigationToolbar2Tk(self.canvas, f)
        toolbar.update()

        self.ax.set_xlim(master_ax.get_xlim())
        self.ax.set_ylim(master_ax.get_ylim())
        self.ax.axis('off')

        xmin, xmax = self.ax.get_xlim()
        if xrange_Value is not None:
            inf.config(text = f'x range: ({xrange_Value[0]} , {xrange_Value[1]})')
        fig.subplots_adjust(left=-0.01, bottom=-0.01, right=1, top=1, wspace=0, hspace=0)

        self.ax_sub = {}
        index = 0
        insetsize = 4.2
        for x, v in data.items():
            for y in v.keys():
                potential, mA = data[x][y]
                if xrange_Value is not None:
                    ii = np.logical_and(potential > xrange_Value[0], potential < xrange_Value[1])

                    potential = potential[ii]
                    mA = mA[ii]


                self.ax_sub[index] = self.ax.inset_axes([x-insetsize/2, y-insetsize/2, insetsize, insetsize], transform=self.ax.transData)
                self.ax_sub[index].plot(potential, mA)
                self.ax_sub[index].set_facecolor('red')
                # self.ax_sub[index].tick_params(axis='both', which='both', bottom=False, top=False, labelbottom=False, right=False, left=False, labelleft=False)
                self.ax_sub[index].axis('off')

                # self.ax_sub[index].set_yticklabels([])
                # self.ax_sub[index].set_xticklabels([])
                index += 1

        self.canvas.draw()



def main():
    root = Tk()
    # path = r'C:\Users\Yu\Dropbox\PythonProgram\SDC_analysis\data\20191122-4580_v5_No2_Ag-Ir-Pd-Pt-Ru_LSV_pH13\20191122-4580_v5_No2_Ag-Ir-Pd-Pt-Ru_LSV_pH13'
    path = r'C:\Users\AI-PC2\Dropbox\PythonProgram\SDC_analysis\data\20191115-AgIrPdPtRu v5-upside down\20191105-191025-K2-1-AgIrPdPtRu_upside down_LSV_pH13'
    data_type = 'LSV2.dat'
    # filenames = filedialog.askopenfilenames(title = "choose a SDC project",filetypes = (("select LSV1 files", "*LSV1.dat"), ("select LSV2 files", "*LSV2.dat"), ("select files", "*.dat"),("all files","*.*")))
    # if len(filenames) == 0:
    #     return
    # filenames = root.tk.splitlist(path) #Possible workaround

    data = defaultdict(dict)

    xx, yy = [], []
    for i, file in enumerate(glob.glob(os.path.join(path,f'*{data_type}'))):
    # for i, file in enumerate(filenames):
        # print(file)
        x, y = [ float(n)/1000 for n in os.path.basename(file).split('.x')[0:2]] #coordinates
        xx.append(x)
        yy.append(y)
        d = pd.read_csv(file, skiprows = [i for i in range(17)], header = None)
        data[x][y] = (d.iloc[:, 2], d.iloc[:, 3]) # (x, y) = (potential, ma)

    # print(data)

    fig = Figure(figsize=(8, 8))
    ax = fig.add_subplot(111)

    wafer = Coords_canvas_SDC(root, need_bg = False)

    wafer.x, wafer.y = np.array(xx), np.array(yy)
    #draw wafer coordinate
    wafer.ax.scatter(wafer.x, wafer.y, marker = 's', linewidths = 2, color = 'blue')# plot all imported coords
    wafer.format_ax()

    app = Curve_overview_SDC(root, data, wafer.ax, [-468.485, -12.528])
    app.pack()
    root.mainloop()

if __name__ == '__main__':
    main()
