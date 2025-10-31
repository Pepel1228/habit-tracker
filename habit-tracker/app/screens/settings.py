from kivymd.uix.screen import MDScreen
from kivy.properties import BooleanProperty, StringProperty
from kivymd.app import MDApp
from kivy.clock import Clock
from app import db


class SettingsScreen(MDScreen):
    dark_theme = BooleanProperty(False)
    primary_color = StringProperty("#6750A4")
    _content_loaded = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("🔍 SettingsScreen создан")

    def on_enter(self):
        print("🔍 SettingsScreen: on_enter вызван")

        if not self._content_loaded:
            Clock.schedule_once(lambda dt: self.load_settings(), 0.1)
            self._content_loaded = True

    def on_leave(self):
        pass

    def go_back(self):
        if self.manager and 'habit_list' in self.manager.screen_names:
            self.manager.current = 'habit_list'

    def load_settings(self):
        try:
            settings = db.get_settings()
            if settings:
                self.dark_theme = settings.get('dark_theme', False)
                self.primary_color = settings.get('primary_color', '#6750A4')

                # Обновляем переключатель в интерфейсе
                if hasattr(self, 'ids') and 'theme_switch' in self.ids:
                    self.ids.theme_switch.active = self.dark_theme

            print(
                f"✅ Настройки загружены: тема={'темная' if self.dark_theme else 'светлая'}, цвет={self.primary_color}")

            # Применяем тему сразу после загрузки
            self.apply_theme()

        except Exception as e:
            print(f"❌ Ошибка загрузки настроек: {e}")

    def toggle_dark_theme(self, switch_instance):
        try:
            # Получаем текущее значение переключателя
            new_value = switch_instance.active
            print(f"🔧 Переключение темы: {new_value}")

            if self.dark_theme != new_value:
                self.dark_theme = new_value
                self.save_settings()
                self.apply_theme()
                print(f"✅ Темная тема {'включена' if self.dark_theme else 'выключена'}")

        except Exception as e:
            print(f"❌ Ошибка переключения темы: {e}")

    def set_primary_color(self, hex_color):
        try:
            if self.primary_color != hex_color:
                self.primary_color = hex_color
                self.save_settings()
                self.apply_theme()
                print(f"✅ Установлен акцентный цвет: {hex_color}")
        except Exception as e:
            print(f"❌ Ошибка установки цвета: {e}")

    def apply_theme(self):
        try:
            app = MDApp.get_running_app()
            if not app:
                return

            # Применяем светлую/темную тему
            app.theme_cls.theme_style = "Dark" if self.dark_theme else "Light"

            # Применяем акцентный цвет
            palette_name = self.get_palette_name(self.primary_color)
            app.theme_cls.primary_palette = palette_name

            print(f"🎨 Тема применена: {app.theme_cls.theme_style}, палитра: {palette_name}")

        except Exception as e:
            print(f"❌ Ошибка применения темы: {e}")

    def get_palette_name(self, hex_color):
        color_map = {
            "#6750A4": "DeepPurple",
            "#4CAF50": "Green",
            "#2196F3": "Blue",
            "#FF9800": "Orange",
            "#F44336": "Red",
            "#9C27B0": "Purple",
            "#00BCD4": "Cyan",
            "#FF5722": "DeepOrange"
        }
        return color_map.get(hex_color, "DeepPurple")

    def save_settings(self):
        try:
            db.save_settings(
                dark_theme=self.dark_theme,
                primary_color=self.primary_color
            )
            print("💾 Настройки сохранены в БД")
        except Exception as e:
            print(f"❌ Ошибка сохранения настроек: {e}")

    def export_data(self):
        print("📤 Экспорт данных (заглушка)")

    def import_data(self):
        print("📥 Импорт данных (заглушка)")

    def show_privacy_policy(self):
        print("🔒 Политика конфиденциальности")