#!/usr/bin/env bash
set -euo pipefail
export DISPLAY=:99
mkdir -p "$HOME/logs"
Xvfb :99 -screen 0 1280x900x24 -nolisten tcp >"$HOME/logs/xvfb.log" 2>&1 &
xvfb_pid=$!
cleanup() { kill "$xvfb_pid" 2>/dev/null || true; }
trap cleanup EXIT
ready=false
for attempt in {1..50}; do
    if xdpyinfo >/dev/null 2>&1; then ready=true; break; fi
    sleep 0.2
done
if [ "$ready" != true ]; then cat "$HOME/logs/xvfb.log" >&2; exit 1; fi
exec /opt/connectiq/bin/simulator
