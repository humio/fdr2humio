# fdr2humio
Falcon Data Replica(ted) to Humio

```
usage: fdr2humio.py [-h] [--aws-access-id AWS_ACCESS_ID] [--aws-access-secret AWS_ACCESS_SECRET] [--humio-batch HUMIO_BATCH] [--debug] [--tmpdir TMPDIR] bucket queue-url humio-host humio-token

This script is used to collect Falcon logs from S3, and send them to a Humio instance.

positional arguments:
  bucket                The S3 bucket from which to export. E.g "demo.humio.xyz"
  queue-url             The SQS queue URL for notifiying new files
  humio-host            The URL to the target Humio instance, including optional port number
  humio-token           Ingest token for this input

optional arguments:
  -h, --help            show this help message and exit
  --aws-access-id AWS_ACCESS_ID
                        The AWS access key ID (not implemented)
  --aws-access-secret AWS_ACCESS_SECRET
                        The AWS access key secret (not implemented)
  --humio-batch HUMIO_BATCH
                        Max events batch size for sending to Humio
  --debug               We do the debug?
  --tmpdir TMPDIR       The temp directory where the work will be done
```

## Building the docker image

You can build this as a docker image using the following commands:

```
git clone <this repo>
cd fdr2humio
docker build --tag YOUR_NAME/fdr2humio:latest .
```

To run the script as a docker container first make a copy of the example config and set your values as required:

```
cp fdr2humio.conf.example fdr2humio.conf
vi fdr2humio.conf
```

Then start the docker container:

```
docker run \
    -d \
    --env-file=fdr2humio.conf \
    --restart=unless-stopped \
    --name=fdr2humio \
    YOUR_NAME/fdr2humio:latest
```

NOTE: Because this script is reading from an SQS queue it is safe to start and run multiple copies of this container in parallel.
