#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" The Largest governed body on the planet, it has various regions and a leader.
"""

import logging
import random
from megacosm.generators.Generator import Generator
from megacosm.generators.Region import Region
from megacosm.generators.Name import Name
#from leader import Leader
from megacosm.generators import Leader


class Country(Generator):
    """ The Country Object includes a leader and one or more regions."""
    def __init__(self, redis, features={}):
        Generator.__init__(self, redis, features)
        self.logger = logging.getLogger(__name__)

        if not hasattr(self, 'regioncount'):
            self.regioncount = random.randint(self.regiondetails['mincount'], self.regiondetails['maxcount'])
        if not hasattr(self, 'leader'):
            self.leader = Leader.Leader(self.redis, {"location":self})
            #self.leader = Leader(self.redis)
        if not hasattr(self, 'name'):
            self.name = Name(self.redis, 'country')

    def add_regions(self):
        """ add regions to the country"""

        if not hasattr(self, 'regions'):
            self.regions = []
            for regionid in range(self.regioncount):
                self.regions.append(Region(self.redis, {'country': self}))

    def __str__(self):
        return self.name.fullname.title()

