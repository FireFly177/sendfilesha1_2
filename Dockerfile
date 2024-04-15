FROM nginx

COPY . /usr/share/nginx/html
# COPY ./nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
EXPOSE 8000

RUN apt-get update && apt-get install -y python3 python3-pip

CMD service nginx start && python3 /usr/share/nginx/html/backend.py