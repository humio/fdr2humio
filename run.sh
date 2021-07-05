#!/bin/sh

# Check the required variables are set
if [[ -z $F2H_SQS_URL || -z $F2H_S3_BUCKET || -z $F2H_HUMIO_URL || -z F2H_HUMIO_TOKEN ]]; then
  echo 'One or more fdr2humio variables are undefined, see fdr2humio.conf.example'
  exit 1
fi

# Now start the python script with the right variables, with or without debug
if [[ -z "$F2H_DEBUG" || ${F2H_DEBUG} == "false" ]]; then
	python3 fdr2humio.py ${F2H_S3_BUCKET} ${F2H_SQS_URL} ${F2H_HUMIO_URL} ${F2H_HUMIO_TOKEN} 
else
	python3 fdr2humio.py ${F2H_S3_BUCKET} ${F2H_SQS_URL} ${F2H_HUMIO_URL} ${F2H_HUMIO_TOKEN} --debug
fi
