import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from physarum import Physarum

def normalize_trail_map(trail_map, a:float = 2):
    x = trail_map * a
    return (np.exp(2*x) - 1) / (np.exp(2*x) + 1)


if __name__ == "__main__":
    m = Physarum(num = 500,
                 height = 480,
                 width = 720, 
                 decay_factor = 0.95, 
                 sensing_dist = 27, 
                 speed = 1,
                 heading_rate = 0.1)
    
    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(10,5))
    plt.subplots_adjust(wspace=0, hspace=0, top=1, bottom=0, right=1,left=0)

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

    def update_ani(i):
        m.run()

        scat1.set_offsets(np.array([m.y, -m.x]).T)
        scat2.set_offsets(np.array([m.sy[0], -m.sx[0]]).T)
        scat3.set_offsets(np.array([m.sy[1], -m.sx[1]]).T)
        scat4.set_offsets(np.array([m.sy[2], -m.sx[2]]).T)
        im.set_array(normalize_trail_map(m.hist))

    ani = FuncAnimation(fig, update_ani, frames=range(100), interval=10)
    # ani.save('bilibili-decay0.9-dist0.05-speed0.005-headingrate20.mp4')
    plt.show()
