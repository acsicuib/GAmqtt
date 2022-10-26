#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  4 13:56:31 2022

@author: carlos
"""

numberOfNodes = 15
numberOfServices = 4

objectivesFunctions = list()
objectivesFunctions.append(('obj1','self.meanNumberOfInstances()'))
objectivesFunctions.append(('obj2','self.meanEdgeDistance()'))