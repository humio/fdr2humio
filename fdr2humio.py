import sys
import datetime
import tempfile
import gzip
import mmap
import time
import os
import json
import shutil
import urllib.parse
import sqlite3
import urllib3
import boto3


def humio_url(args):
    """Return the URL to Humio's HEC raw API"""
    return urllib.parse.urljoin(args["humio-host"], "/api/v1/ingest/hec/raw")


def humio_headers(args):
    """Headers for posting RAW gzipped data"""
    return {
        "Content-Encoding": "gzip",
        "Authorization": "Bearer " + args["humio-token"],
    }


def log(message, level="INFO"):
    """A cheap little log line printer"""
    print("%s [%s] %s" % (datetime.datetime.now(), level, message))


def is_compressed(filename):
    """Detects if a file at a specific path is gzip compressed."""
    fileSize = os.path.getsize(filename)
    if fileSize == 0:
        return False
    try:
        gzip.GzipFile(filename=filename).peek(max(256, fileSize))
        return True
    except OSError:
        return False


def is_suitable_tempdir(path):
    if os.path.isdir(path) and os.access(path, os.W_OK):
        return path
    msg = "%s is not a usable temp dir" % path
    raise argparse.ArgumentTypeError(msg)


def not_implemented(token):
    msg = "This argument is not currently supported."
    raise argparse.ArgumentTypeError(msg)


def pp_args(args):
    print("Running with the following arguments:")
    print()
    for arg in args:
        argNamePadded = "{:<18}".format(arg)
        if arg in ["aws_access_secret", "humio-token"]:
            print("\t%s =>\t%s" % (argNamePadded, str("*" * len(str(args[arg])))))
        else:
            print("\t%s =>\t%s" % (argNamePadded, str(args[arg])))
    print()


def setup_args():
    import argparse

    parser = argparse.ArgumentParser(
        description="This script is used to collect Falcon logs from S3, and send them to a Humio instance."
    )

    # Details for the source bucket and access
    parser.add_argument(
        "bucket",
        type=str,
        action="store",
        help='The S3 bucket from which to export. E.g "demo.humio.xyz"',
    )
    parser.add_argument(
        "queue_url",
        type=str,
        action="store",
        help="The SQS queue URL for notifiying new files",
    )
    parser.add_argument(
        "--aws-access-id",
        type=not_implemented,
        action="store",
        help="The AWS access key ID (not implemented)",
    )
    parser.add_argument(
        "--aws-access-secret",
        type=not_implemented,
        action="store",
        help="The AWS access key secret (not implemented)",
    )

    # Target system where the logs will be sent
    parser.add_argument(
        "humio-host",
        type=str,
        action="store",
        default="https://cloud.humio.com:443/",
        help="The URL to the target Humio instance, including optional port number",
    )
    parser.add_argument(
        "humio-token", type=str, action="store", help="Ingest token for this input"
    )
    parser.add_argument(
        "--humio-batch",
        type=int,
        action="store",
        default=5000,
        help="Max events batch size for sending to Humio",
    )

    # Are we going to do the debug?
    parser.add_argument("--debug", action="store_true", help="We do the debug?")

    # Where can we do our workings
    parser.add_argument(
        "--tmpdir",
        type=is_suitable_tempdir,
        action="store",
        default="/tmp",
        help="The temp directory where the work will be done",
    )

    # Build the argument list
    return vars(parser.parse_args())


def get_new_events(args, sqs, maxEvents=1, maxWaitSeconds=10, reserveSeconds=300):
    queue = sqs.Queue(args["queue_url"])
    return queue.receive_messages(
        MessageAttributeNames=["All"],
        WaitTimeSeconds=maxWaitSeconds,
        VisibilityTimeout=reserveSeconds,
        MaxNumberOfMessages=maxEvents,
    )


def check_valid(args, payload, s3):
    # Confirm that the _SUCCESS file exists
    success_path = payload["pathPrefix"] + "/_SUCCESS"
    try:
        obj = s3.head_object(Bucket=args["bucket"], Key=success_path)
    except Exception as e:
        if args["debug"]:
            log(str(e), level="DEBUG")
        return False
    return True


def post_files_to_humio(args, payload, s3, http):
    # Download from S3 into temp dir
    with tempfile.TemporaryDirectory(dir=args["tmpdir"]) as tmpdirname:

        # Process each file mentioned
        for asset in payload["files"]:

            # Get the filename from the file path
            local_file_path = os.path.join(tmpdirname, os.path.basename(asset["path"]))

            # Download the source file from S3
            s3.download_file(args["bucket"], asset["path"], local_file_path)

            # TODO: Check the checksum

            # TODO: check the size!

            # POST to Humio HEC Raw w/ compression
            with open(local_file_path, "rb") as f:
                r = http.request(
                    "POST",
                    humio_url(args),
                    body=f.read(),
                    headers=humio_headers(args),
                )

                if r.status != 200:
                    return False

    # Everything sent as expected
    return True


if __name__ == "__main__":
    # We only need to do the argparse if we're running interactivley
    args = setup_args()

    # Echo to stdout so we can see the args in use if debug
    if args["debug"]:
        pp_args(args)

    # Initialise the aws clients and an http request pool
    s3 = boto3.client("s3")
    sqs_client = boto3.client("sqs")
    sqs = boto3.resource("sqs")
    http = urllib3.PoolManager()

    # Start by checking the state of the queue
    print(
        sqs_client.get_queue_attributes(
            QueueUrl=args["queue_url"],
            AttributeNames=[
                "ApproximateNumberOfMessages",
                "ApproximateNumberOfMessagesNotVisible",
            ],
        )
    )

    # Start reading the queue and processing files
    # TODO this should process requests in parallel based on the number of CPU available, or something clever like that
    while True:
        for message in get_new_events(
            args, sqs, maxEvents=5, reserveSeconds=300, maxWaitSeconds=20
        ):
            payload = json.loads(message.body)

            # We will have data events, and asset events, need to be handled separately
            if check_valid(args, payload, s3):
                if post_files_to_humio(args, payload, s3, http):
                    log(
                        "Messages shipped to Humio",
                        level="INFO",
                    )
                    message.delete()
            else:
                # The queue item is referring to a batch that doesn't exist any more
                # which probably means its too old and should be deleted from the queue
                log(
                    "Message deleted from queue as notification is too old and now empty, or for some other reason incomplete",
                    level="WARN",
                )
                message.delete()

        # log("No elligible messages, sleeping for 5 mins", level="DEBUG")
        # time.sleep(300)

    sys.exit()
