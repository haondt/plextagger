#!/bin/bash
set -e

while true; do
    python -m plextagger
    echo "Run complete, waiting ${SCHEDULE_MINUTES} minutes until next run"
    sleep $((SCHEDULE_MINUTES*60))
done
