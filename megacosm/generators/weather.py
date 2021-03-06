#!/usr/bin/env python
# -*- coding: utf-8 -*-

from generator import Generator
import logging


class Weather(Generator):

    def __init__(self, redis, features={}):

        Generator.__init__(self, redis, features)
        self.logger = logging.getLogger(__name__)

        if not hasattr(self, 'text'):
            self.text = self.render_template(self.template)
        self.text = self.text[0].capitalize() + self.text[1:]

    def __str__(self):
        return self.temp['name']
