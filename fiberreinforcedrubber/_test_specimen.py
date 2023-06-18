import felupe as fem
import numpy as np

from ._fibers import fibers
from ._rubber import rubber


def create_test_specimen(
    width=50,
    height=50,
    middle=5,
    radius=20,
    angle=120,
    fiber_angle=15,
    fiber_axis=1,
    fiber_distance=1,
    n=201,
):
    """Create a solid mesh and two meshes for the two fiber families rotated by
    an ``angle`` around a given ``axis``. Each fiber consists of ``(n-1)`` line-cells.
    """

    mesh_rubber, limit = rubber(width, height, middle, radius, angle)

    # fiber family 1
    mesh_fibers_1, mask_points_1 = fibers(
        limit, 2 * width, height, middle, -fiber_angle, fiber_axis, fiber_distance, n
    )

    # fiber family 2
    mesh_fibers_2, mask_points_2 = fibers(
        limit, 2 * width, height, middle, fiber_angle, fiber_axis, fiber_distance, n
    )

    mesh_fibers_1.points[mesh_fibers_1.points_without_cells, :] = 0
    mesh_fibers_2.points[mesh_fibers_2.points_without_cells, :] = 0

    return (mesh_rubber, mesh_fibers_1, mesh_fibers_2, mask_points_1, mask_points_2)
