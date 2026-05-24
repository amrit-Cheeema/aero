import math
import numpy as np
import matplotlib.pyplot as plt

import time as Time
import multiprocessing
from pendulumDocs import PendulumDocs
from typing import Literal, Callable

G = 9.81

class Pendulum(PendulumDocs):
    """
    A simulation of a simple pendulum.
    """
    g: float = G
    def __init__(self, angle: float, L: float, dt:float=.1, mass:float=1):
        self.angle: float = angle
        self.L : float = L
        self.dt : float = dt
        self.av: float = 0
        self.x: float = self.L * math.sin(self.angle)
        self.y: float = -self.L * math.cos(self.angle)
        self.mass: float = mass
        self.Integrator: Integrators = Integrators(lambda x: self.angular_acceleration(self.angle, self.L), dt=self.dt)
        self.initial_energy = self.get_total_energy()
    
    def update_position(self):
        self.x = self.L * math.sin(self.angle)
        self.y = -self.L * math.cos(self.angle)

    # make calculations more accurate, errors in sin cos add up
    @staticmethod
    def angular_acceleration(angle: float, L) -> float:
        return -1 * math.sin(angle) * G / L

    def angular_velocity(self):
        """Update the angular velocity based on the current angle and the angular acceleration."""
        # self.av = self.Integrator.forward_euler(self.av)
        self.av += self.angular_acceleration(self.angle, self.L) * self.dt
    
    def angular_posistion(self):
        """Update the angular position based on the current angular velocity."""
        self.angle += self.av * self.dt

    def step(self):
        """Perform a single time step of the simulation."""
        self.angular_velocity()
        self.angular_posistion()
        self.update_position()
        self.get_total_energy()
        self.plot([(self.x, self.y)], (2, 2))

    def get_total_energy(self) -> float:
        m = 1.0 # Assume unit mass
        potential = m * G * (self.L - self.L * math.cos(self.angle))
        kinetic = 0.5 * m * (self.L * self.av)**2
        
        return potential + kinetic
    
    def plot(self, point_mass: list[tuple[float, float]], dim: tuple[int, int]):
        plt.clf() # Clear the current figure
        
        # 1. Draw the anchor point (origin)
        plt.plot(0, 0, 'kX', markersize=12, label='Anchor') 
        
        # 2. Draw the rod(s) connecting the anchor to the masses
        # We start at the origin (0,0)
        prev_x, prev_y = 0.0, 0.0
        for point in point_mass:
            plt.plot([prev_x, point[0]], [prev_y, point[1]], 'b-', linewidth=3)
            prev_x, prev_y = point[0], point[1]
        
        # 3. Draw the bob/mass points
        for point in point_mass:
            plt.plot(point[0], point[1], 'ro', markersize=20, zorder=3)
        
        # Set the limits so the pendulum doesn't fly off screen
        plt.xlim(dim[0]*-1, dim[0])
        plt.ylim(dim[1]*-1, dim[1])
        plt.gca().set_aspect('equal', adjustable='box')

        plt.grid(True)
        plt.pause(0.001) # Pause briefly to allow the UI to update    
    def run(self, time: float):
        """Run the simulation for a given amount of time."""

        # time=10, dt=.1, we have to take 100 steps
        steps = int(time / self.dt)
        start_time = Time.perf_counter()
        
        # We are essentially going to sleep until the next step should start.
        for i in range(steps):
            self.step()
            
            # Calculate exactly when the NEXT step should start in the real world
            next_start_time = start_time + ((i + 1) * self.dt)
            
            # Determine how long to wait
            time_to_sleep = next_start_time - Time.perf_counter()
            
            if time_to_sleep > 0:
                Time.sleep(time_to_sleep)
            else:
                
                # The physics step took longer than step_interval.
                # We don't sleep so the simulation can try to catch up.
                pass


class Integrators():
    def __init__(self, f: Callable[[float], float], dt=.1):
        self.f = f
        self.dt = dt
        self.fig = None
        self.ax = None
    
    def _plot_f(self, a: float, b: float):
        """Adds self.f to plot"""
        self._aplot(self.f, a, b, label="f(x)")
    def _plot_int_f(self, a: float, b: float):
        """Adds the integral of self.f to plot"""
        

        self._aplot(lambda x: self.integrate(self.f, 0, x), a, b, label="Integral f(x)")
    
    
    def plot(self):
        # self._plot_f(0, 5)
        # self._plot_int_f(0, 5)
        def f(i: float) -> float:
            y0 = 9
            for i in range(int((i-0)/self.dt)):
                y0=self.forward_euler(y0)
            return y0
        def F(i: float) -> float:
            y0 = 9
            for i in range(int((i-0)/self.dt)):
                y0=self.RK2(y0)
            return y0
        self._aplot(lambda x: f(x), 0, 5, label="forward euler")
        self._aplot(lambda x: F(x), 0, 5, label="rk2")
        self._aplot(lambda x: 9*math.e**(-2*x), 0, 5, "e^-2", dt=.01)
        # Now show it
        self._show(title="Trig Comparison")
    def _setup_plot(self):
        """Initializes the figure and axis if they don't exist yet."""
        if self.ax is None:
            plt.style.use('seaborn-v0_8-muted')
            self.fig, self.ax = plt.subplots(figsize=(10, 6), dpi=100)
            
            # Apply base styling once
            self.ax.set_facecolor('#fdfdfd')
            self.ax.grid(True, linestyle='--', alpha=0.6)
            for spine in ['top', 'right']:
                self.ax.spines[spine].set_visible(False)
            self.ax.axhline(0, color='black', linewidth=0.8, alpha=.3)

    def _aplot(self, f: Callable[[float], float], a: float, b: float, label: str = "f(x)", dt: float | None = None):
        """Adds a new line to the existing plot."""
        self._setup_plot()
        if dt is not None:
            self.dt = dt
        
        num_steps = int(np.ceil((abs(b - a)) / self.dt)) + 1
        x = np.linspace(min(a, b), max(a, b), num_steps)
        y = [f(val) for val in x]

        # Draw the line
        if self.ax: 
            self.ax.plot(x, y, linewidth=2.5, label=label)
        
    def _show(self, title: str = "Function Visualization"):
        """Finalizes and displays the plot."""
        if self.ax is None:
            print("Nothing to show!")
            return

        self.ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        self.ax.set_xlabel('x', fontsize=12)
        self.ax.set_ylabel('y', fontsize=12)
        self.ax.legend() # Automatically shows labels for all added lines
        
        plt.tight_layout()
        plt.show()
        
        # Reset after showing so the next call starts a fresh plot
        self.fig, self.ax = None, None
    
    
    def integrate(self, f: Callable[[float], float],  a: float, b: float, method: Literal["Left", "Right", "Midpoint", "Trapezoid"]="Midpoint"):
        n: float = max(1, round((b - a) / self.dt))
        dx: float = (b - a) / n

        if method == "Left":
            # Sum of f(x) at the left endpoints
            return sum(f(a + i * dx) for i in range(n)) * dx
            
        elif method == "Right":
            # Sum of f(x) at the right endpoints
            return sum(f(a + (i + 1) * dx) for i in range(n)) * dx
            
        elif method == "Midpoint":
            # Sum of f(x) at the midpoint of each subinterval
            return sum(f(a + (i + 0.5) * dx) for i in range(n)) * dx
            
        elif method == "Trapezoid":
            # Area of a trapezoid: (f(x_left) + f(x_right)) / 2 * dx
            return sum((f(a + i * dx) + f(a + (i + 1) * dx)) / 2 for i in range(n)) * dx
            
        else:
            raise ValueError(f"Unknown integration method: {method}")
    
    def forward_euler(self, y0: float) -> float:
        yn = y0 + self.f(y0) * self.dt
        return yn
    def RK2(self, y0: float) -> float:
        """Runge-Kutta 2nd order method (Heun's method)"""
        k1 = self.f(y0)
        k2 = self.f(y0 + k1 * self.dt)
        yn = y0 + (k1 + k2) / 2 * self.dt
        return yn
    

# class Input:
#     """
#     Stores sensor data in a table
#     """
#     def __init__(self, fetch):
#         self.x

class Pendulum1(PendulumDocs):
    """
    A simulation of a simple pendulum.
    """
    g: float = G
    def __init__(self, angle: float, L: float, dt:float=.1, mass:float=1):
        self.angle: float = angle
        self.L : float = L
        self.dt : float = dt
        self.av: float = 0
        self.x: float = self.L * math.sin(self.angle)
        self.y: float = -self.L * math.cos(self.angle)
        self.mass: float = mass
        self.initial_energy = self.get_total_energy()
    
    def update_position(self):
        self.x = self.L * math.sin(self.angle)
        self.y = -self.L * math.cos(self.angle)

    # make calculations more accurate, errors in sin cos add up
    def angular_acceleration(self) -> float:
        return -1 * math.sin(self.angle) * G / self.L

    def angular_velocity(self):
        """Update the angular velocity based on the current angle and the angular acceleration."""
        self.av +=  self.angular_acceleration() * self.dt
    
    def angular_posistion(self):
        """Update the angular position based on the current angular velocity."""
        self.angle += self.av * self.dt

    def step(self):
        """Perform a single time step of the simulation."""
        self.angular_velocity()
        self.angular_posistion()
        self.update_position()
        self.get_total_energy()
        self.plot([(self.x, self.y)], (2, 2))

    def get_total_energy(self) -> float:
        m = 1.0 # Assume unit mass
        potential = m * G * (self.L - self.L * math.cos(self.angle))
        kinetic = 0.5 * m * (self.L * self.av)**2
        
        return potential + kinetic
    
    def plot(self, point_mass: list[tuple[float, float]], dim: tuple[int, int]):
        plt.clf() # Clear the current figure
        
        # 1. Draw the anchor point (origin)
        plt.plot(0, 0, 'kX', markersize=12, label='Anchor') 
        
        # 2. Draw the rod(s) connecting the anchor to the masses
        # We start at the origin (0,0)
        prev_x, prev_y = 0.0, 0.0
        for point in point_mass:
            plt.plot([prev_x, point[0]], [prev_y, point[1]], 'b-', linewidth=3)
            prev_x, prev_y = point[0], point[1]
        
        # 3. Draw the bob/mass points
        for point in point_mass:
            plt.plot(point[0], point[1], 'ro', markersize=20, zorder=3)
        
        # Set the limits so the pendulum doesn't fly off screen
        plt.xlim(dim[0]*-1, dim[0])
        plt.ylim(dim[1]*-1, dim[1])
        plt.gca().set_aspect('equal', adjustable='box')

        plt.grid(True)
        plt.pause(0.001) # Pause briefly to allow the UI to update    
    def run(self, time: float):
        """Run the simulation for a given amount of time."""

        # time=10, dt=.1, we have to take 100 steps
        steps = int(time / self.dt)
        start_time = Time.perf_counter()
        
        # We are essentially going to sleep until the next step should start.
        for i in range(steps):
            self.step()
            
            # Calculate exactly when the NEXT step should start in the real world
            next_start_time = start_time + ((i + 1) * self.dt)
            
            # Determine how long to wait
            time_to_sleep = next_start_time - Time.perf_counter()
            
            if time_to_sleep > 0:
                Time.sleep(time_to_sleep)
            else:
                
                # The physics step took longer than step_interval.
                # We don't sleep so the simulation can try to catch up.
                pass


def test_func(x: float) -> float:
        return -2*x
integrator = Integrators(f=test_func, dt=.2)
integrator.plot()
# if __name__ == '__main__':
#     # 1. Create your two pendulum instances
#     pendulum = Pendulum(angle=math.pi/2, L=1, dt=0.05)
#     pendulum2 = Pendulum(angle=math.pi/5, L=1, dt=0.05)

#     # 2. Assign each pendulum's run method to a completely separate CPU core
#     #    args=(10,) passes the 10 seconds duration to the run() function
#     process1 = multiprocessing.Process(target=pendulum.run, args=(10,))
#     process2 = multiprocessing.Process(target=pendulum2.run, args=(10,))

#     print("Kicking off both simulations on separate CPU cores...")
    
#     # 3. Start both processes at the exact same time
#     process1.start()
#     process2.start()

#     # 4. Tell your main script to wait here until both cores finish their work
#     process1.join()
#     process2.join()

#     print("Both 10-second simulations completed in parallel!")




