import felupe as fem
import matplotlib.pyplot as plt
import numpy as np
import termtables as tt
from pypardiso import spsolve

import fiberreinforcedrubber as frr


def test_specimen_simulation():
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
    lateral_max = 23
    tension_max = 8

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

    # View the rubber mesh
    view = fem.ViewMesh(mesh)
    plotter = view.plot(
        off_screen=True,
        theme="document",
        add_axes=False,
        edge_color="black",
        color="lightgrey",
        line_width=4,
    )
    plotter.camera.tight()
    # plotter.add_axes(label_size=(0.06, 0.06), viewport=(-0.1, -0.1, 0.2, 0.2))
    # plotter.camera.zoom(0.8)
    img = plotter.screenshot("../docs/images/test_specimen_mesh_rubber.png", scale=2)

    # View the fiber mesh
    view = fem.ViewMesh(fem.mesh.concatenate([fibers_1, fibers_2]))
    plotter = view.plot(
        off_screen=True,
        theme="document",
        add_axes=False,
        color="black",
        line_width=4,
    )
    plotter.camera.tight()
    # plotter.add_axes(label_size=(0.06, 0.06), viewport=(-0.1, -0.1, 0.2, 0.2))
    # plotter.camera.zoom(0.8)
    img = plotter.screenshot("../docs/images/test_specimen_mesh_fibre.png", scale=2)

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
            bounds["compression_top"]: fem.math.linsteps(
                [0, tension_max], num=tension_max
            ),
            bounds["move"]: fem.math.linsteps([0, 0], num=tension_max),
        },
    )

    tension = fem.CharacteristicCurve(steps=[step1], boundary=bounds["move"])
    tension.evaluate(solver=spsolve, tol=1e-2)

    # tension and shear
    step2 = fem.Step(
        items=[rubber, fiber1, fiber2],
        boundaries=bounds,
        ramp={
            bounds["compression_top"]: fem.math.linsteps(
                [0, tension_max], num=tension_max
            ),
            bounds["move"]: fem.math.linsteps(
                [lateral_max, lateral_max], num=tension_max
            ),
        },
    )

    tensionshear = fem.CharacteristicCurve(steps=[step2], boundary=bounds["move"])
    tensionshear.evaluate(solver=spsolve, tol=1e-2)

    # tension and shear at Fy = 3 kN
    step3 = fem.Step(
        items=[rubber, fiber1, fiber2],
        boundaries=bounds,
        ramp={
            bounds["compression_top"]: fem.math.linsteps([3], num=0),
            bounds["move"]: fem.math.linsteps([lateral_max], num=0),
        },
    )

    tensionshear_3kN = fem.CharacteristicCurve(steps=[step3], boundary=bounds["move"])
    tensionshear_3kN.evaluate(solver=spsolve, tol=1e-2)

    # get fiber normal forces per undeformed (fiber) area
    force1 = frr.fiber_force(fiber1, thickness, fiber_area, vector1)
    force2 = frr.fiber_force(fiber2, thickness, fiber_area, vector2)

    # interpolate displacements to the line-meshes of the fiber families
    u_1 = frr.interpolate(mesh, field[0].values, fibers_1, mask_points_1)
    u_2 = frr.interpolate(mesh, field[0].values, fibers_2, mask_points_2)

    # interpolate fiber forces to the line-meshes of the fiber families
    r_1 = frr.interpolate(mesh, force1, fibers_1, mask_points_1)
    r_2 = frr.interpolate(mesh, force2, fibers_2, mask_points_2)

    # deformed line mesh for the fibers
    fibers_1.points += u_1
    fibers_2.points += u_2

    # %% postprocessing

    # init a plot for the force-displacement curves
    fig, ax = plt.subplots(ncols=2, sharey=True)

    # add force-displacement curves
    fig, ax[0] = tension.plot(
        xaxis=1,
        yaxis=1,
        yscale=1e-3 * thickness,
        xlabel=r"Displacement $V$ in mm",
        ylabel=r"Force $F_Y$ in kN",
        fig=fig,
        ax=ax[0],
        ls="--",
        color="C3",
        label=r"$U = 0$ mm",
    )

    fig, ax[0] = tensionshear.plot(
        xaxis=1,
        yaxis=1,
        yscale=1e-3 * thickness,
        xlabel=r"Displacement $V$ in mm",
        ylabel=r"Force $F_Y$ in kN",
        fig=fig,
        ax=ax[0],
        color="C0",
        label=r"$U = \pm 23$ mm",
    )

    fig, ax[1] = tensionshear.plot(
        x=tensionshear.y,
        xaxis=1,
        yaxis=0,
        xscale=1e-3 * thickness,
        yscale=1e-3 * thickness,
        ylabel=r"Force $F_X$ ($U=23$ mm) in kN",
        swapaxes=True,
        fig=fig,
        ax=ax[1],
        color="C2",
    )

    ax[0].legend()
    [axis.grid(True) for axis in ax]

    extensions = [".svg", ".png", ".pdf"]
    for extension in extensions:
        fig.savefig("../docs/images/test_specimen_forces_vs_displacement" + extension)

    # Characteristic Curves as Tables
    # -------------------------------

    header = ["V in mm", "FY(U=0) in kN", "FY(U=23) in kN", "FX(U=23) in kN"]
    data = np.vstack(
        (
            ax[0].lines[0].get_xdata(),
            ax[0].lines[0].get_ydata(),
            ax[0].lines[1].get_ydata(),
            ax[1].lines[0].get_xdata(),
        )
    ).T
    data[:, :] = np.round(data[:, :], 4)

    table = tt.to_string(
        data, header=header, style=tt.styles.markdown, padding=(0, 1), alignment="cccc"
    )

    with open("../docs/images/test_specimen_forces_vs_displacement.md", "w") as file:
        file.write(table)

    np.savetxt(
        "../docs/images/test_specimen_forces_vs_displacement.csv",
        data,
        header="; ".join(header),
        delimiter="; ",
    )

    # Deformed Views
    # --------------

    # Kirchhoff stress tensor is necessary for plane stress analysis
    # due to the incompressible material formulation it is equal to the Cauchy stress
    view = fem.ViewSolid(field, solid=rubber, stress_type="Kirchhoff")
    plotter = view.plot(
        "Principal Values of Kirchhoff Stress",
        label="Cauchy Stress (Max. Principal) in MPa",
        off_screen=True,
        theme="document",
        add_axes=False,
    )
    plotter.add_axes(label_size=(0.06, 0.06))
    img = plotter.screenshot(
        "../docs/images/test_specimen_deformed_rubber.png", scale=2
    )

    # view on fiber families
    fiberfamilies = [(fibers_1, fibers_2, [400, 900]), (fibers_2, fibers_1, [400, 900])]
    for i, (fiberfamily1, fiberfamily2, clim) in enumerate(fiberfamilies):
        view = fem.ViewSolid(field)
        plotter = view.plot(
            off_screen=True,
            theme="document",
            show_edges=False,
            add_axes=False,
        )
        plotter.add_axes(label_size=(0.06, 0.06))

        fiberview1 = fem.ViewMesh(
            fiberfamily1,
            point_data={"Normal Force per Undeformed Area (Fibre) in MPa": r_1},
        )
        fiberview2 = fem.ViewMesh(
            fiberfamily2,
        )
        plotter = fiberview2.plot(
            plotter=plotter,
            line_width=3,
            add_axes=False,
        )
        fiberplotter = fiberview1.plot(
            "Normal Force per Undeformed Area (Fibre) in MPa",
            label="Normal Force per Undeformed Area (Fibre) in MPa",
            plotter=plotter,
            component=None,
            clim=clim,
            below_color="darkgrey",
            above_color="lightgrey",
            line_width=3,
            add_axes=False,
        )
        img = fiberplotter.screenshot(
            f"../docs/images/test_specimen_deformed_fibre-{i + 1}.png", scale=2
        )


if __name__ == "__main__":
    test_specimen_simulation()
