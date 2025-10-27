FROM nginx:alpine

# Устанавливаем geoip для защиты
RUN apk add --no-cache wget && \
    mkdir -p /usr/share/GeoIP && \
    wget -O /usr/share/GeoIP/GeoIP.dat "https://raw.githubusercontent.com/sapics/ip-location-db/main/geo-whois-asn-country/geo-whois-asn-country-ipv4-num.csv" && \
    apk del wget

# Создаем директорию для скриптов
RUN mkdir -p /scripts/

# Копируем скрипты в контейнер
COPY generate_sert.sh /scripts/generate_sert.sh

# Даем права на выполнение
RUN chmod +x /scripts/*.sh