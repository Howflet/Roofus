#!/usr/bin/env bash
# Roofus Hapeville - one-click launcher (Mac/Linux)

cd "$(dirname "$0")"

PY="python3"

if ! command -v "$PY" > /dev/null; then
  echo "[ERROR] python3 not found in PATH."
  exit 1
fi

echo "Starting backend API on http://localhost:8000 ..."
"$PY" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

echo "Starting frontend on http://localhost:5173 ..."
"$PY" -m http.server 5173 --directory frontend &
FRONTEND_PID=$!

echo "Waiting for servers to warm up ..."
sleep 3


echo "Opening browser ..."
if command -v open > /dev/null; then
  open "http://localhost:5173"
elif command -v xdg-open > /dev/null; then
  xdg-open "http://localhost:5173"
else
  echo "Please open http://localhost:5173 in your browser"
fi

echo ""
echo "============================================================"
echo " Roofus is running!"
echo "   App:      http://localhost:5173"
echo "   API docs: http://localhost:8000/docs"
echo ""
echo " Press Ctrl+C to stop both servers."
echo "============================================================"
echo ""

# Wait for user interrupt
trap "echo -e '\nStopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM
wait
