FROM nginx:alpine

# Устанавливаем geoip для защиты
RUN apk add --no-cache wget && \
    mkdir -p /usr/share/GeoIP && \
    wget -O /tmp/GeoIP.dat.gz "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-Country&license_key=YOUR_LICENSE_KEY&suffix=tar.gz" && \
    tar -xzf /tmp/GeoIP.dat.gz -C /tmp --strip-components=1 && \
    mv /tmp/GeoLite2-Country.mmdb /usr/share/GeoIP/ && \
    rm -rf /tmp/* && \
    apk del wget

# Создаем директорию для скриптов
RUN mkdir -p /scripts/

# Копируем скрипты в контейнер
COPY generate_sert.sh /scripts/generate_sert.sh

# Даем права на выполнение
RUN chmod +x /scripts/*.sh