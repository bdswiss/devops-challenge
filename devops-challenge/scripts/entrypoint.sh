#! /bin/sh


if [ "${INTERVAL}" != "" ]; then node ./dist/worker.js; 
else node ./dist/server.js
fi
