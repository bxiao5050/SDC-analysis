import numpy as np
from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
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


def main():
    root = Tk()
    # results = {1: 2.33, 2:3.33, 3: 3.433, 4:5.33}
    values = [23, 59, 56, 100, 93]

    app = ShowHist(root)
    app.pack()

    app.update( values)
    root.mainloop()

if __name__ == '__main__':
    main()









