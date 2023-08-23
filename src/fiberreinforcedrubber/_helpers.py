import felupe as fem
import numpy as np
from scipy.interpolate import griddata


def interpolate(mesh, values, fibers, mask):
    "Interpolate values from the source mesh to a fiber mesh."

    u = np.zeros_like(fibers.points)
    u[mask] = griddata(mesh.points, values, fibers.points[mask])

    return u


def fiber_force(solid, thickness, fiber_area, fiber_vector):
    "Evaluate cell-based fiber forces and project them to mesh-points."

    force = fem.math.dot(
        solid.results.stress[0] * thickness / fiber_area, fiber_vector, mode=(2, 1)
    )

    return fem.project(force, solid.field.region)
