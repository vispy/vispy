# -*- coding: utf-8 -*-
# vispy: testskip

# -----------------------------------------------------------------------------
#  A Galaxy Simulator based on the density wave theory
#  (c) 2012 Ingo Berg
#
#  Simulating a Galaxy with the density wave theory
#  http://beltoforion.de/galaxy/galaxy_en.html
#
#  Python version(c) 2014 Nicolas P.Rougier
# -----------------------------------------------------------------------------
import math
import numpy as np


class Galaxy(object):
    """ Galaxy simulation using the density wave theory """

    def __init__(self, n=20000):
        """ Initialize galaxy """

        # Eccentricity of the innermost ellipse
        self._inner_eccentricity = 0.8

        # Eccentricity of the outermost ellipse
        self._outer_eccentricity = 1.0

        # Velocity at the innermost core in km/s
        self._center_velocity = 30

        # Velocity at the core edge in km/s
        self._inner_velocity = 200

        # Velocity at the edge of the disk in km/s
        self._outer_velocity = 300

        # Angular offset per parsec
        self._angular_offset = 0.019

        # Inner core radius
        self._core_radius = 6000

        # Galaxy radius
        self._galaxy_radius = 15000

        # The radius after which all density waves must have circular shape
        self._distant_radius = 0

        # Distribution of stars
        self._star_distribution = 0.45

        # Angular velocity of the density waves
        self._angular_velocity = 0.000001

        # Number of stars
        self._stars_count = n

        # Number of dust particles
        self._dust_count = int(self._stars_count * 0.75)

        # Number of H-II regions
        self._h2_count = 200

        # Particles
        dtype = [('theta',       np.float32, 1),
                 ('velocity',    np.float32, 1),
                 ('angle',       np.float32, 1),
                 ('m_a',         np.float32, 1),
                 ('m_b',         np.float32, 1),
                 ('size',        np.float32, 1),
                 ('type',        np.float32, 1),
                 ('temperature', np.float32, 1),
                 ('brightness',  np.float32, 1),
                 ('position',    np.float32, 2)]
        n = self._stars_count + self._dust_count + 2*self._h2_count
        self._particles = np.zeros(n, dtype=dtype)

        i0 = 0
        i1 = i0 + self._stars_count
        self._stars = self._particles[i0:i1]
        self._stars['size'] = 3.
        self._stars['type'] = 0

        i0 = i1
        i1 = i0 + self._dust_count
        self._dust = self._particles[i0:i1]
        self._dust['size'] = 64
        self._dust['type'] = 1

        i0 = i1
        i1 = i0 + self._h2_count
        self._h2a = self._particles[i0:i1]
        self._h2a['size'] = 0
        self._h2a['type'] = 2

        i0 = i1
        i1 = i0 + self._h2_count
        self._h2b = self._particles[i0:i1]
        self._h2b['size'] = 0
        self._h2b['type'] = 3

    def __len__(self):
        """ Number of particles """

        if self._particles is not None:
            return len(self._particles)
        return 0

    def __getitem__(self, key):
        """ x.__getitem__(y) <==> x[y] """

        if self._particles is not None:
            return self._particles[key]
        return None

    def reset(self, rad, radCore, deltaAng,
              ex1, ex2, sigma, velInner, velOuter):

        # Initialize parameters
        # ---------------------
        self._inner_eccentricity = ex1
        self._outer_eccentricity = ex2
        self._inner_velocity = velInner
        self._outer_velocity = velOuter
        self._angular_offset = deltaAng
        self._core_radius = radCore
        self._galaxy_radius = rad
        self._distant_radius = self._galaxy_radius * 2
        self.m_sigma = sigma

        # Initialize stars
        # ----------------
        stars = self._stars
        R = np.random.normal(0, sigma, len(stars)) * self._galaxy_radius
        stars['m_a'] = R
        stars['angle'] = 90 - R * self._angular_offset
        stars['theta'] = np.random.uniform(0, 360, len(stars))
        stars['temperature'] = np.random.uniform(3000, 9000, len(stars))
        stars['brightness'] = np.random.uniform(0.05, 0.25, len(stars))
        stars['velocity'] = 0.000005

        for i in range(len(stars)):
            stars['m_b'][i] = R[i] * self.eccentricity(R[i])

        # Initialize dust
        # ---------------
        dust = self._dust
        X = np.random.uniform(0, 2*self._galaxy_radius, len(dust))
        Y = np.random.uniform(-self._galaxy_radius, self._galaxy_radius,
                              len(dust))
        R = np.sqrt(X*X+Y*Y)
        dust['m_a'] = R
        dust['angle'] = R * self._angular_offset
        dust['theta'] = np.random.uniform(0, 360, len(dust))
        dust['velocity'] = 0.000005
        dust['temperature'] = 6000 + R/4
        dust['brightness'] = np.random.uniform(0.01, 0.02)
        for i in range(len(dust)):
            dust['m_b'][i] = R[i] * self.eccentricity(R[i])

        # Initialise H-II
        # ---------------
        h2a, h2b = self._h2a, self._h2b
        X = np.random.uniform(-self._galaxy_radius, self._galaxy_radius,
                              len(h2a))
        Y = np.random.uniform(-self._galaxy_radius, self._galaxy_radius,
                              len(h2a))
        R = np.sqrt(X*X+Y*Y)

        h2a['m_a'] = R
        h2b['m_a'] = R + 1000

        h2a['angle'] = R * self._angular_offset
        h2b['angle'] = h2a['angle']

        h2a['theta'] = np.random.uniform(0, 360, len(h2a))
        h2b['theta'] = h2a['theta']

        h2a['velocity'] = 0.000005
        h2b['velocity'] = 0.000005

        h2a['temperature'] = np.random.uniform(3000, 9000, len(h2a))
        h2b['temperature'] = h2a['temperature']

        h2a['brightness'] = np.random.uniform(0.005, 0.010, len(h2a))
        h2b['brightness'] = h2a['brightness']

        for i in range(len(h2a)):
            h2a['m_b'][i] = R[i] * self.eccentricity(R[i])
        h2b['m_b'] = h2a['m_b']

    def update(self, timestep=100000):
        """ Update simulation """

        self._particles['theta'] += self._particles['velocity'] * timestep

        P = self._particles
        a, b = P['m_a'], P['m_b']
        theta, beta = P['theta'], -P['angle']

        alpha = theta * math.pi / 180.0
        cos_alpha = np.cos(alpha)
        sin_alpha = np.sin(alpha)
        cos_beta = np.cos(beta)
        sin_beta = np.sin(beta)
        P['position'][:, 0] = a*cos_alpha*cos_beta - b*sin_alpha*sin_beta
        P['position'][:, 1] = a*cos_alpha*sin_beta + b*sin_alpha*cos_beta

        D = np.sqrt(((self._h2a['position'] -
                    self._h2b['position'])**2).sum(axis=1))
        S = np.maximum(1, ((1000-D)/10) - 50)
        self._h2a['size'] = 2.0*S
        self._h2b['size'] = S/6.0

    def eccentricity(self, r):

        # Core region of the galaxy. Innermost part is round
        # eccentricity increasing linear to the border of the core.
        if r < self._core_radius:
            return 1 + (r / self._core_radius) * (self._inner_eccentricity-1)

        elif r > self._core_radius and r <= self._galaxy_radius:
            a = self._galaxy_radius - self._core_radius
            b = self._outer_eccentricity - self._inner_eccentricity
            return self._inner_eccentricity + (r - self._core_radius) / a * b

        # Eccentricity is slowly reduced to 1.
        elif r > self._galaxy_radius and r < self._distant_radius:
            a = self._distant_radius - self._galaxy_radius
            b = 1 - self._outer_eccentricity
            return self._outer_eccentricity + (r - self._galaxy_radius) / a * b

        else:
            return 1
