from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.config import Config
import os
from app import db
import sys

print("🐍 Python encoding:", sys.getdefaultencoding())
print("🐍 Filesystem encoding:", sys.getfilesystemencoding())

# Правильные импорты из папки screens
from app.screens.habit_list import HabitListScreen
from app.screens.habit_add import HabitAddScreen
from app.screens.habit_stats import HabitStatsScreen
from app.screens.reminders import RemindersScreen
from app.screens.settings import SettingsScreen
from app.screens.habit_edit import HabitEditScreen

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

# Пробуем инициализировать БД
try:
    db.init_db()
    print("БД подключена ✅")
except Exception as e:
    print(f"Ошибка БД: {e}")


class HabitScreenManager(ScreenManager):
    def add_habit(self):
        if "habit_add" in self.screen_names:
            self.current = "habit_add"


class HabitTrackerApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "DeepPurple"

        # Загружаем KV файлы из папки kv
        kv_files = [
            "habit_tracker.kv",
            "habit_add.kv",
            "habit_stats.kv",
            "reminders.kv",
            "settings.kv",
            "habit_edit.kv"
        ]

        print("🔍 Начинаем загрузку KV файлов...")

        # Просто загружаем файлы без сложных проверок
        loaded_files = []
        for kv_file in kv_files:
            try:
                kv_path = os.path.join("app/kv", kv_file)
                Builder.load_file(kv_path)
                loaded_files.append(kv_file)
                print(f"✅ Загружен {kv_file}")
            except Exception as e:
                print(f"❌ Ошибка загрузки {kv_file}: {e}")

        print(f"📁 Всего загружено KV файлов: {len(loaded_files)}")

        # Создаем ScreenManager и добавляем экраны
        sm = HabitScreenManager()

        # Добавляем экраны
        screens = [
            ("habit_list", HabitListScreen),
            ("habit_add", HabitAddScreen),
            ("habit_stats", HabitStatsScreen),
            ("reminders", RemindersScreen),
            ("settings", SettingsScreen),
            ("habit_edit", HabitEditScreen)
        ]

        for name, screen_class in screens:
            if not sm.has_screen(name):
                sm.add_widget(screen_class(name=name))
                print(f"✅ Добавлен экран: {name}")

        print("✅ Все экраны добавлены")
        return sm

    def on_start(self):
        settings_screen = self.root.get_screen("settings")
        settings_screen.on_enter()

    def back(self):
        if self.root and 'habit_list' in self.root.screen_names:
            self.root.current = 'habit_list'


if __name__ == '__main__':
    HabitTrackerApp().run()