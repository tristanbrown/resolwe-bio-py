"""Annotate samples in a collection."""

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
from collections import OrderedDict

from resdk.data_upload.samplesheet import FileExporter, FileImporter

__all__ = ('annotate_samples', 'export_annotation')

logger = logging.getLogger(__name__)


def annotate_samples(collection, samplesheet_source, schema='sample'):
    """Batch-annotate the samples in a collection.

    This method applies annotations to the samples in a collection based on a
    sample annotation spreadsheet. The entries in the spreadsheet and the
    samples in the collection are matched by sample name, and validated for
    upload.

    :param str samplesheet_source: path to a local sample annotation
        spreadsheet, or name of one in the collection, or an existing
        FileImporter object created from an upload
    :param str schema: slug of the descriptor schema to use
    """
    # Extract the information from a sample annotation spreadsheet
    samplesheet = FileImporter(samplesheet_source)
    valid_entries = samplesheet.sample_list
    err_names = samplesheet.invalid_samples

    # TODO: Try to pull the samplesheet as a data object from the collection
    #       once it is possible to upload samplesheets
    # else:
    #     sheet = collection.data.get(name=samplesheet_source,
    #                                 type='data:annotation')
    #     sheet.download()
    #     samplesheet = FileImporter(sheet.files()[0])
    #     err_names = set()

    # Match annotation entries to collection samples
    coll_samples = OrderedDict(
        (name, collection.samples.filter(name=name)) for name in valid_entries
    )

    # Partition out the samples missing or duplicated in the collection
    ready_samples = OrderedDict(
        (name, samples) for name, samples in coll_samples.items() if len(samples) == 1
    )
    missing_names = {name for name, samples in coll_samples.items() if not samples}
    dupl_names = {name for name, samples in coll_samples.items() if len(samples) > 1}

    err_missing = {
        name for name in err_names if not collection.samples.filter(name=name)
    }
    if '' in err_names:  # TODO: Remove this when empty queries are fixed.
        err_missing.add('')
    missing_names.update(err_missing)

    if missing_names:
        logger.error(
            "\nThe following samples are missing from the collection:"
            " %s. \nPlease check the names.",
            ', '.join(missing_names)
        )
    if dupl_names:
        logger.error(
            "Multiple samples are queried by the name '%s'. Annotation "
            "will not be applied.",
            "', '".join(dupl_names)
        )

    # Apply each annotation to a sample in the collection
    logger.info("\nAnnotating Samples...\n")
    for name, samples in ready_samples.items():
        _apply_annotation(valid_entries[name], samples[0], schema)

    # Report annotation successes.
    sample_count = len(ready_samples)
    logger.info("\nAnnotated %s samples.\n", sample_count)


def export_annotation(collection=None, path=None):
    """Download a sample annotation spreadsheet based on the collection.

    Populate this template with sample annotation data, and re-import it using
    ``Collection.annotate``.

    :param str path: path to save the annotation spreadsheet template
    """
    if collection:
        samples = collection.samples
        if path:
            filepath = path
        else:
            filepath = "{}.xlsm".format(collection.slug)
        logger.info(
            "\nExporting sample annotation template for collection '%s'...\n",
            collection.name)
    else:
        samples = []
        filepath = 'template.xlsm'
        logger.info("Exporting empty sample annotation template.")
    samplesheet = FileExporter(samples, filepath)
    samplesheet.export_template()
    logger.info("\nSample annotation template exported to %s.\n", filepath)


def _apply_annotation(entry, sample, schema):
    """Apply sample and reads annotations."""
    # Apply the sample annotation
    sample.descriptor_schema = schema
    sample.descriptor = entry.sample_annotation
    if entry.community_tag:
        sample.tags.append(entry.community_tag)
    sample.save()
    sample.confirm_is_annotated()

    # Apply the reads descriptor to all of the reads associated with
    # the sample
    for reads in sample.data.filter(type='data:reads'):
        reads.descriptor_schema = 'reads'
        reads.descriptor = entry.reads_annotation
        reads.save()
