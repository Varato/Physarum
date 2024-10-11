import time
import numpy as np
from scipy.ndimage import gaussian_filter


class Physarum:
    def __init__(self, 
                 num: int, 
                 width: int,
                 height: int,
                 decay_factor: float=0.95, 
                 sensing_angle: float=0.7,
                 sensing_dist: float = 3, 
                 speed: float = 1.0,
                 heading_rate: float = 0.5,
                 filter_sigma: float = 0.2):
        self.num = num
        self.width = width
        self.height = height

        self.decay_factor = decay_factor
        self.filter_sigma = filter_sigma

        self.x = np.random.rand(num) * (height - 1) #[0, height-1)
        self.y = np.random.rand(num) * (width - 1)  #[0, width-1)
        # self.x = np.ones(num) * height/2.0
        # self.y = np.ones(num) * width/2.0
        self.heading = np.random.rand(num) * np.pi * 2
        self.heading_rate = heading_rate
        
        self.speed = speed
        self.sensing_dist = sensing_dist
        self.sensing_angles = np.array([0, sensing_angle, -sensing_angle])
        self.sensing_value = np.zeros([3, num])
        
        self.trail_map = np.zeros([height, width])
        self.hist = np.zeros([self.height, self.width])
        
        self.count = 0
        self.last_x = np.copy(self.x)
        self.last_y = np.copy(self.y)

        self._update_velocity()
        self._update_sensing_positions()

    def reset(self):
        print("reset")
        self.x = np.random.rand(self.num) * (self.height - 1) #[0, height-1)
        self.y = np.random.rand(self.num) * (self.width - 1)  #[0, width-1)
        self.heading = np.random.rand(self.num) * np.pi * 2
    
        self.sensing_value = np.zeros([3, self.num])
        self.trail_map = np.zeros([self.height, self.width])
        self.hist = np.zeros([self.height, self.width])
        
        self._update_velocity()
        self._update_sensing_positions()
    
    def set_filter_sigma(self, sigma: float):
        self.filter_sigma = float(sigma)

    def set_decay_factor(self, decay_factor: float):
        self.decay_factor = float(decay_factor)

    def set_speed(self, speed):
        self.speed = float(speed)

    def set_sensing_dist(self, sensing_dist: float):
        self.sensing_dist = float(sensing_dist)

    def set_sensing_angle(self, sensing_angle_deg: float):
        self.sensing_angles = np.array([0, float(sensing_angle_deg), -float(sensing_angle_deg)]) * np.pi/180

    def set_heading_rate(self, heading_rate_deg: float):
        self.heading_rate = float(heading_rate_deg) * np.pi/180

    def sense_pbc(self):
        self._update_sensing_positions()
        sx = np.int32(np.round(self.sx))
        sy = np.int32(np.round(self.sy))
        i = sx % self.height
        j = sy % self.width
        self.sensing_value = self.trail_map[i, j]
        
    def rotate(self):
        forward = np.logical_and(
            self.sensing_value[0] > self.sensing_value[1],
            self.sensing_value[0] > self.sensing_value[2]
        )
        
        left = np.logical_and(
            self.sensing_value[1] > self.sensing_value[2],
            ~forward)
    
        right = np.logical_and(
            self.sensing_value[2] > self.sensing_value[1],
            ~forward)

        random = np.logical_and.reduce([
            ~forward, ~left, ~right
        ])
        
        heading_left = self.heading + self.heading_rate
        heading_right = self.heading - self.heading_rate
        heading_random = self.heading + self.heading_rate * np.random.choice([1, -1])
        
        self.heading[left] = heading_left[left]
        self.heading[right] = heading_right[right]
        self.heading[random] = heading_random[random]
        
    def move_pbc(self):
        self.last_x = np.copy(self.x)
        self.last_y = np.copy(self.y)
        self._update_velocity()

        self.x = (self.x + self.vx)
        self.y = (self.y + self.vy)

        x_exceed = np.logical_or(self.x<0, self.x>=self.height)
        y_exceed = np.logical_or(self.y<0, self.y>=self.width)

        self.x = self.x % self.height
        self.y = self.y % self.width

        self.last_x[x_exceed] = self.x[x_exceed]
        self.last_y[y_exceed] = self.y[y_exceed]
                
    def deposit(self, deposit_amount: float = 1):
        edges_x = np.arange(0, self.height+1) - 0.5
        edges_y = np.arange(0, self.width+1) - 0.5
        hist, _, _ = np.histogram2d(self.x, self.y, bins=[edges_x, edges_y])
        self.hist += hist * deposit_amount 
        self.trail_map += hist * deposit_amount

    def deposit_food(self, food_texture):
        self.trail_map += food_texture

    def diffuse_and_decay(self):
        # self.trail_map = uniform_filter(self.trail_map, size=3, mode='wrap')
        gaussian_filter(self.trail_map, sigma=self.filter_sigma, output=self.trail_map, mode='wrap')
        self.trail_map *= self.decay_factor
        self.hist *= self.decay_factor
        np.clip(self.trail_map, a_min=0, a_max=1.0, out=self.trail_map)

    def run(self):
        tic = time.time()

        self.sense_pbc()
        self.rotate()
        self.move_pbc()
        self.deposit()
        self.diffuse_and_decay()
        toc = time.time()
        print("step {:d}, n = {:d}, hist max: {:f}, time: {:.3f}ms".format(self.count, self.x.shape[0], self.hist.max(), 1000*(toc-tic)))
        self.count += 1
        
    def _update_velocity(self):
        self.vx = np.cos(self.heading) * self.speed
        self.vy = np.sin(self.heading) * self.speed
        
    def _update_sensing_positions(self):
        angles = self.heading + self.sensing_angles[:, None] #(3, n)
        dx = self.sensing_dist * np.cos(angles) #(3, n)
        dy = self.sensing_dist * np.sin(angles) #(3, n)

        self.sx = self.x + dx # (3,n)
        self.sy = self.y + dy # (3,n)
