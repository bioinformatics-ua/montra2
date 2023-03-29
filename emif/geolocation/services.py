# -*- coding: utf-8 -*-
# Copyright (C) 2014 Universidade de Aveiro, DETI/IEETA, Bioinformatics Group - http://bioinformatics.ua.pt/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#
# Adds a city to the internal database of cities with his location (if it doesnt exist yet)
# receives as input a qlist

from emif.models import City
from geopy import geocoders

from questionnaire import Fingerprint_Index

def add_city(qlist_general):
    # iterate until we find the location field (City or location fields)
    for qs_aux, qlist in qlist_general:
        for question, qdict in qlist:

            if question.slug == 'location':
                #import pdb; pdb.set_trace()
                #print "--[services]",Fingerprint_Index['location'](qdict['value'])
                city_name = Fingerprint_Index['location'](qdict['value'])
                
                # check if the city is on the db
                try:
                    city = City.objects.get(name=city_name)

                    #print "-- City already is on the db."
                # if dont have this city yet on the db
                except City.DoesNotExist:
                    #print "City "+qdict['value'].lower()+" is not on the db yet"

                    #obtain lat and longitude
                    city = retrieve_geolocation(city_name)

                    if city != None:   
                        city.save()
                        return True

                    else:
                        print "[services:add_city] Error: retrieving geolocation "
                        return False


    #print "-- No city found at all on questionary"
    return False

def retrieve_geolocation(city_name):
    try:
        #g = geocoders.GeoNames(username='bastiao')     
        g = geocoders.GoogleV3()
        #import pdb; pdb.set_trace()

        if g == None:
            return None

        place, (lat, lng) = g.geocode(city_name)
        print place

        # add to the db
        city = City(name=city_name, lat=lat, long=lng)
        return city

    except:
        return None