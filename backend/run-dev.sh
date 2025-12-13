#!/bin/bash

cd "$(dirname "$0")"

if ! command -v nodemon &> /dev/null; then
    echo "❌ nodemon is not installed."
    echo "📦 Installing nodemon globally..."
    npm install -g nodemon
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install nodemon. Please install it manually: npm install -g nodemon"
        exit 1
    fi
fi

if [ -f "poetry.lock" ] && command -v poetry &> /dev/null; then
    echo "✅ Using Poetry environment with nodemon..."
    echo "🚀 Starting app.py with auto-reload..."
    poetry run nodemon --exec "poetry run python app.py" app.py
else
    echo "✅ Using system Python with nodemon..."
    echo "🚀 Starting app.py with auto-reload..."
    nodemon app.py
fi

