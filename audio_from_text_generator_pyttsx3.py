'''
    Данный скрипт пока в стадии заморозки!
    Выходный голосовой файл генерируется, но качество ужасное.
    Следует разобраться с настройками pyttsx3 для обеспечения приемлемого качества звучания
'''
import pyttsx3
import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv
import sys

load_dotenv()

# --- Настройка конфигурации ---
CONFIG = {
    'input': os.getenv('INPUT_FILE', 'input2.txt'),
    'output': os.getenv('OUTPUT_FILE', 'output.ogg'),
    'verbose': os.getenv('VERBOSE', 'true').lower() == 'true',
    'show_progress': os.getenv('SHOW_PROGRESS', 'true').lower() == 'true',
    'overwrite': os.getenv('OVERWRITE_OUTPUT', 'true').lower() == 'true',
    'language': os.getenv('LANGUAGE', 'ru'), # Язык для pyttsx3
    'rate': int(os.getenv('RATE', 150)),       # Скорость речи pyttsx3
    'volume': float(os.getenv('VOLUME', 1.0)),   # Громкость pyttsx3
    'codec': os.getenv('AUDIO_CODEC', 'libopus'), # Аудио кодек ffmpeg
    'channels': os.getenv('AUDIO_CHANNELS', '1'), # Каналы ffmpeg
    'bitrate': os.getenv('BITRATE', '164k'),   # Битрейт ffmpeg
    'sample_rate': os.getenv('SAMPLE_RATE', '48000'), # Частота дискретизации ffmpeg
    'duration': int(os.getenv('DURATION', 0)),   # Длительность зацикливания (0 - не зацикливать)
}

def get_timestamp() -> str:
    """Возвращает текущее время в формате ЧЧ:ММ:СС."""
    return datetime.now().strftime("%H:%M:%S")

def log_message(message: str):
    """Выводит сообщение в лог, если включен verbose режим."""
    if CONFIG['verbose']:
        print(f"[{get_timestamp()}] {message}", flush=True)

def read_input_text(input_file: str) -> str:
    """Читает текст из входного файла."""
    log_message(f"📖 Чтение текста из файла: {input_file}")
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            text = file.read().strip()
    except FileNotFoundError:
        log_message(f"❌ Ошибка: Файл не найден: {input_file}")
        sys.exit(1)
    if not text:
        log_message(f"❌ Ошибка: Входной файл пуст: {input_file}")
        sys.exit(1)
    log_message(f"Прочитано символов: {len(text)}")
    return text

def initialize_tts_engine() -> pyttsx3.Engine:
    log_message("⚙️ Инициализация TTS движка")
    engine = pyttsx3.init()

    voices = engine.getProperty('voices')
    log_message("Доступные голоса:")
    for voice in voices:
        log_message(f" - Имя: {voice.name}")
        log_message(f"   ID: {voice.id}")
        log_message(f"   Язык(и): {voice.languages}")
        log_message(f"   Пол: {voice.gender}")
        log_message(f"   Возраст: {voice.age}")

    russian_voice_id = "Russian" # Явно указываем ID голоса "Russian"

    try: # Добавим try-except блок на случай, если голос не найдется
        engine.setProperty('voice', russian_voice_id)
        log_message(f"Голос установлен: {russian_voice_id}")
    except Exception as e:
        log_message(f"❌ Ошибка установки голоса '{russian_voice_id}': {e}")
        log_message("Используется голос по умолчанию.")

    return engine

def generate_speech_file(engine: pyttsx3.Engine, text: str, temp_file: str):
    """Генерирует речь из текста и сохраняет во временный файл."""
    log_message("🗣️ Генерация речи...")
    engine.save_to_file(text, temp_file)
    engine.runAndWait() # Ожидание завершения обработки речи
    log_message(f"🔊 Аудио сохранено во временный файл: {temp_file}")

def convert_audio_to_output_format(temp_file: str, output_file: str):
    """Конвертирует временный аудио файл в целевой формат, используя FFmpeg."""
    log_message("🔄 Конвертация аудио...")
    ffmpeg_command = [
        'ffmpeg',
        '-y' if CONFIG['overwrite'] else '-n', # Перезапись или пропуск, если файл существует
        '-loglevel', 'error', # Только ошибки в лог FFmpeg
        '-i', temp_file,      # Входной файл
        '-c:a', CONFIG['codec'],    # Аудио кодек
        '-ar', CONFIG['sample_rate'], # Частота дискретизации
        '-ac', CONFIG['channels'],   # Каналы
        '-b:a', CONFIG['bitrate'],   # Битрейт
    ]
    if CONFIG['duration'] > 0:
        ffmpeg_command.extend(['-stream_loop', '-1', '-t', str(CONFIG['duration'])]) # Зацикливание, если указана длительность
    ffmpeg_command.append(output_file) # Выходной файл

    try:
        subprocess.run(ffmpeg_command, check=True, capture_output=True)
        log_message(f"✅ Аудио успешно сконвертировано в: {output_file}")
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode('utf-8')
        log_message(f"❌ Ошибка FFmpeg: {error_message}")
        sys.exit(1)

def cleanup_temp_file(temp_file: str):
    """Удаляет временный файл."""
    if os.path.exists(temp_file):
        os.remove(temp_file)
        log_message(f"🧹 Временный файл удален: {temp_file}")

def process_text_to_speech():
    """Главная функция для обработки текста в речь."""
    log_message("🚀 Запуск скрипта")
    start_time = datetime.now()
    temp_file = "temp_audio.wav" # Временный файл для pyttsx3 (WAV формат)

    try:
        text_to_process = read_input_text(CONFIG['input'])
        tts_engine = initialize_tts_engine()
        generate_speech_file(tts_engine, text_to_process, temp_file)
        convert_audio_to_output_format(temp_file, CONFIG['output'])

        end_time = datetime.now()
        log_message(f"✅ Успешно завершено за {end_time - start_time}")
        log_message(f"💾 Аудиофайл сохранен: {CONFIG['output']}")

    except Exception as e:
        log_message(f"❌ Произошла ошибка: {e}")
        sys.exit(1)

    finally:
        cleanup_temp_file(temp_file)
        log_message("🛑 Завершение работы")


if __name__ == "__main__":
    process_text_to_speech()