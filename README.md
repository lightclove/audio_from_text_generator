# AudioFromTextGenerator

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![gTTS](https://img.shields.io/badge/gTTS-v2.2.3-green.svg)](https://pypi.org/project/gTTS/)
[![.env configuration](https://img.shields.io/badge/.env%20Config-Declarative-yellow.svg)](https://pypi.org/project/python-dotenv/)

**Минималистичный и простой Python-скрипт для генерации аудио из текста с использованием Google Text-to-Speech (gTTS).**

## 📖 Описание

Этот скрипт предназначен для преобразования текстовых файлов в аудиоформаты, такие как `ogg`, используя мощную библиотеку **gTTS** (Google Text-to-Speech). Он идеально подходит для создания:

*   **Аудиокниг**: Озвучивайте ваши любимые книги или учебные материалы для прослушивания в дороге или во время занятий.
*   **Голосовых заметок**: Преобразуйте текстовые заметки в аудио для удобного прослушивания.
*   **Мультимедийного контента**: Интегрируйте озвученный текст в ваши видеопроекты или презентации.

Скрипт отличается своей **декларативной конфигурацией** через файл `.env` и **исключительной простотой использования**.  Вам не нужно углубляться в код, чтобы изменить параметры аудио или выходные форматы.

## ✨ Ключевые особенности

*   **Декларативный подход:** Настройка скрипта полностью осуществляется через файл `.env`. Это делает конфигурацию интуитивно понятной и легко изменяемой без редактирования кода.
*   **Минимализм и простота:** Скрипт написан с акцентом на читаемость и простоту. Вы сможете быстро понять его логику и при необходимости адаптировать под свои нужды.
*   **Мощность gTTS:** Использует библиотеку [gTTS](https://gtts.readthedocs.io/en/latest/) для высококачественного преобразования текста в речь, предоставляя доступ к широкому выбору языков и голосов, поддерживаемых Google Text-to-Speech API.
*   **Гибкая настройка аудио:**  Вы можете контролировать различные параметры аудио, такие как кодек, битрейт, частота дискретизации и количество каналов, через файл `.env`.
*   **Ограничение длительности:** Возможность задать желаемую длительность аудиозаписи в секундах. Если длительность не указана (или равна 0), аудио будет сгенерировано на всю длину входного текста.
*   **Прогресс-бар (опционально):**  Отображение прогресса обработки аудио через FFmpeg (можно включить/выключить в `.env`).
*   **Перезапись выходного файла (опционально):**  Возможность автоматической перезаписи выходного файла, если он уже существует (управляется через `.env`).
*   **Логирование:** Подробное логирование процесса работы скрипта для отслеживания и отладки (можно включить/выключить в `.env`).

## ⚙️ Настройка и использование

### Предварительные требования

1.  **Python 3.7+** ([https://www.python.org/downloads/](https://www.python.org/downloads/))
2.  **FFmpeg** ([https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)) - должен быть установлен и добавлен в системную переменную `PATH`.
3.  **Python-библиотеки:**

    ```bash
    pip install python-dotenv gTTS
    ```

### Конфигурация через `.env`

Создайте файл `.env` в той же директории, что и скрипт `audio_from_text_generator.py`, и заполните его следующими переменными:

```ini
# .env

# **Настройки ввода/вывода**
INPUT_FILE = "input.txt"          # Путь к текстовому файлу для озвучивания
OUTPUT_FILE = "output.ogg"        # Путь для сохранения выходного аудиофайла
TEMP_FILE = "temp.mp3"           # Временный файл для хранения сгенерированного gTTS mp3 (не меняйте без необходимости)

# **Настройки аудио**
AUDIO_CODEC = "libopus"         # Аудио кодек FFmpeg (например, libopus, libmp3lame, aac)
AUDIO_CHANNELS = "1"             # Количество аудио каналов (1 - моно, 2 - стерео)
SAMPLE_RATE = "48000"           # Частота дискретизации аудио (Гц)
BITRATE = "164k"              # Битрейт аудио (например, 128k, 192k, 256k)

# **Настройки выполнения**
DURATION = 0                    # Длительность аудио в секундах. 0 - для обработки полной длины TTS аудио, или задайте длительность в секундах (целое число).
LANGUAGE = "ru"                 # Язык озвучивания (код языка ISO 639-1, например, ru, en, de, es, fr)
VERBOSE = "true"                # Включить подробное логирование (true/false)
SHOW_PROGRESS = "true"          # Показывать прогресс-бар обработки FFmpeg (true/false)
OVERWRITE_OUTPUT = "true"       # Перезаписывать выходной файл, если он существует (true/false)
```
### Описание параметров:

    INPUT_FILE: Путь к текстовому файлу, который вы хотите озвучить.
    OUTPUT_FILE: Путь и имя файла для сохранения сгенерированного аудио. Поддерживаемые форматы зависят от установленного кодека FFmpeg (ogg, mp3, aac, и другие).
    TEMP_FILE: Временный файл, используемый для сохранения промежуточного mp3-аудио, сгенерированного gTTS. Обычно не требует изменения.
    AUDIO_CODEC: Аудиокодек, используемый FFmpeg для кодирования выходного аудио. libopus - отличный выбор для ogg, libmp3lame - для mp3, aac - для m4a/aac.
    AUDIO_CHANNELS: Количество аудиоканалов: 1 для моно, 2 для стерео.
    SAMPLE_RATE: Частота дискретизации аудио. 48000 Гц - распространенный стандарт для высокого качества.
    BITRATE: Битрейт аудио. Влияет на качество и размер файла. 164k - хорошее значение для libopus.
    DURATION: Длительность генерируемого аудио в секундах.
        0: Аудио будет сгенерировано на всю длину входного текста.
        > 0: Аудио будет ограничено указанной длительностью в секундах.
    LANGUAGE: Язык, на котором будет озвучен текст. Используйте коды языков ISO 639-1 (например, "ru" для русского, "en" для английского, "de" для немецкого и т.д.). Полный список языков, поддерживаемых gTTS, можно найти в документации gTTS.
    VERBOSE: Включает/выключает подробное логирование процесса выполнения скрипта в консоль. Полезно для отслеживания ошибок и понимания хода работы. true - включить, false - выключить.
    SHOW_PROGRESS: Включает/выключает отображение прогресс-бара во время обработки аудио с помощью FFmpeg. true - включить, false - выключить. Прогресс-бар отображается только если задана DURATION > 0.
    OVERWRITE_OUTPUT: Определяет, следует ли перезаписывать выходной файл, если файл с таким именем уже существует. true - перезаписывать, false - не перезаписывать (скрипт завершится с ошибкой, если файл существует).


После завершения работы скрипта, ваш аудиофайл будет сохранен по пути, указанному в OUTPUT_FILE в файле .env.

При выполенении скрипта, вы можете столкнуться с критической ошибкой при попытке использовать API Text-to-Speech (TTS) -  Ошибка 429 (Too Many Requests). Она означает, что API TTS отклонил ваш запрос, потому что вы отправили слишком много запросов за короткий промежуток времени.

Что означает ошибка 429 (Too Many Requests)?

Ошибка 429 Too Many Requests - это стандартный HTTP код ответа, который сервер (в данном случае, TTS API) возвращает, когда клиент (ваш скрипт) отправляет слишком много запросов за определенный период. Это механизм контроля нагрузки и защиты от злоупотреблений, применяемый API-провайдерами.  API устанавливает лимиты на количество запросов, которые можно отправить за минуту, секунду, день и т.д.  
Когда эти лимиты превышаются, API начинает возвращать ошибку 429, чтобы временно заблокировать дальнейшие запросы от данного клиента и предотвратить перегрузку сервиса.

Вероятные причины ошибки 429 в вашем случае (gTTS):

В вашем случае используется библиотека gTTS (Google Text-to-Speech).  Важно понимать, что gTTS – это неофициальная библиотека, которая  использует неофициальный (недокументированный и неподдерживаемый Google) API для синтеза речи.  Из-за этого  ее надежность может быть нестабильной, а ошибки 429 - частым явлением, даже при не очень интенсивном использовании.

Основные вероятные причины ошибки 429 при использовании gTTS:

Превышение неявных лимитов gTTS API:  Несмотря на то, что Google официально не документирует API, который использует gTTS, у него есть неявные лимиты на количество запросов.  Даже умеренное использование gTTS (особенно в короткий промежуток времени) может привести к превышению этих лимитов и ошибке 429.  Фраза "Probable cause: Unknown" в вашем выводе как раз может намекать на то, что gTTS не может точно определить причину лимита, так как API неофициальный.

Слишком частые запросы в скрипте:  Если ваш скрипт генерирует аудио в цикле или обрабатывает много текста подряд без пауз, вы можете легко превысить даже самые либеральные неявные лимиты gTTS.

Проблемы с сетью (менее вероятно в случае 429):  Хотя ошибка 429 прямо указывает на "Too Many Requests", временные проблемы с сетевым соединением (хотя и маловероятно)  теоретически могут иногда привести к некорректной интерпретации ответов от сервера.  Однако, для 429 - это маловероятная причина.

Решения и способы устранения ошибки 429 (Too Many Requests) при использовании gTTS:
К сожалению, поскольку gTTS использует неофициальный API, надежного и гарантированного решения для постоянного устранения ошибки 429 не существует. Возможно стоит не так часто запускать скрипт и полностью воздержаться от ЕГО ЗАПУСКА В НЕСКОЛЬКИХ ЭКЗЕМЛЯРАХ. Меня забанили, когда я запустил сразу два экзепляра(процесса) скрипта почти одновременно с небольшой разницей. Стоит это учитывать, чтобы не попасть в бан.   
Однако, вы можете попробовать следующие подходы, чтобы снизить вероятность возникновения ошибки или обойти ее в определенных ситуациях:
