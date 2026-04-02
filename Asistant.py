import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import requests
import json
import subprocess
import time

# Инициализация голосового движка
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Конфигурация
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"  # Пример API (уточните актуальный URL)
DEEPSEEK_API_KEY = ""  # Замените на реальный ключ


def speak(text):
    """Озвучивание текста с выводом в консоль"""
    print(f"Ассистент: {text}")
    engine.say(text)
    engine.runAndWait()


def listen():
    """Распознавание голосовой команды с улучшенной обработкой ошибок"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        print("Слушаю... (скажите 'помощник' для активации)")
        try:
            audio = r.listen(source, timeout=3, phrase_time_limit=5)
            query = r.recognize_google(audio, language="ru-RU").lower()
            print(f"Вы: {query}")
            return query
        except sr.WaitTimeoutError:
            return ""
        except Exception as e:
            print(f"Ошибка распознавания: {e}")
            return ""


def execute_system_command(command):
    """Обработка локальных системных команд"""
    if "открой браузер" in command:
        subprocess.Popen([CHROME_PATH])
        return "Открываю браузер"

    elif "погода" in command:
        city = "Москва"  # Можно добавить извлечение города из команды
        webbrowser.open(f"https://yandex.ru/pogoda/{city}")
        return f"Открываю погоду для {city}"

    elif "время" in command:
        return f"Сейчас {datetime.datetime.now().strftime('%H:%M')}"

    elif "выключи компьютер" in command:
        os.system("shutdown /s /t 60")
        return "Компьютер будет выключен через 1 минуту"

    return None


def ask_ai(prompt):
    """Запрос к ИИ-посреднику (DeepSeek)"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Ошибка API: {e}")
        return "Не удалось получить ответ от ИИ"


def assistant():
    """Основной цикл работы ассистента"""
    speak("Готов к работе. Скажите 'помощник' для активации.")

    while True:
        query = listen()

        if not query:
            continue

        # Активация по ключевому слову
        if "помощник" in query:
            speak("Да, слушаю вас!")
            query = query.replace("помощник", "").strip()
            if not query:
                query = listen()

        # Выход из программы
        if any(word in query for word in ["пока", "выход", "заверши"]):
            speak("До свидания!")
            break

        # Попытка выполнить системную команду
        system_response = execute_system_command(query)
        if system_response:
            speak(system_response)
            continue

        # Если не системная команда - обращаемся к ИИ
        speak("Думаю...")
        ai_response = ask_ai(query)
        speak(ai_response[:500])  # Ограничение длины ответа


if __name__ == "__main__":
    try:
        assistant()
    except KeyboardInterrupt:
        speak("Работа завершена")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        speak("Произошла ошибка, перезапустите меня")