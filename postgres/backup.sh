#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/dump/"
LOG_FILE="$BACKUP_DIR/backup_${POSTGRES_DB}_${DATE}.log"
BACKUP_NAME="$BACKUP_DIR/backup_${POSTGRES_DB}_${DATE}.dump"

# Создаем директорию для бэкапов
#mkdir -p $BACKUP_DIR
exec > >(tee -a "$LOG_FILE") 2>&1
echo "=== Запущено создание бэкапа: $(date) ==="
echo "$POSTGRES_DB@$POSTGRES_HOST сохраняем в $BACKUP_NAME"
# Делаем удаленный бэкап
PGPASSWORD=$DB_PASSWORD pg_dump \
  -h $POSTGRES_HOST \
  -p $POSTGRES_PORT \
  -U $POSTGRES_USER \
  -d $POSTGRES_DB \
  -F c \
  -Z 9 \
  -v \
  -f $BACKUP_NAME >> $LOG_FILE 2>&1

# Проверяем успешность
if [ $? -eq 0 ]; then
    echo "Бэкап успешно создан: $BACKUP_NAME"
else
    echo "Ошибка при создании бэкапа!"
    exit 1
fi

#find $BACKUP_DIR -name "*.dump" -mtime +30 -delete
#find $BACKUP_DIR -name "*.log" -mtime +30 -delete