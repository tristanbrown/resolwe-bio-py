"""Functional tests for ReSDK."""
import os
import unittest

from resdk import Resolwe
from resdk.analysis.chip_seq import macs

URL = os.environ.get('SERVER_URL', 'http://localhost:8000')
USER_USERNAME = 'user'
USER_PASSWORD = 'user'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

FILES_PATH = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..',
        'files'
    )
)


class BaseResdkFunctionalTest(unittest.TestCase):
    """Base class for functional tests in ReSDK.

    It generates 2 Resolwe classes for connection to server. One with
    admin's credentials (``self.res``) and one with normal user's
    credentials (``self.user_res``).

    It also includes utility functions to generate data objects of basic
    types with dummy input files.

    """

    def setUp(self):
        self.res = Resolwe(ADMIN_USERNAME, ADMIN_PASSWORD, URL)
        self.user_res = Resolwe(USER_USERNAME, USER_PASSWORD, URL)

    def get_genome(self, collection=None, species='Homo sapiens',
                   build='hg38'):
        """Return genome data object.

        :param collection: If defined, data object will be add to given
            collections.
        :type collection: None, int or `~resdk.resources.Collection`
        """
        genome_path = os.path.join(FILES_PATH, 'dummy_genome.fasta')
        collections = {'collections': [collection]} if collection else {}

        return self.res.run(
            'upload-genome',
            input={
                'src': genome_path,
                'species': species,
                'build': build,
            },
            **collections
        )

    def get_gtf(self, collection=None, species='Homo sapiens',
                build='hg38'):
        """Return gff3 data object.

        :param collection: If defined, data object will be add to given
            collections.
        :type collection: None, int or `~resdk.resources.Collection`
        """
        gtf_path = os.path.join(FILES_PATH, 'dummy_gtf.gtf')
        collections = {'collections': [collection]} if collection else {}

        return self.res.run(
            'upload-gtf',
            input={
                'src': gtf_path,
                'source': 'NCBI',
                'species': species,
                'build': build,
            },
            **collections
        )

    def get_reads(self, count=1, collection=None):
        """Return reads data objects.

        :param int count: number of objects to return
        :param collection: If defined, data object will be add to given
            collections.
        :type collection: None, int or `~resdk.resources.Collection`
        """
        reads_path = os.path.join(FILES_PATH, 'dummy_reads.fastq')
        collections = {'collections': [collection]} if collection else {}

        reads = []
        for _ in range(count):
            read = self.res.run(
                'upload-fastq-single',
                input={'src': reads_path},
                **collections
            )
            reads.append(read)

            # TODO: Remove this when samples are automatically added to
            #       the collection in resolwe
            if collection:
                collection.add_samples(read.sample)

        return reads

    def get_multiplexed(self, count=1, collection=None):
        """ Return demultiplexed reads data objects.

        :param int count: number of objects to return
        :param collection: If defined, data object will be add to given
            collections.
        :type collection: None, int or `~resdk.resources.Collection`
        """
        collections = {'collections': [collection]} if collection else {}
        inputs = {
            'reads': 'pool24.read1.small.qseq.bz2',
            'reads2': 'pool24.read3.small.qseq.bz2',
            'barcodes': 'pool24.read2.small.qseq.bz2',
            'annotation': 'pool24.tsv',
        }
        inputs = {k: os.path.join(FILES_PATH, v) for k, v in inputs.items()}

        multi = [
            self.res.run('upload-multiplexed-paired', inputs, **collections)
            for _ in range(count)
        ]
        return multi

    def get_bams(self, count=1, collection=None, species='Homo sapiens',
                 build='hg38'):
        """Return bam data objects.

        :param int count: number of objects to return
        :param collection: If defined, data object will be add to given
            collections.
        :type collection: None, int or `~resdk.resources.Collection`
        """
        bam_path = os.path.join(FILES_PATH, 'dummy_bam.bam')
        collections = {'collections': [collection]} if collection else {}

        bams = []
        for _ in range(count):
            bam = self.res.run(
                'upload-bam',
                input={
                    'src': bam_path,
                    'species': species,
                    'build': build,
                },
                **collections
            )

            bams.append(bam)

            # TODO: Remove this when samples are automatically added to
            #       the collection in resolwe
            if collection:
                collection.add_samples(bam.sample)

        return bams

    def get_macs(self, count=1, collection=None):
        """Return macs data objects.

        :param int count: number of objects to return
        :param collection: If defined, data object will be add to given
            collections.
        :type collection: None, int or `~resdk.resources.Collection`
        """
        bams = self.get_bams(count, collection)

        return macs([bam.sample for bam in bams], use_background=False)

    def get_cuffquants(self, count=1, collection=None, species='Homo sapiens',
                       build='hg38'):
        """Return cuffquant data objects.

        :param int count: number of objects to return
        :param collection: If defined, data object will be add to given
            collections.
        :type collection: None, int or `~resdk.resources.Collection`
        """
        cuffquant_path = os.path.join(FILES_PATH, 'dummy_cuffquant.cxb')
        collections = {'collections': [collection]} if collection else {}

        cuffquants = []
        for _ in range(count):
            cuffquant = self.res.run(
                'upload-cxb',
                input={
                    'src': cuffquant_path,
                    'source': 'NCBI',
                    'species': species,
                    'build': build,
                },
                **collections
            )

            cuffquants.append(cuffquant)

            # TODO: Remove this when samples are automatically added to
            #       the collection in resolwe
            if collection:
                collection.add_samples(cuffquant.sample)

        return cuffquants

    def get_expression(self, count=1, collection=None, species='Homo sapiens',
                       build='hg38'):
        """Return expression data objects.

        :param int count: number of objects to return
        :param colection: If defined, data object will be add to given
            collections.
        :type collection: None, int or `~resdk.resources.Collection`
        """
        expression_path = os.path.join(FILES_PATH, 'dummy_expression.tab')
        collections = {'collections': [collection]} if collection else {}

        expressions = []
        for _ in range(count):
            expression = self.res.run(
                'upload-expression',
                input={
                    'exp': expression_path,
                    'exp_name': 'test_expression',
                    'source': 'NCBI',
                    'species': species,
                    'build': build,
                },
                **collections
            )

            expressions.append(expression)

        return expressions
