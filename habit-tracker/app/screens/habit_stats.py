from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from app import db
from datetime import datetime, timedelta


class HabitStatsScreen(MDScreen):
    habit_name = StringProperty("Название привычки")
    current_streak = NumericProperty(0)
    longest_streak = NumericProperty(0)
    total_done = NumericProperty(0)
    history = ListProperty([])

    habit_id = None

    def on_pre_enter(self, *args):
        if not self.habit_id:
            return

        # Получаем данные привычки
        habits = db.get_habits()
        current_habit = next((h for h in habits if h['id'] == self.habit_id), None)

        if current_habit:
            self.habit_name = current_habit['name']

            # Получаем статистику
            stats = db.get_habit_stats(self.habit_id)
            self.set_stats_from_data(stats)

            # Обновляем визуальные элементы
            self.populate_calendar()
            self.populate_history()
            self.create_progress_chart()

    def set_stats_from_data(self, data: dict):
        self.current_streak = data.get('current_streak', 0)
        self.longest_streak = data.get('longest_streak', 0)
        self.total_done = data.get('total_done', 0)
        self.history = data.get('completions', [])
        self.last_30_days = data.get('last_30_days', [])

    def populate_calendar(self):
        grid = self.ids.get('calendar_grid')
        if not grid:
            return

        grid.clear_widgets()

        # Получаем текущую дату
        today = datetime.now().date()

        # Определяем первый день текущего месяца
        first_day_of_month = today.replace(day=1)

        # Определяем последний день текущего месяца
        if today.month == 12:
            last_day_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            last_day_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

        # Определяем день недели первого дня (0=понедельник, 6=воскресенье)
        start_weekday = first_day_of_month.weekday()

        # Добавляем пустые ячейки для выравнивания
        for i in range(start_weekday):
            empty_box = MDBoxLayout(
                size_hint=(None, None),
                size=(dp(32), dp(32))
            )
            grid.add_widget(empty_box)

        # Заполняем числами текущего месяца
        current_day = first_day_of_month
        while current_day <= last_day_of_month:
            date_str = current_day.strftime('%Y-%m-%d')

            # Проверяем выполнение
            is_completed = date_str in self.last_30_days

            # Цвета
            if is_completed:
                bg_color = [0.2, 0.6, 1, 1]  # Синий
                text_color = [1, 1, 1, 1]  # Белый
            else:
                bg_color = [0.95, 0.95, 0.95, 1]  # Светло-серый
                text_color = [0.5, 0.5, 0.5, 1]  # Серый

            # Создаем карточку дня
            day_card = MDCard(
                size_hint=(None, None),
                size=(dp(32), dp(32)),
                radius=dp(4),
                md_bg_color=bg_color,
                elevation=1 if is_completed else 0,
                padding=0
            )

            # Метка с числом
            label = MDLabel(
                text=str(current_day.day),
                halign='center',
                valign='middle',
                theme_text_color='Custom',
                text_color=text_color,
                font_size='10sp',
                bold=True
            )
            day_card.add_widget(label)
            grid.add_widget(day_card)

            # Переходим к следующему дню
            current_day += timedelta(days=1)

        # Добавляем пустые ячейки в конце если нужно
        total_cells = start_weekday + last_day_of_month.day
        remaining_cells = (7 - (total_cells % 7)) % 7

        for i in range(remaining_cells):
            empty_box = MDBoxLayout(
                size_hint=(None, None),
                size=(dp(32), dp(32))
            )
            grid.add_widget(empty_box)

    def create_progress_chart(self):
        container = self.ids.get('chart_container')
        if not container:
            return

        container.clear_widgets()

        # Создаем простой столбчатый график
        chart_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(2),
            size_hint_y=1
        )

        # Данные за последние 7 дней
        today = datetime.now().date()
        for i in range(7):
            day_date = today - timedelta(days=6 - i)
            date_str = day_date.strftime('%Y-%m-%d')

            # Высота столбца
            height_multiplier = 1 if date_str in self.last_30_days else 0.1

            day_column = MDBoxLayout(
                orientation='vertical',
                size_hint_x=1,
                spacing=dp(2)
            )

            # Столбец графика
            bar = MDCard(
                size_hint_y=height_multiplier,
                radius=dp(2),
                md_bg_color=(0.2, 0.6, 1, 1) if date_str in self.last_30_days else (0.9, 0.9, 0.9, 1)
            )

            # Подпись дня недели
            day_label = MDLabel(
                text=day_date.strftime('%a'),
                halign='center',
                font_style='Caption',
                size_hint_y=None,
                height=dp(20)
            )

            day_column.add_widget(bar)
            day_column.add_widget(day_label)
            chart_layout.add_widget(day_column)

        container.add_widget(chart_layout)

    def populate_history(self):
        container = self.ids.get('history_list')
        if not container:
            return

        container.clear_widgets()

        if not self.history:
            label = MDLabel(
                text="Пока нет выполнений",
                halign='center',
                theme_text_color='Secondary'
            )
            container.add_widget(label)
            return

        # Показываем последние 10 выполнений
        recent_completions = sorted(self.history, reverse=True)[:10]

        for completion_date in recent_completions:
            date_obj = datetime.strptime(completion_date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d.%m.%Y')

            card = MDCard(
                size_hint_y=None,
                height=dp(40),
                padding=dp(8),
                radius=dp(4)
            )

            label = MDLabel(
                text=f"✓ Выполнено: {formatted_date}",
                halign='left'
            )
            card.add_widget(label)
            container.add_widget(card)

    def go_back(self):
        if self.manager and 'habit_list' in self.manager.screen_names:
            self.manager.current = 'habit_list'

    def edit_habit(self):
        if self.manager and 'habit_edit' in self.manager.screen_names:
            edit_screen = self.manager.get_screen('habit_edit')
            edit_screen.habit_id = self.habit_id
            self.manager.current = 'habit_edit'