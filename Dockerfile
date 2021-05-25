# This is the base image
FROM python:3-alpine

# Create a directory for the app
RUN mkdir /fdr2humio

# Set the working directory
WORKDIR /fdr2humio

# Copy the utils files and log-replay.py
COPY requirements.txt requirements.txt
COPY fdr2humio.py fdr2humio.py
COPY run.sh run.sh
COPY LICENSE LICENSE

# Install any requirements
RUN pip install --no-cache-dir -r requirements.txt

# Make the entrypoint executable
RUN chmod +x run.sh

# Run the app
ENTRYPOINT [ "/fdr2humio/run.sh" ]

# Associate the image to the source repo
LABEL org.opencontainers.image.source="https://github.com/humio/fdr2humio"
