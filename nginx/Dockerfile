FROM nginx:alpine
# Устанвока пакетов

# Создаём дирректорию для скриптов
RUN mkdir -p /scripts/
# Копируем скрипты в контейнер
COPY generate_sert.sh /scripts/generate_sert.sh

# Даем права на выполнение
RUN chmod +x /scripts/*.sh

# Запускаем Nginx
CMD ["nginx", "-g", "daemon off;"]


