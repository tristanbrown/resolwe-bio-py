from resdk import Resolwe
res = Resolwe('admin', 'admin', 'https://torta.bcm.genialis.com')

# Recomended: start logging
resdk.start_logging()

sample = res.sample.get(1)
sample.download(type='bam')

samples = res.sample.filter(descriptor__organism="Homo sapiens")
for sample in samples:
    sample.download(type='bam')

sample = res.sample.get(1)
for data_id in sample.data:
    data = res.data.get(data_id)
    print data.process_name

rose2_list = res.data.filter(type='data:chipseq:rose2:')
rose2 = rose2_list[0]
rose2.download(name='20150531-u266-A-H3K27Ac-ML1949_S2_R1_mapped_peaks_Plot_panel.png')

genome = res.data.get('hg19')
genome_id = genome.id
reads_id = sample.data[0]
aligned = res.run('alignment-bowtie-2-2-3_trim', input={
                      'genome': genome_id,
                      'reads': reads_id,
                      'reporting': {'rep_mode': 'k', 'k_reports': 1}
                  })
aligned.status

aligned.update()
aligned.status

###################

collection_2 = res.collection.get(2)
# collection_2 is a resdk Collection object with id=2

sample_12 = res.sample.get('wt-rep1-10w')
# sample12 is a resdk Sample object with slug='wt-rep1-10w'

processes_by_user1 = res.process.filter(contributor=1)
# processes_by_user1 is a list of Process objects created by contributor with id=1.

data_ok = res.data.filter(status="OK")
# data_ok is a list of Data objects that have status="OK".

data_list = res.data.filter(status="OK", contributor=2, process_name="Aligner (Bowtie 1.0.0)", ordering='created', limit=3)

sample2 = res.sample.get(2)
sample_name = sample.name

data3 = res.data.get(3)
creation_time = data.created

bowtie_process = res.data.get("alignment-bowtie-2-2-3_trim")
public_permissions = bowtie_process.permissions["public"]

###################

upload_processes = res.process.filter(category='upload')

reads = res.run(slug='import-upload-reads-fastq',
                input={'src': '/path/to/file/reads.fastq'})

assembled_reads = res.run(slug='assembler-abyss',
                          input={'se': reads.id})

abyss_inputs = res.process.get('assembler-abyss').input_schema

res.process.get('assembler-abyss').print_inputs()

desc_sch = res.api.descriptorschema.get(slug="reads")[0]
desc = descriptor = {
    'barcode': 'TGACCA',
    'barcode_removed': True,
    'instrument_type': 'NextSeq 500',
    'seq_date': '2015-12-31'}

inputs = {'se': reads.id,
          'options': {
              'name': 'blah_blah',
              'k': 20,
              'n': 30}}

assembled_reads = res.run(slug='assembler-abyss',
                          input=inputs,
                          descriptor=desc,
                          descriptor_schema=desc_sch,
                          collections=[1, 2],
                          data_name="my_favourite_name")


result = res.run("some_bad_inputs")
# do not forget to update the data object to get the most recent info:
result.update()
print(result.stdout())

result.process_info
result.process_warning
result.process_error
