import felupe as fem
import matplotlib.pyplot as plt
import numpy as np
import termtables as tt
from pypardiso import spsolve

import fiberreinforcedrubber as frr


def test_specimen_amplitudes(path=".", take_screenshots=False):
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
    if take_screenshots:
        img = plotter.screenshot(f"{path}/test_specimen_mesh_rubber.png", scale=2)

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
    if take_screenshots:
        img = plotter.screenshot(f"{path}/test_specimen_mesh_fibre.png", scale=2)

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

    # tension and shear at V = 3 mm (Fy = 3 kN)

    fiber_forces = [[], []]

    def evaluate_fiber_forces(i, j, substep):
        field = substep.x

        # get fiber normal forces per undeformed (fiber) area
        force1 = frr.fiber_force(fiber1, thickness, fiber_area, vector1)
        force2 = frr.fiber_force(fiber2, thickness, fiber_area, vector2)

        # interpolate fiber forces to the line-meshes of the fiber families
        r_1 = frr.interpolate(mesh, force1, fibers_1, mask_points_1)
        r_2 = frr.interpolate(mesh, force2, fibers_2, mask_points_2)

        fiber_forces[0].append(r_1)
        fiber_forces[1].append(r_2)

    step = fem.Step(
        items=[rubber, fiber1, fiber2],
        boundaries=bounds,
        ramp={
            bounds["compression_top"]: fem.math.linsteps([3, 3], num=2),
            bounds["move"]: lateral_max * fem.math.linsteps([-1, 1], num=2),
        },
    )
    job = fem.Job(steps=[step], callback=evaluate_fiber_forces)
    job.evaluate(solver=spsolve, tol=1e-2)

    # interpolate displacements to the line-meshes of the fiber families
    u_1 = frr.interpolate(mesh, field[0].values, fibers_1, mask_points_1)
    u_2 = frr.interpolate(mesh, field[0].values, fibers_2, mask_points_2)

    # deformed line mesh for the fibers
    fibers_1.points += u_1
    fibers_2.points += u_2

    # %% postprocessing

    # Deformed Views
    # --------------

    # view on fiber families
    fiberfamilies = [
        (fiber_forces[0], fibers_1, fibers_2, [400, 900]),
        (fiber_forces[1], fibers_2, fibers_1, [400, 900]),
    ]
    for i, (fiberforce, fiberfamily1, fiberfamily2, clim) in enumerate(fiberfamilies):
        view = fem.ViewSolid(field)
        plotter = view.plot(
            off_screen=True,
            theme="document",
            show_edges=False,
            add_axes=False,
        )
        plotter.add_axes(label_size=(0.06, 0.06))

        forcerange = np.abs(fiberforce[-1] - fiberforce[-3])

        fiberview1 = fem.ViewMesh(
            fiberfamily1,
            point_data={
                "Normal Force (Range) per Undeformed Area (Fibre) in MPa": forcerange
            },
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
            "Normal Force (Range) per Undeformed Area (Fibre) in MPa",
            label="Normal Force (Range) per Undeformed Area (Fibre) in MPa",
            plotter=plotter,
            component=None,
            clim=clim,
            below_color="darkgrey",
            above_color="lightgrey",
            line_width=3,
            add_axes=False,
        )
        if take_screenshots:
            img = fiberplotter.screenshot(
                f"{path}/test_specimen_deformed_fibre-amplitudes-{i + 1}.png",
                scale=2,
            )


if __name__ == "__main__":
    test_specimen_amplitudes(path="../docs/images", take_screenshots=True)
