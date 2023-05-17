#!/bin/sh

# Usage: sh convert.sh <input webm> <out gif>

# Speedup video by 10
ffmpeg -i $1 -filter:v "setpts=PTS/10" temp.webm

# Convert to gif
ffmpeg -i temp.webm -pix_fmt rgb24 $2

# Remove temporary file
rm temp.webm
