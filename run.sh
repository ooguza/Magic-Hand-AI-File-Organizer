#!/bin/bash

# Hata durumunda scripti durdur
set -e

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Gerekli paketleri yükle
echo "Installing required packages..."
python3.11 -m pip install -r requirements.txt

# Eski build ve dist klasörlerini temizle
echo "Cleaning build directories..."
sudo rm -rf build dist

# Uygulamayı derle
echo "Building the application..."
python3.11 setup.py py2app

# İzinleri düzelt
echo "Fixing permissions..."
sudo chown -R $(whoami) dist

# Uygulamayı çalıştır
echo "Starting the application..."
"$DIR/dist/Magic Hand.app/Contents/MacOS/Magic Hand"
