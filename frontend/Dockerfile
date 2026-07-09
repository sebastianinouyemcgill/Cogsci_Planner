FROM node:20

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 5173

# Re-install on start so the node_modules volume stays in sync with package.json.
CMD ["sh", "-c", "npm install && npm run dev -- --host --port 5173"]