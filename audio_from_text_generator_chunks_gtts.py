"""
Модуль для конвертации больших текстовых файлов в аудиоформат с использованием Google TTS
Версия 3.1 (с защитой от перегрузок и детальным логированием)
"""

from datetime import datetime
from dotenv import load_dotenv
from gtts import gTTS
import subprocess
import os
import sys
import time
import shutil
import hashlib

# Загрузка переменных окружения
load_dotenv()

# Конфигурация приложения
CONFIG = {
    # Настройки ввода-вывода
    "input": os.getenv("INPUT_FILE", "input.txt"),
    "output": os.getenv("OUTPUT_FILE", "output.ogg"),
    "temp_file": os.getenv("TEMP_FILE", "temp_combined.mp3"),
    "temp_dir": os.getenv("TEMP_DIR", "tts_chunks"),
    # Параметры обработки текста
    "chunk_size": max(500, int(os.getenv("CHUNK_SIZE", 3500))),  # Минимум 500 символов
    "delay_between_chunks": max(5, int(os.getenv("DELAY_BETWEEN_CHUNKS", 20))),
    "max_filename_length": min(255, int(os.getenv("MAX_FILENAME_LENGTH", 100))),
    # Настройки аудио
    "codec": os.getenv("AUDIO_CODEC", "libopus"),
    "channels": os.getenv("AUDIO_CHANNELS", "1"),
    "bitrate": os.getenv("BITRATE", "164k"),
    "sample_rate": os.getenv("SAMPLE_RATE", "48000"),
    "language": os.getenv("LANGUAGE", "ru"),
    # Параметры повторных попыток
    "max_retries": max(1, int(os.getenv("MAX_RETRIES", 5))),
    "retry_delay": max(1, int(os.getenv("RETRY_DELAY", 15))),
    "backoff_factor": max(1, int(os.getenv("BACKOFF_FACTOR", 3))),
    # Настройки выполнения
    "duration": max(0, int(os.getenv("DURATION", 0))),
    "verbose": os.getenv("VERBOSE", "true").lower() == "true",
    "overwrite": os.getenv("OVERWRITE_OUTPUT", "true").lower() == "true",
}


def log(message: str, level: str = "INFO"):
    """Расширенная система логирования с уровнями важности"""
    if CONFIG["verbose"] or level in ("ERROR", "WARN"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        colored_level = {
            "INFO": "\033[94mINFO\033[0m",  # Синий
            "WARN": "\033[93mWARN\033[0m",  # Желтый
            "ERROR": "\033[91mERROR\033[0m",  # Красный
            "DEBUG": "\033[90mDEBUG\033[0m",  # Серый
        }.get(level, level)
        print(f"[{timestamp}] {colored_level} - {message}", flush=True)


def split_text(text: str, chunk_size: int) -> list:
    """
    Умное разбиение текста на части с сохранением целостности структуры
    Алгоритм:
    1. Ищет последний подходящий разделитель в пределах chunk_size
    2. Если разделители не найдены - делает принудительный разрыв
    3. Объединяет слишком маленькие чанки
    """
    chunks = []
    start = 0
    text_length = len(text)
    separators = ["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " "]

    log(f"Начало разбиения текста (общий размер: {text_length} символов)", "DEBUG")

    while start < text_length:
        end = min(start + chunk_size, text_length)

        # Поиск оптимальной точки разрыва
        if end < text_length:
            best_pos = -1
            for sep in separators:
                pos = text.rfind(sep, start, end + len(sep))
                if pos > best_pos:
                    best_pos = pos

            if best_pos != -1 and (best_pos - start) > chunk_size * 0.5:
                end = best_pos + 1  # Включаем разделитель в текущий чанк

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
            log(f"Создан чанк [{len(chunks)}] размером {len(chunk)} символов", "DEBUG")

        start = end

    # Оптимизация: объединение маленьких чанков
    if len(chunks) > 1:
        merged = []
        buffer = chunks[0]
        for chunk in chunks[1:]:
            if len(buffer) + len(chunk) <= chunk_size * 1.2:
                buffer += " " + chunk
                log(f"Объединение чанков [{len(merged) + 1}]", "DEBUG")
            else:
                merged.append(buffer)
                buffer = chunk
        merged.append(buffer)
        log(f"Оптимизация чанков: {len(chunks)} → {len(merged)}", "DEBUG")
        return merged

    return chunks


def generate_tts(text: str, output_file: str) -> bool:
    """
    Генерация аудиофайла через Google TTS с экспоненциальной задержкой при ошибках
    Возвращает:
        True - успешная генерация
        False - неудача после всех попыток
    """
    log(f"Инициализация генерации TTS для файла {output_file}", "DEBUG")

    for attempt in range(CONFIG["max_retries"] + 1):
        try:
            tts = gTTS(
                text=text,
                lang=CONFIG["language"],
                lang_check=False,  # Отключаем проверку для нестандартных текстов
                slow=False,
                timeout=30,  # Максимальное время ожидания ответа
            )
            tts.save(output_file)
            log(f"Успешная генерация {output_file} (попытка {attempt + 1})", "DEBUG")
            return True
        except Exception as e:
            error_msg = str(e).lower()

            # Обработка ошибки перегрузки сервера
            if "429" in error_msg or "too many requests" in error_msg:
                delay = CONFIG["retry_delay"] * (CONFIG["backoff_factor"] ** attempt)
                log(
                    f"Ошибка 429: Превышен лимит запросов. Попытка {attempt + 1}/{CONFIG['max_retries']} через {delay} сек",
                    "WARN",
                )
                time.sleep(delay)

            # Обработка сетевых ошибок
            elif "timed out" in error_msg:
                log(
                    f"Таймаут подключения. Попытка {attempt + 1}/{CONFIG['max_retries']}",
                    "WARN",
                )
                time.sleep(10)

            else:
                log(
                    f"Критическая ошибка генерации: {type(e).__name__} - {str(e)}",
                    "ERROR",
                )
                return False

    log(f"Достигнут максимум попыток для {output_file}", "ERROR")
    return False


def ffmpeg_process():
    """
    Обработка аудио через FFmpeg с контролем качества и формата
    Этапы:
    1. Конвертация в конечный формат
    2. Нормализация звука
    3. Применение параметров качества
    """
    log("Инициализация обработки FFmpeg", "DEBUG")

    try:
        cmd = [
            "ffmpeg",
            "-y" if CONFIG["overwrite"] else "-n",
            "-loglevel",
            "error",
            "-i",
            CONFIG["temp_file"],
            "-c:a",
            CONFIG["codec"],
            "-ar",
            CONFIG["sample_rate"],
            "-ac",
            CONFIG["channels"],
            "-b:a",
            CONFIG["bitrate"],
            "-af",
            "loudnorm=I=-16:LRA=11:TP=-1.5",  # Нормализация звука
            "-hide_banner",
        ]

        if CONFIG["duration"] > 0:
            cmd.extend(["-t", str(CONFIG["duration"])])

        cmd.append(CONFIG["output"])

        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        log(f"FFmpeg завершен с кодом {result.returncode}", "DEBUG")

    except subprocess.CalledProcessError as e:
        log(f"Ошибка FFmpeg (код {e.returncode}): {e.stderr}", "ERROR")
        raise


def main():
    """Основной процесс конвертации"""
    start_time = datetime.now()
    temp_files = []
    success_count = 0
    concat_list = None

    try:
        log("=" * 60)
        log(f"🚀 СТАРТ ПРОЦЕССА КОНВЕРТАЦИИ")
        log(f"Входной файл: {os.path.abspath(CONFIG['input'])}")
        log(f"Целевой файл: {os.path.abspath(CONFIG['output'])}")
        log("=" * 60)

        # Проверка входных данных
        if not os.path.exists(CONFIG["input"]):
            raise FileNotFoundError(f"Файл {CONFIG['input']} не найден")

        if os.path.getsize(CONFIG["input"]) == 0:
            raise ValueError("Входной файл пуст")

        # Чтение текста
        with open(CONFIG["input"], "r", encoding="utf-8") as f:
            text = f.read().strip()

        log(f"Прочитано {len(text):,} символов", "INFO")

        # Подготовка временного хранилища
        os.makedirs(CONFIG["temp_dir"], exist_ok=True)
        log(f"Временная директория: {os.path.abspath(CONFIG['temp_dir'])}", "DEBUG")

        # Разбиение текста
        chunks = split_text(text, CONFIG["chunk_size"])
        log(f"Получено {len(chunks)} частей для обработки", "INFO")

        # Обработка чанков
        for idx, chunk in enumerate(chunks):
            chunk_hash = hashlib.md5(chunk.encode()).hexdigest()[:8]
            temp_file = os.path.join(
                CONFIG["temp_dir"], f"part_{idx + 1:04d}_{chunk_hash}.mp3"
            )

            log(f"[{idx + 1}/{len(chunks)}] Обработка чанка {temp_file}", "INFO")
            log(
                f"Содержимое чанка (первые 50 символов): {chunk[:50].replace('\n', ' ')}...",
                "DEBUG",
            )

            if generate_tts(chunk, temp_file):
                temp_files.append(temp_file)
                success_count += 1

                # Прогресс обработки
                progress = (idx + 1) / len(chunks) * 100
                log(
                    f"Прогресс: {progress:.1f}% | Обработано: {success_count}/{len(chunks)}",
                    "INFO",
                )

                # Задержка между запросами
                if idx < len(chunks) - 1:
                    delay = CONFIG["delay_between_chunks"]
                    log(f"Пауза {delay} сек перед следующим запросом...", "DEBUG")
                    time.sleep(delay)
            else:
                log(f"Пропуск чанка {idx + 1} из-за ошибок генерации", "WARN")

        # Проверка успешных генераций
        if success_count == 0:
            raise RuntimeError("Не удалось сгенерировать ни одного аудиофрагмента")

        # Создание списка для объединения
        concat_list = os.path.join(CONFIG["temp_dir"], "concat_list.txt")
        with open(concat_list, "w", encoding="utf-8") as f:
            for file in temp_files:
                f.write(f"file '{os.path.abspath(file)}'\n")

        log(f"Создан список объединения: {concat_list}", "DEBUG")

        # Объединение аудиофайлов
        log("Объединение аудиофрагментов...", "INFO")
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    concat_list,
                    "-c",
                    "copy",
                    "-loglevel",
                    "error",
                    CONFIG["temp_file"],
                ],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            log(f"Ошибка объединения: {e.stderr.decode()}", "ERROR")
            raise

        # Финализация аудио
        log("Финализация аудиофайла...", "INFO")
        ffmpeg_process()

        # Успешное завершение
        log("=" * 60)
        log(f"✅ УСПЕШНОЕ ЗАВЕРШЕНИЕ")
        log(f"Общее время: {datetime.now() - start_time}")
        log(f"Итоговый файл: {os.path.abspath(CONFIG['output'])}")
        log(
            f"Эффективность: {success_count}/{len(chunks)} чанков ({success_count / len(chunks) * 100:.1f}%)"
        )
        log("=" * 60)

    except Exception as e:
        log("=" * 60)
        log(f"💥 КРИТИЧЕСКАЯ ОШИБКА: {type(e).__name__}", "ERROR")
        log(f"Сообщение: {str(e)}", "ERROR")
        log("=" * 60)
        sys.exit(1)

    finally:
        # Очистка временных ресурсов
        def safe_remove(path):
            try:
                if path and os.path.exists(path):
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                        log(f"Удалена директория: {path}", "DEBUG")
                    else:
                        os.remove(path)
                        log(f"Удален файл: {path}", "DEBUG")
            except Exception as e:
                log(f"Ошибка очистки {path}: {str(e)}", "WARN")

        log("Очистка временных ресурсов...", "INFO")
        safe_remove(CONFIG["temp_dir"])
        safe_remove(CONFIG["temp_file"])
        if concat_list:
            safe_remove(concat_list)


if __name__ == "__main__":
    main()
