#!/usr/bin/env bash
# Move the register out of ~/Desktop and schedule the nightly refresh — then prove it.
#
# macOS denies scheduled jobs access to ~/Desktop. Verified 2026-08-28, not assumed:
# a LaunchAgent could list a file there but reading it returned "Operation not
# permitted". The project therefore lives in the home directory; a symlink keeps the
# familiar Desktop path working from the terminal.
set -euo pipefail
SRC="$HOME/Desktop/crypto-bot/sito"
DST="$HOME/auftragsregister"
PLIST="$HOME/Library/LaunchAgents/ch.auftragsregister.nightly.plist"

if [ -L "$SRC" ] && [ -d "$DST" ]; then
  echo "  già installato in $DST"
else
  [ -e "$DST" ] && { echo "$DST esiste già — sposta o rinomina prima" >&2; exit 1; }
  echo "  sposto $SRC -> $DST"
  mv "$SRC" "$DST"
  ln -s "$DST" "$SRC"
fi

cat > "$PLIST" <<PLISTEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>ch.auftragsregister.nightly</string>
  <key>ProgramArguments</key>
  <array><string>/usr/bin/python3</string><string>$DST/aggiorna.py</string></array>
  <key>WorkingDirectory</key><string>$DST</string>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>5</integer><key>Minute</key><integer>40</integer></dict>
  <key>StandardOutPath</key><string>$DST/launchd.log</string>
  <key>StandardErrorPath</key><string>$DST/launchd.log</string>
</dict></plist>
PLISTEOF
launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"

# Prove the scheduled job can actually READ the files. Installing a job that cannot
# is the failure this whole move exists to avoid, and it fails silently at 05:40.
PROBE="$HOME/Library/LaunchAgents/ch.auftragsregister.probe.plist"
cat > "$PROBE" <<PROBEEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>ch.auftragsregister.probe</string>
  <key>ProgramArguments</key>
  <array><string>/bin/bash</string><string>-c</string>
  <string>head -c 40 "$DST/genera.py" > /tmp/auftragsregister_probe.txt 2>&1</string></array>
  <key>RunAtLoad</key><true/>
</dict></plist>
PROBEEOF
rm -f /tmp/auftragsregister_probe.txt
launchctl unload "$PROBE" 2>/dev/null || true
launchctl load "$PROBE"
for _ in $(seq 1 20); do [ -s /tmp/auftragsregister_probe.txt ] && break; sleep 1; done
launchctl unload "$PROBE" 2>/dev/null || true
rm -f "$PROBE"

if grep -q "not permitted" /tmp/auftragsregister_probe.txt 2>/dev/null; then
  echo "  FALLITO: il lavoro pianificato non riesce a leggere $DST" >&2
  echo "  concedi 'Accesso completo al disco' a launchd, oppure sposta altrove" >&2
  exit 1
fi
if [ ! -s /tmp/auftragsregister_probe.txt ]; then
  echo "  ATTENZIONE: la verifica non ha prodotto output — controlla a mano" >&2
  exit 1
fi
echo "  verifica superata: il lavoro pianificato legge i file"
echo "  aggiornamento notturno attivo, ogni giorno alle 05:40"
echo "  controllo:  launchctl list | grep auftragsregister"
echo "  log:        $DST/aggiorna.log"
