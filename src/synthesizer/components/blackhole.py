"""A module for holding blackhole emission models.

The class defined here should never be instantiated directly, there are only
ever instantiated by the parametric/particle child classes.
"""

import numpy as np
from unyt import c, cm, deg, km, s

from synthesizer import exceptions
from synthesizer.sed import plot_spectra
from synthesizer.units import Quantity


class BlackholesComponent:
    """
    The parent class for stellar components of a galaxy.

    This class contains the attributes and spectra creation methods which are
    common to both parametric and particle stellar components.

    This should never be instantiated directly, instead it provides the common
    functionality and attributes used by the child parametric and particle
    BlackHole/s classes.

    Attributes:
        spectra (dict, Sed)
            A dictionary containing black hole spectra.
        mass (array-like, float)
            The mass of each blackhole.
        accretion_rate (array-like, float)
            The accretion rate of each blackhole.
        epsilon (array-like, float)
            The radiative efficiency of the blackhole.
        accretion_rate_eddington (array-like, float)
            The accretion rate expressed as a fraction of the Eddington
            accretion rate.
        inclination (array-like, float)
            The inclination of the blackhole disc.
        spin (array-like, float)
            The dimensionless spin of the blackhole.
        bolometric_luminosity (array-like, float)
            The bolometric luminosity of the blackhole.
        metallicity (array-like, float)
            The metallicity of the blackhole which is assumed for the line
            emitting regions.

    Attributes (For EmissionModels):
        ionisation_parameter_blr (array-like, float)
            The ionisation parameter of the broad line region.
        hydrogen_density_blr (array-like, float)
            The hydrogen density of the broad line region.
        covering_fraction_blr (array-like, float)
            The covering fraction of the broad line region (effectively
            the escape fraction).
        velocity_dispersion_blr (array-like, float)
            The velocity dispersion of the broad line region.
        ionisation_parameter_nlr (array-like, float)
            The ionisation parameter of the narrow line region.
        hydrogen_density_nlr (array-like, float)
            The hydrogen density of the narrow line region.
        covering_fraction_nlr (array-like, float)
            The covering fraction of the narrow line region (effectively
            the escape fraction).
        velocity_dispersion_nlr (array-like, float)
            The velocity dispersion of the narrow line region.
        theta_torus (array-like, float)
            The angle of the torus.
        torus_fraction (array-like, float)
            The fraction of the torus angle to 90 degrees.
    """

    # Define class level Quantity attributes
    accretion_rate = Quantity()
    inclination = Quantity()
    bolometric_luminosity = Quantity()
    eddington_luminosity = Quantity()
    bb_temperature = Quantity()
    mass = Quantity()

    def __init__(
        self,
        mass=None,
        accretion_rate=None,
        epsilon=0.1,
        accretion_rate_eddington=None,
        inclination=0.0 * deg,
        spin=None,
        bolometric_luminosity=None,
        metallicity=None,
        ionisation_parameter_blr=0.1,
        hydrogen_density_blr=1e9 / cm**3,
        covering_fraction_blr=0.1,
        velocity_dispersion_blr=2000 * km / s,
        ionisation_parameter_nlr=0.01,
        hydrogen_density_nlr=1e4 / cm**3,
        covering_fraction_nlr=0.1,
        velocity_dispersion_nlr=500 * km / s,
        theta_torus=10 * deg,
        **kwargs,
    ):
        """
        Initialise the BlackholeComponent.

        Where they're not provided missing quantities are automatically
        calcualted. Not all parameters need to be set for every emission model.

        Args:
            mass (array-like, float)
                The mass of each blackhole.
            accretion_rate (array-like, float)
                The accretion rate of each blackhole.
            epsilon (array-like, float)
                The radiative efficiency of the blackhole.
            accretion_rate_eddington (array-like, float)
                The accretion rate expressed as a fraction of the Eddington
                accretion rate.
            inclination (array-like, float)
                The inclination of the blackhole disc.
            spin (array-like, float)
                The dimensionless spin of the blackhole.
            bolometric_luminosity (array-like, float)
                The bolometric luminosity of the blackhole.
            metallicity (array-like, float)
                The metallicity of the blackhole which is assumed for the line
                emitting regions.
            ionisation_parameter_blr (array-like, float)
                The ionisation parameter of the broadline region.
            hydrogen_density_blr (array-like, float)
                The hydrogen density of the broad line region.
            covering_fraction_blr (array-like, float)
                The covering fraction of the broad line region (effectively
                the escape fraction).
            velocity_dispersion_blr (array-like, float)
                The velocity dispersion of the broad line region.
            ionisation_parameter_nlr (array-like, float)
                The ionisation parameter of the narrow line region.
            hydrogen_density_nlr (array-like, float)
                The hydrogen density of the narrow line region.
            covering_fraction_nlr (array-like, float)
                The covering fraction of the narrow line region (effectively
                the escape fraction).
            velocity_dispersion_nlr (array-like, float)
                The velocity dispersion of the narrow line region.
            theta_torus (array-like, float)
                The angle of the torus.
            kwargs (dict)
                Any other parameter for the emission models can be provided as
                kwargs.
        """
        # Initialise spectra
        self.spectra = {}

        # Intialise the photometry dictionaries
        self.photo_luminosities = {}
        self.photo_fluxes = {}

        # Save the black hole properties
        self.mass = mass
        self.accretion_rate = accretion_rate
        self.epsilon = epsilon
        self.accretion_rate_eddington = accretion_rate_eddington
        self.spin = spin
        self.bolometric_luminosity = bolometric_luminosity
        self.metallicity = metallicity

        # Below we attach all the possible attributes that could be needed by
        # the emission models.

        # Set BLR attributes
        self.ionisation_parameter_blr = ionisation_parameter_blr
        self.hydrogen_density_blr = hydrogen_density_blr
        self.covering_fraction_blr = covering_fraction_blr
        self.velocity_dispersion_blr = velocity_dispersion_blr

        # Set NLR attributes
        self.ionisation_parameter_nlr = ionisation_parameter_nlr
        self.hydrogen_density_nlr = hydrogen_density_nlr
        self.covering_fraction_nlr = covering_fraction_nlr
        self.velocity_dispersion_nlr = velocity_dispersion_nlr

        # The inclination of the black hole disc
        self.inclination = (
            inclination if inclination is not None else 0.0 * deg
        )

        # The angle of the torus
        self.theta_torus = theta_torus
        self.torus_fraction = (self.theta_torus / (90 * deg)).value
        self._torus_edgeon_cond = self.inclination + self.theta_torus

        # Set any of the extra attribute provided as kwargs
        for key, val in kwargs.items():
            setattr(self, key, val)

        # Check to make sure that both accretion rate and bolometric luminosity
        # haven't been provided because that could be confusing.
        if (self.accretion_rate is not None) and (
            self.bolometric_luminosity is not None
        ):
            raise exceptions.InconsistentArguments(
                """Both accretion rate and bolometric luminosity provided but
                that is confusing. Provide one or the other!"""
            )

        if (self.accretion_rate_eddington is not None) and (
            self.bolometric_luminosity is not None
        ):
            raise exceptions.InconsistentArguments(
                """Both accretion rate (in terms of Eddington) and bolometric
                luminosity provided but that is confusing. Provide one or
                the other!"""
            )

        # If mass, accretion_rate, and epsilon provided calculate the
        # bolometric luminosity.
        if (
            self.mass is not None
            and self.accretion_rate is not None
            and self.epsilon is not None
        ):
            self.calculate_bolometric_luminosity()

        # If mass, accretion_rate, and epsilon provided calculate the
        # big bump temperature.
        if (
            self.mass is not None
            and self.accretion_rate is not None
            and self.epsilon is not None
        ):
            self.calculate_bb_temperature()

        # If mass calculate the Eddington luminosity.
        if self.mass is not None:
            self.calculate_eddington_luminosity()

        # If mass, accretion_rate, and epsilon provided calculate the
        # Eddington ratio.
        if (
            self.mass is not None
            and self.accretion_rate is not None
            and self.epsilon is not None
        ):
            self.calculate_eddington_ratio()

        # If mass, accretion_rate, and epsilon provided calculate the
        # accretion rate in units of the Eddington accretion rate. This is the
        # bolometric_luminosity / eddington_luminosity.
        if (
            self.mass is not None
            and self.accretion_rate is not None
            and self.epsilon is not None
        ):
            self.calculate_accretion_rate_eddington()

        # If inclination, calculate the cosine of the inclination, required by
        # some models (e.g. AGNSED).
        if self.inclination is not None:
            self.cosine_inclination = np.cos(
                self.inclination.to("radian").value
            )

    def _prepare_sed_args(self, *args, **kwargs):
        """
        This method is a prototype for generating the arguments for spectra
        generation from AGN grids. It is redefined on the child classes to
        handle the different attributes of parametric and particle cases.
        """
        raise Warning(
            (
                "_prepare_sed_args should be overloaded by child classes:\n"
                "`particle.BlackHoles`\n"
                "`parametric.BlackHole`\n"
                "You should not be seeing this!!!"
            )
        )

    def generate_lnu(
        self,
        grid,
        spectra_name,
        fesc=0.0,
        mask=None,
        verbose=False,
        grid_assignment_method="cic",
        nthreads=0,
    ):
        """
        Generate integrated rest frame spectra for a given key.

        Args:
            emission_model (synthesizer.blackhole_emission_models.*)
                An instance of a blackhole emission model.
            grid (obj):
                Spectral grid object.
            fesc (float):
                Fraction of emission that escapes unattenuated from
                the birth cloud (defaults to 0.0).
            spectra_name (string)
                The name of the target spectra inside the grid file
                (e.g. "incident", "transmitted", "nebular").
            mask (array-like, bool)
                If not None this mask will be applied to the inputs to the
                spectra creation.
            verbose (bool)
                Are we talking?
            grid_assignment_method (string)
                The type of method used to assign particles to a SPS grid
                point. Allowed methods are cic (cloud in cell) or nearest
                grid point (ngp) or there uppercase equivalents (CIC, NGP).
                Defaults to cic.
            nthreads (int)
                The number of threads to use in the C extension. If -1 then
                all available threads are used.
        """
        # Ensure we have a key in the grid. If not error.
        if spectra_name not in list(grid.spectra.keys()):
            raise exceptions.MissingSpectraType(
                f"The Grid does not contain the key '{spectra_name}'"
            )

        # If the mask is False (parametric case) or contains only
        # 0 (particle case) just return an array of zeros
        if isinstance(mask, bool) and not mask:
            return np.zeros(len(grid.lam))
        if mask is not None and np.sum(mask) == 0:
            return np.zeros(len(grid.lam))

        from ..extensions.integrated_spectra import compute_integrated_sed

        # Prepare the arguments for the C function.
        args = self._prepare_sed_args(
            grid,
            fesc=fesc,
            spectra_type=spectra_name,
            mask=mask,
            grid_assignment_method=grid_assignment_method.lower(),
            nthreads=nthreads,
        )

        # Get the integrated spectra in grid units (erg / s / Hz)
        return compute_integrated_sed(*args)

    def __str__(self):
        """
        Return a basic summary of the BlackHoles object.

        Returns a string containing the total mass formed and lists of the
        available SEDs, lines, and images.

        Returns
            str
                Summary string containing the total mass formed and lists
                of the available SEDs, lines, and images.
        """
        # Define the width to print within
        width = 80
        pstr = ""
        pstr += "-" * width + "\n"
        pstr += "SUMMARY OF BLACKHOLE".center(width + 4) + "\n"
        # pstr += get_centred_art(Art.blackhole, width) + "\n"

        pstr += f"Number of blackholes: {self.mass.size} \n"

        for attribute_id in [
            "mass",
            "accretion_rate",
            "accretion_rate_eddington",
            "bolometric_luminosity",
            "eddington_ratio",
            "bb_temperature",
            "eddington_luminosity",
            "spin",
            "epsilon",
            "inclination",
            "cosine_inclination",
        ]:
            attr = getattr(self, attribute_id, None)
            if attr is not None:
                attr = np.round(attr, 3)
                pstr += f"{attribute_id}: {attr} \n"

        return pstr

    def calculate_bolometric_luminosity(self):
        """
        Calculate the black hole bolometric luminosity. This is by itself
        useful but also used for some emission models.

        Returns
            unyt_array
                The black hole bolometric luminosity
        """

        self.bolometric_luminosity = self.epsilon * self.accretion_rate * c**2

        return self.bolometric_luminosity

    def calculate_eddington_luminosity(self):
        """
        Calculate the eddington luminosity of the black hole.

        Returns
            unyt_array
                The black hole bolometric luminosity
        """

        # Note: the factor 1.257E38 comes from:
        # 4*pi*G*mp*c*Msun/sigma_thompson
        self.eddington_luminosity = 1.257e38 * self._mass

        return self.eddington_luminosity

    def calculate_eddington_ratio(self):
        """
        Calculate the eddington ratio of the black hole.

        Returns
            unyt_array
                The black hole eddington ratio
        """

        self.eddington_ratio = (
            self._bolometric_luminosity / self._eddington_luminosity
        )

        return self.eddington_ratio

    def calculate_bb_temperature(self):
        """
        Calculate the black hole big bump temperature. This is used for the
        cloudy disc model.

        Returns
            unyt_array
                The black hole bolometric luminosity
        """

        # Calculate the big bump temperature
        self.bb_temperature = (
            2.24e9 * self._accretion_rate ** (1 / 4) * self._mass**-0.5
        )

        return self.bb_temperature

    def calculate_accretion_rate_eddington(self):
        """
        Calculate the black hole accretion in units of the Eddington rate.

        Returns
            unyt_array
                The black hole accretion rate in units of the Eddington rate.
        """

        self.accretion_rate_eddington = (
            self._bolometric_luminosity / self._eddington_luminosity
        )

        return self.accretion_rate_eddington

    def get_photo_luminosities(self, filters, verbose=True):
        """
        Calculate luminosity photometry using a FilterCollection object.

        Args:
            filters (filters.FilterCollection)
                A FilterCollection object.
            verbose (bool)
                Are we talking?

        Returns:
            photo_luminosities (dict)
                A dictionary of rest frame broadband luminosities.
        """
        # Loop over spectra in the component
        for spectra in self.spectra:
            # Create the photometry collection and store it in the object
            self.photo_luminosities[spectra] = self.spectra[
                spectra
            ].get_photo_luminosities(filters, verbose)

        return self.photo_luminosities

    def get_photo_fluxes(self, filters, verbose=True):
        """
        Calculate flux photometry using a FilterCollection object.

        Args:
            filters (object)
                A FilterCollection object.
            verbose (bool)
                Are we talking?

        Returns:
            (dict)
                A dictionary of fluxes in each filter in filters.
        """
        # Loop over spectra in the component
        for spectra in self.spectra:
            # Create the photometry collection and store it in the object
            self.photo_fluxes[spectra] = self.spectra[
                spectra
            ].get_photo_fluxes(filters, verbose)

        return self.photo_fluxes

    def plot_spectra(
        self,
        spectra_to_plot=None,
        show=False,
        ylimits=(),
        xlimits=(),
        figsize=(3.5, 5),
        **kwargs,
    ):
        """
        Plots either specific spectra (specified via spectra_to_plot) or all
        spectra on the child Stars object.

        Args:
            spectra_to_plot (string/list, string)
                The specific spectra to plot.
                    - If None all spectra are plotted.
                    - If a list of strings each specifc spectra is plotted.
                    - If a single string then only that spectra is plotted.
            show (bool)
                Flag for whether to show the plot or just return the
                figure and axes.
            ylimits (tuple)
                The limits to apply to the y axis. If not provided the limits
                will be calculated with the lower limit set to 1000 (100)
                times less than the peak of the spectrum for rest_frame
                (observed) spectra.
            xlimits (tuple)
                The limits to apply to the x axis. If not provided the optimal
                limits are found based on the ylimits.
            figsize (tuple)
                Tuple with size 2 defining the figure size.
            kwargs (dict)
                arguments to the `sed.plot_spectra` method called from this
                wrapper

        Returns:
            fig (matplotlib.pyplot.figure)
                The matplotlib figure object for the plot.
            ax (matplotlib.axes)
                The matplotlib axes object containing the plotted data.
        """
        # Handling whether we are plotting all spectra, specific spectra, or
        # a single spectra
        if spectra_to_plot is None:
            spectra = self.spectra
        elif isinstance(spectra_to_plot, (list, tuple)):
            spectra = {key: self.spectra[key] for key in spectra_to_plot}
        else:
            spectra = self.spectra[spectra_to_plot]

        return plot_spectra(
            spectra,
            show=show,
            ylimits=ylimits,
            xlimits=xlimits,
            figsize=figsize,
            draw_legend=isinstance(spectra, dict),
            **kwargs,
        )

    def get_spectra(
        self,
        emission_model,
        dust_curves=None,
        tau_v=None,
        covering_fraction=None,
        mask=None,
        verbose=True,
        **kwargs,
    ):
        """
        Generate black hole spectra as described by the emission model.

        Args:
            emission_model (EmissionModel):
                The emission model to use.
            dust_curves (dict):
                An override to the emission model dust curves. Either:
                    - None, indicating the dust_curves defined on the emission
                      models should be used.
                    - A single dust curve to apply to all emission models.
                    - A dictionary of the form {<label>: <dust_curve instance>}
                      to use a specific dust curve instance with particular
                      properties.
            tau_v (dict):
                An override to the dust model optical depth. Either:
                    - None, indicating the tau_v defined on the emission model
                      should be used.
                    - A float to use as the optical depth for all models.
                    - A dictionary of the form {<label>: float(<tau_v>)}
                      to use a specific optical depth with a particular
                      model or {<label>: str(<attribute>)} to use an attribute
                      of the component as the optical depth.
            fesc (dict):
                An override to the emission model escape fraction. Either:
                    - None, indicating the fesc defined on the emission model
                      should be used.
                    - A float to use as the escape fraction for all models.
                    - A dictionary of the form {<label>: float(<fesc>)}
                      to use a specific escape fraction with a particular
                      model or {<label>: str(<attribute>)} to use an
                      attribute of the component as the escape fraction.
            mask (dict):
                An override to the emission model mask. Either:
                    - None, indicating the mask defined on the emission model
                      should be used.
                    - A dictionary of the form {<label>: {"attr": attr,
                      "thresh": thresh, "op": op}} to add a specific mask to
                      a particular model.
            verbose (bool)
                Are we talking?
            kwargs (dict)
                Any additional keyword arguments to pass to the generator
                function.

        Returns:
            dict
                A dictionary of spectra which can be attached to the
                appropriate spectra attribute of the component
                (spectra/particle_spectra)
        """
        # Get the spectra
        spectra = emission_model._get_spectra(
            emitters={"blackhole": self},
            per_particle=False,
            dust_curves=dust_curves,
            tau_v=tau_v,
            fesc=covering_fraction,
            mask=mask,
            verbose=verbose,
            **kwargs,
        )

        # Update the spectra dictionary
        self.spectra.update(spectra)

        return self.spectra[emission_model.label]

    def get_lines(
        self,
        line_ids,
        emission_model,
        dust_curves=None,
        tau_v=None,
        covering_fraction=None,
        mask=None,
        verbose=True,
        **kwargs,
    ):
        """
        Generate stellar lines as described by the emission model.

        Args:
            line_ids (list):
                A list of line_ids. Doublets can be specified as a nested list
                or using a comma (e.g. 'OIII4363,OIII4959').
            emission_model (EmissionModel):
                The emission model to use.
            dust_curves (dict):
                An override to the emission model dust curves. Either:
                    - None, indicating the dust_curves defined on the emission
                      models should be used.
                    - A single dust curve to apply to all emission models.
                    - A dictionary of the form {<label>: <dust_curve instance>}
                      to use a specific dust curve instance with particular
                      properties.
            tau_v (dict):
                An override to the dust model optical depth. Either:
                    - None, indicating the tau_v defined on the emission model
                      should be used.
                    - A float to use as the optical depth for all models.
                    - A dictionary of the form {<label>: float(<tau_v>)}
                      to use a specific optical depth with a particular
                      model or {<label>: str(<attribute>)} to use an attribute
                      of the component as the optical depth.
            fesc (dict):
                An override to the emission model escape fraction. Either:
                    - None, indicating the fesc defined on the emission model
                      should be used.
                    - A float to use as the escape fraction for all models.
                    - A dictionary of the form {<label>: float(<fesc>)}
                      to use a specific escape fraction with a particular
                      model or {<label>: str(<attribute>)} to use an
                      attribute of the component as the escape fraction.
            mask (dict):
                An override to the emission model mask. Either:
                    - None, indicating the mask defined on the emission model
                      should be used.
                    - A dictionary of the form {<label>: {"attr": attr,
                      "thresh": thresh, "op": op}} to add a specific mask to
                      a particular model.
            verbose (bool)
                Are we talking?
            kwargs (dict)
                Any additional keyword arguments to pass to the generator
                function.

        Returns:
            LineCollection
                A LineCollection object containing the lines defined by the
                root model.
        """
        # Get the lines
        lines = emission_model._get_lines(
            line_ids=line_ids,
            emitters={"blackhole": self},
            per_particle=False,
            dust_curves=dust_curves,
            tau_v=tau_v,
            fesc=covering_fraction,
            mask=mask,
            verbose=verbose,
            **kwargs,
        )

        # Update the lines dictionary
        self.lines.update(lines)

        return self.lines[emission_model.label]
