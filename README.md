<p align="center">
  <a href="https://felupe.readthedocs.io/en/latest/?badge=latest"><img src="https://user-images.githubusercontent.com/5793153/235789118-eb03eb25-2556-401d-8a0f-580f37e72f8d.png" height="40px"/></a>
  <p align="center"><img src="results/test_specimen_mesh_fibre.png" height="150px"/></p>
  <p align="center"><b>Fiber-Reinforced-Rubber</b></p>
  <p align="center"><em>Numeric simulation of a test specimen with a fiber-reinforced rubber composite.</em></p>
</p>

This repository provides the reproducible simulation data performed in the paper *Investigating damage mechanisms in cord-rubber composite air spring bellows of rail vehicles and representative specimen design*, submitted to [Applied Composite Materials](https://www.springer.com/journal/10443).

# Installation
Install [Python](https://www.python.org/downloads/) (3.7 - 3.10), open a terminal and install the requirements.

```
pip install felupe[all] matadi matplotlib pypardiso termtables
```

# Usage
Edit and run the scripts [`script_test-specimen-simulation.py`](script_test-specimen-simulation.py) and [`script_test-specimen-strain.py`](script_test-specimen-strain.py).

# Results
The scripts generate undeformed and deformed views on the test specimen, force-displacement characteristic curves of the test specimen as well as plots of the strain distribution. Results are stored in [results/](results/).

## Undeformed Views
The views on the undeformed test specimen show the quad mesh for the rubber and the (helper) meshes for the fibers.

<p align="center">
  <img src="results/test_specimen_mesh_rubber.png" height="300px"/>    <img src="results/test_specimen_mesh_fibre.png" height="300px"/>
</p>

## Deformed Views
The views on the deformed test specimen are carried out for $F_Z=3$ kN ($V=7$ mm) at $U=23$ mm.

![](results/test_specimen_deformed_fibre.png)

![](results/test_specimen_deformed_rubber.png)

## Force-displacement characteristic curves

![](results/test_specimen_forces_vs_displacement.svg)

[Table of Force-Displacement Data](results/test_specimen_forces_vs_displacement.md) [(csv)](results/test_specimen_forces_vs_displacement.csv)

## Strain distribution

The strain distribution of $\varepsilon_{yy}$ is evaluated at an applied tension of $V=6$ mm

![](results/LogStrainYY_V=6mm.svg)

and of $V=7$ mm, both located in the middle of the height of the test specimen (at $Y=0$).

![](results/LogStrainYY_V=7mm.svg)

[Table of Strain Distribution (6 mm)](results/LogStrainYY_V=6mm.md) [(csv)](results/LogStrainYY_V=6mm.csv)

[Table of Strain Distribution (7 mm)](results/LogStrainYY_V=7mm.md) [(csv)](results/LogStrainYY_V=7mm.csv)

