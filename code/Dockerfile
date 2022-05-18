FROM node:14-alpine

WORKDIR /app
COPY . .
RUN npm install && npm run build

ENTRYPOINT [ "/bin/sh", "deployments/entrypoint.sh" ]