# .env
# INPUT_FILE = "input2.txt"
# OUTPUT_FILE = "output.ogg"
# DURATION = 0
# LANGUAGE = "ru"
# TEMP_FILE = "temp.mp3"
# AUDIO_CODEC = "libopus"
# AUDIO_CHANNELS = "1"
# SAMPLE_RATE = "48000"
# BITRATE = "164k"
# VERBOSE = "true"
# SHOW_PROGRESS = "true"
# OVERWRITE_OUTPUT = "true"

from datetime import datetime
from dotenv import load_dotenv
from gtts import gTTS
import subprocess
import os
import sys

load_dotenv()

# Конфигурация
CONFIG = {
    # IO settings
    'input': os.getenv('INPUT_FILE'),
    'output': os.getenv('OUTPUT_FILE'),
    'temp_file': os.getenv('TEMP_FILE'),

    # Audio params
    'codec': os.getenv('AUDIO_CODEC'),
    'channels': os.getenv('AUDIO_CHANNELS'),
    'bitrate': os.getenv('BITRATE'),
    'sample_rate': os.getenv('SAMPLE_RATE'),

    # Runtime settings
    'duration': int(os.getenv('DURATION')),
    'language': os.getenv('LANGUAGE'),
    'verbose': os.getenv('VERBOSE').lower() == 'true',
    'show_progress': os.getenv('SHOW_PROGRESS').lower() == 'true',
    'overwrite': os.getenv('OVERWRITE_OUTPUT').lower() == 'true'
}


def log(message: str):
    if CONFIG['verbose']:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}", flush=True)


def parse_time(time_str: str) -> float:
    """Конвертирует время из формата FFmpeg в секунды"""
    try:
        hours, mins, secs = map(float, time_str.split(':'))
        return hours * 3600 + mins * 60 + secs
    except:
        return 0


def print_progress(current: float, total: float):
    """Отображает прогресс-бар с процентами"""
    percent = min(100, max(0, (current / total) * 100))
    bar_length = 40
    filled = int(bar_length * percent // 100)
    bar = '█' * filled + '-' * (bar_length - filled)
    sys.stdout.write(f"\r[{bar}] {percent:.1f}% ")
    sys.stdout.flush()


def main():
    start_script = datetime.now()

    try:
        log("🚀 Запуск скрипта генерации аудио")

        # Чтение входного файла
        log(f"📖 Чтение файла: {CONFIG['input']}")
        with open(CONFIG['input'], 'r', encoding='utf-8') as f:
            text = f.read().strip()
            if not text:
                raise ValueError("❌ Входной файл пуст")
        log(f"✔ Прочитано {len(text)} символов")

        # Генерация TTS
        log("🔊 Генерация аудио с помощью gTTS...")
        tts_start = datetime.now()
        gTTS(text=text, lang=CONFIG['language']).save(CONFIG['temp_file'])
        log(f"✔ Аудио сгенерировано за {datetime.now() - tts_start}")

        # Сборка команды FFmpeg
        cmd = [
            'ffmpeg',
            '-y' if CONFIG['overwrite'] else '-n',
            '-loglevel', 'error',
        ]
        if CONFIG['duration'] > 0: # Добавляем stream_loop только если duration > 0
            cmd.extend(['-stream_loop', '-1'])
        cmd.extend([ # Добавляем остальную часть команды
            '-i', CONFIG['temp_file'],
            '-c:a', CONFIG['codec'],
            '-ar', CONFIG['sample_rate'],
            '-ac', CONFIG['channels'],
            '-b:a', CONFIG['bitrate'],
        ])
        if CONFIG['duration'] > 0: # Добавляем -t только если duration > 0
            cmd.extend(['-t', str(CONFIG['duration'])])
        cmd.append(CONFIG['output'])

        if CONFIG['show_progress']:
            cmd[1:1] = ['-progress', 'pipe:1']

        # Обработка аудио
        log("⚙ Начало обработки аудио...")
        process = subprocess.Popen(
            cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE, # Изменено на PIPE для stdout
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        if CONFIG['show_progress']:
            if CONFIG['duration'] > 0: # Добавляем проверку на duration > 0
                print("\nПрогресс обработки:")
                while True:
                    line = process.stdout.readline() # Изменено на stdout
                    if not line:
                        break
                    if 'out_time=' in line:
                        current_time = parse_time(line.split('=')[1].strip())
                        print_progress(current_time, CONFIG['duration'])
            else: # Если duration == 0, просто выводим сообщение, что обработка идет
                print("\nОбработка аудио в процессе (прогресс не отображается для duration=0)...")
                while True:
                    line = process.stdout.readline() # Изменено на stdout
                    if not line:
                        break

        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd)

        print()  # Новая строка после прогресс-бара
        log(f"✅ Обработка завершена за {datetime.now() - start_script}")
        log(f"💾 Файл сохранен как: {CONFIG['output']}")

    except Exception as e:
        print(f"\n❌ Критическая ошибка: {str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        if os.path.exists(CONFIG['temp_file']):
            log("🧹 Очистка временных файлов")
            os.remove(CONFIG['temp_file'])
        log("🛑 Скрипт завершил работу")


if __name__ == "__main__":
    main()