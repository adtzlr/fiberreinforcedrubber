import felupe as fem
import numpy as np


def rubber(width=50, height=50, middle=5, radius=20, angle=120):
    "Create a 2d-quad mesh for the test specimen."

    # parameters
    w = width
    H = height
    R = radius

    # half angle
    phi = angle / 2

    # other angle of 90deg corner (in radians)
    alpha = np.deg2rad(90 - phi)

    # parameters for top right, lower part (rectangle)
    L3 = w / 2
    H3 = middle / 2

    # top right, middle part (radius)
    L1 = w / 2 + R * (1 - np.cos(alpha))
    H1 = R * np.sin(alpha)
    mesh1 = fem.Rectangle(b=(L1, H1), n=(int(L1), int(H1)))
    Y1 = mesh1.points[:, 1]
    fx1 = 1 + R * np.cos(alpha) / L1 - np.sqrt(R**2 - Y1**2) / L1
    mesh1.points[:, 0] *= fx1
    mesh1.points[:, 1] += H3

    # top right, lower part (rectangle)
    mesh3 = fem.Rectangle(b=(L3, H3), n=(int(L1), 2 * int(H3)))

    # top right, upper part (tangential continuation)
    L2 = L1
    H2 = H / 2 - H1 - H3
    mesh2 = fem.Rectangle(b=(L2, H2), n=(int(L2), int(H2)))
    Y2 = mesh2.points[:, 1]
    fx2 = 1 + np.tan(alpha) * Y2 / L2
    mesh2.points[:, 0] *= fx2
    mesh2.points[:, 1] += mesh1.points[:, 1].max()

    # top right combined
    mesh12 = fem.Mesh(
        points=np.vstack((mesh1.points, mesh2.points, mesh3.points)),
        cells=np.vstack(
            (
                mesh1.cells,
                mesh2.cells + mesh1.npoints,
                mesh3.cells + mesh1.npoints + mesh2.npoints,
            )
        ),
        cell_type=mesh1.cell_type,
    )

    # top left
    mesh21 = fem.mesh.mirror(mesh12)
    mesh1221 = fem.Mesh(
        points=np.vstack((mesh12.points, mesh21.points)),
        cells=np.vstack((mesh12.cells, mesh21.cells + mesh12.npoints)),
        cell_type=mesh12.cell_type,
    )

    # bottom
    mesh3443 = fem.mesh.mirror(mesh1221, normal=[0, 1])

    # total mesh
    mesh = fem.mesh.sweep(
        fem.Mesh(
            points=np.vstack((mesh1221.points, mesh3443.points)),
            cells=np.vstack((mesh1221.cells, mesh3443.cells + mesh1221.npoints)),
            cell_type=mesh1221.cell_type,
        ),
        decimals=3,
    )

    def limit(y):
        "Evaluate the maximum x-value for a given y-coordinate."

        # init the limit
        lim = np.zeros_like(y)

        # lower part as rectangle
        mask = np.logical_and(y <= H3, y >= -H3)
        lim[mask] = L3

        # middle part with radius
        mask = np.logical_or(
            np.logical_and(y <= H1 + H3, y > H3), np.logical_and(y >= -H1 - H3, y < -H3)
        )
        lim[mask] = L1 + R * np.cos(alpha) - np.sqrt(R**2 - (abs(y[mask]) - H3) ** 2)

        # upper part with tangential continuation
        mask = np.logical_or(y > H1 + H3, y < -H1 - H3)
        lim[mask] = L2 + np.tan(alpha) * (abs(y[mask]) - H1 - H3)

        return lim

    return mesh, limit
