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

from coords_canvas import Coords_canvas
from plot_canvas import Plot_canvas
from result_heatmap import Result_heatmap




from coords_canvas import Coords_canvas



from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter import *
from matplotlib.figure import Figure

from vertical_drag_1 import RangeDrag
from xrangeDrag import XRangeDrag
from curve_overview import Curve_overview




class XRangeDrag():
    def __init__(self, master, color = 'blue', ax = None, startPos_left = None,startPos_right = None):


        if ax is None:
            f = Figure(figsize=(5, 4), dpi=100)
            ax = f.add_subplot(111, picker = True)
            # ax.set_xlim(0, 20)

            self.canvas = FigureCanvasTkAgg(f, master=master)
            self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

        self.inf = Label(master)
        self.inf.pack()



        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()
        self.width = abs(xmax-xmin)/150

        if startPos_left is None:
            startPos_left = np.random.randint(xmin - self.width, xmax, size = 1)
        if startPos_right is None:
            startPos_right = startPos_left + self.width*5

        self.rect1 = ax.bar(startPos_left+self.width/2,bottom = ymin, height = abs(ymax-ymin)*0.95,  color = color, width = self.width, alpha = 0.4)[0]
        self.rect2 = ax.bar(startPos_right+self.width/2,bottom = ymin, height = abs(ymax-ymin)*0.95,  color = color, width = self.width, alpha = 0.4)[0]

        self.middle = ax.bar((self.rect2.xy[0] + self.rect1.xy[0] + self.width)/2,bottom = ymin, height = abs(ymax-ymin)*0.95,  color = color, alpha = 0.05, width = self.rect2.xy[0] - self.rect1.xy[0] - self.width)[0]
        # self.middle = ax.bar((self.rect2.xy[0] + self.rect1.xy[0])/2, ymax,  color = color, alpha = 0.1, width = self.rect2.xy[0] - self.rect1.xy[0] )[0]
        l1 = self.rect1.xy[0]
        l2 = self.rect2.xy[0]
        # self.inf.config(text = '{:.3f}'.format(min(l1, l2)) + ' - ' + '{:.3f}'.format(max(l1, l2)))

        self.dr1 = self.DraggableRectangle(self.rect1, self.middle, self.rect2, self.inf, self.width)
        self.dr2 = self.DraggableRectangle(self.rect2, self.middle, self.rect1, self.inf, self.width )
        self.dr3 = self.DraggableRectangle(self.middle, self.rect1, self.rect2, self.inf, self.width, ismiddle = True)
        self.dr1.connect()
        self.dr2.connect()
        self.dr3.connect()
        # plt.show()

    def getXrange(self):
        return self.inf.cget('text')

    def getRangeV(self):
        return [float(i) for i in self.getXrange().replace('x range: (', '').replace(')', '').split(' , ')]


    def changeColor(self, color):
        self.rect1.set_color(color)
        self.rect2.set_color(color)
        self.middle.set_color(color)
        self.rect1.figure.canvas.draw()



    class DraggableRectangle:
        lock = None  # only one can be animated at a time

        def __init__(self, rect, middle, other, inf, width, ismiddle = False):

            self.middle = middle
            self.rect = rect
            self.other = other
            self.press = None
            self.background = None
            self.width = width
            self.inf = inf
            self.ismiddle = ismiddle



        def connect(self):
            'connect to all the events we need'

            self.cidpress = self.rect.figure.canvas.mpl_connect(
                'button_press_event', lambda event: self.on_press(event))
            self.cidrelease = self.rect.figure.canvas.mpl_connect(
                'button_release_event', lambda event: self.on_release(event))
            self.cidmotion = self.rect.figure.canvas.mpl_connect(
                'motion_notify_event', lambda event: self.on_motion(event))

        def on_press(self, event):
            'on button press we will see if the mouse is over us and store some data'
            if event.inaxes != self.rect.axes: return
            if self.lock is not None: return
            contains, attrd = self.rect.contains(event)
            if not contains: return

            if self.ismiddle == True:
                self.l10 = self.middle.xy[0]
                self.l20 = self.other.xy[0]
                self.other.set_animated(True)


            x0, y0 = self.rect.xy
            self.press = x0, y0, event.xdata, event.ydata
            self.lock = self

            # draw everything but the selected rectangle and store the pixel buffer
            canvas = self.rect.figure.canvas
            axes = self.rect.axes
            self.rect.set_animated(True)
            self.middle.set_animated(True)
            canvas.draw()
            self.background = canvas.copy_from_bbox(self.rect.axes.bbox)

            # now redraw just the rectangle
            axes.draw_artist(self.rect)

            # and blit just the redrawn area
            canvas.blit(axes.bbox)

        def on_motion(self, event):
            self.motion(event)

        def motion(self, event):
            'on motion we will move the rect if the mouse is over us'
            if self.lock is not self:
                return
            if event.inaxes != self.rect.axes: return
            x0, y0, xpress, ypress = self.press
            dx = event.xdata - xpress


            if self.ismiddle == False:
                l1 = self.rect.xy[0]
                l2 = self.other.xy[0]
                self.rect.set_x(x0+dx)
                self.middle.set_x(min(l1, l2) + self.width)
                self.middle.set_width(max(l1, l2) - min(l1, l2) - self.width)
            elif self.ismiddle == True:
                l1 = self.middle.xy[0]
                l2 = self.other.xy[0]

                self.middle.set_x(self.l10+dx)
                self.other.set_x(self.l20+dx)

                self.rect.set_x(min(l1, l2) + self.width)
                self.rect.set_width(max(l1, l2) - min(l1, l2) - self.width)

            self.inf.config(text = 'x range: ({:.3f}'.format(min(l1, l2)) + ' , ' + '{:.3f}'.format(max(l1, l2)) + ')')


            canvas = self.rect.figure.canvas
            axes = self.rect.axes



            # restore the background region
            canvas.restore_region(self.background)
            axes.draw_artist(self.rect)
            canvas.blit(axes.bbox)

        def on_release(self, event):
            'on release we reset the press data'
            if self.lock is not self:
                return

            self.press = None
            self.lock = None

            # turn off the rect animation property and reset the background
            self.rect.set_animated(False)
            self.middle.set_animated(False)
            self.other.set_animated(False)
            self.background = None

            # redraw the full figure
            self.rect.figure.canvas.draw()




class RangeDrag(Frame):
    def __init__(self, master, color = 'orange', ax = None, v1 = None, vline_value = None):
        super().__init__(master)


        if ax is None:
            f = Figure(figsize=(5, 4), dpi=100)
            ax = f.add_subplot(111, picker = True)

            self.canvas = FigureCanvasTkAgg(f, master=master)
            self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

        self.inf = Label(master)
        self.inf.pack()

        xmin, xmax = ax.get_xlim() #fix ax
        # ax.set_xlim(ax.get_xlim())

        ymin, ymax = ax.get_ylim()
        ax.set_ylim(ax.get_ylim())
        if v1 is None:
            v1 = 0.9*ymax
            # v1 = np.random.randint(xmin - self.width, xmax, size = 1)

        if vline_value is None:
            self.vline_value = (xmax+xmin)/2
        else:
            self.vline_value=vline_value
        self.rect1 = ax.bar(self.vline_value,bottom = ymin, height = abs(ymax-ymin)*2, align = 'center', color = color, width = abs(xmax-xmin)/50, alpha = 0.2)[0]
        self.inf.config(text = round(self.vline_value, 2), fg = 'red', font= ('courier', 16))
        vline = ax.vlines(self.vline_value, ymin = ymin, ymax = ymax, color = 'red', linestyles = 'dashed')

        self.dr1 = self.DraggableRectangle(self.rect1, ax, vline, self.inf)
        self.dr1.connect()

    def get_vline_value(self):
        return float(self.inf.cget('text'))

    def getRangeV(self):
        return [float(i) for i in self.getXrange().split(' - ')]

    def changeColor(self, color):
        self.rect1.set_color(color)
        self.rect2.set_color(color)
        self.middle.set_color(color)
        self.rect1.figure.canvas.draw()

    def vline_remove(self):
        self.dr1.vline.remove()


    class DraggableRectangle:
        lock = None  # only one can be animated at a time

        def __init__(self, rect1, ax, vline, inf):
            # self.line_and_text = []
            self.rect1 = rect1
            self.vline = vline
            self.inf = inf

            self.ax = ax
            self.press = None
            self.background = None

        def connect(self):
            'connect to all the events we need'

            self.cidpress = self.rect1.figure.canvas.mpl_connect(
                'button_press_event', lambda event: self.on_press(event))
            self.cidrelease = self.rect1.figure.canvas.mpl_connect(
                'button_release_event', lambda event: self.on_release(event))
            self.cidmotion = self.rect1.figure.canvas.mpl_connect(
                'motion_notify_event', lambda event: self.on_motion(event))

        def on_press(self, event):
            'on button press we will see if the mouse is over us and store some data'
            if event.inaxes != self.rect1.axes: return
            if self.lock is not None: return
            contains, attrd = self.rect1.contains(event)
            if not contains: return

            # if self.ismiddle == True:
            self.vline.remove()
            self.l10 = self.rect1.xy[0]
            # self.l20 = self.rect2.xy[1]

            x0, y0 = self.rect1.xy
            self.press = x0, y0, event.xdata, event.ydata
            self.lock = self

            # draw everything but the selected rectangle and store the pixel buffer
            canvas = self.rect1.figure.canvas
            axes = self.rect1.axes
            self.rect1.set_animated(True)

            canvas.draw()
            self.background = canvas.copy_from_bbox(self.rect1.axes.bbox)

            # now redraw just the rectangle
            axes.draw_artist(self.rect1)

            # and blit just the redrawn area
            canvas.blit(axes.bbox)

        def on_motion(self, event):
            self.motion(event)

        def motion(self, event):
            'on motion we will move the rect if the mouse is over us'
            if self.lock is not self:
                return
            if event.inaxes != self.rect1.axes: return
            x0, y0, xpress, ypress = self.press
            dx = event.xdata - xpress

            self.rect1.set_x(self.l10+dx)

            canvas = self.rect1.figure.canvas
            axes = self.rect1.axes

            # restore the background region
            canvas.restore_region(self.background)
            axes.draw_artist(self.rect1)
            canvas.blit(axes.bbox)

            self.inf.config(text = round(self.rect1.get_xy()[0] + self.rect1.get_width()/2, 2), fg = 'red', font= ('courier', 16))

        def on_release(self, event):
            'on release we reset the press data'
            if self.lock is not self:
                return

            self.press = None
            self.lock = None
            ymin, ymax = self.ax.get_ylim()
            # y1 = min(self.rect1.get_xy()[1], self.rect2.get_xy()[1])
            # y2 = max(self.rect1.get_xy()[1], self.rect2.get_xy()[1])

            self.vline_value= self.rect1.get_xy()[0] + self.rect1.get_width()/2

            self.vline = self.ax.vlines(self.vline_value, ymin = ymin, ymax = ymax, color = 'red', linestyles = 'dashed')

            self.rect1.set_animated(False)
            self.background = None

            # redraw the full figure
            self.rect1.figure.canvas.draw()






class ShowHist(LabelFrame):
    def __init__(self, master):
        super().__init__(master)
        self.config(text = f'distribution')
        fig = Figure(figsize = (4.5,2.5))
        self.ax = fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(fig, master = self)
        self.canvas.get_tk_widget().pack(fill = 'both', expand = True)
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()

    def update(self, values):
        text = f'distribution for all {len(values)}'
        # self.config(text = text)
        self.ax.clear()
        self.ax.set_title(text)

        # values = [v for v in results.values()]

        self.ax.grid(zorder=0)
        n, bins, patches=self.ax.hist(x = values, facecolor='green', alpha=0.5, rwidth=0.85)
        self.ax.set_xlabel('mA')
        self.ax.set_ylabel('numbers')
        start, end = self.ax.get_ylim()
        self.ax.yaxis.set_ticks(np.round(np.linspace(start, end, num=10)))

        # self.ax.set_title(f'Thickness distribution for all {len(results)}')
        self.canvas.draw()




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

    wafer = Coords_canvas(root, need_bg = False)

    wafer.x, wafer.y = np.array(xx), np.array(yy)
    #draw wafer coordinate
    wafer.ax.scatter(wafer.x, wafer.y, marker = 's', linewidths = 2, color = 'blue')# plot all imported coords
    wafer.format_ax()

    app = Curve_overview(root, data, wafer.ax, [-468.485, -12.528])
    app.pack()
    root.mainloop()


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

    def on_import(self):
        # path = r'C:\Users\Yu\Dropbox\PythonProgram\SDC_analysis\data\20191122-4580_v5_No2_Ag-Ir-Pd-Pt-Ru_LSV_pH13\20191122-4580_v5_No2_Ag-Ir-Pd-Pt-Ru_LSV_pH13'
        # data_type = 'LSV2.dat'
        filenames = filedialog.askopenfilenames(title = "choose a SDC project",filetypes = (("select LSV1 files", "*LSV1.dat"), ("select LSV2 files", "*LSV2.dat"), ("select files", "*.dat"),("all files","*.*")))
        if len(filenames) == 0:
            return
        filenames = self.tk.splitlist(filenames) #Possible workaround

        self.data = defaultdict(dict)
        # for i, file in enumerate(glob.glob(os.path.join(path,f'*{data_type}'))):
        xx, yy = [], []
        for i, file in enumerate(filenames):
            x, y = [ float(n)/1000 for n in os.path.basename(file).split('.x')[0:2]] #coordinates
            xx.append(x)
            yy.append(y)
            d = pd.read_csv(file, skiprows = [i for i in range(17)], header = None)
            self.data[x][y] = (d.iloc[:, 2], d.iloc[:, 3]) # (x, y) = (potential, ma)
        self.wafer.x, self.wafer.y = np.array(xx), np.array(yy)
        #draw wafer coordinate
        self.wafer.ax.scatter(self.wafer.x, self.wafer.y, marker = 's', linewidths = 2, color = 'blue')# plot all imported coords
        self.wafer.format_ax()

        #override button
        self.wafer.b_clear.config(command = self._on_clear)
        self.wafer.canvas.mpl_disconnect(self.wafer.cid1)
        #override the self.wafer interactive methods
        self.wafer.canvas.mpl_connect('button_press_event', self.on_click)

        self.wafer.canvas.draw()

        if self.b_project.cget('state') == 'normal':
            self.b_project.config(state = 'disabled')
            self.bImport.config(state = 'disabled')
        messagebox.showinfo(title = None, message = f'total {len(filenames)} files imported')

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

    def on_curve_overview(self):
        w = Toplevel()
        w.title('overview for all the curves')
        if self.plot_canvas is None:
            Curve_overview(w, self.data, self.wafer.ax, None)
        else:
            Curve_overview(w, self.data, self.wafer.ax, self.plot_canvas.get_Xrange_Value())


    def line_select_callback(self, eclick, erelease):
        self.wafer.line_select_callback(eclick, erelease)
        self.plot_selected()

    def on_click(self, event):
        if event.inaxes!=self.wafer.ax: return
        if self.b_project.cget('state') == 'normal':
            self.b_project.config(state = 'disabled')
        self.wafer.on_click(event)
        self.plot_selected()


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


    def on_export_selections(self):
        df = pd.DataFrame()
        for x, y in self.wafer.get_clicked():
            if (x in self.data )and (y in self.data[x]):
                potential, mA = self.data[x][y]
                df.insert(len(df.columns), 'potential'+ f"({x}, {y})", potential)
                df.insert(len(df.columns), 'mA' + f"({x}, {y})", mA)
        filename = filedialog.asksaveasfilename(title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*")))
        df.to_csv(filename + '.csv', index = False)
        if len(filename) > 0:
            messagebox.showinfo(title = None, message = 'file saved!')


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

    root.title('SDC analysis')
    app.pack(fill = 'both', expand=1)
    app.mainloop()

if __name__=='__main__':
    main()
