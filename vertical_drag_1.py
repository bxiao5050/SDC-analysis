
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from tkinter import *

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




def main():
    root = Tk()

    app = RangeDrag(root)
    root.mainloop()



if __name__ == '__main__':
    main()
