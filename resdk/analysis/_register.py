"""Patch ReSDK resources with analysis methods."""
from __future__ import absolute_import, division, print_function, unicode_literals

from resdk.resources import Collection, Relation, Sample

from resdk.analysis.chip_seq import macs, rose2
from resdk.analysis.expressions import cuffnorm, cuffquant
from resdk.analysis.plots import bamplot


Collection.run_bamplot = bamplot
Collection.run_cuffnorm = cuffnorm
Collection.run_cuffquant = cuffquant
Collection.run_macs = macs
Collection.run_rose2 = rose2

Relation.run_bamplot = bamplot
Relation.run_cuffnorm = cuffnorm
Relation.run_cuffquant = cuffquant
Relation.run_macs = macs
Relation.run_rose2 = rose2

Sample.run_cuffquant = cuffquant
Sample.run_macs = macs
Sample.run_rose2 = rose2
