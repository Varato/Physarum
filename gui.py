import imageio
import numpy as np
from collections import OrderedDict

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter

from physarum import Physarum

import matplotlib
matplotlib.use('TkAgg')

contrast_factor = 2
reset_flag = False

def normalize_trail_map(trail_map):
    x = trail_map * contrast_factor
    return (np.exp(2*x) - 1) / (np.exp(2*x) + 1)

def set_contrast_factor(x):
    global contrast_factor
    contrast_factor = float(x)


if __name__=="__main__":
    m = Physarum(num = 3000,
                 height = 300,
                 width = 400)

    # blbl = imageio.v2.imread('imgs/bilibili-480.png')
    # blbl_gray = 0.2989 * blbl[:, :, 0] + 0.5870 * blbl[:, :, 1] + 0.1140 * blbl[:, :, 2]
    # blbl_gray /= blbl.max()

    # food_map = np.zeros([m.height, m.width])
    # food_map[:, 120:120+480] = blbl_gray


    fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=(6, 8))
    plt.subplots_adjust(wspace=0, hspace=0.1, left=0, bottom=0.05, top=0.95, right=1)

    ax1.axis('off')
    ax2.axis('off')
    ax1.set_xlim([0, m.width])
    ax1.set_ylim([-m.height,0])
    ax1.set_aspect('equal')

    scat1 = ax1.scatter(m.y, -m.x, c='k', s=5)
    scat2 = ax1.scatter(m.sy[0], -m.sx[0], c='r', s=1)
    scat3 = ax1.scatter(m.sy[1], -m.sx[1], c='g', s=1)
    scat4 = ax1.scatter(m.sy[2], -m.sx[2], c='b', s=1)

    im = ax2.imshow(normalize_trail_map(m.hist), cmap="cividis", vmin=0, vmax=1.0)

    root = tkinter.Tk()
    root.title("Physarum Simulation")

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().grid(column=0,row=0)

    after_id = None
    def update_ani():
        global after_id, reset_flag
        # m.deposit_food(food_map)
        if reset_flag:
            m.reset()
            reset_flag = False
        m.run()

        scat1.set_offsets(np.array([m.y, -m.x]).T)
        scat2.set_offsets(np.array([m.sy[0], -m.sx[0]]).T)
        scat3.set_offsets(np.array([m.sy[1], -m.sx[1]]).T)
        scat4.set_offsets(np.array([m.sy[2], -m.sx[2]]).T)
        im.set_array(normalize_trail_map(m.hist))
        canvas.draw()

        after_id = root.after(50, update_ani)

    config_pannel = tkinter.Frame(master=root, padx=5)
    config_pannel.grid(column=1, row=0)

    config_sliders = OrderedDict({
                 #min, max, resolution, default, command
        "speed": (0.0, 5, 0.5, m.speed, m.set_speed),
        "sensing_dist": (0, 100, 1, m.sensing_dist, m.set_sensing_dist),
        "sensing_angle": (20, 120, 0.5, m.sensing_angles[1] * 180/np.pi, m.set_sensing_angle),
        "heading_rate": (0, 120, 1, m.heading_rate * 180/np.pi, m.set_heading_rate),
        "diffusion_factor": (0, 3, 0.1, m.filter_sigma, m.set_filter_sigma),
        "decay_factor": (0.5, 1.0, 0.01, m.decay_factor, m.set_decay_factor),
        "contrast_factor": (0.1, 10, 0.1, contrast_factor, set_contrast_factor),
    })

    for i, k in enumerate(config_sliders):
        label = tkinter.Label(master=config_pannel, text=k)
        label.grid(column=0, row=i)

        vmin, vmax, res, default_value, cmd = config_sliders[k]

        slider = tkinter.Scale(master=config_pannel,
                               from_=vmin,
                               to=vmax,
                               resolution=res,
                               command=cmd,
                               orient="horizontal")
        slider.grid(column=1, row=i)
        slider.set(default_value)

    msg = tkinter.Label(master=config_pannel, text="Number of Agents: {}\nHit space bar to reset".format(m.num), pady=10)
    msg.grid(column=0, row=len(config_sliders))

    def on_reset(event=None):
        global reset_flag
        reset_flag = True

    def on_destroy(event):
        global after_id
        if event.widget is not root:
            return
        if after_id:
            root.after_cancel(after_id)
            after_id = None
        root.destroy()
        root.quit()

    root.bind("<space>", on_reset)
    root.bind("<Destroy>", on_destroy)
    update_ani()
    tkinter.mainloop()
