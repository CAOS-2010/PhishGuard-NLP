#!/bin/bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
exec streamlit run src/ui/app.py \
  --server.port "$PORT" \
  --server.address 0.0.0.0 \
  --server.headless true
