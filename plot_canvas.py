import pandas as pd
import numpy as np

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter import *
from matplotlib.figure import Figure

from vertical_drag_1 import RangeDrag
from xrangeDrag import XRangeDrag
from curve_overview import Curve_overview
class Plot_canvas(Frame):
    def __init__(self, master):
        super().__init__(master)

        #buton frame
        f = Frame(self)
        f.pack()
        self.b_xrange = Button(f, text = 'set x range', command = self.on_x_dragrange, state = 'disabled')
        self.b_xrange.grid(row =0, column =0, padx = (5,20))
        self.xrangeinf = Label(f).grid(row =0, column =1, padx = (5,20))
        Button(f, text = 'choose potential [mV]', command = self.on_dragrange).grid(row =0, column =2, padx = (5,10))
        bF = LabelFrame(f, text = 'set potential value:', fg = 'red')
        bF.grid(row =0, column =3)
        self.e_potential = Entry(bF, width = 8)
        self.e_potential.pack(side = 'left', padx = (5,0))
        Button(bF, text = 'set', command = self.on_set_potential).pack(side = 'right', padx = (0,5))

        # self.vline_inf = Label(self)

        fig = Figure()
        self.canvas = FigureCanvasTkAgg(fig, master=self)  # A tk.DrawingArea.
        self.ax = fig.add_subplot(111)
        self.canvas.get_tk_widget().pack(fill='both', expand=1)
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()

        self.ax.set_xlabel('Potential [mV]', fontsize=14)
        self.ax.set_ylabel('Current', fontsize=14)
        self.rangedrag = None
        self.x_rangeDrag = None

    def on_set_potential(self):
        if self.rangedrag is not None:
            self.rangedrag.vline_remove()
            vline_value = float(self.e_potential.get())
            self.rangedrag.rect1.set_x(vline_value - self.rangedrag.rect1.get_width()/2)
            ymin, ymax = self.ax.get_ylim()
            self.rangedrag.dr1.vline = self.ax.vlines(vline_value, ymin = ymin, ymax = ymax, color = 'red', linestyles = 'dashed')
            self.rangedrag.inf.config(text = round(self.rangedrag.rect1.get_xy()[0] + self.rangedrag.rect1.get_width()/2, 2), fg = 'red', font= ('courier', 16))
            self.canvas.draw()

    def on_dragrange(self):
        if self.rangedrag is None:
            self.rangedrag = RangeDrag(self, ax = self.ax)
            self.b_xrange.config(state = 'normal')
        self.canvas.draw()

    def on_x_dragrange(self):
        if self.x_rangeDrag is None:
            self.x_rangeDrag = XRangeDrag(self, ax = self.ax)
        self.canvas.draw()

    def get_Xrange_Value(self):
        if self.x_rangeDrag is not None:
            return self.x_rangeDrag.getRangeV()
        else:
            return None

    #set draggable x range
    def set_xrange_project(self, x_range):
        if self.x_rangeDrag is None:
            self.x_rangeDrag = XRangeDrag(self, ax = self.ax, color = 'yellow', startPos_left = x_range[0],startPos_right = x_range[1])
        self.canvas.draw()

    #for porject import
    def on_dragrange_project(self, vline_value=None):
        if self.rangedrag is None:
            self.rangedrag = RangeDrag(self, ax = self.ax, color = 'green', vline_value=vline_value)
        self.canvas.draw()



        # #plot some
        # for i in range(10):
        #     self.ax.plot(data['potential'][i], data['mA'][i], label = f"(x, y) =({data['x'][i]}, {data['y'][i]})")

    def plot_selected(self, coords):
        pass







def main():
    root = Tk()
    app = Plot_canvas(root)
    app.pack()
    app.mainloop()

if __name__=='__main__':
    main()
