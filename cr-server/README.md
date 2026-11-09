# ChartReady server

One small Node.js program that does two things:
1. Serves the ChartReady app (the files in `public/`).
2. Relays remote-control messages between your computer and your phone (WebSocket at `/ws`).
   The sound is always produced on the computer; the phone only sends commands.

The remote-control password is checked **on the server**, so nobody can use your relay without it.
Pairings are saved in `data/pairs.json`, so the phone reconnects by itself next time.

## Option A: run with Node.js (Linux server)

```bash
# 1. copy this folder to the server, then inside it:
npm ci --omit=dev
# 2. start it (pick your own password; it must match what you type in the app)
REMOTE_PASSWORD=135246 PORT=8787 node server.js
```

To keep it running after you log out, use pm2:
```bash
sudo npm i -g pm2
REMOTE_PASSWORD=135246 PORT=8787 pm2 start server.js --name chartready
pm2 save && pm2 startup
```

## Option B: run with Docker

```bash
docker build -t chartready .
docker run -d --name chartready --restart unless-stopped \
  -e REMOTE_PASSWORD=135246 -p 8787:8787 -v chartready-data:/data chartready
```

## HTTPS (required for phones)

Phones only allow the app and its connection over HTTPS. Put nginx in front of the server
and get a free certificate with Let's Encrypt (`sudo certbot --nginx -d chartready.your-domain.com`).

nginx site config:
```nginx
server {
  server_name chartready.your-domain.com;
  location / {
    proxy_pass http://127.0.0.1:8787;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;     # needed for the WebSocket at /ws
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_read_timeout 1h;
  }
  listen 443 ssl; # certbot fills in the certificate lines
}
```

## Using it

1. On the computer open `https://chartready.your-domain.com`, go to Settings, tap **שליטה מרחוק** at the bottom, enter the password, tap **חבר את הטלפון**.
2. Scan the QR code with the phone (or open the app on the phone, same place, and type the 6-digit code).
3. Done. Next time just open the app on both; they find each other.
   Settings › שליטה מרחוק › **בטל שיוך** removes the phone.

## Updating the app

Replace the files in `public/` with the new ones and restart (`pm2 restart chartready` or rebuild the Docker image).
Phones pick up the new version the next time they open the app online.

## Changing the password

The app checks a fingerprint (SHA-256) of the password before it shows the remote section, and the server checks the real password.
If you change it, change `REMOTE_PASSWORD` here and ask Claude to update the fingerprint in the app.
