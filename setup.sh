#!/bin/zsh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
echo "Setup complete. Run 'source .venv/bin/activate' to activate the virtual environment."