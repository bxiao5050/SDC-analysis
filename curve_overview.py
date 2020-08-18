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

from coords_canvas import Coords_canvas
class Curve_overview(Frame):
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


        self.canvas.draw()



