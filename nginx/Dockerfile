FROM nginx:alpine
## https://thomaswildetech.com/blog/2025/03/16/nginx-in-docker-with-geoip/ Огромная благодарность автору!
# Устанвока пакетов
RUN apk add --no-cache \
    wget \
    build-base \
    pcre-dev \
    zlib-dev \
    linux-headers \
    libressl-dev \
    libmaxminddb-dev \
    git

# Загрузка исходников NGINX
RUN nginx_version=$(nginx -v 2>&1 | awk -F/ '{print $2}') && \
    wget http://nginx.org/download/nginx-${nginx_version}.tar.gz && \
    tar -xzf nginx-${nginx_version}.tar.gz && \
    cd nginx-${nginx_version} && \
    git clone https://github.com/leev/ngx_http_geoip2_module.git

# СБорка модуля
RUN cd nginx-$(nginx -v 2>&1 | awk -F/ '{print $2}') && \
    ./configure --with-compat --add-dynamic-module=ngx_http_geoip2_module && \
    make modules && \
    cp objs/ngx_http_geoip2_module.so /etc/nginx/modules/

RUN wget -O /tmp/dbip-country-lite.mmdb.gz "https://download.db-ip.com/free/dbip-country-lite-$(date +%Y-%m).mmdb.gz" && \
    gunzip -c /tmp/dbip-country-lite.mmdb.gz > /usr/share/GeoIP/GeoLite2-Country.mmdb && \
    rm /tmp/dbip-country-lite.mmdb.gz && \
    apk del wget
# Очистка
RUN rm -rf /var/cache/apk/* nginx-* ngx_http_geoip2_module

# Создаём дирректорию для скриптов
RUN mkdir -p /scripts/
# Копируем скрипты в контейнер
COPY generate_sert.sh /scripts/generate_sert.sh

# Даем права на выполнение
RUN chmod +x /scripts/*.sh

# Запускаем Nginx
CMD ["nginx", "-g", "daemon off;"]


