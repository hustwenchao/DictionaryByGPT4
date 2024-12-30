from llm_helper.deep_seek_helper import get_word_meaning

from PyQt6.QtCore import QObject, pyqtSignal

class QuestGenerator(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.words = []
        self.word_meanings = {}

    def add_words(self, words):
        for word in words:
            self.add_word(word)

    def add_word(self, word):
        self.words.append(word)

    def generate_quest(self):
        for i in range(len(self.words)):
            word = self.words[i]
            meaning = get_word_meaning(word)
            self.word_meanings[word] = meaning
            self.progress.emit(i)
        self.finished.emit()

    def get_word_meaning(self, word):
        return self.word_meanings[word]