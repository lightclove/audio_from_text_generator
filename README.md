# Audio from text generator

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![gTTS](https://img.shields.io/badge/gTTS-v2.2.3-green.svg)](https://pypi.org/project/gTTS/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-important)](https://ffmpeg.org/)
[![.env configuration](https://img.shields.io/badge/.env%20Config-Declarative-yellow.svg)](https://pypi.org/project/python-dotenv/)

**Мощный Python-скрипт для генерации аудио из текста с использованием Google Text-to-Speech (gTTS) и обработкой больших файлов**

## 📖 Описание

Этот скрипт преобразует текстовые файлы любого размера в аудиоформаты (OGG, MP3 и др.) с использованием **gTTS** и **FFmpeg**. Особенности:

* Обработка текстов до 1.5+ млн символов
* Автоматическое разбиение на части с сохранением целостности предложений
* Защита от блокировок Google (ошибка 429)
* Экспоненциальные повторы при сбоях
* Поддержка длительных операций (часы)

Идеален для создания:
- Аудиокниг и учебных материалов
- Голосовых заметок и подкастов
- Озвучки видеоконтента

## ✨ Ключевые особенности

* **Работа с большими файлами** - автоматическое разбиение текста на части
* **Устойчивость к ошибкам** - повторы с задержкой при блокировках
* **Интеллектуальное разделение** - сохранение структуры текста
* **Экспоненциальные паузы** - автоматическое увеличение задержки при ошибках
* **Детальное логирование** - цветная маркировка и уровни важности
* **Нормализация звука** - автоматическая оптимизация громкости
* **Прогресс-бар** - визуализация процесса конвертации
* **Кроссплатформенность** - работает на Windows, Linux, macOS

## ⚙️ Настройка и использование

### Предварительные требования

1. **Python 3.7+** ([официальный сайт](https://www.python.org/downloads/))
2. **FFmpeg** ([скачать](https://ffmpeg.org/download.html)) - добавьте в PATH
3. **Библиотеки Python**:
```bash
pip install python-dotenv gTTS
```
### Конфигурация (.env)
```
# Настройки ввода/вывода
INPUT_FILE = "input.txt"
OUTPUT_FILE = "output.ogg"
TEMP_FILE = "temp_combined.mp3"
TEMP_DIR = "tts_temp"

# Обработка текста
CHUNK_SIZE = 3500          # Символов в части (500-5000)
DELAY_BETWEEN_CHUNKS = 20  # Пауза между частями (сек)

# Настройки аудио
AUDIO_CODEC = "libopus"    # libopus, libmp3lame, aac
AUDIO_CHANNELS = "1"       # 1 (моно) или 2 (стерео)
BITRATE = "164k"           # 64k-320k
SAMPLE_RATE = "48000"      # Частота дискретизации
LANGUAGE = "ru"            # Язык озвучки (код ISO 639-1)

# Повторы при ошибках
MAX_RETRIES = 5            # Попыток генерации части
RETRY_DELAY = 15           # Базовая пауза (сек)
BACKOFF_FACTOR = 3         # Множитель задержки

# Системные
VERBOSE = "true"           # Подробное логирование
OVERWRITE_OUTPUT = "true"  # Перезапись файлов
```
### Запуск
```
python audio_from_text_generator_gtts.py
```
### 🛠 Обработка ошибки 429
Причины:
- Превышение лимитов Google TTS API

- Частые запросы без задержек

- Параллельные запуски скрипта

### Решения проблемы ошибки 429 в скрипте:
- Автоматические повторы - до 5 попыток на чанк

- Экспоненциальные паузы - задержка растет по формуле:
```
задержка = RETRY_DELAY * (BACKOFF_FACTOR ^ попытка)
```
- Изоляция частей - сбой одной части не останавливает процесс

### Рекомендации:
- Увеличьте DELAY_BETWEEN_CHUNKS до 30-60

- Уменьшите CHUNK_SIZE до 2000-3000

- Не запускайте параллельные процессы

- Используйте стабильное интернет-соединение

📄 Логирование примера выполнения:
```
[2024-02-20 14:35:12] INFO - 🚀 СТАРТ ПРОЦЕССА КОНВЕРТАЦИИ
[2024-02-20 14:35:12] INFO - Прочитано 423,189 символов
[2024-02-20 14:35:13] INFO - Текст разбит на 121 частей
[2024-02-20 14:35:18] WARN - Ошибка 429. Повтор через 15 сек...
[2024-02-20 14:35:33] INFO - Успешная генерация части 1/121
[2024-02-20 15:12:47] INFO - ✅ УСПЕШНОЕ ЗАВЕРШЕНИЕ (37m 35s)
```
📌 Важно
Google TTS - неофициальный API, возможны нестабильности

Для коммерческого использования рассмотрите официальные API

Всегда проверяйте сгенерированные файлы! Проверяйте вероятные утечки памяти, ресурсы пространства жесткого диска, особенно в директории со скриптом, проверьте нет ли процессов поедающих RAM и disk space (Дисклеймер)!!
### .env файл:
```
# Настройки ввода/вывода
INPUT_FILE = "input.txt"
OUTPUT_FILE = "output.ogg"
TEMP_FILE = "temp_combined.mp3"
TEMP_DIR = "tts_temp"

# Обработка текста
CHUNK_SIZE = 3500
DELAY_BETWEEN_CHUNKS = 20
MAX_FILENAME_LENGTH = 100

# Настройки аудио
AUDIO_CODEC = "libopus"
AUDIO_CHANNELS = "1"
BITRATE = "164k"
SAMPLE_RATE = "48000"
LANGUAGE = "ru"

# Повторы при ошибках
MAX_RETRIES = 5
RETRY_DELAY = 15
BACKOFF_FACTOR = 3

# Системные
VERBOSE = "true"
OVERWRITE_OUTPUT = "true"
```
