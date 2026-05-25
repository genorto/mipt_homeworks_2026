# GigaVibeMiptCode

*Консольный ИИ-ассистент*

### Функционал

- Отправка запросов к LLM через консоль. Модель умеет хранить контекст.
- `@::filepath::` - Встраивание содержимого файла в запрос. Аналог прикрепления файла.
- `/filechunk` - Интерактивный почанковый режим обработки файла. Доступные параметры: `paragraph=` количество параграфов, `length=` длина параграфов, `-y` моментальная обработка без подтверждения пользователя.
- `/reset` - Очистка истории.
- `\q` - Выход.

### Настройка ассистента

1. Клонирование репозитория
```bash
git clone https://github.com/genorto/mipt_homeworks_2026.git
cd mipt_homeworks_2026/final_project
```

2. Установка зависимостей
```bash
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

3. Запуск ИИ-ассистента
```bash
python3 main.py
```

### Переменные окружения

Поддерживается как файл конфигурации `config.yaml`, так и переменные окружения (они приоритетнее).

`config.yaml` в корне проекта должен иметь вид:
```yaml
api_host: http://localhost:11434/v1/
api_key: ollama
limit_message: 100
limit_chars: 2000
model: gemma3:270m
temperature: 0.7
system_prompt: You are an assistant for the Python backend development tasks.
```

Переменные окружения должны иметь вид:
```bash
export API_HOST=http://localhost:11434/v1/
export API_KEY=ollama
export LIMIT_MESSAGE=100
export LIMIT_CHARS=2000
export MODEL=gemma3:270m
export TEMPERATURE=0.7
```

`limit_message` и `limit_chars` являются необязательными параметрами. Значение `temperature` принимает значения от 0 (более детерменированная) до 1 (более креативная). По умолчанию `temperature=0.5`.
