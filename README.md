# Square Packing Simulation

This python project is the primary version of a simulation for the unsolved mathematical problem called 'square packing'

- The goal is to determine how many 1×1 squares can be squeezed into a larger square container.

- Some solutions were already proven to be optimal, but the maximum number of squares than can be packed in an a*a square remains still unknown.

- In 2009 mathematician Erich Friedman published [Packing Unit Squares in Squares: A Survey and New Results](https://www.combinatorics.org/files/Surveys/ds7/ds7v5-2009/ds7-2009.html)
in THE ELECTRONIC JOURNAL OF COMBINATORICS summarizing the state of the art.

## Features

The project features an interactive graphical user interface (GUI) built on Matplotlib. Users can adjust various parameters via the UI before starting the simulation, such as:

- **Container Area:** The total area of the larger square (e.g., 100 for a 10×10 container).
- **Max Failures:** The maximum number of consecutive failed insertion attempts allowed before the simulation stops.
- **Attempts/Frame:** How many candidate insertions are attempted in each simulation frame.
- **Rearr/Frame:** How many rearrangement (squeezing) moves are executed per frame.
- **Trans Step:** The maximum translation distance used in a rearrangement move.
- **Rot Step:** The maximum rotation (in radians) applied in a rearrangement move.

> **Note:**  
> I still don't know what the optimals parameters are but, in future versions, a backend statistical analysis module could be added to run multiple simulations with different parameters and determine the optimal parameter set for maximum packing.


## How it works
In this simulation, candidate squares are inserted using a Gaussian distribution biased toward the container’s center. The rationale is that as the simulation progresses, the already placed squares are pushed toward the container’s edges, leaving the center with more free space. By biasing insertion toward the center, the simulation efficiently finds available space.

## How to Run

1. **install requirements**

- python 3.x
- Matplotlib

2. **Clone the Repository:**

   ```bash
   git clone https://github.com/leove4/Square-packing-simulation
   cd square-packing-simulation

3. **run simulation.py**

   ```bash
   python simulation.py

# Licence
This project is under MIT licence so feel free to use it for research :)
