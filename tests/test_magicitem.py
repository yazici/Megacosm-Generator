#!/usr/bin/env python
# -*- coding: utf-8 -*-

"Fully test this module's functionality through the use of fixtures."

from megacosm.generators import MagicItem
from megacosm.generators import NPC
from megacosm.generators import Curse
import unittest2 as unittest
import fixtures
import fakeredis
from config import TestConfiguration


class TestMagicItem(unittest.TestCase):

    def setUp(self):
        """  """
        self.redis = fakeredis.FakeRedis()
        fixtures.magicitem.import_fixtures(self)
        fixtures.npc.import_fixtures(self)
        fixtures.phobia.import_fixtures(self)
        fixtures.motivation.import_fixtures(self)
        fixtures.curse.import_fixtures(self)
        self.redis.lpush('npc_race','gnome')

    def tearDown(self):
        self.redis.flushall()

    def test_random_magicitem(self):
        """  Test a "random" magicitem. """
        magicitem = MagicItem(self.redis)
        self.assertEqual('Muffled Leather Armor Of Shock', str(magicitem))

    def test_magicitem_static_npc(self):
        """  Pass in all magicitem fields. """
        npc=NPC(self.redis)
        magicitem = MagicItem(self.redis, { 'npc':npc })
        self.assertEqual('Muffled Leather Armor Of Shock', str(magicitem))

    def test_magicitem_static_curse(self):
        """  Pass in all magicitem fields. """
        curse=Curse(self.redis, {'text':'Buzzkill Curse'})
        magicitem = MagicItem(self.redis, { 'curse':curse })
        self.assertEqual('Muffled Leather Armor Of Shock', str(magicitem))
        self.assertEqual('Buzzkill Curse', str(magicitem.curse))

    def test_magicitem_rolled_curse(self):
        """  Pass in all magicitem fields. """
        magicitem = MagicItem(self.redis, { 'curse_chance':1090 })
        self.assertEqual('Muffled Leather Armor Of Shock', str(magicitem))
        self.assertIn('The Bezerker Curse', str(magicitem.curse))


    def test_magicitem_static_text(self):
        """  Pass in all magicitem fields. """
        magicitem = MagicItem(self.redis, {
            'text': 'Tacos Tacos Tacos',
            })
        self.assertEqual('Tacos Tacos Tacos', magicitem.text)

    def test_magicitem_static_potion(self):
        """  Pass in all magicitem fields. """
        self.redis.lpush('magicitem_kind', 'potion')

        magicitem = MagicItem(self.redis, { 'kind':'potion'})
        self.assertEqual('Powerful Accuracy Boost Potion', str(magicitem))


    def test_magicitem_static_scroll(self):
        """  Pass in all magicitem fields. """
        self.redis.lpush('magicitem_kind', 'scroll')

        magicitem = MagicItem(self.redis, { 'kind':'scroll'})
        self.assertEqual('Powerful Ad Nauseum Scroll', str(magicitem))


    def test_magicitem_static_weapon(self):
        """  Pass in all magicitem fields. """
        self.redis.lpush('magicitem_kind', 'weapon')

        magicitem = MagicItem(self.redis, { 'kind':'weapon'})
        self.assertEqual('Sharp Sword Of The Bull', str(magicitem))

