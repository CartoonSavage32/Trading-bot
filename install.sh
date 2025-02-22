#!/bin/bash

# Upgrade pip
python3 -m pip install --upgrade pip

# Install poetry
pip3 install poetry

# Enable the creation of virtual environments in the project directory
poetry config virtualenvs.in-project true

# Install project with poetry
poetry lock
poetry install

