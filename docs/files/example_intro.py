from example_index import *

# Get a Collection object by id
res.collection.get(75)

# Get a Sample by slug
res.sample.get('human-example-chr22') # NO LONGER EXISTS
# MAYBE SWITCH TO 'mouse-example-chr19'

# Filter processes by the contributer
res.process.filter(contributor=1)

# Filter data by status
res.data.filter(status='OK')

# Filter data by several fields
res.data.filter(status='OK', process_name='Bowtie 1.0.0', ordering='created', limit=3)

# Get a sample by slug
sample = res.sample.get('human-example-chr22') # NO LONGER EXISTS

# Access the sample name
sample.name

# Access the creation date
sample.created

# Get the Bowtie process
bowtie_process = res.process.get('alignment-bowtie2')

# Access the process' permissions
bowtie_process.permissions

# Get data by slug
data = res.data.get('human-example-chr22-bam') # NO LONGER EXISTS

# Print a list of files
print(data.files())

# Filter the list of files by file name
print(data.files(file_name='human_example_chr22.bam')) # NO LONGER EXISTS

# Filter the list of files by field name
print(data.files(field_name='output.bam'))

# Get sample by slug
sample = res.sample.get('human-example-chr22') # NO LONGER EXISTS

# Download the NGS reads file
sample.download(file_name='human_example_chr22.bam', download_dir='/path/to/target/dir/') # NO LONGER EXISTS