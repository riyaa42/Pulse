#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

if ! command -v uv >/dev/null 2>&1; then
  echo "Error: 'uv' is not installed. Install it first: https://docs.astral.sh/uv/"
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "Error: 'npm' is not installed. Install Node.js + npm first."
  exit 1
fi

if [[ ! -f "$BACKEND_DIR/.env" && -f "$BACKEND_DIR/.env.example" ]]; then
  cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
  echo "Created backend/.env from .env.example"
  echo "Make sure DB_PASSWORD in backend/.env is correct."
fi

if [[ ! -f "$FRONTEND_DIR/.env" && -f "$FRONTEND_DIR/.env.example" ]]; then
  cp "$FRONTEND_DIR/.env.example" "$FRONTEND_DIR/.env"
  echo "Created frontend/.env from .env.example"
fi

echo "Installing backend dependencies (uv sync)..."
(cd "$BACKEND_DIR" && uv sync)

echo "Installing frontend dependencies (npm install)..."
(cd "$FRONTEND_DIR" && npm install)

BACKEND_PID=""
FRONTEND_PID=""
STOPPED=0

cleanup() {
  if [[ "$STOPPED" -eq 1 ]]; then
    return
  fi
  STOPPED=1
  echo
  echo "Stopping services..."
  if [[ -n "$BACKEND_PID" ]]; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi
  if [[ -n "$FRONTEND_PID" ]]; then
    kill "$FRONTEND_PID" 2>/dev/null || true
  fi
  wait 2>/dev/null || true
}

trap cleanup INT TERM EXIT

echo "Starting backend on http://localhost:8000 ..."
(cd "$BACKEND_DIR" && uv run python main.py) &
BACKEND_PID=$!

echo "Starting frontend dev server..."
(cd "$FRONTEND_DIR" && npm run dev -- --host) &
FRONTEND_PID=$!

echo
echo "MusicDB is starting up."
echo "Backend:  http://localhost:8000/api/health"
echo "Frontend: http://localhost:5173"
echo "Press Ctrl+C to stop both."

wait -n "$BACKEND_PID" "$FRONTEND_PID"
echo "One of the services exited."
