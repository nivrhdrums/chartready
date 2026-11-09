# ChartReady · source

Branch `source` = build sources. Branch `main` = the published site (GitHub Pages).

    git clone -b source https://github.com/nivrhdrums/chartready /tmp/src && bash /tmp/src/setup.sh
    git clone https://github.com/nivrhdrums/chartready /home/claude/chartready   # site checkout used by deploy.py
    cd /tmp/claude-0/build
    python3 build.py && node --check /tmp/t.js     # build + syntax check (test.html for Playwright)
    python3 deploy.py "message"                    # bumps version, builds public + personal, pushes main

Personal (secret open) copy is published at /c40b604d/.
