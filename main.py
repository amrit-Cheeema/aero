import math
import matplotlib.pyplot as plt

G = 9.81

class Pendulum:
    """
    A simulation of a simple pendulum.
    
   
    """
    def __init__(self, angle: float, L: float):
        self.angle: float = angle
        self.L : float = L
        self.dt = .1
        self.av = 0
        self.x = math.cos(angle) * L
        self.y = math.sin(angle) * L
    
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
        self.plot_pendulum()

    def get_total_energy(self) -> float:
        m = 1.0 # Assume unit mass
        potential = m * G * (self.L - self.L * math.cos(self.angle))
        kinetic = 0.5 * m * (self.L * self.av)**2
        print(f"Total Energy: {potential + kinetic:.4f} J")
        return potential + kinetic
    
    def plot_pendulum(self):
        plt.clf() # Clear the current figure
        
        # 1. Plot the "Pivot" at (0,0)
        plt.plot(0, 0, 'ko', markersize=10) 
        
        # 2. Plot the "Rod" from (0,0) to (x,y)
        plt.plot([0, self.x], [0, self.y], 'b-', linewidth=3)
        
        # 3. Plot the "Bob" (the mass) at (x,y)
        plt.plot(self.x, self.y, 'ro', markersize=20)
        
        # Set the limits so the pendulum doesn't fly off screen
        plt.xlim(-self.L - 0.5, self.L + 0.5)
        plt.ylim(-self.L - 0.5, self.L + 0.5)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.grid(True)
        plt.pause(0.001) # Pause briefly to allow the UI to update
    def run(self, time: float):
        """Run the simulation for a given amount of time."""
        steps = int(time / self.dt)
        for _ in range(steps):
            self.step()

pendulum = Pendulum(angle=math.pi/4, L=2)
pendulum.run(50)





# mgsin0
# f=ma
# f=mLa
# mgsin0/mL
