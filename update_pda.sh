#!/bin/bash

REPO_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_URL="https://raw.githubusercontent.com/M0nya-0d/PDA/main/vers.txt"
LOCAL_VER_FILE="$REPO_DIR/vers.txt"

echo "🔁 Проверка обновлений..."

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
    git -C "$REPO_DIR" pull origin main

    echo "🔄 Перезапуск обновлённого скрипта..."
    exec /bin/bash "$REPO_DIR/update_pda.sh"
else
    echo "✅ Уже последняя версия."

    # Запускаем основной скрипт, если нужно
    if [ -x "$REPO_DIR/run.sh" ]; then
        echo "🚀 Запуск run.sh..."
        "$REPO_DIR/run.sh"
    fi
fi