"""
SemkaApp для Android
Адаптировано из tkinter в Kivy
Автор: @plsemen (telegram)
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.properties import ListProperty
from kivy.metrics import dp, sp

import urllib.request
import urllib.error
import urllib.parse
import threading

# ======== НАСТРОЙКИ ========
PASTEBIN_URL = "https://pastebin.com/raw/2V7sWegJ"

# ======== КЛАСС ДЛЯ ГРАДИЕНТНОГО ФОНА ========
class GradientWidget(Widget):
    """Виджет с градиентным фоном"""
    color_start = ListProperty([0.55, 0, 1, 1])  # #8C00FF в RGBA
    color_end = ListProperty([0.29, 0, 0.69, 1])  # #4A00B0 в RGBA
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_gradient, size=self.update_gradient)
    
    def update_gradient(self, *args):
        """Рисуем градиент"""
        self.canvas.before.clear()
        with self.canvas.before:
            if self.height <= 0:
                return
            
            # Верхняя часть
            Color(*self.color_start)
            Rectangle(pos=(self.x, self.y + self.height/2), size=(self.width, self.height/2))
            
            # Нижняя часть
            Color(*self.color_end)
            Rectangle(pos=(self.x, self.y), size=(self.width, self.height/2))


# ======== КЛАСС ДЛЯ ТЕКСТА С ПРОКРУТКОЙ (ИСПРАВЛЕННЫЙ) ========
class ScrollableLabel(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scroll_type = ['content']
        self.bar_width = dp(10)
        self.bar_color = (0.55, 0, 1, 0.8)
        self.bar_inactive_color = (0.55, 0, 1, 0.3)
        
        # Создаем контейнер для текста
        self.content = BoxLayout(orientation='vertical', size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter('height'))
        
        # Создаем метку для текста
        self.label = Label(
            size_hint_y=None,
            halign='left',
            valign='top',
            font_size=sp(16),
            color=(0.55, 0, 1, 1),  # Фиолетовый текст
            padding=(dp(10), dp(10)),
            markup=True
        )
        
        # ВАЖНО: Привязываем обновление размера
        self.label.bind(
            texture_size=self._update_label_size
        )
        
        self.content.add_widget(self.label)
        self.add_widget(self.content)
        
        # Запланировать обновление при изменении размера
        self.bind(width=self._update_label_width)
    
    def _update_label_size(self, instance, texture_size):
        """Обновляем размер метки"""
        instance.height = max(texture_size[1], 1)  # Минимум 1 пиксель
        if hasattr(self, 'width') and self.width > 0:
            instance.width = self.width - dp(20)
            instance.text_size = (instance.width, None)
    
    def _update_label_width(self, instance, width):
        """Обновляем ширину метки при изменении ширины контейнера"""
        if width > 0:
            self.label.width = width - dp(20)
            self.label.text_size = (self.label.width, None)
            self.label.texture_update()
    
    def set_text(self, text):
        """Устанавливаем текст"""
        self.label.text = text
        self.label.texture_update()
        # Принудительно обновляем размер
        if hasattr(self, 'width') and self.width > 0:
            self.label.width = self.width - dp(20)
            self.label.text_size = (self.label.width, None)
            self._update_label_size(self.label, self.label.texture_size)


# ======== ОСНОВНОЙ ЭКРАН ========
class SemkaAppScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.padding = [dp(20), dp(10), dp(20), dp(10)]
        self.spacing = dp(10)
        
        # Фон с градиентом
        self.gradient = GradientWidget()
        self.add_widget(self.gradient)
        
        # ======== ВЕРХНЯЯ ПАНЕЛЬ ========
        top_bar = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(60),
            spacing=dp(10)
        )
        
        # Заголовок
        title_label = Label(
            text="[b]📰 НОВОСТИ КАНАЛА[/b]",
            markup=True,
            font_size=sp(20),
            color=(1, 1, 1, 1),
            halign='left',
            valign='middle',
            size_hint=(0.8, 1)
        )
        
        # Кнопка информации
        self.info_btn = Button(
            text="?",
            font_size=sp(24),
            size_hint=(0.2, 1),
            background_normal='',
            background_color=(1, 0.65, 0, 1),
            color=(1, 1, 1, 1)
        )
        self.info_btn.bind(on_press=self.show_info)
        
        top_bar.add_widget(title_label)
        top_bar.add_widget(self.info_btn)
        self.add_widget(top_bar)
        
        # ======== ОСНОВНАЯ ОБЛАСТЬ (НОВОСТИ) ========
        # Создаем контейнер для новостей с белым фоном
        self.news_container = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            padding=dp(5)
        )
        
        # Белый фон
        with self.news_container.canvas.before:
            Color(1, 1, 1, 1)
            self.news_bg = Rectangle(pos=self.news_container.pos, size=self.news_container.size)
        
        def update_bg(instance, value):
            self.news_bg.pos = instance.pos
            self.news_bg.size = instance.size
        
        self.news_container.bind(pos=update_bg, size=update_bg)
        
        # Текстовое поле с прокруткой
        self.scroll_label = ScrollableLabel()
        self.news_container.add_widget(self.scroll_label)
        
        self.add_widget(self.news_container)
        
        # ======== НИЖНЯЯ ПАНЕЛЬ ========
        bottom_bar = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(70),
            spacing=dp(10)
        )
        
        # Кнопка обновления
        self.update_btn = Button(
            text="🔄 ОБНОВИТЬ",
            font_size=sp(16),
            size_hint=(0.4, 1),
            background_normal='',
            background_color=(0.47, 0, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        self.update_btn.bind(on_press=self.load_news_thread)
        
        # Статус
        self.status_label = Label(
            text="✨ Готов к работе",
            font_size=sp(14),
            color=(1, 1, 1, 1),
            size_hint=(0.4, 1),
            halign='center',
            valign='middle'
        )
        
        # Кнопка выхода
        exit_btn = Button(
            text="✕ ВЫХОД",
            font_size=sp(16),
            size_hint=(0.2, 1),
            background_normal='',
            background_color=(1, 0, 0, 1),
            color=(1, 1, 1, 1)
        )
        exit_btn.bind(on_press=self.exit_app)
        
        bottom_bar.add_widget(self.update_btn)
        bottom_bar.add_widget(self.status_label)
        bottom_bar.add_widget(exit_btn)
        
        self.add_widget(bottom_bar)
        
        # Автоматически загружаем новости при запуске
        Clock.schedule_once(lambda dt: self.load_news_thread(), 1)
    
    # ======== ФУНКЦИИ ========
    def load_news_thread(self, *args):
        """Запускает загрузку в отдельном потоке"""
        self.status_label.text = "⏳ Загрузка..."
        self.status_label.color = (1, 1, 0, 1)  # Желтый
        self.update_btn.disabled = True
        
        # Запускаем в потоке
        thread = threading.Thread(target=self.load_news)
        thread.daemon = True
        thread.start()
    
    def load_news(self):
        """Загружает новости с Pastebin"""
        try:
            req = urllib.request.Request(
                PASTEBIN_URL,
                headers={'User-Agent': 'Mozilla/5.0 (Android 13; Mobile) Kivy App'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                news_content = response.read().decode('utf-8')
            
            # Обновляем интерфейс
            Clock.schedule_once(lambda dt: self.update_news_text(news_content, success=True))
            
        except urllib.error.HTTPError as e:
            Clock.schedule_once(lambda dt: self.update_news_text(f"❌ Ошибка HTTP: {e.code}\n{e.reason}", error=True))
        except urllib.error.URLError as e:
            Clock.schedule_once(lambda dt: self.update_news_text(f"❌ Ошибка сети:\n{e.reason}", error=True))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.update_news_text(f"❌ Ошибка:\n{str(e)}", error=True))
    
    def update_news_text(self, text, success=False, error=False):
        """Обновляет текст новостей"""
        self.scroll_label.set_text(text)
        self.update_btn.disabled = False
        
        if success:
            self.status_label.text = "✅ Новости загружены"
            self.status_label.color = (0, 1, 0, 1)
        elif error:
            self.status_label.text = "❌ Ошибка"
            self.status_label.color = (1, 0, 0, 1)
    
    def show_info(self, instance):
        """Показывает информацию о программе"""
        info_text = """📱 SemkaApp

═════════════════════════════
     ИНФОРМАЦИЯ
═════════════════════════════

🔹 Новости загружаются с Pastebin
🔹 Сделано на Python + Kivy
🔹 Версия 0.3beta (Android)
🔹 Дизайн: Градиент

👨‍💻 Автор: @plsemen
📅 Год: 2026"""
        
        # Создаем всплывающее окно
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Используем обычный Label без сложных привязок
        info_label = Label(
            text=info_text,
            font_size=sp(14),
            halign='left',
            valign='top',
            size_hint_y=None,
            height=dp(300),  # Фиксированная высота
            text_size=(dp(250), None)
        )
        content.add_widget(info_label)
        
        btn = Button(
            text="OK",
            size_hint=(1, None),
            height=dp(50),
            background_color=(0.47, 0, 0.8, 1)
        )
        content.add_widget(btn)
        
        popup = Popup(
            title="ℹ О программе",
            content=content,
            size_hint=(0.8, 0.6),
            separator_color=(0.55, 0, 1, 1),
            title_color=(1, 1, 1, 1),
            title_size=sp(18)
        )
        
        btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def exit_app(self, instance):
        """Выход из приложения"""
        # Создаем диалог подтверждения
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        content.add_widget(Label(
            text="Вы действительно хотите выйти?",
            font_size=sp(16),
            size_hint_y=None,
            height=dp(50)
        ))
        
        buttons = BoxLayout(size_hint=(1, None), height=dp(50), spacing=dp(10))
        
        yes_btn = Button(text="Да", background_color=(1, 0, 0, 1))
        no_btn = Button(text="Нет", background_color=(0.5, 0.5, 0.5, 1))
        
        buttons.add_widget(yes_btn)
        buttons.add_widget(no_btn)
        content.add_widget(buttons)
        
        popup = Popup(
            title="Выход",
            content=content,
            size_hint=(0.7, 0.25),
            auto_dismiss=False,
            separator_color=(1, 0, 0, 1),
            title_color=(1, 1, 1, 1)
        )
        
        yes_btn.bind(on_press=lambda x: App.get_running_app().stop())
        no_btn.bind(on_press=popup.dismiss)
        
        popup.open()


# ======== ГЛАВНЫЙ КЛАСС ПРИЛОЖЕНИЯ ========
class SemkaApp(App):
    def build(self):
        self.title = "📢 SemkaApp"
        # Для тестирования на Windows
        Window.size = (450, 800)
        Window.clearcolor = (1, 1, 1, 1)
        return SemkaAppScreen()
    
    def on_start(self):
        print("=" * 50)
        print("SemkaApp by @plsemen (telegram)")
        print("Версия: 0.3beta (Android)")
        print("Дизайн: Градиент")
        print("=" * 50)


if __name__ == "__main__":
    SemkaApp().run()