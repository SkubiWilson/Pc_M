import os

# Шлях до вашого файлу .bat
bat_file_path = "Launcher.bat"  # Замініть на фактичний шлях до вашого файлу .bat

# Перевіряємо, чи існує файл .bat
if os.path.exists(bat_file_path):
    try:
        # Відкриваємо файл .bat у відповідній програмі для виконання
        os.system(bat_file_path)
    except Exception as e:
        print(f"Помилка при відкритті файлу .bat: {str(e)}")
else:
    print(f"Файл .bat '{bat_file_path}' не знайдено.")
