"""Patch ReSDK Resolwe objects with import methods."""

from resdk.data_upload.annotate_samples import annotate_samples, export_annotation
from resdk.data_upload.multiplexed import upload_demulti
from resdk.data_upload.reads import upload_reads
from resdk.resources import Collection

Collection.annotate = annotate_samples
Collection.export_annotation = export_annotation
Collection.upload_reads = upload_reads
Collection.upload_demulti = upload_demulti
