#!/bin/bash
source venv/bin/activate
source .env
python3 trigger-pipeline.py --repo-owner tosin2013 --repo-name rhel9-bootstrap --hostname 123.123.123.123 \
    --cluster-name test1 --base-domain example.com