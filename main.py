import pandas as pd
import numpy as np

import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter import *
from matplotlib.figure import Figure
from collections import defaultdict
from matplotlib.widgets import RectangleSelector
from tkinter import filedialog, messagebox
import pickle

from curve_overview import Curve_overview
from coords_canvas import Coords_canvas
from plot_canvas import Plot_canvas
from result_heatmap import Result_heatmap

class SDC_analysis_main(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        frame_left = Frame(self)
        self.frame_right = LabelFrame(self, text = 'plot selected positions') #wafer, buttons...
        frame_left.pack(side = 'left', anchor = 'n')
        self.frame_right.pack(side = 'right', fill = 'both', expand = True)
        #left side
        self.bImport = Button(frame_left, text = 'import data', command = self.on_import)
        self.bImport.grid(row = 0 ,column = 0, padx = (5,5), pady = (5,50))
        self.b_project = Button(frame_left, text = 'import project', fg = 'white', bg = 'blue', command = self.on_import_project)
        self.b_project.grid(row = 0 ,column = 1, padx = (5,5), pady = (5,50))
        wFrame = LabelFrame(frame_left, text = 'measurement areas')
        self.wafer = Coords_canvas(wFrame, need_bg = False)
        self.wafer.pack()
        wFrame.grid(row = 1 ,column = 0, padx = (5,5), pady = (5,5))

        Button(frame_left, text = 'export selections', command = self.on_export_selections).grid(row = 2 ,column = 0, padx = (5,5), pady = (0,100))
        bLabel = LabelFrame(frame_left, text = 'show result', fg = 'red')
        bLabel.grid(row = 3 ,column = 0, padx = (5,5), pady = (5,5))
        Button(bLabel, text = 'curve overview', command = self.on_curve_overview).pack(padx = (5,5), pady = (2,2))
        Button(bLabel, text = 'show heatmap', fg = 'green', command = self.on_show_heatmap).pack()

        # right side
        self.plot_canvas = None


        # ______________variables_____________________________
        self.plotLines = []
        # self.data



    def on_import_project(self):
        filename = filedialog.askopenfilename(title = "choose a SDC project",filetypes = (("SDC analysis project","*.SDC"),("all files","*.*")))
        if len(filename) == 0:
            return
        with open(filename, 'rb') as f:
            etitle, potential0, self.data, mA, current_N, mA_all, wafer_clicked, x_range = pickle.load(f)
        #draw wafer coordinate
        self.wafer.x = [x for x, y in mA_all]
        self.wafer.y = [y for x, y in mA_all]
        self.wafer.ax.scatter(self.wafer.x, self.wafer.y, marker = 's', linewidths = 2, color = 'blue')# plot all imported coords
        self.wafer.format_ax()

        self.wafer.set_clicked(wafer_clicked) # highlight selection
        self.plot_selected() #plot selected curves
        self.plot_canvas.on_dragrange_project(vline_value=potential0) #plot drag vertical line
        self.plot_canvas.set_xrange_project(x_range) # plot x range
        self.on_show_heatmap_project(etitle, potential0,mA, current_N, mA_all, x_range) #deal with heatmap

        if self.b_project.cget('state') == 'normal':
            self.b_project.config(state = 'disabled')
            self.bImport.config(state = 'disabled')

    def on_curve_overview(self):
        w = Toplevel()
        w.title('overview for all the curves')
        if self.plot_canvas is None:
            Curve_overview(w, self.data, self.wafer.ax, None)
        else:
            Curve_overview(w, self.data, self.wafer.ax, self.plot_canvas.get_Xrange_Value())

    def on_show_heatmap_project(self, etitle, potential0, mA, current_N, mA_all, x_range):
        w = Toplevel()
        w.title('SDC result')

        heatmap = Result_heatmap(w,potential0 = potential0)
        #prepare parameters for heatmap
        heatmap.Etitle.insert('0', etitle) #set title
        heatmap.data, heatmap.mA, heatmap.current_N, heatmap.mA_all = self.data, mA, current_N, mA_all
        heatmap.plot_scatter() #plot scatter

        wafer_clicked = self.wafer.get_clicked()
        heatmap.set_project( wafer_clicked, x_range)



    def line_select_callback(self, eclick, erelease):
        self.wafer.line_select_callback(eclick, erelease)
        self.plot_selected()

    def on_click(self, event):
        if event.inaxes!=self.wafer.ax: return
        if self.b_project.cget('state') == 'normal':
            self.b_project.config(state = 'disabled')
        self.wafer.on_click(event)
        self.plot_selected()

    def _on_show(self):
        scatter = []
        potential0 = self.plot_canvas.rangedrag.get_vline_value()

        for x, v in self.data.items():
            for y in v.keys():
                potential, mA = self.data[x][y]
                mA0 = np.round(mA[np.abs(potential - potential0).idxmin], 3) # get nearest y value
                scatter.append((x,y,mA0))

        x1 = [x for x, y, c in scatter]
        y1 = [y for x, y, c in scatter]
        c1 = [c for x, y, c in scatter]

        w = Toplevel()
        w.title('SDC result')

        heatmap = Result_heatmap(w, x = x1, y = y1, c=c1, potential0 = round(potential0,3), data = self.data, xrange_Value = self.plot_canvas.get_Xrange_Value())
        wafer_clicked = self.wafer.get_clicked()
        x_range = self.plot_canvas.get_Xrange_Value()
        heatmap.set_project(wafer_clicked, x_range)


    def _on_clear(self):
        self.wafer._on_clear() #clear wafer
        for line in self.plotLines:
            line.remove()
        self.plotLines.clear()
        self.plot_canvas.ax.legend().set_visible(False)
        self.plot_canvas.canvas.draw()

    def plot_selected(self):
        if self.plot_canvas is None:
            self.plot_canvas = Plot_canvas(self.frame_right)
            self.plot_canvas.pack(fill = 'both', expand = True)
            self.plot_canvas.RS = RectangleSelector(self.wafer.ax, self.line_select_callback,
                                               drawtype='box', useblit=True,
                                               button=[1, 3],  # don't use middle button
                                               minspanx=5, minspany=5,
                                               spancoords='pixels',
                                               interactive=False)

        # clear old one
        for line in self.plotLines:
            line.remove()
        self.plotLines.clear()
        for x, y in self.wafer.get_clicked():
            if (x in self.data )and (y in self.data[x]):
                potential, mA = self.data[x][y]
                line, = self.plot_canvas.ax.plot(potential, mA, label = f"(x, y) =({x}, {y})")
                self.plotLines.append(line)
        self.plot_canvas.ax.legend().set_draggable(True)
        self.plot_canvas.canvas.draw()

    def on_click(self, event):
        if event.inaxes!=self.wafer.ax: return
        if self.b_project.cget('state') == 'normal':
            self.b_project.config(state = 'disabled')
        self.wafer.on_click(event)
        self.plot_selected()


    def on_show_heatmap(self):
        scatter = []
        potential0 = self.plot_canvas.rangedrag.get_vline_value()

        for x, v in self.data.items():
            for y in v.keys():
                potential, mA = self.data[x][y]
                mA0 = np.round(mA[np.abs(potential - potential0).idxmin], 3) # get nearest y value
                scatter.append((x,y,mA0))

        x1 = [x for x, y, c in scatter]
        y1 = [y for x, y, c in scatter]
        c1 = [c for x, y, c in scatter]

        w = Toplevel()
        w.title('SDC result')

        heatmap = Result_heatmap(w, x = x1, y = y1, c=c1, potential0 = round(potential0,3), data = self.data, xrange_Value = self.plot_canvas.get_Xrange_Value())
        wafer_clicked = self.wafer.get_clicked()
        x_range = self.plot_canvas.get_Xrange_Value()
        heatmap.set_project(wafer_clicked, x_range)



















def main():
    root = Tk()
    app = SDC_analysis_main(root)
    root.title('SDC analysis')
    app.pack(fill = 'both', expand=1)
    app.mainloop()

if __name__=='__main__':
    main()
