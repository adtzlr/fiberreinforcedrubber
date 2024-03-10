import felupe as fem
import matplotlib.pyplot as plt
import numpy as np
import termtables as tt
from pypardiso import spsolve

import fiberreinforcedrubber as frr


def test_specimen_strain(path="."):
    # geometry
    H = 80  # mm
    W = 60  # mm
    thickness = 5  # mm
    middle = 5  # mm
    angle = 54.7546 * 2  # mm
    radius = 42.3  # mm

    # material properties of the two fiber families
    fiber_angle = 19  # deg
    fiber_axis = 1  # axis from which the fiber-angle is measured
    fiber_area = 0.08  # mm^2
    fiber_modulus = 5500  # N/mm^2
    fiber_distance = 1 / 0.95  # mm
    strain_exponent = 1

    # rubber material properties
    C10 = 0.5  # N/mm^2 (half shear modulus)

    # deformation parameters
    tension_max = 7  # mm

    # plot options
    line_segments = 501  # number of lines per cord

    # generate the meshes
    mesh, fibers_1, fibers_2, mask_points_1, mask_points_2 = frr.create_test_specimen(
        width=W,
        height=H,
        radius=radius,
        angle=angle,
        fiber_angle=fiber_angle,
        fiber_axis=fiber_axis,
        fiber_distance=fiber_distance,
        n=line_segments,
        middle=middle,
    )

    # create a numeric region and a displacement field
    region = fem.RegionQuad(mesh)
    field = fem.FieldContainer([fem.Field(region, dim=2)])

    # setup boundary conditions
    bounds, loadcase = fem.dof.shear(field)

    # constitutive material behavior for rubber and cord
    neohooke, fibermat1, fibermat2, vector1, vector2 = frr.fiber_reinforced_rubber(
        C10=C10,
        fiber_angle=fiber_angle,
        fiber_modulus=fiber_modulus,
        fiber_area=fiber_area,
        thickness=thickness,
        strain_exponent=strain_exponent,
        axis=fiber_axis,
        fiber_distance=fiber_distance,
    )

    # solid bodies
    rubber = fem.SolidBody(neohooke, field)
    fiber1 = fem.SolidBody(fibermat1, field)
    fiber2 = fem.SolidBody(fibermat2, field)

    # tension
    step1 = fem.Step(
        items=[rubber, fiber1, fiber2],
        boundaries=bounds,
        ramp={
            bounds["compression_top"]: fem.math.linsteps([0, tension_max], num=5),
            bounds["move"]: fem.math.linsteps([0, 0], num=[5]),
        },
    )

    tension = fem.CharacteristicCurve(steps=[step1], boundary=bounds["move"])
    tension.evaluate(solver=spsolve, tol=1e-2)

    # log. strain as path-plot at y=0 from left to right
    middle = mesh.points[:, 1] == 0

    # deformation gradient of the displacement field
    F = field.extract()[0]

    # principal values of the right Cauchy-Green deformation tensor
    w, v = fem.math.eigh(fem.math.dot(fem.math.transpose(F), F))

    # principal stretches
    stretch = np.sqrt(w)

    # lagrangian log. strain tensor
    strain = np.einsum("a...,ia...,ja...->ij...", np.log(stretch), v, v)[1, 1]  # eps_yy

    # project strain tensor at quadrature points of cells to mesh-points
    log_strain = fem.project(strain, region)

    # mask the middle (y=0)
    coordinates = mesh.points[middle]
    displacements = field[0].values[middle]

    # create a figure
    plt.figure(figsize=(4, 3), dpi=600)
    plt.plot(coordinates[:, 0], log_strain[middle])
    plt.xlabel(r"Position $X$ in mm")
    plt.ylabel(r"Log. Strain $\varepsilon_{yy}$")
    plt.grid()
    plt.tight_layout()

    extensions = [".svg", ".png", ".pdf"]
    for extension in extensions:
        plt.savefig(f"{path}/LogStrainYY_V={tension_max}mm" + extension)

    # combine strain data
    straindata = np.vstack(
        [
            coordinates[:, 0],  # X
            coordinates[:, 1],  # Y
            displacements[:, 0],  # u_x
            displacements[:, 1],  # u_y
            log_strain[middle].ravel(),  # eps_yy
        ]
    ).T
    strainheader = ["X in mm", "Y in mm", "U in mm", "V in mm", "Log. Strain YY"]

    straintable = tt.to_string(
        straindata,
        header=strainheader,
        style=tt.styles.markdown,
        padding=(0, 1),
        alignment="ccccc",
    )

    with open(f"{path}/LogStrainYY_V={tension_max}mm.md", "w") as file:
        file.write(straintable)

    np.savetxt(
        f"{path}/LogStrainYY_V={tension_max}mm.csv",
        straindata,
        header="; ".join(strainheader),
        delimiter="; ",
    )


if __name__ == "__main__":
    test_specimen_strain(path="../docs/images")
