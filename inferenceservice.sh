#!/bin/bash

FILE_PATH="/tmp/gesture-ipc.sock"

while [ ! -f "$FILE_PATH" ]; do
    echo "Waiting for file: $FILE_PATH"
    sleep 5  # Wait for 5 seconds before checking again
done

cd $HOME/Envision-API
. venv/bin/activate
python live_stream_analysis.py
