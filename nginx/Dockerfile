FROM nginx:alpine

# Устанавливаем geoip для защиты
RUN apk add --no-cache wget && \
    mkdir -p /usr/share/GeoIP && \
    wget -O /tmp/GeoIP.dat.gz http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz && \
    gunzip -c /tmp/GeoIP.dat.gz > /usr/share/GeoIP/GeoIP.dat && \
    rm /tmp/GeoIP.dat.gz && \
    apk del wget

# Создаем директорию для скриптов
RUN mkdir -p /scripts/

# Копируем скрипты в контейнер
COPY generate_sert.sh /scripts/generate_sert.sh

# Даем права на выполнение
RUN chmod +x /scripts/*.sh