import matadi as mat
import numpy as np


def fiber_reinforced_rubber(
    C10=0.5,
    fiber_angle=15,
    fiber_modulus=3600,
    fiber_area=0.08,
    thickness=5,
    strain_exponent=0,
    axis=1,
    fiber_distance=1,
):
    """Constitutive material formulation for a fiber-reinforced rubber composite."""

    if axis == 1:
        fiber_axis = 90
    elif axis == 0:
        fiber_axis = 0

    # fiber angle in rad
    a = np.deg2rad(fiber_angle)

    # effective elastic modulus per thickness - correction factor
    factor = fiber_area / (fiber_distance / np.cos(a)) / thickness

    # isotropic hyperelastic material formulation for the rubber
    rubber = mat.MaterialHyperelasticPlaneStressIncompressible(
        mat.models.neo_hooke, C10=C10
    )

    # anisotropic hyperelastic material formulations for the fiber families
    fiber1 = mat.MaterialHyperelasticPlaneStressIncompressible(
        mat.models.fiber,
        E=fiber_modulus * factor,
        angle=fiber_axis - fiber_angle,
        axis=2,
        k=strain_exponent,
    )
    fiber2 = mat.MaterialHyperelasticPlaneStressIncompressible(
        mat.models.fiber,
        E=fiber_modulus * factor,
        angle=fiber_axis + fiber_angle,
        axis=2,
        k=strain_exponent,
    )

    # fiber normal vectors (undeformed configuration)
    vector1 = np.array(
        [
            np.cos(np.deg2rad(fiber_axis - fiber_angle)),
            np.sin(np.deg2rad(fiber_axis - fiber_angle)),
        ]
    )
    vector2 = np.array(
        [
            np.cos(np.deg2rad(fiber_axis + fiber_angle)),
            np.sin(np.deg2rad(fiber_axis + fiber_angle)),
        ]
    )

    return rubber, fiber1, fiber2, vector1, vector2
