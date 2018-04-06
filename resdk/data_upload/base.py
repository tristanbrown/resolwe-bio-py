"""Upload base."""
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import os

from resdk.data_upload.samplesheet import FileImporter

__all__ = ('upload_and_annotate',)

logger = logging.getLogger(__name__)


def upload_and_annotate(collection, samplesheet_path, process):
    """Upload data files to the Resolwe server, and annotate.

    The data files and sample sheet (.tsv or .xls*) should be in the
    same directory.

    :param collection: collection to contain the uploaded reads
    :param samplesheet_path: filepath of the sample annotation spreadsheet
    :param process: data upload function to use (returns failed sample names)
    """
    # Read and validate the annotation template
    basedir = os.path.dirname(os.path.abspath(samplesheet_path))
    logger.debug(
        "\nChecking the sample annotation spreadsheet at:\n%s",
        samplesheet_path
    )
    samplesheet = FileImporter(samplesheet_path)
    err_names = samplesheet.invalid_names

    # Run the upload process
    failed_uploads = process(
        sample_dict=samplesheet.valid_samples,
        basedir=basedir,
        collection=collection,
        pre_invalid=err_names
    )

    # Report failures
    logger.error(
        "The following samples could not be uploaded: %s.", ', '.join(failed_uploads)
    )

    # Annotate the samples
    collection.annotate(samplesheet)
    collection.update()
