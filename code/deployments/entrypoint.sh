#!/bin/sh

# variable is empty run worker
if [ -z "$PORT" ]; then
  node dist/worker
else
  node dist/server
fi