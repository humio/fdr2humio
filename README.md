# fdr2humio
Falcon Data Replica(ted) data to Humio

```usage: fdr2humio.py [-h] [--aws-access-id AWS_ACCESS_ID] [--aws-access-secret AWS_ACCESS_SECRET] [--humio-batch HUMIO_BATCH] [--debug] [--tmpdir TMPDIR] bucket queue_url humio-host humio-token

This script is used to collect Falcon logs from S3, and send them to a Humio instance.

positional arguments:
  bucket                The S3 bucket from which to export. E.g "demo.humio.xyz"
  queue_url             The SQS queue URL for notifiying new files
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