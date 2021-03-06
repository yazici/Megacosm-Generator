#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" A Sect is an unusual following of a deity."""

import logging
import random
from megacosm.generators.generator import Generator
from megacosm.generators.name import Name
#from megacosm.generators import deity
import deity

class Sect(Generator):
    """ A group of religious believers """
    def __init__(self, redis, features={}):

        Generator.__init__(self, redis, features)
        self.logger = logging.getLogger(__name__)

        if not hasattr(self, 'deity'):
            self.deity = deity.Deity(redis)

        if not hasattr(self, 'domain'):
            portfolio = self.deity.portfolios
            random.shuffle(portfolio)
            self.domain = portfolio[0]

        self.name = Name(self.redis, 'sect')

    def __str__(self):
        return self.name.shortname

