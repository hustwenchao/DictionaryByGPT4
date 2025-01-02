import sys
import json
import random
import time
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QDialog,
    QScrollArea,
)
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtGui import QFont

from settings_dialog import SettingsDialog
from word_manager import WordManager
from gui_components import (
    StyleSheet,
    create_title_label,
    create_word_label,
    create_input_layout,
    create_info_layout,
    create_stats_layout,
)
from quest_generator import QuestGenerator


class WordTestApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("单词测试程序")
        self.setStyleSheet(StyleSheet.MAIN_STYLE)

        # 初始化单词管理器
        try:
            self.word_manager = WordManager()
        except Exception as e:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("错误")
            msg.setText(str(e))
            msg.setWindowFlags(msg.windowFlags())
            msg.exec()
            sys.exit(1)

        self.current_index = 0
        self.correct_count = 0
        self.test_results = []

        # 创建主窗口部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(30, 30, 30, 30)

        # 创建GUI元素
        self.setup_gui()
        self.resize(600, 500)

        # 加载设置
        try:
            with open("user/settings.json", "r", encoding="utf-8") as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            self.settings = {"words_per_test": 10}

        # 创建菜单栏
        self.create_menu_bar()

        # 开始新的测试
        self.start_new_test()

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        settings_menu = menubar.addMenu("设置")
        settings_action = settings_menu.addAction("首选项")
        settings_action.triggered.connect(self.show_settings)

    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self)
        dialog.words_count.setValue(self.settings.get("words_per_test", 10))

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.settings["words_per_test"] = dialog.words_count.value()
            # 保存设置
            with open("user/settings.json", "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)

            # 询问是否立即开始新的测试
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Question)
            msg.setWindowTitle("设置已更新")
            msg.setText("设置已保存。是否立即开始新的测试？")
            msg.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            msg.setWindowFlags(msg.windowFlags())
            if msg.exec() == QMessageBox.StandardButton.Yes:
                # 确保之前的线程已经清理
                if hasattr(self, "thread") and isinstance(self.thread, QThread):
                    if self.thread.isRunning():
                        self.thread.quit()
                        self.thread.wait()
                self.start_new_test()

    def setup_gui(self):
        """设置GUI界面"""
        # 创建标题标签
        self.title_label = create_title_label()
        self.layout.addWidget(self.title_label)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(200)  # 设置最小高度
        scroll_area.setStyleSheet(
            """
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c1c1c1;
                min-height: 30px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a8a8a8;
            }
        """
        )

        # 创建一个容器widget来放置word_label
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        # 单词显示区域
        self.word_label = QLabel()
        self.word_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.word_label.setFont(QFont("Arial", 14))  # 减小字体大小
        self.word_label.setWordWrap(True)
        self.word_label.setTextFormat(Qt.TextFormat.RichText)  # 启用富文本支持
        self.word_label.setStyleSheet(
            """
            QLabel {
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
        """
        )

        container_layout.addWidget(self.word_label)
        scroll_area.setWidget(container)
        self.layout.addWidget(scroll_area)

        # 答案输入区域
        self.answer_entry = QLineEdit()
        self.submit_btn = QPushButton("提交")
        self.dont_know_btn = QPushButton("不认识")

        self.answer_entry.returnPressed.connect(self.check_answer)
        self.submit_btn.clicked.connect(self.check_answer)
        self.dont_know_btn.clicked.connect(self.show_word_meaning)

        input_layout = create_input_layout(
            self.answer_entry, self.submit_btn, self.dont_know_btn
        )
        self.layout.addLayout(input_layout)

        # 进度和分数显示
        self.progress_label = QLabel()
        self.score_label = QLabel()
        info_layout = create_info_layout(self.progress_label, self.score_label)
        self.layout.addLayout(info_layout)

        # 统计信息显示
        self.difficult_words_label = QLabel()
        self.mastered_words_label = QLabel()
        self.update_difficult_words_label()
        self.update_mastered_words_label()
        stats_layout = create_stats_layout(
            self.difficult_words_label, self.mastered_words_label
        )
        self.layout.addLayout(stats_layout)

    def update_difficult_words_label(self):
        """更新生词本标签"""
        count = self.word_manager.get_difficult_words_count()
        self.difficult_words_label.setText(f"生词本：{count}个")

    def update_mastered_words_label(self):
        """更新已掌握单词标签"""
        count, total, percentage = self.word_manager.get_mastered_words_stats()
        self.mastered_words_label.setText(
            f"已掌握：{count}/{total} ({percentage:.1f}%)"
        )

    def show_word_meaning(self):
        """显示单词含义"""
        if self.current_index >= len(self.word_manager.current_words):
            return

        word = self.word_manager.current_words[self.current_index]
        meaning = self.worker.get_word_meaning(word)

        # 添加到生词本
        self.word_manager.add_to_difficult_words(word, meaning)
        self.update_difficult_words_label()

        # 显示提示信息
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("单词")
        msg.setText(f"单词 {word} 已加入生词本")
        msg.setWindowFlags(msg.windowFlags())
        msg.exec()

        # 记录结果并进入下一个单词
        self.test_results.append(
            {
                "word": word,
                "meaning": meaning,
                "user_answer": "不认识",
                "is_correct": False,
                "added_to_difficult": True,
            }
        )

        self.current_index += 1
        self.show_current_word()

    def start_new_test(self):
        """开始新的测试"""
        self.word_manager.current_words = self.select_test_words()
        self.current_index = 0
        self.correct_count = 0
        self.test_results = []
        self.start_quest_task()

    def select_test_words(self):
        """选择测试单词"""
        words_per_test = self.settings.get("words_per_test", 10)
        difficult_words_list = list(self.word_manager.difficult_words.keys())
        regular_words_list = [
            word
            for word in self.word_manager.words_data
            if word not in self.word_manager.difficult_words
        ]

        # 计算生词和普通单词的比例
        difficult_count = min(
            int(words_per_test * 0.3), len(difficult_words_list)
        )  # 30%是生词
        regular_count = words_per_test - difficult_count  # 剩余的是普通单词

        selected_difficult = (
            random.sample(difficult_words_list, difficult_count)
            if difficult_count > 0
            else []
        )
        selected_regular = (
            random.sample(regular_words_list, regular_count)
            if regular_count > 0
            else []
        )

        words = selected_difficult + selected_regular
        random.shuffle(words)
        return words

    def start_quest_task(self):
        """启动问题生成任务"""
        # 确保之前的线程已经清理
        if hasattr(self, "thread") and isinstance(self.thread, QThread):
            if self.thread.isRunning():
                self.thread.quit()
                self.thread.wait()

        self.thread = QThread()
        self.worker = QuestGenerator()
        self.worker.moveToThread(self.thread)

        self.worker.add_words(self.word_manager.current_words)

        self.thread.started.connect(self.worker.generate_quest)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def update_progress(self, progress):
        """更新进度"""
        if progress == 1:
            self.show_current_word()

    def show_current_word(self):
        """显示当前单词"""
        if self.current_index < len(self.word_manager.current_words):
            word = self.word_manager.current_words[self.current_index]
            meaning = self.worker.get_word_meaning(word)
            # 使用HTML格式化文本
            formatted_meaning = (
                "<div style='text-align: left; margin-bottom: 20px;'>"
                + meaning.replace("\n", "<br>")
                + "</div>"
            )
            hint = (
                "<div style='text-align: center; margin-top: 10px; font-size: 15px;'>"
                "提示：单词以 <span style='color: #3498db; font-weight: bold;'>"
                f"{word[0]}</span> 开头，总长度为 "
                f"<span style='color: #e74c3c; font-weight: bold;'>{len(word)}</span> 个字母"
                "</div>"
            )

            self.word_label.setText(f"{formatted_meaning}{hint}")
            total_words = len(self.word_manager.current_words)
            self.progress_label.setText(f"进度：{self.current_index + 1}/{total_words}")
            self.score_label.setText(f"当前得分：{self.correct_count}")

            self.answer_entry.clear()
            self.answer_entry.setFocus()
        else:
            self.save_results()
            self.show_final_score()

    def check_answer(self):
        """检查答案"""
        if self.current_index >= len(self.word_manager.current_words):
            return

        user_answer = self.answer_entry.text().strip().lower()
        word = self.word_manager.current_words[self.current_index]
        meaning = self.worker.get_word_meaning(word)
        is_correct = user_answer == word.lower()

        if is_correct:
            self.correct_count += 1
            self.answer_entry.setStyleSheet("background-color: #a8e6cf;")

            # 添加到已掌握列表
            self.word_manager.add_to_mastered_words(word)
            self.update_mastered_words_label()

            # 处理生词本中的单词
            if word in self.word_manager.difficult_words:
                if self.word_manager.increment_review_count(word):
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.setWindowTitle("恭喜")
                    msg.setText(f"单词 {word} 已经掌握，已从生词本中移除！")
                    msg.setWindowFlags(msg.windowFlags())
                    msg.exec()
                self.update_difficult_words_label()
        else:
            self.answer_entry.setStyleSheet("background-color: #ffb3b3;")
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("答案")
            msg.setText(f"正确答案是：{word}")
            msg.setWindowFlags(msg.windowFlags())
            msg.exec()

        # 记录本次答题结果
        self.test_results.append(
            {
                "word": word,
                "meaning": meaning,
                "user_answer": user_answer,
                "is_correct": is_correct,
                "added_to_difficult": False,
            }
        )

        # 延迟显示下一个单词
        self.answer_entry.repaint()
        QApplication.processEvents()
        time.sleep(0.5)

        self.current_index += 1
        self.show_current_word()
        self.answer_entry.setStyleSheet("")

    def save_results(self):
        """保存测试结果"""
        result_data = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "score": self.correct_count,
            "total": len(self.word_manager.current_words),
            "details": self.test_results,
        }

        try:
            self.word_manager.save_test_results(result_data)
        except Exception as e:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("警告")
            msg.setText("保存结果时出错：" + str(e))
            msg.setWindowFlags(msg.windowFlags())
            msg.exec()

    def show_final_score(self):
        """显示最终得分"""
        message = f"测试完成！\n正确数量：{self.correct_count}/{len(self.word_manager.current_words)}\n得分：{self.correct_count * 10}分"
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle("测试结果")
        msg.setText(message + "\n\n是否开始新的测试？")
        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg.setWindowFlags(msg.windowFlags())
        reply = msg.exec()

        if reply == QMessageBox.StandardButton.Yes:
            self.start_new_test()
        else:
            self.close()

    def closeEvent(self, event):
        """窗口关闭事件"""
        if hasattr(self, "thread") and isinstance(self.thread, QThread):
            if self.thread.isRunning():
                self.thread.quit()
                self.thread.wait()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = WordTestApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
