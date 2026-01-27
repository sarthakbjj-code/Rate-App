FROM nginx:1.25.3-alpine

COPY public /usr/share/nginx/html

EXPOSE 80
