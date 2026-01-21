#!/bin/bash
set -e

echo "Creating S3 bucket..."

aws --endpoint-url=http://localhost:4566 s3 mb s3://tofu-blog-image-local || true

echo "S3 bucket created"
