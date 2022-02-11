import pandas as pd
import numpy as np
from collections import defaultdict
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter import *
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector
from matplotlib import cm
from tkinter import filedialog, messagebox,  Scale
from tkinter.ttk import Combobox
import pandas as pd
from tkinter import filedialog, messagebox
import pickle
from mpl_toolkits.mplot3d import axes3d

from showHist_SDC import ShowHist_SDC
from curve_overview_heatmap import Curve_overview_heatmap
from publication_SDC import Publication_SDC

class Result_heatmap(Frame):
    def __init__(self, master, x = None, y = None, c = None, potential0 = None, data= None, xrange_Value = None ):
        super().__init__(master)
        self.pack()
        self.sc_potential_var = DoubleVar()
        self.sc_potential_var.set(potential0)
        potential_range, xx = data[0][0] #get potential range

        bFrame = Frame(self) #buttons frame
        cFrame = Frame(self) #canvas frame
        scFrame = LabelFrame(self, text = 'change potential', fg='violet red')
        titleF = Frame(self)

        bFrame.pack()
        cFrame.pack()
        scFrame.pack()
        titleF.pack()

        l1 = LabelFrame(bFrame, text = 'select')
        Button(l1, text = 'unselect all',width = 10, command = self._on_clear).grid(row = 0, column =0, padx = (2,2), pady = (2,2))
        Button(l1, text = 'select inverse',width = 10, command = self._on_inverse).grid(row = 1, column =0, padx = (2,2), pady = (2,2))
        Button(l1, text = 'delete selected',width = 12, fg = 'red', command = self._on_delete).grid(row = 0, column =1, padx = (2,2), pady = (2,2))
        Button(l1, text = 'advanced select',width = 12, fg = 'blue', command = self._on_advanced_selection).grid(row = 1, column =1, padx = (2,2), pady = (2,2))
        l2 = LabelFrame(bFrame, text = 'show')
        Button(l2, text = 'plot selected', width = 10, command = self._on_plot_selected).grid(row = 0, column =0, padx = (2,2), pady = (2,2))
        Button(l2, text = 'overview', width = 10, command = self._on_plot_overview).grid(row = 0, column =1, padx = (2,2), pady = (2,2))
        Button(l2, text = 'distribution', width = 10, command = self._on_distribution).grid(row = 1, column =0, padx = (2,2), pady = (2,2))
        l3 = LabelFrame(bFrame, text = 'save')
        Button(l3, text = 'save to .csv',width = 10, fg = 'green', command = self._on_save).pack( padx = (2,2), pady = (2,2))
        Button(l3, text = 'save project',width = 10, bg = 'blue', fg = 'white', command = self._on_save_project).pack( padx = (2,2), pady = (2,2))
        l4 = LabelFrame(bFrame, text = 'regret', fg = 'blue')
        Button(l4, text = 'undo',width = 6, command = self._on_undo).pack( padx = (2,2), pady = (2,2))
        Button(l4, text = 'redo',width = 6, command = self._on_redo).pack( padx = (2,2), pady = (2,2))
        l5 = LabelFrame(bFrame, text = 'visualization')
        self.brotate = Button(l5, text = '45 deg clockwise', width = 16, state = 'disabled', command = self._on_rotate)
        self.brotate.grid(row =0, column=0, columnspan = 2, padx = (2,2), pady = (2,2))
        Button(l5, text = 'flip colorbar', width = 10, command = self._on_flip_colorbar).grid(row =1, column=0, padx = (2,2), pady = (2,2))
        self.b3D = Button(l5, text = '3D', width = 4, command = self._on_3D)
        self.b3D.grid(row =1, column=1, padx = (2,2), pady = (2,2))
        lf51 = LabelFrame(l5, text = 'choose color', fg = 'blue')
        lf51.grid(row =2, column=0, columnspan = 2)
        self.cb_color = Combobox(lf51, values = ['jet','rainbow','viridis', 'Greys', 'Reds', 'Blues', 'Purples', 'Greens'])
        self.cb_color.pack()
        self.cb_color.current(0)
        self.cb_color.bind('<<ComboboxSelected>>', self.on_colorchange)

        self.l6 = LabelFrame(bFrame, text = 'set colorbar unit', fg = 'green')
        self.e_unitV = Entry(self.l6, width = 9)
        self.e_unitU = Entry(self.l6, width = 9)
        self.e_unitV.insert(0, '0.007352')
        self.e_unitU.insert(0, 'mA')
        self.e_unitV.grid(row = 0, column = 0,pady = (2,2))
        self.e_unitU.grid(row = 0, column = 1, pady = (2,2))
        fff = Frame(self.l6)
        fff.grid(row = 1, column = 0, columnspan = 2, sticky ='e',  pady = (5,2))
        Button(fff, text = 'export',  command = self._on_unit_export).grid(row = 0, column = 0, sticky ='e',  pady = (5,2))
        Button(fff, text = 'import',  command = self._on_unit_import).grid(row = 0, column = 1, sticky ='e',  pady = (5,2))
        Button(fff, text = 'set', command = self._on_unit).grid(row = 0, column = 2,sticky ='e',  pady = (5,2))

        sc_potential = Scale(scFrame,from_ =min(potential_range), to = max(potential_range), orient = 'horizontal', command = self._on_potential_scale, variable = self.sc_potential_var, length = 550, resolution = 0.2 )
        sc_potential.pack()

        l7 = LabelFrame(bFrame, text = 'fig setting')
        Button(l7, text = 'publication', command = self.on_fig_publication).pack()

        l1.pack(side = 'left', padx = (2,2), anchor = 'n')
        l2.pack(side = 'left', padx = (2,2), anchor = 'n')
        l4.pack(side = 'left', padx = (2,2), anchor = 'n')
        l5.pack(side = 'left', padx = (2,2), anchor = 'n')
        self.l6.pack(side = 'right', anchor = 'n')

        self.Etitle = Entry(titleF, text = ' ', fg = 'blue', width = 50, font = ('courier', 14, 'bold'))
        self.Etitle.pack(pady = (10,0))
        l7.pack(side = 'left', padx = (2,2), anchor = 'n')
        l3.pack(side = 'left', padx = (2,2), anchor = 'n')

        self.width = 4

        self.fig = Figure(figsize=(7, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)  # A tk.DrawingArea.
        self.ax = self.fig.add_subplot(111)
        self.canvas.get_tk_widget().pack()
        toolbar = NavigationToolbar2Tk(self.canvas,  self)
        toolbar.update()
        self.setup_ax()

        # self.ax.scatter(x, y, marker = 's', linewidths = 2, color = 'lightgray')# plot all the coords

        self.cbar = None #colarbar for corlormap

        self.colormaptype = self.cb_color.get() #'jet' or 'jet_r'
        self.deg_rotate = 0
        self.potential0 = potential0
        self.data = data

        self.mA = []# could be changed
        self.current_N = 0 # store self.mA for redo and undo
        self.mA_all = {}# could not be changed

        self.x_range = xrange_Value # x range used for  plotting overview


        ma = {}
        if x is not None:
            for xx, yy, cc in zip(x, y, c):
                ma[(xx,yy)] = cc
                self.mA_all[(xx,yy)] = cc
            self.mA.append(ma) #version n = 0
        # self.current_N+=1

        self.clicked_xy=[]
        self.plot_clicked = []

        if x is not None:
            self.plot_scatter()

    def on_fig_publication(self):
        w = Toplevel()

        ma = self.mA[self.current_N]
        c = np.array([ma[(x,y)] for x,y in ma])
        x = np.array([x for x, y in ma])
        y = np.array([y for x, y in ma])

        fig = Figure(figsize=(7.5, 6), dpi = 100)
        ax = fig.add_subplot(111)

        cax=ax.scatter(x, y, c = c, s = 140, cmap = 'jet', marker = 's')
        cbar=fig.colorbar(cax, ticks = np.linspace(min(c), max(c), num = 9))

        cbar.ax.set_title('mA')
        # ax.set_title('\t')

        app = Publication_SDC(w,  c, ax,fig, cbar, cax)
        app.pack(fill = 'both', expand =1)



    def on_colorchange(self, e):
        self.cax.set_cmap(cm.get_cmap(self.cb_color.get()))
        self.colormaptype = self.cb_color.get()
        self.canvas.draw()

    def _on_plot_overview(self):
        w = Toplevel()
        w.title('overview for curves based on colormap')

        ma = self.mA[self.current_N]

        #self.cax is the scater plot
        Curve_overview_heatmap(w, self.data, ma, self.ax, self.cax, xrange_Value = self.x_range)
        # Curve_overview(w, self.data, self.wafer.ax, self.plot_canvas.get_Xrange_Value())

    def _on_unit_export(self):
        filename = filedialog.asksaveasfilename(title = "Select file",filetypes = (("colorbar unit","*.colorbar_unit"),("all files","*.*")))
        with open(filename + '.colorbar_unit', 'wb') as f:
            d = [self.e_unitV.get(), self.e_unitU.get()]
            pickle.dump(d, f, protocol = -1)
            if len(filename) > 0:
                messagebox.showinfo(title = None, message = f' file "{filename}.colorbar_unit" saved!')

    def _on_unit_import(self):
        filename = filedialog.askopenfilename(title = "choose a colorbar unit",filetypes = (("colorbar unit","*.colorbar_unit"),("all files","*.*")))
        if len(filename) == 0:
            return
        with open(filename, 'rb') as f:
            d = pickle.load(f)
            self.e_unitV.delete(0, 'end'), self.e_unitU.delete(0, 'end')
            self.e_unitV.insert(0, d[0]), self.e_unitU.insert(0, d[1])

    def setup_ax(self):
        self.ax.format_coord = self.format_coord
        self.ax.invert_yaxis()

        self.cid1 = self.canvas.mpl_connect('button_press_event', self.on_click)
        # __________________uncomment when multi-mouse selection needed______________
        self.RS = RectangleSelector(self.ax, self.line_select_callback,
                                               drawtype='box', useblit=True,
                                               button=[1, 3],  # don't use middle button
                                               minspanx=5, minspany=5,
                                               spancoords='pixels',
                                               interactive=False)
    def _on_unit(self):
        ma = self.mA[self.current_N]
        ma_original = self.mA[0].copy() #original ma, is defined when heatmap is created
        cm = float(self.e_unitV.get())
        for x, y in ma:
            ma[(x, y)] = round(ma_original[(x,y)]/cm,2)

        # self.mA.append(ma)#save it as the new version
        # self.current_N+=1 #establish a new version
        self.plot_scatter() #redraw scatter

        self.l6.config(text = self.e_unitU.get())


    def _on_flip_colorbar(self):
        # print(dir(self.cax))
        if '_r' not in self.colormaptype :
            self.cax.set_cmap(cm.get_cmap(self.colormaptype+'_r'))
            self.colormaptype = self.colormaptype+'_r'
        elif '_r' in self.colormaptype :
            self.cax.set_cmap(cm.get_cmap(self.colormaptype.replace('_r', '')))
            self.colormaptype = self.colormaptype.replace('_r', '')
        self.canvas.draw()

    def _on_rotate(self):
        if self.b3D.cget('text') == '2D':
            self.deg_rotate +=45
            self.ax.elev = 90
            self.ax.azim  = self.deg_rotate
            self.canvas.draw()

    def _on_3D(self):
        self.fig.delaxes(self.ax)
        if self.b3D.cget('text') == '3D':
            self.b3D.config(text = '2D')
            self.brotate.config(state = 'normal')
            self.deg_rotate = 90
            self.ax=self.fig.add_subplot(111,projection='3d')
            self.ax.dist = 5.5
            self.ax.elev = 90
            self.ax.azim  = self.deg_rotate
            self.ax.set_zticks([])
            # make the panes transparent
            self.ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            self.ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            self.ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            # make the grid lines transparent
            self.ax.xaxis._axinfo["grid"]['color'] =  (1,1,1,0)
            self.ax.yaxis._axinfo["grid"]['color'] =  (1,1,1,0)
            self.ax.zaxis._axinfo["grid"]['color'] =  (1,1,1,0)
            self.ax.invert_yaxis()
            self.plot_scatter(is_title = False)
            self.cax.set_edgecolors = self.cax.set_facecolors = lambda *args:None
            self.scatter_deleted.set_edgecolors = self.scatter_deleted.set_facecolors = lambda *args:None

        elif self.b3D.cget('text') == '2D':
            self.b3D.config(text = '3D')
            self.brotate.config(state = 'disabled')
            # self.fig.set_size_inches(6,5)
            self.ax = self.fig.add_subplot(111)
            self.plot_scatter()
            self.setup_ax()

        self.canvas.draw()


    def _on_save_project(self):
        filename = filedialog.asksaveasfilename(title = "Select file",filetypes = (("SDC analysis files","*.SDC"),("all files","*.*")))
        with open(filename + '.SDC', 'wb') as f:
            d = [self.Etitle.get(), self.potential0, self.data, self.mA, self.current_N, self.mA_all, self.wafer_clicked, self.x_range]
            pickle.dump(d, f, protocol = -1)
            if len(filename) > 0:
                messagebox.showinfo(title = None, message = f'project file "{filename}.SDC" saved!')

    def set_project(self, wafer_clicked, x_range):
         self.wafer_clicked =  wafer_clicked
         self.x_range = x_range


    def _on_distribution(self):
        w = Toplevel()
        hist = ShowHist_SDC(w)
        hist.pack()
        ma = self.mA[self.current_N]
        hist.update([ma[(x,y)] for x, y in ma])

    def _on_undo(self):
        if self.current_N > 0:
            self.current_N -= 1
        self.plot_scatter()


    def _on_redo(self):
        if self.current_N < len(self.mA) - 1:
            self.current_N += 1
        self.plot_scatter()


    def _on_save(self):
        df = pd.DataFrame()
        ma = self.mA[self.current_N]

        df['X'] = [x for x,y in ma]
        df['Y'] = [y for x,y in ma]
        df['mA'] = [ma[(xx,yy)] for (xx, yy) in ma]
        filename = filedialog.asksaveasfilename(title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*")))
        df.to_csv(filename + '.csv', index = False)
        if len(filename) >0:
            messagebox.showinfo(title = None, message = f'"{filename}" file saved!')

    def _on_inverse(self):
        ma = self.mA[self.current_N]
        inverse = []
        for x, y in ma:
            if (x, y) not in self.clicked_xy:
                inverse.append((x,y))
        self.clicked_xy = inverse
        self.updata_canvas()



    def _on_advanced_selection(self):
        self.w_advanced_selection = Toplevel()
        self.w_advanced_selection.title('advaced selection method')
        self.v = IntVar()
        f = LabelFrame(self.w_advanced_selection, text = 'Choose a selection')
        f.pack()
        self.r1 = Radiobutton(f, text = '1. > (mA value large than):', padx = 20, variable =self.v, value =1, command= self.radio_)
        self.r1.grid(row = 0, column =0, sticky = 'w',  padx = (2,2), pady = (2,2))
        self.e_large = Entry(f, width =8, state = 'disabled')
        self.e_large.grid(row = 0, column =1, sticky = 'w', pady = (2,2))
        self.r2 = Radiobutton(f, text = '2. < (mA value small than):', padx = 20, variable =self.v, value =2, command= self.radio_)
        self.r2.grid(row = 1, column =0, sticky = 'w', padx = (2,2), pady = (2,2))
        self.e_small = Entry(f, width =8, state = 'disabled')
        self.e_small.grid(row = 1, column =1, sticky = 'w', pady = (2,2))
        self.r3 =Radiobutton(f, text = '3. >= and <= (mA value between):', padx = 20, variable =self.v, value =3, command= self.radio_)
        self.r3.grid(row = 2, column =0, sticky = 'w', columnspan = 4, padx = (2,2), pady = (2,2))
        f2 = Frame(f)
        f2.grid(row = 4, column =0, sticky = 'w',pady = (2,2), padx = (20,0), columnspan =2)
        Label(f2, text = 'from:').grid(row = 0, column =0, sticky = 'w', padx = (2,2), pady = (2,2))
        self.e_from_value = Entry(f2, width =8, state = 'disabled')
        self.e_from_value.grid(row = 0, column =1, sticky = 'w', padx = (2,2), pady = (2,2))
        Label(f2, text = 'to:').grid(row = 0, column =2, sticky = 'w', padx = (2,2), pady = (2,2))
        self.e_to_value = Entry(f2, width =8, state = 'disabled')
        self.e_to_value.grid(row = 0, column =3, sticky = 'w', padx = (2,2), pady = (2,2))

        Button(f, text = 'OK', command = self._advanced_selection_OK).grid(row = 5, column =2, sticky = 'w', padx = (2,2), pady = (2,2))

    def radio_(self):
        if self.v.get() == 1:
            self.e_large.config(state = 'normal')
            self.e_small.config(state = 'disabled')
            self.e_from_value.config(state = 'disabled')
            self.e_to_value.config(state = 'disabled')
        if self.v.get() == 2:
            self.e_large.config(state = 'disabled')
            self.e_small.config(state = 'normal')
            self.e_from_value.config(state = 'disabled')
            self.e_to_value.config(state = 'disabled')
        if self.v.get() == 3:
            self.e_large.config(state = 'disabled')
            self.e_small.config(state = 'disabled')
            self.e_from_value.config(state = 'normal')
            self.e_to_value.config(state = 'normal')


    def _advanced_selection_OK(self):
        # self.w_advanced_selection.destroy
        self.clicked_xy.clear()
        ma = self.mA[self.current_N]

        for x,y in ma:
            if self.v.get() == 1:
                if ma[(x,y)] > float(self.e_large.get()):
                    self.clicked_xy.append((x,y))
            elif self.v.get() == 2:
                 if ma[(x,y)] < float(self.e_small.get()):
                    self.clicked_xy.append((x,y))
            elif self.v.get() == 3:
                 if ma[(x,y)] >= float(self.e_from_value.get()) and ma[(x,y)] <= float(self.e_to_value.get()):
                    self.clicked_xy.append((x,y))
        self.updata_canvas()


    def _on_plot_selected(self):
        w = Toplevel()
        w.title('show plot from choosed selection')
        fig = Figure()
        canvas = FigureCanvasTkAgg(fig, master=w)  # A tk.DrawingArea.
        ax = fig.add_subplot(111)
        canvas.get_tk_widget().pack(fill = 'both', expand = 1)
        toolbar = NavigationToolbar2Tk(canvas,  w)
        toolbar.update()
        for x, y in self.get_clicked():
            potential, mA = self.data[x][y]
            ax.plot(potential, mA, label = f'(x, y) = ({x},{y})')
        #vertical line (potential)
        ymin, ymax = ax.get_ylim()
        ax.set_ylim(ax.get_ylim())
        ax.vlines(self.potential0, ymin = ymin, ymax = ymax, color = 'red', linestyles = 'dashed')

        ax.set_title(f'Potential = {self.potential0} [mV]')
        ax.legend().set_draggable(True)
        canvas.draw()


    def _on_delete(self):
        if self.current_N < len(self.mA):
            del self.mA[self.current_N+1: len(self.mA)]

        ma = self.mA[self.current_N].copy()
        for x, y in self.get_clicked():
            if (x,y) in ma:
                del ma[(x, y)]

        self.mA.append(ma)#save it as the new version
        self.current_N+=1 #establish a new version

        self.plot_scatter() #redraw scatter

    # change potential, only change potential, don't change x, y
    def _on_potential_scale(self, e):
        scatter = []
        potential0 = float(self.sc_potential_var.get())
        self.potential0 = potential0
        for x, v in self.data.items():
            for y in v.keys():
                potential, mA = self.data[x][y]
                mA0 = np.round(mA[np.abs(potential - potential0).idxmin], 3) # get nearest y value
                scatter.append((x,y,mA0))

        x1 = [x for x, y, c in scatter]
        y1 = [y for x, y, c in scatter]
        c1 = [c for x, y, c in scatter]

        ma = self.mA[self.current_N]
        # if x is not None:
        for xx, yy, cc in zip(x1, y1, c1):
            if (xx, yy) in ma:
                ma[(xx,yy)] = cc
            self.mA_all[(xx,yy)] = cc #update
        # self.mA.append(ma) #version n = 0



        self.plot_scatter(is_title = True)




    def plot_scatter(self, is_title = True):
        for line in self.plot_clicked:
            line.remove()

        if self.cbar is not None:
            self.cbar.remove()
            self.cax.remove()
            self.scatter_deleted.remove()

        ma = self.mA[self.current_N]
        c = np.array([ma[(x,y)] for x,y in ma])
        self.cax = self.ax.scatter(np.array([x for x, y in ma]), np.array([y for x, y in ma]), c = c, s = 100, marker = 's', cmap = self.cb_color.get())
        self.colormaptype = self.cb_color.get()

        x_d, y_d = [], [] # record current deleted x, y
        for (xx, yy) in self.mA_all:
            if (xx, yy) not in ma:
                x_d.append(xx)
                y_d.append(yy)

        self.scatter_deleted = self.ax.scatter(x_d, y_d, c = 'black', s=10, marker = '.')

        self.cbar = self.fig.colorbar(self.cax, ax = self.ax, ticks = np.round(np.linspace(start = min(c), stop = max(c), num =9), 3))
        self.cbar.ax.set_title(' '+self.e_unitU.get()+'\n')
        if is_title:
            title = f'Potential = {self.potential0} [mV]' + '\n\n'+ f'(from {min(c)} to {max(c)} {self.e_unitU.get()})'
            self.ax.set_title(title, fontsize = 11)



        self.clicked_xy.clear()
        self.plot_clicked.clear()
        self.canvas.draw()
   #formatted coordinates
    def format_coord(self, xdata,ydata):
        x_all, y_all = [], []
        for x, y in self.mA_all:
            x_all.append(x)
            y_all.append(y)
        x_all, y_all = np.array(x_all), np.array(y_all)

        index_x = np.abs(x_all-xdata) < self.width/2
        index_y = np.abs(y_all-ydata) < self.width/2
        click_x = x_all[index_x][0] if len(x_all[index_x]) >0 else None
        click_y = y_all[index_y][0] if len(y_all[index_y]) >0 else None
        X = np.where(x_all == click_x)[0]
        Y =np.where(y_all == click_y)[0]

        if len(np.intersect1d(X, Y)): #find commen value between two arrays
            return f'(x, y, mA) = ({click_x}, {click_y}, {self.mA_all[(click_x,click_y)]} mA)'
        else:
            return []
    #return clicked positions
    def get_clicked(self):
        return list(set(self.clicked_xy))

    def on_click(self, event):
        # self.ax.focus()
        if event.inaxes!=self.ax: return
        self.get_click_xy(event.xdata, event.ydata)


    def _on_clear(self):
        for line in self.plot_clicked:
            line.remove()
        self.clicked_xy.clear()
        self.plot_clicked.clear()
        self.canvas.draw()

    # return clicked x, y
    def get_click_xy(self, xdata, ydata):
        ma = self.mA[self.current_N]
        x_left= np.array([x for x, y in ma])
        y_left = np.array([y for x, y in ma])
        index_x = np.abs(x_left-xdata) < self.width/2
        index_y = np.abs(y_left-ydata) < self.width/2
        click_x = x_left[index_x][0] if len(x_left[index_x]) >0 else None
        click_y = y_left[index_y][0] if len(y_left[index_y]) >0 else None
        X = np.where(x_left == click_x)[0]
        Y =np.where(y_left == click_y)[0]

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

        ma = self.mA[self.current_N]
        for x, y in ma:
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
        line, = self.ax.plot(x, y,linestyle='none', marker='s', alpha = 1, markeredgecolor="red", markersize = 9, markerfacecolor='white',markeredgewidth =2)
        self.plot_clicked.append(line)
        self.canvas.draw()
