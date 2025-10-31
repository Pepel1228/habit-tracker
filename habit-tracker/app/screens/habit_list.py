from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDRoundFlatIconButton
from datetime import datetime
from app import db


class HabitListScreen(MDScreen):

    def on_enter(self, *args):
        print("🔍 HabitListScreen: on_enter вызван")
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.load_habits(), 0.1)

    def load_habits(self):
        print("🔍 Загрузка привычек...")
        container = self.ids.get('habit_list')
        if not container:
            print("❌ Не найден контейнер habit_list")
            return

        print("✅ Контейнер найден, загружаем привычки...")
        container.clear_widgets()

        try:
            habits = db.get_habits()
            print(f"📊 Получено привычек из БД: {len(habits)}")
        except Exception as e:
            print(f"❌ Ошибка БД: {e}")
            habits = []

        if not habits:
            lbl = MDLabel(
                text="Пока нет привычек. Нажмите +, чтобы добавить.",
                halign="center",
                size_hint_y=None,
                height="48dp"
            )
            container.add_widget(lbl)
            return

        for habit in habits:
            # Получаем статистику для отображения текущей серии
            stats = db.get_habit_stats(habit["id"])

            card = self.create_habit_card(habit, stats)
            container.add_widget(card)

    def create_habit_card(self, habit, stats):
        card = MDCard(
            orientation="vertical",
            padding="16dp",
            size_hint_y=None,
            height="120dp",
            radius=[12],
            ripple_behavior=True,
            elevation=2
        )

        # Верхняя часть - информация о привычке
        top_box = MDBoxLayout(orientation="horizontal", size_hint_y=0.6)

        # Левая часть - название и цель
        info_box = MDBoxLayout(orientation="vertical", size_hint_x=0.8)

        # Название привычки
        name_label = MDLabel(
            text=habit["name"],
            halign="left",
            font_style="Subtitle1",
            theme_text_color="Primary",
            size_hint_y=0.6
        )

        # Цель привычки
        goal_label = MDLabel(
            text=f"Цель: {habit.get('goal', 'Не указана')}",
            halign="left",
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=0.4
        )

        info_box.add_widget(name_label)
        info_box.add_widget(goal_label)

        # Правая часть - простая статистика (текстом)
        stats_box = MDBoxLayout(orientation="vertical", size_hint_x=0.2, spacing="2dp")

        # Текущая серия (просто текст)
        streak_label = MDLabel(
            text=f"Текущая серия: {stats.get('current_streak', 0)}",
            halign="center",
            font_style="Caption",
            theme_text_color="Primary",
            size_hint_y=0.5
        )

        # Общее количество (просто текст)
        total_label = MDLabel(
            text=f"Самая длинная серия: {stats.get('total_done', 0)}",
            halign="center",
            font_style="Caption",
            theme_text_color="Primary",
            size_hint_y=0.5
        )

        stats_box.add_widget(streak_label)
        stats_box.add_widget(total_label)

        top_box.add_widget(info_box)
        top_box.add_widget(stats_box)

        # Нижняя часть - кнопки действий
        bottom_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=0.4,
            spacing="8dp"
        )

        # Кнопка "Выполнено сегодня" - проверяем, выполнена ли уже сегодня
        today = datetime.now().strftime('%Y-%m-%d')
        is_done_today = today in stats.get('last_30_days', [])

        if is_done_today:
            # Если уже выполнено сегодня - показываем кнопку с галочкой
            done_button = MDRoundFlatIconButton(
                text="✔ Выполнено сегодня",
                icon="check",
                size_hint_x=0.5,
                on_release=lambda x, hid=habit["id"]: self.show_info_message("Уже выполнено сегодня!"),
                text_color=(0.4, 0.4, 0.4, 1),  # Серый цвет
                line_color=(0.4, 0.4, 0.4, 0.5)  # Серая рамка
            )
        else:
            # Если еще не выполнено - активная кнопка
            done_button = MDRoundFlatIconButton(
                text="Выполнено сегодня",
                icon="check",
                size_hint_x=0.5,
                on_release=lambda x, hid=habit["id"]: self.toggle_habit_done(hid),
                text_color=(0.2, 0.7, 0.3, 1),  # Зеленый цвет
                line_color=(0.2, 0.7, 0.3, 0.5)  # Зеленая рамка
            )

        # Контейнер для кнопок редактирования и статистики
        actions_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_x=0.5,
            spacing="4dp"
        )

        # Кнопка редактирования
        edit_btn = MDIconButton(
            icon="pencil",
            on_release=lambda x, hid=habit["id"]: self.edit_habit(hid),
            theme_icon_color="Custom",
            icon_color=(0.2, 0.6, 0.8, 1)
        )

        # Кнопка статистики
        stats_btn = MDIconButton(
            icon="chart-line",
            on_release=lambda x, hid=habit["id"]: self.open_stats(hid),
            theme_icon_color="Custom",
            icon_color=(0.3, 0.7, 0.3, 1)
        )

        actions_box.add_widget(edit_btn)
        actions_box.add_widget(stats_btn)

        bottom_box.add_widget(done_button)
        bottom_box.add_widget(actions_box)

        # Собираем карточку
        card.add_widget(top_box)
        card.add_widget(bottom_box)

        return card

    def toggle_habit_done(self, habit_id):
        print(f"✅ Отметка выполнения привычки {habit_id}")
        try:
            result = db.log_habit_done(habit_id)
            if result:
                print(f"✅ Привычка {habit_id} отмечена выполненной")
                # Обновляем список привычек
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: self.load_habits(), 0.1)
            else:
                print(f"⚠️ Привычка уже была отмечена сегодня")
                # Обновляем список, чтобы показать правильный статус
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: self.load_habits(), 0.1)
        except Exception as e:
            print(f"❌ Ошибка отметки привычки: {e}")

    def show_info_message(self, message):
        print(f"ℹ️ {message}")

    def edit_habit(self, habit_id):
        print(f"✏️ Редактирование привычки {habit_id}")
        if self.manager and "habit_edit" in self.manager.screen_names:
            edit_screen = self.manager.get_screen("habit_edit")
            edit_screen.habit_id = habit_id
            self.manager.current = "habit_edit"
            print("✅ Переход к редактированию")
        else:
            print("❌ Не могу найти экран редактирования")

    def open_stats(self, habit_id):
        print(f"📊 Открытие статистики привычки {habit_id}")
        if self.manager and "habit_stats" in self.manager.screen_names:
            stats_screen = self.manager.get_screen("habit_stats")
            stats_screen.habit_id = habit_id
            self.manager.current = "habit_stats"
            print("✅ Переход к статистике")
        else:
            print("❌ Не могу найти экран статистики")

    def open_settings(self):
        print("⚙️ Открытие настроек")
        if self.manager and "settings" in self.manager.screen_names:
            self.manager.current = "settings"
            print("✅ Переход к настройкам")
        else:
            print("❌ Не могу найти экран настроек")

    def add_habit(self):
        print("➕ Добавление новой привычки")
        if self.manager and "habit_add" in self.manager.screen_names:
            self.manager.current = "habit_add"
            print("✅ Переход к добавлению привычки")
        else:
            print("❌ Не могу найти экран добавления привычки")