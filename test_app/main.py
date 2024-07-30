from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.scrollview import ScrollView
from kivy.core.text import LabelBase
from kivy.uix.spinner import Spinner
import json
import os
import random

# Adjust the window size for better development experience
Window.size = (360, 640)

# Path to save the word list
WORD_LIST_FILE = 'word_list.json'

LabelBase.register(name='ComicNeue', fn_regular='fonts/ComicNeue.ttf')
LabelBase.register(name='Poppins', fn_regular='fonts/Poppins.ttf')

# Load word list from file
def load_word_list():
    if os.path.exists(WORD_LIST_FILE):
        with open(WORD_LIST_FILE, 'r') as file:
            return json.load(file)
    return []

# Save word list to file
def save_word_list(word_list):
    with open(WORD_LIST_FILE, 'w') as file:
        json.dump(word_list, file, indent=4)

# Define colors and font styles

BACKGROUND_COLOR_DARK = (0, 0, 0, 0)
PRIMARY_COLOR_LIGHT = (0.5, 0.5, 0.5, 1)
BLACK = (0.1, 0.1, 0.1, 1)
BUTTON_COLOR_DARK = (0.2, 0.2, 0.2, 1)
ERROR_COLOR_DARK = (0.9, 0.2, 0.2, 1)


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Top Bar with Search
        top_bar = BoxLayout(size_hint_y=None, height=60, spacing=10, padding=[10, 10], orientation='horizontal')
        self.update_top_bar_background(top_bar)
        layout.add_widget(top_bar)

        # Search bar
        self.search_bar = TextInput(hint_text='Search words...', size_hint=(0.8, None), height=40, multiline=False, font_name='Poppins')
        self.search_bar.bind(text=self.update_word_list)
        top_bar.add_widget(self.search_bar)

        # Create ScrollView for the word list
        self.scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height - 120))
        self.scroll_view.do_scroll_x = False
        self.scroll_view.do_scroll_y = True
        
        # Word list layout inside the ScrollView
        self.word_list_layout = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.word_list_layout.bind(minimum_height=self.word_list_layout.setter('height'))
        self.scroll_view.add_widget(self.word_list_layout)
        
        layout.add_widget(self.scroll_view)
        
        # Bottom button layout
        button_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        add_word_button = Button(text='+ Add Word', size_hint_x=None, width=150)
        add_word_button.bind(on_press=self.add_word)
        button_layout.add_widget(add_word_button)
        
        start_quiz_button = Button(text='Start Quiz', size_hint_x=None, width=150)
        start_quiz_button.bind(on_press=self.start_quiz)
        button_layout.add_widget(start_quiz_button)
        
        layout.add_widget(button_layout)
        self.add_widget(layout)
        self.update_word_list()

    def get_button_color(self):
        return BUTTON_COLOR_DARK

    def update_top_bar_background(self, top_bar):
        with top_bar.canvas.before:
            Color(*BACKGROUND_COLOR_DARK)
            self.rect_top_bar = Rectangle(size=top_bar.size, pos=top_bar.pos)
        top_bar.bind(size=self._update_top_bar_rect, pos=self._update_top_bar_rect)

    def _update_top_bar_rect(self, instance, value):
        self.rect_top_bar.pos = instance.pos
        self.rect_top_bar.size = instance.size


        self.word_list_layout.clear_widgets()
        search_text = self.search_bar.text.lower()
        for word, definition in word_list:
            if search_text in word.lower() or search_text in definition.lower():
                # Create a BoxLayout for each word entry
                box = BoxLayout(orientation='horizontal', size_hint_y=None, height=80, padding=10, spacing=10)
                
                # Set the background color
                with box.canvas.before:
                    Color(*BACKGROUND_COLOR_DARK)
                    self.rect_box = Rectangle(size=box.size, pos=box.pos)
                box.bind(size=self._update_box_rect, pos=self._update_box_rect)
                
                # Add the word label (centered)
                word_label = Label(
                    text=f'[b][color=ffffff]{word}[/color][/b]', 
                    markup=True, 
                    font_size='20sp', 
                    font_name='ComicNeue', 
                    size_hint_x=None, 
                    width=self.width * 0.6,  # Adjust width as needed
                    halign='center',
                    valign='middle'
                )
                word_label.bind(size=word_label.setter('text_size'))
                box.add_widget(word_label)
                
                # Add the definition label (right-aligned)
                definition_label = Label(
                    text=definition, 
                    font_size='14sp', 
                    font_name='Poppins', 
                    color=(1, 1, 1, 1),
                    size_hint_x=None, 
                    width=self.width * 0.4,  # Adjust width as needed
                    halign='right',
                    valign='middle'
                )
                definition_label.bind(size=definition_label.setter('text_size'))
                box.add_widget(definition_label)
                
                # Add the delete button
                delete_button_layout = BoxLayout(size_hint_y=None, height=50, padding=[0, 10, 0, 0])  # Padding at the top for some space
                delete_button = Button(
                text='Delete', 
                size_hint=(None, None), 
                width=80, 
                height=40, 
                background_color=ERROR_COLOR_DARK
                )
                delete_button.bind(on_press=lambda btn, w=word: self.delete_word(w))
                delete_button_layout.add_widget(delete_button)
                box.add_widget(delete_button_layout)
                
                # Add the BoxLayout to the word list layout
                self.word_list_layout.add_widget(box)

    def update_word_list(self, *args):
        self.word_list_layout.clear_widgets()
        search_text = self.search_bar.text.lower()
        for word, definition in word_list:
            if search_text in word.lower() or search_text in definition.lower():
                # Create a BoxLayout for each word entry
                box = BoxLayout(orientation='vertical', size_hint_y=None, height=140, padding=10, spacing=5)  # Adjusted spacing
                
                # Set the background color
                with box.canvas.before:
                    Color(*BACKGROUND_COLOR_DARK)
                    self.rect_box = Rectangle(size=box.size, pos=box.pos)
                box.bind(size=self._update_box_rect, pos=self._update_box_rect)
                
                # Add the word label (centered)
                word_label = Label(
                    text=f'[b][color=ffffff]{word}[/color][/b]', 
                    markup=True, 
                    font_size='20sp', 
                    font_name='ComicNeue', 
                    size_hint_y=None, 
                    height=40,
                    halign='center',
                    valign='middle'
                )
                word_label.bind(size=word_label.setter('text_size'))
                box.add_widget(word_label)
                
                # Add the definition label (left-aligned)
                definition_label = Label(
                    text=definition, 
                    font_size='14sp', 
                    font_name='Poppins', 
                    color=(1, 1, 1, 1),
                    size_hint_y=None, 
                    height=40,
                    halign='left',
                    valign='middle'
                )
                definition_label.bind(size=definition_label.setter('text_size'))
                box.add_widget(definition_label)
                
                # Add the delete button (below the definition)
                delete_button = Button(
                    text='Delete', 
                    size_hint_y=None, 
                    height=40,
                    width=80,
                    halign='left',
                    valign='middle',
                    background_color=ERROR_COLOR_DARK
                )
                delete_button.bind(on_press=lambda btn, w=word: self.delete_word(w))
                box.add_widget(delete_button)
                
                # Add the BoxLayout to the word list layout
                self.word_list_layout.add_widget(box)

    def _update_box_rect(self, instance, value):
        self.rect_box.pos = instance.pos
        self.rect_box.size = instance.size

        self.rect_box.pos = instance.pos
        self.rect_box.size = instance.size

        self.rect_box.pos = instance.pos
        self.rect_box.size = instance.size

        self.rect_box.pos = instance.pos
        self.rect_box.size = instance.size

    def delete_word(self, word):
        global word_list
        word_list = [item for item in word_list if item[0] != word]
        save_word_list(word_list)
        self.update_word_list()

    def add_word(self, instance):
        self.manager.current = 'add_word'

    def start_quiz(self, instance):
        self.manager.current = 'quiz'
    

class AddWordScreen(Screen):
    def __init__(self, **kwargs):
        super(AddWordScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.word_input = TextInput(hint_text='Enter word', size_hint_y=None, height=40, multiline=False)
        self.definition_input = TextInput(hint_text='Enter definition', size_hint_y=None, height=40, multiline=True)
        save_button = Button(text='Save', size_hint_y=None, height=50)
        save_button.bind(on_press=self.save_word)
        
        layout.add_widget(self.word_input)
        layout.add_widget(self.definition_input)
        layout.add_widget(save_button)
        
        self.add_widget(layout)

    def save_word(self, instance):
        word = self.word_input.text.strip()
        definition = self.definition_input.text.strip()
        if word and definition:
            if any(word == w for w, _ in word_list):
                self.show_popup('Error', 'This word already exists.')
            else:
                word_list.append((word, definition))
                save_word_list(word_list)
                self.word_input.text = ''
                self.definition_input.text = ''
                self.manager.current = 'main'
                self.manager.get_screen('main').update_word_list()
        else:
            self.show_popup('Error', 'Both fields must be filled.')

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.2))
        popup.open()

class QuizScreen(Screen):
    def __init__(self, **kwargs):
        super(QuizScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.question_label = Label(font_size='20sp', font_name='ComicNeue', halign='center', valign='middle')
        self.layout.add_widget(self.question_label)
        self.answer_input = TextInput(hint_text='Enter your answer', size_hint_y=None, height=40, multiline=False)
        self.layout.add_widget(self.answer_input)
        self.submit_button = Button(text='Submit', size_hint_y=None, height=50)
        self.submit_button.bind(on_press=self.check_answer)
        self.layout.add_widget(self.submit_button)
        self.add_widget(self.layout)
        self.current_word = None
        self.next_question()

    def next_question(self):
        if not word_list:
            self.show_popup('Info', 'No words available for the quiz.')
            self.manager.current = 'main'
            return
        self.current_word = random.choice(word_list)
        self.question_label.text = f'Define: {self.current_word[0]}'
        self.answer_input.text = ''

    def check_answer(self, instance):
        answer = self.answer_input.text.strip().lower()
        correct_answer = self.current_word[1].lower()
        if answer == correct_answer:
            self.show_popup('Correct!', 'Your answer is correct.')
        else:
            self.show_popup('Incorrect!', f'The correct answer is: {self.current_word[1]}')
        self.next_question()

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.2))
        popup.open()
        
    def __init__(self, **kwargs):
        super(QuizScreen, self).__init__(**kwargs)

        self.score = 0
        self.total_questions = 0
        self.current_word = None
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.question_label = Label(text='', size_hint_y=None, height=40)
        layout.add_widget(self.question_label)
        
        self.options_layout = BoxLayout(orientation='vertical', spacing=10)
        layout.add_widget(self.options_layout)
        
        finish_button = Button(text='Finish', size_hint_y=None, height=50)
        finish_button.bind(on_press=self.finish_quiz)
        layout.add_widget(finish_button)
        
        self.add_widget(layout)
        self.ask_question()


        
    def ask_question(self):
        if word_list:
            self.total_questions += 1
            self.current_word, correct_definition = random.choice(word_list)
            self.question_label.text = f'What is the definition of "{self.current_word}"?'
            definitions = [correct_definition] + [d for _, d in random.sample(word_list, min(3, len(word_list)))]
            random.shuffle(definitions)
            self.options_layout.clear_widgets()
            for definition in definitions:
                button = Button(text=definition, size_hint_y=None, height=50)
                button.bind(on_press=self.check_answer)
                self.options_layout.add_widget(button)

    def check_answer(self, button):
        if button.text == [d for _, d in word_list if _ == self.current_word][0]:
            self.score += 1
        self.ask_question()

    def finish_quiz(self, instance):
        popup = Popup(title='Quiz Finished', content=Label(text=f'Your score: {self.score}/{self.total_questions}'), size_hint=(0.8, 0.2))
        popup.open()
        self.manager.current = 'main'

class DictioQuizApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(AddWordScreen(name='add_word'))
        sm.add_widget(QuizScreen(name='quiz'))
        return sm

if __name__ == '__main__':
    word_list = load_word_list()
    DictioQuizApp().run()
