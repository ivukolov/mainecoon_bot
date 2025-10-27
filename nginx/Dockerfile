FROM nginx:alpine

# Устанавливаем geoip для защиты
RUN apk add --no-cache wget libmaxminddb && \
    mkdir -p /usr/share/GeoIP && \
    wget -O /usr/share/GeoIP/GeoLite2-Country.mmdb "https://download.db-ip.com/free/dbip-country-lite-$(date +%Y-%m).mmdb" && \
    apk del wget

# Создаем директорию для скриптов
RUN mkdir -p /scripts/

# Копируем скрипты в контейнер
COPY generate_sert.sh /scripts/generate_sert.sh

# Даем права на выполнение
RUN chmod +x /scripts/*.sh