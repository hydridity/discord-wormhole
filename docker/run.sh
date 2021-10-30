#!/bin/bash

cp config.default.json config.json

if [ -n "${ADMIN_ID+set}" ] ; then
    jq -r \
        --arg ADMIN_ID "${ADMIN_ID}" \
        '."admin id" = $ADMIN_ID' config.json > config.json.tmp && \
        cat config.json.tmp > config.json
fi
if [ -n "${BOT_ID+set}" ] ; then
    jq -r \
        --arg BOT_ID "${BOT_ID}" \
        '."bot id" = $BOT_ID' config.json > config.json.tmp && \
        cat config.json.tmp > config.json
fi
if [ -n "${BOT_KEY+set}" ] ; then
    jq -r \
        --arg BOT_KEY "${BOT_KEY}" \
        '."bot key" = $BOT_KEY' config.json > config.json.tmp && \
        cat config.json.tmp > config.json
fi
if [ -n "${PREFIX+set}" ] ; then
    jq -r \
        --arg PREFIX "${PREFIX}" \
        '.prefix = $PREFIX' config.json > config.json.tmp && \
        cat config.json.tmp > config.json
fi
if [ -n "${LOGO_FILL+set}" ] ; then
    jq -r \
        --arg LOGO_FILL "${LOGO_FILL}" \
        '."logo fill" = $LOGO_FILL' config.json > config.json.tmp && \
        cat config.json.tmp > config.json
fi
if [ -n "${LOG_CHANNEL+set}" ] ; then
    jq -r \
        --arg LOG_CHANNEL "${LOG_CHANNEL}" \
        '."log channel" = $LOG_CHANNEL' config.json > config.json.tmp && \
        cat config.json.tmp > config.json
fi
if [ -n "${LOG_LEVEL+set}" ] ; then
    jq -r \
        --arg LOG_LEVEL "${LOG_LEVEL}" \
        '."log level" = $LOG_LEVEL' config.json > config.json.tmp && \
        cat config.json.tmp > config.json
fi
if [ -n "${DATABASE_URI+set}" ] ; then
    jq -r \
        --arg DATABASE_URI "${DATABASE_URI}" \
        '."database path" = $DATABASE_URI' config.json > config.json.tmp && \
        cat config.json.tmp > config.json
fi
if [ -n "${DATABASE_PORT+set}" ] ; then
    jq -r \
        --arg DATABASE_PORT "${DATABASE_PORT}" \
        '."database port" = $DATABASE_PORT' config.json > config.json.tmp && \
        cat config.json.tmp > config.json
fi

# start bot
python init.py
