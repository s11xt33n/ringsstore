#!/bin/bash
# Скрипт развертывания для filadelvof.russianode.ru

set -e

DOMAIN="filadelvof.russianode.ru"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="ringshop"
SERVICE_NAME="ringshop"
USER="www-data"

echo "🚀 Развертывание Ring Shop на $DOMAIN"
echo "===================================="

# Проверка прав root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Запустите скрипт с правами root (sudo ./deploy.sh)"
    exit 1
fi

cd "$PROJECT_DIR"

# 1. Обновление системы
echo ""
echo "📦 Обновление системы..."
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv python3-full nginx certbot python3-certbot-nginx

# 2. Создание виртуального окружения
echo ""
echo "🐍 Создание виртуального окружения..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# 3. Активация и установка зависимостей
echo ""
echo "📥 Установка зависимостей..."
# Убеждаемся что venv правильно создан
if [ ! -f "venv/bin/pip" ]; then
    echo "Пересоздаю venv..."
    rm -rf venv
    python3 -m venv venv
fi
venv/bin/pip install --upgrade pip -q
venv/bin/pip install -r requirements.txt -q

# 4. Генерация SECRET_KEY если нет .env
echo ""
echo "🔑 Настройка переменных окружения..."
if [ ! -f ".env" ]; then
    SECRET_KEY=$(venv/bin/python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    cat > .env << EOF
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=filadelvof.russianode.ru,138.124.74.169,localhost,127.0.0.1
SECURE_SSL_REDIRECT=True
EOF
    echo "✅ Создан файл .env"
else
    echo "✅ Файл .env уже существует"
    # Обновляем ALLOWED_HOSTS в .env если нужно
    if ! grep -q "filadelvof.russianode.ru" .env; then
        sed -i 's/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=filadelvof.russianode.ru,138.124.74.169,localhost,127.0.0.1/' .env || true
    fi
fi

# 5. Применение миграций
echo ""
echo "🗄️  Применение миграций БД..."
venv/bin/python manage.py migrate --noinput

# 6. Сбор статических файлов
echo ""
echo "📁 Сбор статических файлов..."
venv/bin/python manage.py collectstatic --noinput --clear

# 7. Создание директорий для логов
echo ""
echo "📝 Создание директорий для логов..."
mkdir -p /var/log/$SERVICE_NAME
chown -R $USER:$USER /var/log/$SERVICE_NAME

# 8. Настройка прав доступа
echo ""
echo "🔐 Настройка прав доступа..."
chown -R $USER:$USER "$PROJECT_DIR"
chmod -R 755 "$PROJECT_DIR"
chmod 600 .env 2>/dev/null || true

# 9. Создание systemd service
echo ""
echo "⚙️  Создание systemd сервиса..."
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Ring Shop Gunicorn daemon
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn \\
    --access-logfile /var/log/$SERVICE_NAME/access.log \\
    --error-logfile /var/log/$SERVICE_NAME/error.log \\
    --workers 3 \\
    --bind 127.0.0.1:8001 \\
    --timeout 120 \\
    ringshop.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# 10. Настройка Nginx
echo ""
echo "🌐 Настройка Nginx..."
cat > /etc/nginx/sites-available/$SERVICE_NAME << EOF
server {
    listen 80;
    server_name $DOMAIN;

    # Редирект на HTTPS (будет настроен после получения сертификата)
    # return 301 https://\$server_name\$request_uri;

    # Временно без HTTPS для первоначальной настройки
    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
    }

    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

    client_max_body_size 20M;
}
EOF

# Активация сайта в Nginx
if [ -f "/etc/nginx/sites-enabled/$SERVICE_NAME" ]; then
    rm /etc/nginx/sites-enabled/$SERVICE_NAME
fi
ln -sf /etc/nginx/sites-available/$SERVICE_NAME /etc/nginx/sites-enabled/

# Проверка конфигурации Nginx
nginx -t

# 11. Перезагрузка systemd и запуск сервисов
echo ""
echo "🔄 Запуск сервисов..."
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME
systemctl restart nginx

# 12. Получение SSL сертификата
echo ""
echo "🔒 Настройка SSL сертификата..."
echo "Попытка получить SSL сертификат от Let's Encrypt..."
if certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN --redirect 2>/dev/null; then
    echo "✅ SSL сертификат успешно установлен!"
    systemctl restart nginx
else
    echo "⚠️  Не удалось получить SSL сертификат автоматически."
    echo "   Убедитесь, что домен $DOMAIN указывает на IP 138.124.74.169"
    echo "   Затем выполните вручную: certbot --nginx -d $DOMAIN"
fi

# 13. Проверка статуса
echo ""
echo "✅ Развертывание завершено!"
echo ""
echo "📊 Статус сервисов:"
systemctl status $SERVICE_NAME --no-pager -l || true
echo ""
echo "🌐 Сайт должен быть доступен по адресу: http://$DOMAIN"
echo ""
echo "📝 Полезные команды:"
echo "   Статус сервиса: systemctl status $SERVICE_NAME"
echo "   Логи: journalctl -u $SERVICE_NAME -f"
echo "   Перезапуск: systemctl restart $SERVICE_NAME"
echo "   Создать админа: cd $PROJECT_DIR && source venv/bin/activate && python manage.py createsuperuser"
echo ""
