#!/bin/bash
cd "$(dirname "$0")"
echo ""
echo "  Iniciando Facturador RJCH..."
python3 server.py &
SERVER_PID=$!
sleep 1
# Abrir el navegador automáticamente
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000
elif command -v open &> /dev/null; then
    open http://localhost:3000
fi
echo "  Servidor PID: $SERVER_PID"
echo "  Presiona Enter para detener el servidor..."
read
kill $SERVER_PID 2>/dev/null
echo "  Servidor detenido."
