"""Sample utils."""
from __future__ import absolute_import, division, print_function, unicode_literals

from resdk.resources.utils import get_data_id


def abbreviate_organism(name):
    """Return abbrevation of organisms used in sample descriptor."""
    mapping = {
        'homo sapiens': 'hs',
        'mus musculus': 'mm',
        'dictyostelium discoideum': 'dd',
    }
    return mapping[name.lower()]


class SampleUtilsMixin(object):
    """Mixin with utility functions for `~resdk.resources.sample.Sample` resource.

    This mixin includes handy methods for common tasks like getting
    data object of specific type from sample (or list of them, based on
    common usecase) and running analysis on the objects in the sample.

    """

    def get_bam(self):
        """Return ``bam`` object on the sample."""
        return self.data.get(type='data:alignment:bam:')

    def get_macs(self):
        """Return list of ``bed`` objects on the sample."""
        return self.data.filter(type='data:chipseq:macs14:')

    def get_cuffquant(self):
        """Return ``cuffquant`` object on the sample."""
        return self.data.get(type='data:cufflinks:cuffquant:')

    def run_macs(self, use_background=True, background_slug='', p_value=None):
        """Run ``MACS 1.4`` process on the sample.

        This method runs `MACS 1.4`_ process with ``p-value`` specified
        in arguments and ``bam`` file from the sample.

        If ``use_background`` argument is set to ``True``, ``bam`` file
        from background sample is passed to the process as the control.
        Mappable genome size is taken from the sample annotation.

        .. _MACS 1.4:
            http://resolwe-bio.readthedocs.io/en/latest/catalog-definitions.html#process-macs14

        :param bool use_background: if set to ``True``, background
            sample will be used in the process
        :param float p_value: p-value used in the process

        """
        inputs = {
            'treatment': self.get_bam().id,
            'gsize': abbreviate_organism(self.descriptor['geo']['organism']),
        }

        if p_value is not None:
            inputs['pvalue'] = p_value

        if use_background:
            background = self.get_background(background_slug, fail_silently=True)

            if background:
                inputs['control'] = background.get_bam().id
            else:
                self.logger.info('Macs will run without a control sample.')

        macs = self.resolwe.get_or_run(slug='macs14', input=inputs)
        self.add_data(macs)

        return macs

    def run_rose2(self, use_background=True, background_slug='', genome='HG19', tss=None,
                  stitch=None, beds=None):
        """Run ``ROSE 2`` process on the sample.

        This method runs `ROSE2`_ process with ``tss_exclusion`` and
        ``stitch`` parameters specified in arguments.

        Separate process is run for each bed file on the sample. To
        run process only on subset of those files, list them in ``beds``
        argument (if only one object is given, it will be auto-wrapped
        in list, if it is not already).

        If ``use_background`` argument is set to ``True``, bam file
        from background sample is passed to the process as the control.

        .. _ROSE2:
            http://resolwe-bio.readthedocs.io/en/latest/catalog-definitions.html#process-rose2

        :param bool use_background: if set to ``True``, background
            sample will be used in the process
        :param str genome: Genome used in the process (options are HG18,
            HG19, MM9 and MM10), default is ``HG19``
        :param int tss: TSS exclusion used in process
        :param int stitch: Stitch used in process
        :param list beds: subset of bed files to run process on, if
            empty processes for all bed files will be run

        """
        valid_genomes = ['HG18', 'HG19', 'MM9', 'MM10']
        if genome not in valid_genomes:
            raise KeyError('Invalid `genome`, please use one of the following: '
                           '{}'. format(', '.join(valid_genomes)))

        inputs = {
            'genome': genome,
            'rankby': self.get_bam().id,
        }

        if tss is not None:
            inputs['tss'] = tss

        if stitch is not None:
            inputs['stitch'] = stitch

        if use_background:
            background = self.get_background(background_slug, fail_silently=True)

            if background:
                inputs['control'] = background.get_bam().id
            else:
                self.logger.info('Rose-2 will run without a control sample.')

        bed_list = self.get_macs()
        if beds is not None:
            # Convert objects to the list of their ids
            if isinstance(beds, list):
                bed_filter = [get_data_id(bed) for bed in beds]
            else:
                bed_filter = [get_data_id(beds)]

            bed_list = bed_list.filter(id__in=bed_filter)

        results = []
        for bed in bed_list:
            inputs['input'] = bed.id

            rose = self.resolwe.get_or_run(slug='rose2', input=inputs)
            self.add_data(rose)
            results.append(rose)

        return results

    def run_cuffquant(self, gff):
        """Run Cuffquant_ for selected cuffquats.

        This method runs `Cuffquant`_ process with ``annotation``
        specified in arguments.

         .. _Cuffquant:
            http://resolwe-bio.readthedocs.io/en/latest/catalog-definitions.html#process-cuffquant

        :param gff: id of annotation file is given
        :type gff: int or `~resdk.resources.data.Data`

        """
        inputs = {
            'alignment': self.get_bam().id,
            'gff': get_data_id(gff),
        }

        cuffquant = self.resolwe.get_or_run(slug='cuffquant', input=inputs)

        return cuffquant
