from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class StyleSheet:
    """应用样式表"""
    MAIN_STYLE = """
        QMainWindow {
            background-color: #f0f2f5;
        }
        QLabel {
            color: #2c3e50;
        }
        QLineEdit {
            padding: 8px;
            border: 2px solid #bdc3c7;
            border-radius: 5px;
            background-color: white;
            font-size: 14px;
        }
        QLineEdit:focus {
            border-color: #3498db;
        }
        QPushButton {
            padding: 8px 15px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:pressed {
            background-color: #2472a4;
        }
        QPushButton#dontKnowButton {
            background-color: #e74c3c;
        }
        QPushButton#dontKnowButton:hover {
            background-color: #c0392b;
        }
    """

def create_title_label():
    """创建标题标签"""
    title_label = QLabel("英语单词测试")
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
    return title_label

def create_word_label():
    """创建单词显示标签"""
    word_label = QLabel()
    word_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    word_label.setFont(QFont("Arial", 16))
    word_label.setWordWrap(True)
    word_label.setStyleSheet("""
        QLabel {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            min-height: 100px;
        }
    """)
    return word_label

def create_input_layout(answer_entry, submit_btn, dont_know_btn):
    """创建输入区域布局"""
    input_layout = QHBoxLayout()
    
    answer_entry.setPlaceholderText("请输入单词...")
    dont_know_btn.setObjectName("dontKnowButton")
    
    input_layout.addWidget(answer_entry)
    input_layout.addWidget(submit_btn)
    input_layout.addWidget(dont_know_btn)
    
    return input_layout

def create_info_layout(progress_label, score_label):
    """创建信息显示布局"""
    info_layout = QHBoxLayout()
    info_layout.addWidget(progress_label)
    info_layout.addWidget(score_label)
    return info_layout

def create_stats_layout(difficult_words_label, mastered_words_label):
    """创建统计信息布局"""
    stats_layout = QHBoxLayout()
    
    difficult_words_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    mastered_words_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    stats_layout.addWidget(difficult_words_label)
    stats_layout.addWidget(mastered_words_label)
    
    return stats_layout
