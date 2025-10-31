from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.clock import Clock
from app import db


class HabitEditScreen(MDScreen):
    habit_id = None
    habit_repeat = StringProperty("Ежедневно")
    _is_loading = False

    def on_enter(self):
        if self._is_loading:
            return

        self._is_loading = True
        print(f"🔍 Загрузка экрана редактирования, habit_id={self.habit_id}")

        if self.habit_id:
            Clock.schedule_once(lambda dt: self.load_habit_data(), 0.1)
        else:
            self._is_loading = False

    def on_leave(self):
        self._is_loading = False

    def load_habit_data(self):
        try:
            habits = db.get_habits()
            current_habit = next((h for h in habits if h['id'] == self.habit_id), None)

            if current_habit:
                print(f"✅ Загружена привычка: {current_habit['name']}")
                self.ids.habit_title.text = current_habit.get('name', '')
                self.ids.habit_description.text = current_habit.get('goal', '')

                # Обновляем кнопки повторения
                self.habit_repeat = current_habit.get('repeat', 'Ежедневно')
                self.update_repeat_buttons()
            else:
                print("❌ Привычка не найдена")

        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
        finally:
            self._is_loading = False

    def set_repeat(self, repeat_type):
        self.habit_repeat = repeat_type
        self.update_repeat_buttons()

    def update_repeat_buttons(self):
        if not hasattr(self, 'ids') or not self.ids:
            return

        daily_btn = self.ids.daily_btn
        weekly_btn = self.ids.weekly_btn

        # Сбрасываем цвета
        from kivymd.app import MDApp
        app = MDApp.get_running_app()

        daily_btn.md_bg_color = app.theme_cls.primary_color if self.habit_repeat == "Ежедневно" else [0.7, 0.7, 0.7, 1]
        weekly_btn.md_bg_color = app.theme_cls.primary_color if self.habit_repeat == "Еженедельно" else [0.7, 0.7, 0.7,
                                                                                                         1]

    def save_edited_habit(self):
        if not self.habit_id:
            print("❌ Нет ID привычки")
            return

        name = self.ids.habit_title.text.strip()
        goal = self.ids.habit_description.text.strip()

        if not name:
            print("⚠️ Введите название привычки")
            return

        try:
            # Обновляем привычку
            db.delete_habit(self.habit_id)
            new_id = db.add_habit(name, goal, self.habit_repeat)
            print(f"💾 Привычка обновлена: {name}")
            self.go_back()

        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")

    def go_back(self):
        print("🔙 Возврат к списку")
        if self.manager:
            self.manager.transition.direction = 'right'
            self.manager.current = "habit_list"

            # Обновляем список привычек
            Clock.schedule_once(lambda dt: self.refresh_habit_list(), 0.2)

    def refresh_habit_list(self):
        try:
            if self.manager and self.manager.has_screen("habit_list"):
                habit_list_screen = self.manager.get_screen("habit_list")
                habit_list_screen.load_habits()
        except Exception as e:
            print(f"❌ Ошибка обновления списка: {e}")

    def delete_habit(self):
        if not self.habit_id:
            return

        try:
            db.delete_habit(self.habit_id)
            print(f"🗑️ Привычка удалена: {self.habit_id}")
            self.go_back()
        except Exception as e:
            print(f"❌ Ошибка удаления: {e}")
