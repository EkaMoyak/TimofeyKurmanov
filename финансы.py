import sys
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QSizePolicy, QSpacerItem, QTabWidget,
                             QLineEdit, QFormLayout, QMessageBox, QComboBox, QTableWidget,
                             QTableWidgetItem, QHeaderView, QAbstractItemView, QDialog)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QColor, QFont, QPainter, QPalette
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QStackedBarSeries, \
    QPieSeries


class TipDialog(QDialog):
    def __init__(self, tip, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Финансовый совет")
        self.setFixedSize(400, 200)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        self.tip_label = QLabel(tip)
        self.tip_label.setWordWrap(True)
        self.tip_label.setAlignment(Qt.AlignCenter)
        self.tip_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333;
            }
        """)

        self.close_btn = QPushButton("Закрыть")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.close_btn.clicked.connect(self.close)

        layout.addWidget(self.tip_label)
        layout.addWidget(self.close_btn)
        self.setLayout(layout)


class AnimatedButton(QPushButton):
    def __init__(self, text, color, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(120, 120)
        self.color = color
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 60px;
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #333;
            }}
            QPushButton:hover {{
                background-color: {self.adjust_color(color, 20)};
                border: 3px solid #333;
            }}
        """)

    def adjust_color(self, color, amount):
        """Make color lighter or darker"""
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        r = min(255, max(0, r + amount))
        g = min(255, max(0, g + amount))
        b = min(255, max(0, b + amount))
        return f"#{r:02x}{g:02x}{b:02x}"


class AddMoneyWindow(QWidget):
    def __init__(self, parent=None, category_type=None, category=None):
        super().__init__(parent)
        self.category_type = category_type
        self.category = category
        self.setWindowTitle(f"Добавить {category_type.lower()} - {category.lower()}")
        self.setFixedSize(350, 300)

        # Set window background color
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#f5f5f5"))
        self.setPalette(palette)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Введите сумму")
        self.amount_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
        """)

        self.month_combo = QComboBox()
        self.month_combo.addItems(["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                                   "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"])
        self.month_combo.setCurrentIndex(0)
        self.month_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
        """)

        form_layout.addRow("Сумма:", self.amount_input)
        form_layout.addRow("Месяц:", self.month_combo)

        # Add subcategory selection for income and expenses
        if category_type in ["Доходы", "Расходы"]:
            self.subcategory_combo = QComboBox()
            self.subcategory_combo.setStyleSheet("""
                QComboBox {
                    padding: 6px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    font-size: 14px;
                }
            """)
            if category_type == "Доходы":
                self.subcategory_combo.addItems(["Зарплата", "Подарок", "Прочее"])
            else:
                self.subcategory_combo.addItems(["Транспорт", "Продукты", "Развлечения", "Прочее"])
            form_layout.addRow("Подкатегория:", self.subcategory_combo)

        self.add_button = QPushButton("Добавить")
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.add_button.clicked.connect(self.add_money)

        layout.addLayout(form_layout)
        layout.addSpacing(20)
        layout.addWidget(self.add_button)
        self.setLayout(layout)

    def add_money(self):
        try:
            amount = float(self.amount_input.text())
            month = self.month_combo.currentIndex()

            subcategory = None
            if hasattr(self, 'subcategory_combo'):
                subcategory = self.subcategory_combo.currentText()

            self.parent().add_to_category(self.category_type, self.category, month, amount, subcategory)
            self.close()

        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректную сумму")


class FinancialApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_data()
        self.init_ui()
        self.show_chart("Доходы")

        # Показываем случайный совет при запуске
        self.show_random_tip()

        # Store button animations to keep them alive
        self.button_animations = []

    def show_random_tip(self):
        tips = [
            "Откладывайте минимум 10% от каждого дохода - это основа финансовой стабильности.",
            "Перед крупной покупкой подождите 24 часа - это поможет избежать импульсных трат.",
            "Используйте правило 50/30/20: 50% на нужды, 30% на желания, 20% на сбережения.",
            "Заведите отдельный счет для накоплений и не снимайте с него деньги без крайней необходимости.",
            "Анализируйте свои расходы раз в месяц - это поможет выявить ненужные траты.",
            "Планируйте крупные покупки заранее, откладывая небольшие суммы каждый месяц.",
            "Используйте кэшбэк и бонусные программы - это может дать до 10% экономии.",
            "Автоматизируйте платежи и накопления - так вы не забудете про важные финансовые операции.",
            "Сравнивайте цены перед покупкой, особенно для дорогих товаров.",
            "Создайте финансовую подушку безопасности - 3-6 месячных доходов на непредвиденные случаи.",
            "Инвестируйте в свое образование - это самые выгодные долгосрочные вложения.",
            "Избегайте кредитов на потребительские товары - они часто ведут к долговой яме.",
            "Покупайте качественные вещи - они служат дольше и в итоге экономят ваши деньги.",
            "Планируйте меню на неделю - это сократит расходы на еду и уменьшит количество спонтанных покупок.",
            "Регулярно пересматривайте свои подписки и откажитесь от ненужных."
        ]

        tip = random.choice(tips)
        self.tip_dialog = TipDialog(tip, self)
        self.tip_dialog.exec_()

    def init_data(self):
        self.chart_data = {
            "Доходы": {
                "total": [0] * 12,
                "Зарплата": [0] * 12,
                "Подарок": [0] * 12,
                "Прочее": [0] * 12
            },
            "Расходы": {
                "total": [0] * 12,
                "Транспорт": [0] * 12,
                "Продукты": [0] * 12,
                "Развлечения": [0] * 12,
                "Прочее": [0] * 12
            },
            "Сбережения": [0] * 12,
            "Благотворительность": [0] * 12,
            "Кредиты": [0] * 12
        }

        # Transaction history
        self.transactions = []

    def init_ui(self):
        self.setWindowTitle("Финансовая визуализация")
        self.setGeometry(100, 100, 1200, 850)

        # Set main window background color
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#f0f0f0"))
        self.setPalette(palette)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Верхняя часть с кнопками и диаграммами
        top_panel = QWidget()
        top_panel.setStyleSheet("background-color: white; border-radius: 10px;")
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(15, 15, 15, 15)
        top_layout.setSpacing(20)

        # Левая панель с кнопками категорий
        buttons_panel = QWidget()
        buttons_panel.setStyleSheet("background-color: #f9f9f9; border-radius: 10px;")
        buttons_layout = QVBoxLayout(buttons_panel)
        buttons_layout.setAlignment(Qt.AlignCenter)
        buttons_layout.setSpacing(20)
        buttons_layout.setContentsMargins(15, 15, 15, 15)

        # Кнопки категорий с цветами
        self.income_btn = AnimatedButton("Доходы", "#4CAF50", self)  # Green
        self.expense_btn = AnimatedButton("Расходы", "#F44336", self)  # Red
        self.savings_btn = AnimatedButton("Сбережения", "#2196F3", self)  # Blue
        self.charity_btn = AnimatedButton("Благотворительность", "#9C27B0", self)  # Purple
        self.loans_btn = AnimatedButton("Кредиты", "#FF9800", self)  # Orange
        self.all_btn = AnimatedButton("Общая", "#607D8B", self)  # Gray

        # Добавляем кнопку для показа советов
        self.tip_btn = AnimatedButton("Совет", "#FFC107", self)  # Yellow
        self.tip_btn.clicked.connect(self.show_random_tip)

        # Подключаем обработчики кликов
        self.income_btn.clicked.connect(lambda: self.show_chart("Доходы"))
        self.expense_btn.clicked.connect(lambda: self.show_chart("Расходы"))
        self.savings_btn.clicked.connect(lambda: self.show_chart("Сбережения"))
        self.charity_btn.clicked.connect(lambda: self.show_chart("Благотворительность"))
        self.loans_btn.clicked.connect(lambda: self.show_chart("Кредиты"))
        self.all_btn.clicked.connect(self.show_all_categories)

        # Добавляем кнопки в layout
        buttons_layout.addWidget(self.income_btn)
        buttons_layout.addWidget(self.expense_btn)
        buttons_layout.addWidget(self.savings_btn)
        buttons_layout.addWidget(self.charity_btn)
        buttons_layout.addWidget(self.loans_btn)
        buttons_layout.addWidget(self.all_btn)
        buttons_layout.addWidget(self.tip_btn)

        buttons_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        top_layout.addWidget(buttons_panel, stretch=1)

        # Правая панель с диаграммами и таблицей
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 5px;
                background: white;
            }
            QTabBar::tab {
                padding: 8px 15px;
                background: #f1f1f1;
                border: 1px solid #ddd;
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 1px solid white;
                margin-bottom: -1px;
            }
        """)

        # Вкладка с текущей диаграммой
        self.current_chart_tab = QWidget()
        current_chart_layout = QVBoxLayout(self.current_chart_tab)
        current_chart_layout.setContentsMargins(10, 10, 10, 10)
        current_chart_layout.setSpacing(15)

        self.chart_title = QLabel("Доходы")
        self.chart_title.setAlignment(Qt.AlignCenter)
        self.chart_title.setStyleSheet("""
            QLabel {
                font-size: 20px; 
                font-weight: bold; 
                color: #333;
                margin-bottom: 10px;
            }
        """)

        # Добавляем виджет для круговой диаграммы подкатегорий
        self.subcategories_chart_view = QChartView()
        self.subcategories_chart_view.setRenderHint(QPainter.Antialiasing)
        self.subcategories_chart_view.setStyleSheet("background: transparent;")

        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setStyleSheet("background: transparent;")

        current_chart_layout.addWidget(self.chart_title)
        current_chart_layout.addWidget(self.subcategories_chart_view, stretch=1)
        current_chart_layout.addWidget(self.chart_view, stretch=2)

        # Панель с итоговой суммой
        summary_panel = QWidget()
        summary_panel.setStyleSheet("background-color: #f5f5f5; border-radius: 5px;")
        summary_layout = QHBoxLayout(summary_panel)
        summary_layout.setContentsMargins(15, 10, 15, 10)

        total_label = QLabel("Сумма за год:")
        total_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #555;")

        self.total_amount = QLabel("0 ₽")
        self.total_amount.setStyleSheet("""
            QLabel {
                font-size: 24px; 
                color: #4e54c8; 
                font-weight: bold;
            }
        """)

        summary_layout.addWidget(total_label)
        summary_layout.addWidget(self.total_amount)
        summary_layout.addStretch()

        current_chart_layout.addWidget(summary_panel)

        # Вкладка с общей диаграммой
        self.all_chart_tab = QWidget()
        all_chart_layout = QVBoxLayout(self.all_chart_tab)
        all_chart_layout.setContentsMargins(10, 10, 10, 10)

        all_chart_title = QLabel("Общая финансовая картина")
        all_chart_title.setAlignment(Qt.AlignCenter)
        all_chart_title.setStyleSheet("""
            QLabel {
                font-size: 20px; 
                font-weight: bold; 
                color: #333;
                margin-bottom: 15px;
            }
        """)

        self.all_chart_view = QChartView()
        self.all_chart_view.setRenderHint(QPainter.Antialiasing)
        self.all_chart_view.setStyleSheet("background: transparent;")

        all_chart_layout.addWidget(all_chart_title)
        all_chart_layout.addWidget(self.all_chart_view)

        # Вкладка с таблицей транзакций
        self.transactions_tab = QWidget()
        transactions_layout = QVBoxLayout(self.transactions_tab)
        transactions_layout.setContentsMargins(10, 10, 10, 10)

        transactions_title = QLabel("История операций")
        transactions_title.setAlignment(Qt.AlignCenter)
        transactions_title.setStyleSheet("""
            QLabel {
                font-size: 20px; 
                font-weight: bold; 
                color: #333;
                margin-bottom: 15px;
            }
        """)

        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(5)
        self.transactions_table.setHorizontalHeaderLabels(["Тип", "Категория", "Подкатегория", "Месяц", "Сумма"])
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.transactions_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.transactions_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                background: white;
            }
            QHeaderView::section {
                background-color: #f1f1f1;
                padding: 5px;
                border: none;
            }
        """)

        transactions_layout.addWidget(transactions_title)
        transactions_layout.addWidget(self.transactions_table)

        # Добавляем вкладки
        self.tab_widget.addTab(self.current_chart_tab, "Детали")
        self.tab_widget.addTab(self.all_chart_tab, "Общая картина")
        self.tab_widget.addTab(self.transactions_tab, "История операций")

        top_layout.addWidget(self.tab_widget, stretch=3)
        main_layout.addWidget(top_panel)

        # Нижняя панель с кнопками добавления денег
        bottom_panel = QWidget()
        bottom_panel.setStyleSheet("background-color: white; border-radius: 10px;")
        bottom_layout = QHBoxLayout(bottom_panel)
        bottom_layout.setContentsMargins(20, 15, 20, 15)
        bottom_layout.setSpacing(15)

        # Кнопки для добавления денег
        self.add_income_btn = QPushButton("Добавить доходы")
        self.add_expense_btn = QPushButton("Добавить расходы")
        self.add_savings_btn = QPushButton("Добавить сбережения")
        self.add_charity_btn = QPushButton("Добавить благотворительность")
        self.add_loans_btn = QPushButton("Добавить кредиты")

        # Стиль для кнопок
        button_style = """
            QPushButton {
                background-color: %s;
                color: white;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                border: none;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: %s;
            }
        """

        self.add_income_btn.setStyleSheet(button_style % ("#4CAF50", "#45a049"))
        self.add_expense_btn.setStyleSheet(button_style % ("#F44336", "#d32f2f"))
        self.add_savings_btn.setStyleSheet(button_style % ("#2196F3", "#1976D2"))
        self.add_charity_btn.setStyleSheet(button_style % ("#9C27B0", "#7B1FA2"))
        self.add_loans_btn.setStyleSheet(button_style % ("#FF9800", "#F57C00"))

        # Подключаем обработчики
        self.add_income_btn.clicked.connect(lambda: self.open_add_money_window("Доходы", "Доходы"))
        self.add_expense_btn.clicked.connect(lambda: self.open_add_money_window("Расходы", "Расходы"))
        self.add_savings_btn.clicked.connect(lambda: self.open_add_money_window("Сбережения", "Сбережения"))
        self.add_charity_btn.clicked.connect(
            lambda: self.open_add_money_window("Благотворительность", "Благотворительность"))
        self.add_loans_btn.clicked.connect(lambda: self.open_add_money_window("Кредиты", "Кредиты"))

        # Добавляем кнопки в layout
        bottom_layout.addWidget(self.add_income_btn)
        bottom_layout.addWidget(self.add_expense_btn)
        bottom_layout.addWidget(self.add_savings_btn)
        bottom_layout.addWidget(self.add_charity_btn)
        bottom_layout.addWidget(self.add_loans_btn)

        main_layout.addWidget(bottom_panel)

        # Сразу строим общую диаграмму
        self.create_all_categories_chart()

    def animate_buttons(self):
        # Animate all category buttons
        buttons = [self.income_btn, self.expense_btn, self.savings_btn,
                   self.charity_btn, self.loans_btn, self.all_btn, self.tip_btn]

        for i, button in enumerate(buttons):
            anim = QPropertyAnimation(button, b"geometry")
            anim.setDuration(500)
            anim.setEasingCurve(QEasingCurve.OutBack)

            start_pos = button.geometry()
            end_pos = QRect(start_pos.x(), start_pos.y() + 20, start_pos.width(), start_pos.height())

            anim.setStartValue(start_pos)
            anim.setEndValue(end_pos)
            anim.setLoopCount(1)

            # Reverse animation after moving down
            anim.finished.connect(lambda pos=start_pos, b=button: self.reverse_animation(b, pos))

            anim.start()
            self.button_animations.append(anim)

    def reverse_animation(self, button, end_pos):
        anim = QPropertyAnimation(button, b"geometry")
        anim.setDuration(500)
        anim.setEasingCurve(QEasingCurve.OutBack)

        start_pos = button.geometry()

        anim.setStartValue(start_pos)
        anim.setEndValue(end_pos)
        anim.start()
        self.button_animations.append(anim)

    def open_add_money_window(self, category_type, category):
        self.add_window = AddMoneyWindow(self, category_type, category)
        self.add_window.show()
        self.animate_buttons()

    def add_to_category(self, category_type, category, month, amount, subcategory=None):
        try:
            month_name = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                          "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"][month]

            if category_type in ["Доходы", "Расходы"]:
                # Добавляем в общую сумму категории
                self.chart_data[category_type]["total"][month] += amount

                # Добавляем в подкатегорию
                if subcategory:
                    self.chart_data[category_type][subcategory][month] += amount

                # Добавляем в историю операций
                self.transactions.append({
                    "type": category_type,
                    "category": category,
                    "subcategory": subcategory,
                    "month": month_name,
                    "amount": amount
                })

                # Если это доход, автоматически добавляем в сбережения и благотворительность
                if category_type == "Доходы":
                    savings_amount = amount * 0.1
                    charity_amount = amount * 0.05
                    self.chart_data["Сбережения"][month] += savings_amount
                    self.chart_data["Благотворительность"][month] += charity_amount

                    # Добавляем автоматические операции в историю
                    self.transactions.append({
                        "type": "Автоматическое",
                        "category": "Сбережения",
                        "subcategory": "Автоначисление",
                        "month": month_name,
                        "amount": savings_amount
                    })

                    self.transactions.append({
                        "type": "Автоматическое",
                        "category": "Благотворительность",
                        "subcategory": "Автоначисление",
                        "month": month_name,
                        "amount": charity_amount
                    })
            else:
                self.chart_data[category][month] += amount
                # Добавляем в историю операций
                self.transactions.append({
                    "type": category_type,
                    "category": category,
                    "subcategory": "",
                    "month": month_name,
                    "amount": amount
                })

            self.show_chart(category_type if category_type in ["Доходы", "Расходы"] else category)
            self.create_all_categories_chart()
            self.update_transactions_table()

            QMessageBox.information(self, "Успех", f"Добавлено {amount} ₽ в {category.lower()} за {month_name.lower()}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось добавить данные: {str(e)}")

    def update_transactions_table(self):
        self.transactions_table.setRowCount(len(self.transactions))

        for row, transaction in enumerate(self.transactions):
            self.transactions_table.setItem(row, 0, QTableWidgetItem(transaction["type"]))
            self.transactions_table.setItem(row, 1, QTableWidgetItem(transaction["category"]))
            self.transactions_table.setItem(row, 2, QTableWidgetItem(transaction["subcategory"]))
            self.transactions_table.setItem(row, 3, QTableWidgetItem(transaction["month"]))
            self.transactions_table.setItem(row, 4, QTableWidgetItem(f"{transaction['amount']} ₽"))

            # Set color based on transaction type
            if transaction["type"] == "Доходы":
                color = QColor("#4CAF50")
            elif transaction["type"] == "Расходы":
                color = QColor("#F44336")
            else:
                color = QColor("#2196F3")

            for col in range(5):
                self.transactions_table.item(row, col).setBackground(color.lighter(180))

    def show_chart(self, category):
        self.chart_title.setText(category)

        if category in ["Доходы", "Расходы"]:
            self.show_category_with_subcategories(category)
        else:
            self.show_simple_category(category)

    def show_category_with_subcategories(self, category):
        # Создаем основную диаграмму (гистограмму)
        chart = QChart()
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTitle(f"Месячные {category.lower()}")
        chart.setTitleFont(QFont("Arial", 12, QFont.Bold))
        chart.setBackgroundBrush(QColor("transparent"))

        # Создаем круговую диаграмму для подкатегорий
        pie_chart = QChart()
        pie_chart.setAnimationOptions(QChart.SeriesAnimations)
        pie_chart.setTitle("Распределение по подкатегориям")
        pie_chart.setTitleFont(QFont("Arial", 10, QFont.Bold))
        pie_chart.setBackgroundBrush(QColor("transparent"))

        # Создаем серии для гистограммы
        series = QBarSeries()
        bar_set = QBarSet(category)

        # Цвета для категорий
        colors = {
            "Доходы": QColor("#4CAF50"),  # Green
            "Расходы": QColor("#F44336"),  # Red
            "Сбережения": QColor("#2196F3"),  # Blue
            "Благотворительность": QColor("#9C27B0"),  # Purple
            "Кредиты": QColor("#FF9800")  # Orange
        }

        bar_set.setColor(colors[category])

        for value in self.chart_data[category]["total"]:
            bar_set.append(value)

        series.append(bar_set)
        chart.addSeries(series)

        # Настройка осей для гистограммы
        axis_x = QBarCategoryAxis()
        months = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн",
                  "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]
        axis_x.append(months)
        axis_x.setTitleText("Месяцы")
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        max_value = max(self.chart_data[category]["total"]) * 1.2
        axis_y.setRange(0, max(max_value, 100))
        axis_y.setTitleText("Сумма (₽)")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

        # Создаем круговую диаграмму подкатегорий
        pie_series = QPieSeries()
        pie_series.setLabelsVisible(True)

        # Добавляем подкатегории в круговую диаграмму
        subcategories = [key for key in self.chart_data[category].keys() if key != "total"]
        subcategory_colors = {
            "Зарплата": QColor("#388E3C"),
            "Подарок": QColor("#81C784"),
            "Прочее": QColor("#A5D6A7"),
            "Транспорт": QColor("#E53935"),
            "Продукты": QColor("#EF5350"),
            "Развлечения": QColor("#FFCDD2")
        }

        for subcat in subcategories:
            total = sum(self.chart_data[category][subcat])
            if total > 0:
                slice = pie_series.append(subcat, total)
                slice.setColor(subcategory_colors.get(subcat, QColor(200, 200, 200)))
                slice.setLabel(f"{subcat}: {total} ₽")
                slice.setLabelVisible(True)

        pie_chart.addSeries(pie_series)

        # Обновляем итоговую сумму
        total = sum(self.chart_data[category]["total"])
        self.total_amount.setText(f"{total} ₽")

        self.chart_view.setChart(chart)
        self.subcategories_chart_view.setChart(pie_chart)
        self.subcategories_chart_view.setVisible(True)
        self.tab_widget.setCurrentIndex(0)

    def show_simple_category(self, category):
        # Скрываем круговую диаграмму для простых категорий
        self.subcategories_chart_view.setVisible(False)

        chart = QChart()
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTitle(f"Месячные {category.lower()}")
        chart.setTitleFont(QFont("Arial", 12, QFont.Bold))
        chart.setBackgroundBrush(QColor("transparent"))

        series = QBarSeries()
        bar_set = QBarSet(category)

        # Устанавливаем цвет в зависимости от категории
        colors = {
            "Сбережения": QColor("#2196F3"),  # Blue
            "Благотворительность": QColor("#9C27B0"),  # Purple
            "Кредиты": QColor("#FF9800")  # Orange
        }

        bar_set.setColor(colors.get(category, QColor(100, 100, 100)))

        for value in self.chart_data[category]:
            bar_set.append(value)

        series.append(bar_set)
        chart.addSeries(series)

        # Настройка осей
        axis_x = QBarCategoryAxis()
        months = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн",
                  "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]
        axis_x.append(months)
        axis_x.setTitleText("Месяцы")
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        max_value = max(self.chart_data[category]) * 1.2
        axis_y.setRange(0, max(max_value, 100))
        axis_y.setTitleText("Сумма (₽)")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

        # Обновляем итоговую сумму
        total = sum(self.chart_data[category])
        self.total_amount.setText(f"{total} ₽")

        self.chart_view.setChart(chart)
        self.tab_widget.setCurrentIndex(0)

    def show_all_categories(self):
        self.tab_widget.setCurrentIndex(1)

    def create_all_categories_chart(self):
        chart = QChart()
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTitle("Общая финансовая картина")
        chart.setTitleFont(QFont("Arial", 12, QFont.Bold))
        chart.setBackgroundBrush(QColor("transparent"))

        series = QStackedBarSeries()

        # Создаем наборы данных для каждой категории
        categories = ["Доходы", "Расходы", "Сбережения", "Благотворительность", "Кредиты"]
        colors = {
            "Доходы": QColor("#4CAF50"),
            "Расходы": QColor("#F44336"),
            "Сбережения": QColor("#2196F3"),
            "Благотворительность": QColor("#9C27B0"),
            "Кредиты": QColor("#FF9800")
        }

        for category in categories:
            bar_set = QBarSet(category)
            bar_set.setColor(colors[category])

            if category in ["Доходы", "Расходы"]:
                values = self.chart_data[category]["total"]
            else:
                values = self.chart_data[category]

            for value in values:
                bar_set.append(value)
            series.append(bar_set)

        chart.addSeries(series)

        # Настройка осей
        axis_x = QBarCategoryAxis()
        months = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн",
                  "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]
        axis_x.append(months)
        axis_x.setTitleText("Месяцы")
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        max_value = 0
        for month in range(12):
            month_total = (self.chart_data["Доходы"]["total"][month] +
                           self.chart_data["Расходы"]["total"][month] +
                           self.chart_data["Сбережения"][month] +
                           self.chart_data["Благотворительность"][month] +
                           self.chart_data["Кредиты"][month])
            if month_total > max_value:
                max_value = month_total

        axis_y.setRange(0, max(max_value * 1.2, 100))
        axis_y.setTitleText("Сумма (₽)")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

        self.all_chart_view.setChart(chart)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Set application style and palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#f0f0f0"))
    palette.setColor(QPalette.WindowText, Qt.black)
    palette.setColor(QPalette.Base, QColor("#ffffff"))
    palette.setColor(QPalette.AlternateBase, QColor("#f5f5f5"))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.black)
    palette.setColor(QPalette.Text, Qt.black)
    palette.setColor(QPalette.Button, QColor("#e0e0e0"))
    palette.setColor(QPalette.ButtonText, Qt.black)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Highlight, QColor("#4CAF50"))
    palette.setColor(QPalette.HighlightedText, Qt.white)
    app.setPalette(palette)

    try:
        from PyQt5.QtChart import QChart
    except ImportError:
        print("Ошибка: Необходимо установить модуль PyQtChart")
        sys.exit(1)

    window = FinancialApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()