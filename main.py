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
    def plot_euler(self, f: Callable[[float], float], y0: float, a, b):
        """
        Graphs the full numerical solution using the Forward Euler method from t = a to t = b.
        
        Note: Updated f to f(t, y) to support time-dependent ODEs, 
        which is standard for autonomous/non-autonomous systems.
        """
        # 1. Clear the time steps based on interval and dt
        num_steps = int(np.ceil((b - a) / self.dt))
        
        # 2. Initialize arrays to store time (t) and solution (y) values
        t_space = np.linspace(a, b, num_steps + 1)
        y_space = np.zeros(num_steps + 1)
        y_space[0] = y0
        
        # 3. Run the Forward Euler loop over the entire interval
        for n in range(num_steps):
            # Forward Euler formula: y_{n+1} = y_n + dt * f(t_n, y_n)
            # (If your f only takes y, change this to f(y_space[n]))
            y_space[n+1] = self.forward_euler(y_space[n])
            
        # 4. Plotting the full trajectory
        plt.figure(figsize=(10, 6))
        
        # Plot the Euler approximation approximation
        plt.plot(t_space, y_space, 'g-o', markersize=4, linewidth=2, label=f'Euler Approximation (dt={self.dt})')
        
        # Highlight initial and final states
        plt.plot(t_space[0], y_space[0], 'ko', label=f'Initial State $y({a})={y0:.2f}$')
        plt.plot(t_space[-1], y_space[-1], 'ro', label=f'Final State $y({b})={y_space[-1]:.2f}$')
        
        # Labels and formatting
        plt.title(f"Forward Euler Method Solution from $t={a}$ to $t={b}$")
        plt.xlabel("Time ($t$)")
        plt.ylabel("Solution ($y$)")
        plt.xlim(a, b)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend(loc='best')
        plt.show()
    def integrate(self, a: float, b: float, method: Literal["Left", "Right", "Midpoint", "Trapezoid"]="Midpoint"):
        n: float = max(1, round((b - a) / self.dt))
        dx: float = (b - a) / n

        if method == "Left":
            # Sum of f(x) at the left endpoints
            return sum(self.f(a + i * dx) for i in range(n)) * dx
            
        elif method == "Right":
            # Sum of f(x) at the right endpoints
            return sum(self.f(a + (i + 1) * dx) for i in range(n)) * dx
            
        elif method == "Midpoint":
            # Sum of f(x) at the midpoint of each subinterval
            return sum(self.f(a + (i + 0.5) * dx) for i in range(n)) * dx
            
        elif method == "Trapezoid":
            # Area of a trapezoid: (f(x_left) + f(x_right)) / 2 * dx
            return sum((self.f(a + i * dx) + self.f(a + (i + 1) * dx)) / 2 for i in range(n)) * dx
            
        else:
            raise ValueError(f"Unknown integration method: {method}")
    
    def forward_euler(self, y0: float) -> float:
        yn = y0 + self.f(y0) * self.dt
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
integrator = Integrators(f=test_func, dt=0.5)
# integrator.plot_euler(lambda x: np.e**(-2*x) , 1.0)
integrator.plot_euler(lambda x: np.e**(-2*x), 0.0, 0, 5)
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




