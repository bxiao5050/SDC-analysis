import pandas as pd
import numpy as np

import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter import *
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector



class Coords_canvas_SDC(Frame):
    '''show canvas in scatter
    '''
    def __init__(self, master,need_bg = True):
        super().__init__(master)
        self.width = 4
        self.b_clear = Button(self, text = 'unselect all', fg = 'blue', command = self._on_clear)
        self.b_clear.pack()

        fig = Figure(figsize=(4, 4))
        self.canvas = FigureCanvasTkAgg(fig, master=self)  # A tk.DrawingArea.
        self.ax = fig.add_subplot(111)
        self.canvas.get_tk_widget().pack(fill='both', expand=1)
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        #formatted coordinates
        self.x, self.y = None, None

        if need_bg:
            coords = pd.read_csv('coords.txt', header = None)
            #change unit to mm
            self.x, self.y = coords.iloc[:,0].to_numpy()/1000, coords.iloc[:,1].to_numpy()/1000
            scatter_bg = self.ax.scatter(self.x, self.y, marker = 's', linewidths = 2, color = 'lightgray')# plot all the coords
            self.format_ax()

        self.clicked_xy=[]
        self.plot_clicked = []

    def format_ax(self):
        self.ax.format_coord = self.format_coord
        xmin, xmax = self.ax.get_xlim()
        ymin, ymax = self.ax.get_ylim()
        self.ax.set_xlabel('X (mm)')
        self.ax.set_ylabel('Y (mm)')

        self.ax.invert_yaxis()


        self.cid1 = self.canvas.mpl_connect('button_press_event', self.on_click)
        #__________________uncomment when multi-mouse selection needed______________
        # self.RS = RectangleSelector(self.ax, self.line_select_callback,
        #                                        drawtype='box', useblit=True,
        #                                        button=[1, 3],  # don't use middle button
        #                                        minspanx=5, minspany=5,
        #                                        spancoords='pixels',
        #                                        interactive=False)

  #for porject import
    def set_clicked(self, wafer_clicked):
        self.clicked_xy = wafer_clicked
        self.updata_canvas()

   #formatted coordinates
    def format_coord(self, xdata,ydata):
        try:
            index_x = np.abs(self.x-xdata) < self.width/2
            index_y = np.abs(self.y-ydata) < self.width/2
            click_x = self.x[index_x][0] if len(self.x[index_x]) >0 else None
            click_y = self.y[index_y][0] if len(self.y[index_y]) >0 else None
            X = np.where(self.x == click_x)[0]
            Y =np.where(self.y == click_y)[0]

            if len(np.intersect1d(X, Y)): #find commen value between two arrays
                return f'(x, y) = ({click_x}, {click_y})'
            else:
                return []
        except:
            pass

    #return clicked positions
    def get_clicked(self):
        return list(set(self.clicked_xy))

    def _on_clear(self):
        for line in self.plot_clicked:
            line.remove()
        self.clicked_xy.clear()
        self.plot_clicked.clear()
        self.canvas.draw()


    def on_click(self, event):
        if event.inaxes!=self.ax: return
        self.get_click_xy(event.xdata, event.ydata)


    # return clicked x, y
    def get_click_xy(self, xdata, ydata):
        index_x = np.abs(self.x-xdata) < self.width/2
        index_y = np.abs(self.y-ydata) < self.width/2
        click_x = self.x[index_x][0] if len(self.x[index_x]) >0 else None
        click_y = self.y[index_y][0] if len(self.y[index_y]) >0 else None
        X = np.where(self.x == click_x)[0]
        Y =np.where(self.y == click_y)[0]

        if len(np.intersect1d(X, Y)): #find commen value between two arrays
            if (click_x, click_y) in self.get_clicked(): # click again then remove
                self.clicked_xy.remove((click_x, click_y))
            else:
                self.clicked_xy.append((click_x, click_y))

        self.updata_canvas()

    def line_select_callback(self, eclick, erelease):
        'eclick and erelease are the press and release events'
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata

        # self.clicked_xy = []
        for x, y in zip(self.x, self.y):
            if x> min(x1, x2) and x < max(x1, x2) and y > min(y1, y2) and y< max(y1, y2):
                self.clicked_xy.append((x,y))

        self.updata_canvas()
        # return clicked_xy

    def updata_canvas(self):
        #clear all highlights
        for line in self.plot_clicked:
            line.remove()
        self.plot_clicked.clear()

        x = [x for x, y in self.clicked_xy]
        y = [y for x, y in self.clicked_xy]
        line, = self.ax.plot(x, y,linestyle='none', marker='s', markeredgecolor="orange",markersize = 7, markerfacecolor='red',markeredgewidth =2)
        self.plot_clicked.append(line)
        self.canvas.draw()










def main():
    root = Tk()
    app = Coords_canvas_SDC(root)
    app.pack()
    app.mainloop()

if __name__=='__main__':
    main()
