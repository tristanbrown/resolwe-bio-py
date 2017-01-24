"""Resolwe utils."""
from __future__ import absolute_import, division, print_function, unicode_literals

from resdk.resources.utils import get_data_id


class ResolweUtilsMixin(object):
    """Mixin with utility functions for `~resdk.resolwe.Resolwe` resource."""

    def run_bamplot(self, bam, genome, input_gff=None, input_region=None, stretch_input=None,
                    color=None, sense=None, extension=None, rpm=None, yscale=None, names=None,
                    plot=None, title=None, scale=None, bed=None, multi_page=None):
        """Run ``bamplot`` on the list of bam files.

        This method runs `bamplot`_ with bams, genome and gff or region
        specified in arguments. If only one bam file is given, it will
        be auto-wrapped in list, if it is not already.

        .. _bamplot:
            http://resolwe-bio.readthedocs.io/en/latest/catalog-definitions.html#process-bamplot

        :param list bam: subset of bam files to run process on
        :param str genome: Genome used in the process (options are HG18,
            HG19, MM9 and MM10)
        :param input_gff: id of annotation file is given
        :type input_gff: int or `~resdk.resources.data.Data`
        :param str input_region: enter a genomic region
        :param int stretch_input: stretch the input regions to a minimum
            length
        :param str color: enter a colon separated list of colors
        :param str sense: map to forward, reverse or'both strand,
            default maps to ``both``
        :param int extension: extends reads by n bp, dfault value is
             200bp
        :param bool rpm: normalizes density to reads per million (rpm),
            default is ``False``
        :param str yscale: choose either relative or uniform y axis
             scaling, default is ``relative scaling``
        :param str names: a comma separated list of names for your bams
        :param str plot: choose all lines on a single plot or multiple
            plots
        :param str title: title for the output plot(s), default will be
            the coordinate region
        :param str scale: a comma separated list of multiplicative
            scaling factors for your bams, default is ``None``
        :param list beds: subset of bed files to run process on, if
            empty processes for all bed files will be run
        :param bool multi_page: if flagged will create a new pdf for
            each region

        """
        if not input_gff and not input_region:
            raise KeyError('Please specify `input_gff` or `input_region.')
        if input_gff and input_region:
            raise KeyError('Please specify `input_gff` or `input_region.')

        valid_genomes = ['HG18', 'HG19', 'MM8', 'MM9', 'MM10']
        if genome not in valid_genomes:
            raise KeyError('Invalid `genome`, please use one of the following: '
                           '{}'. format(', '.join(valid_genomes)))

        if isinstance(bam, list):
            bam = [get_data_id(bam_obj) for bam_obj in bam]
        else:
            bam = [get_data_id(bam)]

        inputs = {
            'genome': genome,
            'bam': bam,
        }

        if color is not None:
            inputs['color'] = color

        if sense is not None:
            inputs['scale'] = scale

        if extension is not None:
            inputs['extension'] = extension

        if rpm is not None:
            inputs['rpm'] = rpm

        if yscale is not None:
            inputs['yscale'] = yscale

        if names is not None:
            inputs['names'] = names

        if plot is not None:
            inputs['plot'] = plot

        if title is not None:
            inputs['title'] = title

        if scale is not None:
            inputs['scale'] = scale

        if multi_page is not None:
            inputs['multi_page'] = multi_page

        if input_gff is not None:
            inputs['input_gff'] = get_data_id(input_gff)

        if input_region is not None:
            inputs['input_region'] = input_region

        if bed is not None:
            if isinstance(bed, list):
                inputs['bed'] = [get_data_id(bed_obj) for bed_obj in bed]
            else:
                inputs['bed'] = [get_data_id(bed)]

        bamplot = self.get_or_run(slug='bamplot', input=inputs)

        return bamplot

    def run_cuffnorm(self, cuffquant, replicates, annotation, labels, use_ercc=None, threads=None):
        """Run Cuffnorm_ for selected cuffquats.

         This method runs `Cuffnorm`_ process with ``cuffquant``
         ``replicates``, ``annotation``, ``labels``, ``useERCC`` and
        ``threads`` parameters specified in arguments.

        .. _Cuffnorm:
            http://resolwe-bio.readthedocs.io/en/latest/catalog-definitions.html#process-upload-expression-cuffnorm

        :param list cuffquant: subset of cuffquant files to run process
            on
        :param list replicates: list where sample groups and/or sample
            replicates are defined
        :param annotation: id of annotation file is given
        :type annotation: int or `~resdk.resources.data.Data`
        :param list labels: labels for each sample group are defined
        :param bool useERCC: use ERRCC spike-in controls for
            normalization
        :param int threads: use this many threads to align reads, the
            default is ``1``

        """
        cuffquant = [get_data_id(cuffquant_obj) for cuffquant_obj in cuffquant]

        inputs = {
            'cuffquant': cuffquant,
            'replicates': replicates,
            'annotation': annotation,
            'labels': labels,
        }

        if use_ercc is not None:
            inputs['useERCC'] = use_ercc

        if threads is not None:
            inputs['threads'] = threads

        cuffnorm = self.get_or_run(slug='cuffnorm', input=inputs)

        return cuffnorm
