FROM nginx

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/nginx.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]