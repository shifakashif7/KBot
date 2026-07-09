#!/bin/bash
STORAGE_DIR="/app/KBot Storage"
VECTORS="$STORAGE_DIR/vectors.npy"

if [ ! -f "$VECTORS" ] || [ ! -s "$VECTORS" ]; then
    echo "Downloading pre-built index..."
    rm -rf "$STORAGE_DIR"
    python -c "
import urllib.request
url = 'https://github.com/shifakashif7/KBot/releases/download/v1.0-index/kbot_storage.tar.gz'
print('Fetching', url)
urllib.request.urlretrieve(url, '/tmp/kbot_storage.tar.gz')
print('Download complete.')
"
    cd /app && tar -xzf /tmp/kbot_storage.tar.gz
    rm /tmp/kbot_storage.tar.gz
    echo "Index ready."
else
    echo "Index already present, skipping download."
fi

exec gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 1
