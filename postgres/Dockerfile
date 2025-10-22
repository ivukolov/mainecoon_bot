FROM postgres:16.1

# Создаем директорию для скриптов
RUN mkdir -p /scripts/

# Копируем скрипты в контейнер
COPY backup.sh /scripts/backup.sh

# Даем права на выполнение
RUN chmod +x /scripts/*.sh