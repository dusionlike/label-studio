#!/usr/bin/env bash

# Ensure conda is initialized for non-interactive shells
CONDA_BASE=""
if command -v conda >/dev/null 2>&1; then
	CONDA_BASE="$(conda info --base 2>/dev/null)"
fi
if [ -n "$CONDA_BASE" ] && [ -f "$CONDA_BASE/etc/profile.d/conda.sh" ]; then
	. "$CONDA_BASE/etc/profile.d/conda.sh"
elif [ -f "./.conda/bin/activate" ]; then
	. "./.conda/bin/activate"
fi

conda activate ./.conda
nohup python label_studio/manage.py runserver 0.0.0.0:8099 > label_studio.log 2>&1 &
echo "Label Studio is running in the background. Logs are being written to label_studio.log"