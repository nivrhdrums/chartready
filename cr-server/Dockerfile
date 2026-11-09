FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY server.js ./
COPY public ./public
ENV PORT=8787 DATA_FILE=/data/pairs.json
VOLUME /data
EXPOSE 8787
CMD ["node", "server.js"]
