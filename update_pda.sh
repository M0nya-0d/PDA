#!/bin/bash
pkill -f stall.py          
sleep 3

REPO_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_URL="https://raw.githubusercontent.com/M0nya-0d/PDA/master/vers.txt"
LOCAL_VER_FILE="$REPO_DIR/vers.txt"

echo "🔁 Проверка обновлений..."

# Синхронизация времени
sudo timedatectl set-timezone Europe/Kiev
echo "⏰ Синхронизация времени..."
if command -v ntpdate >/dev/null 2>&1; then
    sudo ntpdate pool.ntp.org
else
    sudo timedatectl set-ntp true
    sleep 5
fi

# Проверка локальной версии
if [ ! -f "$LOCAL_VER_FILE" ]; then
    echo "❌ Локальный vers.txt не найден!"
    exit 1
fi

LOCAL_VERSION=$(cat "$LOCAL_VER_FILE")
REMOTE_VERSION=$(curl -s "$REPO_URL")

echo "🔍 Локальная версия: $LOCAL_VERSION"
echo "🌐 Версия в репозитории: $REMOTE_VERSION"

if [ "$LOCAL_VERSION" != "$REMOTE_VERSION" ]; then
    echo "⬇️ Обнаружено обновление, выполняется git pull..."
    git -C "$REPO_DIR" reset --hard HEAD
    git -C "$REPO_DIR" pull --no-rebase origin master

    chmod +x "/home/orangepi/PDA/update_pda.sh"
    chmod +x "$REPO_DIR/stall/flash_nextion.py"

    echo "🔄 Перезапуск обновлённого скрипта..."
    exec /bin/bash "$REPO_DIR/update_pda.sh"
else
    echo "✅ Уже последняя версия."

    
    echo "🚀 Запуск stall.py..."
    #exec python3 "$REPO_DIR/stall/stall.py"
    
fi
