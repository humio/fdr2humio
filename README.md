

# fdr2humio

Falcon Data Replica(ted) to Humio

This project provides a simple way to move your Falcon data from the FDR service into a Humio instance, including shipping the data to Humio's cloud (SaaS) service. This utility should be combined with the crowdstrike/fdr package in the Humio marketplace, at a minimum you will want to use the parser provided in that package.

For more details on Falcon Data Replicator please see the documentation in your Falcon console under Support >  Documentation > Tools and Reference > Falcon Data Replicator.

For more details on Humio Packages and the Marketplace please see: https://docs.humio.com/docs/packages/ 



## How to Use this tool

The fdr2humio tool is available as a python script (fdr2humio.py) or as a docker container (fdr2humio) hosted in GitHub. It is recommended to use the docker container where possible.

The first step for either option is to gather the required inputs for use with fdr2humio.

From the Falcon console go to Support > API Clients and Keys and setup the credentials for Falcon Data Replicator (this is an additional component of Falcon that you need to subscribe to). The inputs for the FDR side of the integration are:

- SQS Queue URL (e.g. `https://sqs.us-west-3.amazonaws.com/1234567890/your-fdr-ident-12345-1234567890`)
- S3 Bucket (e.g. `s3://your-fdr-ident-12345-1234567890/data`)
- AWS Access ID and Key (the key will only be shown to you once during setup)

From Humio you will need the following information:

- The URL of your Humio server (e.g. `https://cloud.humio.com/`)
- The Ingest API token from your repository (e.g. `11111111-2222-aaaa-bbbb-333333333333`)

NOTE: it is recommended, although not required, that the `crowdstrike/fdr` package from the Humio Marketplace is installed in your repository and the `FDR` parser is associated with your ingest token.

NOTE: Because this tool is reading from an SQS queue it is safe to start and run multiple copies of this in parallel.



### Cloud Based Deployments

[AWS Fargate](docs/deploy-in-aws-fargate.md)
[Microsoft Azure](docs/deploy-in-azure.md)



### Example Docker Run

To deploy the container locally you must first pull the image:

`docker pull ghcr.io/humio/fdr2humio:latest`

Make a copy of the `fdr2humio.conf.example` file (available [here](https://raw.githubusercontent.com/humio/fdr2humio/main/fdr2humio.conf.example)):

`cp fdr2humio.conf.example fdr2humio.conf` 

And configure with the variables collected above.

You can now start the docker container using the `fdr2humio.conf` to intialise the container:

```docker run \
docker run \
    -d \
    --env-file=fdr2humio.conf \
    --restart=unless-stopped \
    --name=fdr2humio \
    ghcr.io/humio/fdr2humio:latest
```



### Example Command Line

The `fdr2humio.py` can be run as command line tool as well. The arguments are as described below:

```usage: fdr2humio.py [-h] [--aws-access-id AWS_ACCESS_ID] [--aws-access-secret AWS_ACCESS_SECRET] [--aws-region AWS_REGION] [--debug] [--tmpdir TMPDIR] bucket queue-url humio-host humio-token
usage: fdr2humio.py [-h] [--aws-access-id AWS_ACCESS_ID] [--aws-access-secret AWS_ACCESS_SECRET] [--aws-region AWS_REGION] [--debug] [--tmpdir TMPDIR] bucket queue-url humio-host humio-token

This script is used to collect Falcon logs from S3, and send them to a Humio instance.

positional arguments:
  bucket                The S3 bucket from which to export. E.g "demo.humio.xyz"
  queue-url             The SQS queue URL for notifiying new files
  humio-host            The URL to the target Humio instance, including optional port number
  humio-token           Ingest token for this input

optional arguments:
  -h, --help            show this help message and exit
  --aws-access-id AWS_ACCESS_ID
                        The AWS access key ID
  --aws-access-secret AWS_ACCESS_SECRET
                        The AWS access key secret
  --aws-region AWS_REGION
                        The AWS region (should match SQS queue region)
  --debug               We do the debug?
  --tmpdir TMPDIR       The temp directory where the work will be done
```

When the script is used in this way it must be considered carefully how the AWS credentials will be passed. The script uses the `boto3` library from AWS, but the credential handling has been overridden. The script will look for AWS credentials in this order:

- Credentials passed directly as command line arguments (`--aws-access-id` ,  `--aws-access-secret`, and `--aws-region`)
- Credentials set in environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_DEFAULT_REGION`)
- Local credentials file (`~/.aws/credentials`)



## Verifying the Operation

When the tool is running (with debug off) you will see log events like below:

```2021-07-20 09:15:02 INFO     Found credentials in environment variables.
2021-07-20 09:15:03 INFO     {'Attributes': {'ApproximateNumberOfMessages': '0', 'ApproximateNumberOfMessagesNotVisible': '0'}, 'ResponseMetadata': {'RequestId': '6e6742fd-d484-4f7b-b6ff-0c1b4a05b238', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '6e6742fd-d484-4f7b-b6ff-0c1b4a05b238', 'date': 'Tue, 20 Jul 2021 09:15:03 GMT', 'content-type': 'text/xml', 'content-length': '446'}, 'RetryAttempts': 0}}
2021-07-20 09:20:57 INFO     1 file(s) of 1 shipped to Humio (2690230 bytes of 2690230) from 2021-07-20 09:20:52.426000
2021-07-20 09:26:45 INFO     1 file(s) of 1 shipped to Humio (2119130 bytes of 2119130) from 2021-07-20 09:26:41.184000
2021-07-20 09:32:37 INFO     1 file(s) of 1 shipped to Humio (2222584 bytes of 2222584) from 2021-07-20 09:32:32.317000
2021-07-20 09:38:51 INFO     1 file(s) of 1 shipped to Humio (2404796 bytes of 2404796) from 2021-07-20 09:38:46.719000
2021-07-20 09:45:11 INFO     1 file(s) of 1 shipped to Humio (1056 bytes of 1056) from 2021-07-20 09:45:09.373000
2021-07-20 09:45:58 INFO     1 file(s) of 1 shipped to Humio (2787707 bytes of 2787707) from 2021-07-20 09:45:53.505000
2021-07-20 09:50:35 INFO     1 file(s) of 1 shipped to Humio (350 bytes of 350) from 2021-07-20 09:50:34.032000
2021-07-20 09:50:53 INFO     1 file(s) of 1 shipped to Humio (945 bytes of 945) from 2021-07-20 09:50:52.417000
2021-07-20 09:52:31 INFO     1 file(s) of 1 shipped to Humio (31103 bytes of 31103) from 2021-07-20 09:52:29.606000
2021-07-20 09:53:36 INFO     1 file(s) of 1 shipped to Humio (2357370 bytes of 2357370) from 2021-07-20 09:53:31.180000
2021-07-20 09:59:22 INFO     1 file(s) of 1 shipped to Humio (2365363 bytes of 2365363) from 2021-07-20 09:59:17.003000
2021-07-20 10:05:59 INFO     1 file(s) of 1 shipped to Humio (2348701 bytes of 2348701) from 2021-07-20 10:05:54.293000
2021-07-20 10:12:26 INFO     1 file(s) of 1 shipped to Humio (2135982 bytes of 2135982) from 2021-07-20 10:12:21.810000
2021-07-20 10:15:54 INFO     1 file(s) of 1 shipped to Humio (344 bytes of 344) from 2021-07-20 10:15:52.820000
2021-07-20 10:15:56 INFO     1 file(s) of 1 shipped to Humio (674 bytes of 674) from 2021-07-20 10:15:54.863000
...

```



## Building the docker image

You may wish to build your own version of the docker image:

```
git clone <this repo>
cd fdr2humio
docker build --tag YOUR_NAME/fdr2humio:latest .
```

