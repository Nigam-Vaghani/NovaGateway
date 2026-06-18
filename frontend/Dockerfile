FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
RUN echo -e 'server {\n    listen       80;\n    listen  [::]:80;\n    server_name  localhost;\n\n    location / {\n        root   /usr/share/nginx/html;\n        index  index.html index.htm;\n        try_files $uri $uri/ /index.html;\n    }\n\n    error_page   500 502 503 504  /50x.html;\n    location = /50x.html {\n        root   /usr/share/nginx/html;\n    }\n}' > /etc/nginx/conf.d/default.conf

COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
