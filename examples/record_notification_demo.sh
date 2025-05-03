#!/bin/bash
# Script to record the notification demo
# This requires asciinema to be installed: pip install asciinema

# Check if asciinema is installed
if ! command -v asciinema &> /dev/null; then
    echo "asciinema not found. Installing..."
    pip install asciinema
fi

# Record the demo
echo "Recording notification demo..."
asciinema rec --title "Remedy Notification Service Demo" --command "python examples/notification_demo.py" examples/notification_demo.cast

echo "Recording completed. Cast file saved to examples/notification_demo.cast"
echo "You can play it with: asciinema play examples/notification_demo.cast"
echo "Or upload it to asciinema.org for sharing."

# Optional: Convert to GIF if asciicast2gif is available
if command -v asciicast2gif &> /dev/null; then
    echo "Converting to GIF..."
    asciicast2gif examples/notification_demo.cast examples/notification_demo.gif
    echo "GIF created at examples/notification_demo.gif"
else
    echo "To convert to GIF, install asciicast2gif: pip install asciicast2gif"
fi

echo "Demo recording complete!" 