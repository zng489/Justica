# Bundle JS code
FROM node:12-alpine as node-builder

USER root
WORKDIR /app/
COPY . /app
RUN yarn cache clean && \
    rm -rf node_modules && \
    yarn install && \
    yarn run build:dist && \
    yarn cache clean && \
    rm -rf node_modules

# nginx to serve static assets
FROM nginx:1.18-alpine as webserver
COPY --from=node-builder /app/www /usr/share/nginx/html
COPY --from=node-builder /app/version.txt /usr/share/nginx/html
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
