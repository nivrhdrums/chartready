#!/bin/bash
# Recreates the working layout the build scripts expect. Run from the checkout of the "source" branch.
set -e
D="$(cd "$(dirname "$0")" && pwd)"
mkdir -p /tmp/claude-0/build /home/claude/chartready-site /home/claude/cr-server/public
cp -r "$D/build/." /tmp/claude-0/build/
cp "$D/site/"* /home/claude/chartready-site/
cp "$D/site/"* /home/claude/cr-server/public/   # build.py also writes the server copy of sw.js
cp "$D/cr-server/"* /home/claude/cr-server/ 2>/dev/null || true
cp "$D/cr-server/.env.example" /home/claude/cr-server/ 2>/dev/null || true
cp "$D/tools/rhythm-map.html" /home/claude/ 2>/dev/null || true
cd /home/claude/cr-server && npm install --silent ws@8 >/dev/null 2>&1 || true
# the site index.html wrapper is taken from chartready-site/index.html: seed it once from the public build
[ -f /home/claude/chartready-site/index.html ] || cp "$D/site-index.html" /home/claude/chartready-site/index.html
echo "ready: cd /tmp/claude-0/build && python3 build.py"
