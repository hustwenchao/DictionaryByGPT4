from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
)

class SettingsDialog(QDialog):
    """设置对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setModal(True)

        layout = QVBoxLayout()

        # 单词数量设置
        words_layout = QHBoxLayout()
        words_label = QLabel("每次学习的单词数量：")
        self.words_count = QSpinBox()
        self.words_count.setRange(5, 50)  # 设置范围从5到50个单词
        self.words_count.setValue(10)  # 默认值为10
        words_layout.addWidget(words_label)
        words_layout.addWidget(self.words_count)
        layout.addLayout(words_layout)

        # 确定和取消按钮
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)
