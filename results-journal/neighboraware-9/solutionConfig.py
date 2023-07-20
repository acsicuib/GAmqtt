#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  4 13:56:31 2022

@author: carlos
"""

numberOfNodes = 100
numberOfServices = 4
numberOfServices = 10

objectivesFunctions = list()
objectivesFunctions.append(('Number of instances','self.meanNumberOfInstances()'))
objectivesFunctions.append(('Mean distance to clients','self.meanEdgeDistance()'))