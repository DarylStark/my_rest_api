#!/bin/bash

cd /workspaces/${FOLDERNAME}
rm -rf .venv
poetry config virtualenvs.in-project true
poetry install --with dev --with doc
