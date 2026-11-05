#!/usr/bin/env bash
# Local Docker helper. Does not edit or publish environment configuration.
set -euo pipefail
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
sdk_dir="${CONNECTIQ_HOME:-/workspace/.toolchains/garmin/9.3.0}"
state_dir="${CIQ_RUNTIME_STATE:-/workspace/.toolchains/garmin/runtime/state}"
image_name="garmin-ciq-runtime:ubuntu22.04"
container_name="garmin-ciq-simulator"
docker_local() {
    env -u DOCKER_HOST -u DOCKER_CONTEXT -u DOCKER_TLS -u DOCKER_TLS_VERIFY -u DOCKER_CERT_PATH \
        docker --host=unix:///var/run/docker.sock "$@"
}
case "${1:-status}" in
    build)
        docker_local build --secret id=ca,src=/etc/ssl/certs/ca-certificates.crt \
            -t "$image_name" "$project_dir/tools/ciq"
        ;;
    start)
        test -x "$sdk_dir/bin/simulator"
        if docker_local container inspect "$container_name" >/dev/null 2>&1; then
            label="$(docker_local container inspect --format '{{index .Config.Labels "org.garminshemah.runtime"}}' "$container_name")"
            if [ "$label" != 1 ]; then
                echo "Container name is in use by an unmanaged container; inspect it before continuing." >&2
                exit 1
            fi
            docker_local rm -f "$container_name" >/dev/null
        fi
        mkdir -p "$state_dir"
        docker_local run -d --init --name "$container_name" \
            --label org.garminshemah.runtime=1 --user "$(id -u):$(id -g)" -e HOME=/home/garmin \
            --mount "type=bind,src=$sdk_dir,dst=/opt/connectiq,readonly" \
            --mount "type=bind,src=$project_dir,dst=/workspace/GarminShemah,readonly" \
            --mount "type=bind,src=$state_dir,dst=/home/garmin" \
            --mount "type=bind,src=$project_dir/tools/ciq/start-simulator.sh,dst=/opt/start-simulator.sh,readonly" \
            "$image_name" /opt/start-simulator.sh
        ready=false
        for attempt in {1..50}; do
            if docker_local exec -e DISPLAY=:99 "$container_name" \
                xwininfo -name 'CIQ Simulator' >/dev/null 2>&1; then
                ready=true
                break
            fi
            sleep 0.2
        done
        if [ "$ready" != true ]; then
            docker_local logs --tail 30 "$container_name" >&2
            echo "Simulator window did not become ready." >&2
            exit 1
        fi
        ;;
    status)
        docker_local exec "$container_name" bash -c \
            'ldd /opt/connectiq/bin/simulator > /tmp/ciq-libraries.txt; if grep "not found" /tmp/ciq-libraries.txt; then exit 1; fi; /opt/connectiq/bin/monkeyc --version'
        docker_local exec -e DISPLAY=:99 "$container_name" xwininfo -name 'CIQ Simulator'
        ;;
    screenshot)
        docker_local exec -e DISPLAY=:99 "$container_name" xwd -name 'CIQ Simulator' \
            -silent -out /home/garmin/logs/simulator-startup.xwd
        echo "$state_dir/logs/simulator-startup.xwd"
        ;;
    shell)
        shift
        docker_local exec "$container_name" timeout 15 /opt/connectiq/bin/shell "$@"
        ;;
    stop)
        label="$(docker_local container inspect --format '{{index .Config.Labels "org.garminshemah.runtime"}}' "$container_name")"
        test "$label" = 1
        docker_local stop "$container_name"
        ;;
    *) echo "Usage: $0 {build|start|status|screenshot|shell COMMAND|stop}" >&2; exit 2 ;;
esac
