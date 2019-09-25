from tkinter.colorchooser import *
from matplotlib import colors
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter.colorchooser import *
from tkinter import *

import numpy as np


class Curve_overview_heatmap(Frame):
    def __init__(self, master, data, ma,  master_ax,cax,xrange_Value):
        super().__init__(master)
        self.pack()
        # inf = Label(self, font= ('courier', 14))
        # inf.pack(side = 'top')

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

        if xrange_Value is not None:
            # inf.config(, fg = 'blue')
            text = f'x range: ({xrange_Value[0]} , {xrange_Value[1]})'
            self.ax.set_title(text, fontsize = 12)
        fig.subplots_adjust(left=0.01, bottom=0.0, right=0.9, top=0.95, wspace=0, hspace=0)

        self.ax_sub = {}
        index = 0
        insetsize = 4.2
        for x, y in ma:
            potential, mA = data[x][y]
            if xrange_Value is not None:
                ii = np.logical_and(potential > xrange_Value[0], potential < xrange_Value[1])
                potential = potential[ii]
                mA = mA[ii]
            self.ax_sub[index] = self.ax.inset_axes([x-insetsize/2, y-insetsize/2, insetsize, insetsize], transform=self.ax.transData)
            self.ax_sub[index].plot(potential, mA, color = cax.to_rgba(ma[(x,y)]))
            self.ax_sub[index].set_facecolor('red')
            # self.ax_sub[index].tick_params(axis='both', which='both', bottom=False, top=False, labelbottom=False, right=False, left=False, labelleft=False)
            self.ax_sub[index].axis('off')

            # self.ax_sub[index].set_yticklabels([])
            # self.ax_sub[index].set_xticklabels([])
            index += 1
        c = np.array([ma[(x,y)] for x,y in ma])
        self.cbar = fig.colorbar(cax, ax = self.ax, ticks = np.round(np.linspace(start = min(c), stop = max(c), num =9), 3), fraction=0.026, pad=0.05)

        self.canvas.draw()



