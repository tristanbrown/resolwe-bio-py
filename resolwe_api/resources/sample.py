"""Sample"""
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import six

from .base import DOWNLOAD_TYPES

class Sample(object):
    """
    Resolwe sample annotation.
    """

    endpoint = 'sample'

    def __init__(self, ann_data, resolwe):
        """
        Resolwe sample annotation.

        :param ann_data: Sample annotation - (field, value) pairs
        :type ann_data: dictionary
        :param resolwe: Resolwe instance
        :type resolwe: Resolwe

        :rtype: None
        """

        for field in ann_data:
            setattr(self, field, ann_data[field])

        self.resolwe = resolwe
        self.id = getattr(self, 'id', None)
        self.name = getattr(self, 'name', None)

    def __str__(self):
        return self.name or 'n/a'

    def __repr__(self):
        return "{}: {} - {}".format(endpoint.capitalize(), self.id, self.name)

    def files(self, verbose=False):
        """
        Get a list of all files contained in sample.
        """
        file_list = []
        for data_id in self.data:
            file_list += self.resolwe.data.get(data_id)._get_download_list(verbose=verbose)
        return file_list

    def download(self, name=None, typ=None, download_dir=None, force=False):
        """
        Download files in sample that match name/typ.

        :param name: name of file
        :type name: string
        :param typ: (process_type, output_field) or abbreviation for most of such common tuples.
        :type typ: tuple or string
        :param download_dir: download path
        :type download_dir: string
        :param force: if true, download all files regardless of match
        :type force: boolean

        :rtype: None

        Sample usually contains multiple data objects and each data
        object can contain multiple files. Default option is to download
        all of them, but this may not be desired, since some files can be
        rather large. User can provide:

            * name of the desired file (with keyword **name**)
                Only file with corresponding name will be downloaded.
                Example:
                re.sample.get(42).download(name="alignment7.bam")

            or

            * (process_type, output_field) tuple (with keyword **typ**)
                In this case only files from output_field from data object
                with process_type will be downloaded.
                Example:
                re.sample.get(42).download(typ=('data:alignment:bam:', 'output.bam'))

                For most common types of downloads (bam files,
                expression files, etc.) shortcut notation is provided:
                    * 'bam' for BAM files
                    * 'exp' for expression files
                    * 'fastq' for fastq files
                Example:
                re.sample.get(42).download(typ='bam')

        The current working directory is the default download location. With
        download_dir parameter, this can be modified.
        """

        if not download_dir:
            download_dir = os.getcwd()

        # list of all files to download - this list is yet to be
        # filtered by name/typ:
        dfiles = self.files(verbose=True)

        if not (name or typ) or force:
            pass

        elif name:
            dfiles = [d for d in dfiles if d[1] == name]

        elif typ:
            data_type, output_field = None, None
            if isinstance(typ, six.string_types):
                # typ is abbreviation (string)
                data_type, output_field = DOWNLOAD_TYPES[typ]
            elif isinstance(typ, tuple) and len(typ) == 2:
                data_type, output_field = typ
            else:
                raise ValueError('Invalid argument typ.')
            dfiles = [d for d in dfiles if (data_type in d[3] and output_field == d[2])]

        print("Following files will be downloaded to direcotry {}:".format(download_dir))
        for f in dfiles:
            print("* {}".format(f[1]))
            # TODO: add file size in print!

        for data_id, filename, field, _ in dfiles:
            with open(os.path.join(download_dir, filename), 'wb') as f:
                handle = self.resolwe.download([data_id], field)
                for chunk in handle:
                    f.write(chunk)

    def get_dowoad_handle():
        """
        Do not start download, just return handle.
        """
        raise NotImplementedError()
