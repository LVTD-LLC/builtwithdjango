#!/bin/sh
set -eu

# All commands before the conditional ones
export DJANGO_SETTINGS_MODULE=builtwithdjango.settings
export PROJECT_NAME=builtwithdjango
APP_PORT="${PORT:-80}"
process_type="${APP_PROCESS_TYPE:-}"

# export OTEL_EXPORTER_OTLP_ENDPOINT=https://signoz-otel-collector-proxy.cr.lvtd.dev
# export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf

# Parse command-line arguments
while getopts ":sw" option; do
    case "${option}" in
        s)  # Run server
            process_type="server"
            ;;
        w)  # Run worker
            process_type="worker"
            ;;
        *)  # Invalid option
            echo "Invalid option: -$OPTARG" >&2
            exit 1
            ;;
    esac
done
shift $((OPTIND - 1))

if [ -z "$process_type" ]; then
    echo "APP_PROCESS_TYPE was not set. Defaulting to server."
    process_type="server"
fi

case "$process_type" in
server)
    python manage.py collectstatic --noinput
    python manage.py migrate --noinput

    # python manage.py djstripe_sync_models
    # export OTEL_SERVICE_NAME=builtwithdjango_${ENV:-dev}
    # export OTEL_RESOURCE_ATTRIBUTES=service.name=builtwithdjango_${ENV:-dev}
    # opentelemetry-instrument gunicorn builtwithdjango.wsgi:application --bind 0.0.0.0:80 --workers 3 --threads 2 --reload
    exec gunicorn builtwithdjango.wsgi:application --bind 0.0.0.0:${APP_PORT} --workers 3 --threads 2 --reload
    ;;
worker)
    # export OTEL_SERVICE_NAME="builtwithdjango_${ENV:-dev}_workers"
    # export OTEL_RESOURCE_ATTRIBUTES=service.name=builtwithdjango_${ENV:-dev}_workers
    # opentelemetry-instrument python manage.py qcluster
    exec python manage.py qcluster
    ;;
*)
    echo "Invalid APP_PROCESS_TYPE: $process_type. Expected 'server' or 'worker'." >&2
    exit 1
    ;;
esac
