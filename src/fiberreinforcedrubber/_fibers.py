import felupe as fem
import numpy as np


def fibers(
    limit, width=50, height=50, middle=5, angle=15, axis=1, fiber_distance=1.0, n=201
):
    """A mesh of a fiber family rotated by ``angle`` around a given
    ``axis``. Each fiber consists of ``(n-1)`` line-cells.
    """

    # fiber mesh parameters
    H = 2 * height
    W = 2 * width
    center = np.array([H / 2, W / 2])

    # init the grid and create the points in 2d-space
    x, y = np.meshgrid(
        np.linspace(0, H, n), np.arange(0, W + fiber_distance, fiber_distance)
    )
    points = np.vstack((x.ravel(), y.ravel())).T

    # connect points to lines
    cells = np.repeat(np.arange(0, len(points)), 2)[1:-1].reshape(-1, 2)
    mask = np.ones(len(cells), dtype=bool)
    mask[np.arange(0, len(cells), n)[1:] - 1] = False
    cells = cells[mask]

    mesh = fem.Mesh(points, cells, "line")

    # mean angle from given axis
    angle_mean = {0: 0, 1: 90}[axis]

    # create two meshes for the fibers
    fibers = fem.mesh.rotate(mesh, angle_deg=angle_mean + angle, axis=2, center=center)

    # subtract the center
    fibers.points -= center

    # cut out the test specimen (with the limit function in x)
    p = fibers.points
    mask_points = np.logical_and(
        np.logical_and(
            p[:, 0] >= -limit(fibers.points[:, 1]),
            p[:, 0] <= limit(fibers.points[:, 1]),
        ),
        np.logical_and(
            p[:, 1] >= -height / 2,
            p[:, 1] <= height / 2,
        ),
    )
    points_to_keep = np.arange(len(p))[mask_points]
    mask_cells = np.all(np.isin(fibers.cells, points_to_keep), axis=1)

    fibers = fem.Mesh(fibers.points, fibers.cells[mask_cells], cell_type="line")

    return fibers, mask_points
