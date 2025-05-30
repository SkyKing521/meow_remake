# Meow Voice Chat - User Guide

## English

### Table of Contents
1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Audio Settings](#audio-settings)
4. [Troubleshooting](#troubleshooting)

### Getting Started

#### System Requirements
- Windows 10 or later
- Python 3.7 or higher
- Working microphone and speakers/headphones
- Internet connection

#### Installation
1. Download and install Python from [python.org](https://python.org)
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Basic Usage

#### Starting the Application
1. Open a terminal/command prompt
2. Navigate to the application directory
3. Run the main application:
   ```bash
   python main.py
   ```

#### Audio Controls
- **Microphone**: The application will automatically detect and use your default microphone
- **Speakers**: Audio will play through your default audio output device
- **Volume Control**: Use your system's volume controls to adjust audio levels

### Audio Settings

#### Technical Specifications
- Audio Format: 16-bit PCM
- Sample Rate: 48kHz
- Channels: Stereo (2 channels)
- Buffer Size: 1024 samples

#### Adjusting Audio Quality
The application uses high-quality audio settings by default. These settings can be modified in the `audio_handler.py` file if needed.

### Troubleshooting

#### Common Issues
1. **No Sound**
   - Check if your microphone and speakers are properly connected
   - Verify that the correct audio devices are selected in your system settings
   - Ensure the application has permission to access your microphone

2. **Poor Audio Quality**
   - Check your internet connection
   - Ensure you're using a good quality microphone
   - Verify that your system's audio drivers are up to date

3. **Application Crashes**
   - Make sure all dependencies are properly installed
   - Check if you have the latest version of Python
   - Verify that your system meets the minimum requirements

## Русский

### Содержание
1. [Начало работы](#начало-работы)
2. [Базовое использование](#базовое-использование)
3. [Настройки звука](#настройки-звука)
4. [Устранение неполадок](#устранение-неполадок)

### Начало работы

#### Системные требования
- Windows 10 или новее
- Python 3.7 или выше
- Работающий микрофон и динамики/наушники
- Подключение к интернету

#### Установка
1. Скачайте и установите Python с [python.org](https://python.org)
2. Установите необходимые зависимости:
   ```bash
   pip install -r requirements.txt
   ```

### Базовое использование

#### Запуск приложения
1. Откройте терминал/командную строку
2. Перейдите в директорию приложения
3. Запустите основное приложение:
   ```bash
   python main.py
   ```

#### Управление звуком
- **Микрофон**: Приложение автоматически определит и будет использовать ваш микрофон по умолчанию
- **Динамики**: Звук будет воспроизводиться через ваше устройство вывода звука по умолчанию
- **Регулировка громкости**: Используйте системные регуляторы громкости

### Настройки звука

#### Технические характеристики
- Формат звука: 16-бит PCM
- Частота дискретизации: 48кГц
- Каналы: Стерео (2 канала)
- Размер буфера: 1024 сэмпла

#### Настройка качества звука
Приложение по умолчанию использует настройки высокого качества звука. Эти настройки можно изменить в файле `audio_handler.py` при необходимости.

### Устранение неполадок

#### Распространенные проблемы
1. **Нет звука**
   - Проверьте правильность подключения микрофона и динамиков
   - Убедитесь, что в системных настройках выбраны правильные аудиоустройства
   - Проверьте, что приложение имеет разрешение на доступ к микрофону

2. **Плохое качество звука**
   - Проверьте подключение к интернету
   - Убедитесь, что вы используете качественный микрофон
   - Проверьте актуальность драйверов звука

3. **Сбои приложения**
   - Убедитесь, что все зависимости установлены правильно
   - Проверьте, что у вас установлена последняя версия Python
   - Убедитесь, что ваша система соответствует минимальным требованиям 