FROM nginx:1.28.1-alpine

COPY public /usr/share/nginx/html

EXPOSE 80
