#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" The City class is one of the more complex modules due to its reliance
    on many other modules as well as a good deal of statistical logic. """
import json
import random
import logging
from megacosm.generators.generator import Generator
from megacosm.generators.business import Business
from megacosm.generators.name import Name
from megacosm.generators.npc import NPC

from megacosm.generators import leader
from megacosm.generators import region


class City(Generator):
    """ Generate a full city population."""
    def __init__(self, redis, features={}):
        Generator.__init__(self, redis, features)
        self.logger = logging.getLogger(__name__)
        if not hasattr(self, 'region'):
            # print "noregion!!!"
            self.region = region.Region(self.redis)

        self.gatheringplace = Business(self.redis, {'kind': 'bus_' + self.gatheringplace})
        if not hasattr(self, 'leader'):
            self.leader = leader.Leader(self.redis, {"location":self})
            #self.leader = Leader(self.redis)

        if not hasattr(self, 'name'):
            self.name = Name(self.redis, 'city')

        self.citizen = NPC(self.redis)

        self.calculate_population()
        self.calculate_racial_breakdown()
        self.select_subraces()

    def calculate_population(self):
        """ Estimate the population, then calculate the density."""
        self.population_estimate = random.randint(int(self.size['minpop']), int(self.size['maxpop']))
        self.population_density = random.randint(int(self.size['min_density']), int(self.size['max_density']))

    def calculate_racial_breakdown(self):
        """ Split the population by race."""
        total = random.randint(1, 10)  # % reserved for "other"
        racelist = {'other': total}
        races = self.redis.lrange('npc_race', 0, -1)
        random.shuffle(races)
        for race in races:
            print "total at %s" % total
            percentage = random.randint(10, 100)
            print "%s gets %s" % (race, percentage)
            racelist[race] = percentage
            if total + percentage < 100:
                total += percentage
            else:
                racelist[race] = 100 - total
                total = 100
                break

        if total < 100:
            # Check to make sure we didn't run out of races before hitting 100
            total_without_other = total - racelist['other']
            racelist['other'] = 100 - total_without_other
            total = 100

        self.races = racelist

    def calculate_which_subraces(self, parentrace, parentpercentage):
        """ Determine which subraces will be shown. """
        total = 0
        subracelist = {}

        subraces = self.redis.lrange(parentrace + '_subrace', 0, -1)
        random.shuffle(subraces)
        for subrace in subraces:
            print "for %s in %s" %(subrace, subraces)
            print "parentpercentage: %s" % (parentpercentage)
            subracepercentage = random.randint(1, parentpercentage)
            if total + subracepercentage < parentpercentage:
                total += subracepercentage
                subracelist[subrace] = subracepercentage
            else:
                subracelist[subrace] = parentpercentage - total
                total = parentpercentage
                break
        if total < parentpercentage:
            # Check to make sure we didn't run out of races before hitting parentpercentage
            subrace = subracelist.keys()[0]
            total_without_other = total - subracelist[subrace]
            subracelist[subrace] = parentpercentage - total_without_other
            total = parentpercentage
        return subracelist

    def select_subraces(self):
        """ Determine if each race will show subraces """
        final_racelist = {}
        self.racequalifiers = {'mostly': []}
        for race in sorted(self.races):
            #print "has_subraces: %s for %s, want subraces?" %(self.has_subraces(race), race)
            #if self.has_subraces(race):
            #    print self.want_subraces(race)
            if self.has_subraces(race) and self.want_subraces(race):
                print "race: %s, races: %s" %(race, self.races[race])
                if isinstance(self.races[race], int):
                    subraces = self.calculate_which_subraces(race, self.races[race])
                else:
                    subraces = self.races[race]
                final_racelist[race] = subraces
            else:
                final_racelist[race] = self.races[race]
        self.races = final_racelist

    def has_subraces(self, race):
        """ Check to see if a race has subraces."""
        return bool(self.redis.llen(race + '_subrace'))

    def want_subraces(self, race):
        """ Determine if we should mention subraces for a given race."""
        roll = random.randint(0, 100)
        #print "want_race %s with %s chance and roll %s" %(race, int(self.redis.get(race + '_subrace_chance')), roll)
        return bool(roll < int(self.redis.get(race + '_subrace_chance')))

    def get_race_breakdown(self):
        """ return a simple dict of proper race names and percentages """
        results = {}
        for race in self.races:
            if isinstance(self.races[race], dict):
                # Time to handle the subraces and squeeze them into the results
                for subrace in self.races[race]:
                    subracejson = json.loads(self.redis.hget(race + '_subrace_description', subrace))
                    results[subracejson['subrace']] = self.races[race][subrace]
            elif race == 'other':
                results['Other'] = self.races[race]
            else:
                # FIXME elf_details, etc should be elf_description in data files
                racejson = json.loads(self.redis.get(race + '_details'))
                results[racejson['name']] = self.races[race]
        return results

    def get_scale(self):
        """ Return the proper scale for a city, minus unneeded values."""
        scales = []
        for scale in self.redis.zrange('city_size', 0, -1):
            #print scale
            scalejson = json.loads(scale)
            del scalejson['maxpop']
            del scalejson['minpop']
            del scalejson['min_density']
            del scalejson['max_density']
            scales.append(scalejson)
        return scales

    def __str__(self):
        return '%s' % (self.name.fullname)
