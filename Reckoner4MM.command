#!/bin/bash
set -e
cd "$(dirname "$0")"
python3 scripts/local.py open
printf '\nLa contraseña se muestra solo en esta terminal local:\n'
python3 scripts/local.py password
printf '\nPuedes cerrar esta ventana; Reckoner seguirá funcionando.\n'
