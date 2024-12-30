# -*- coding: utf-8 -*-

import sys
import json
import random
from datetime import datetime
import os

# 禁用 libpng 警告
os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QLabel, QLineEdit, QPushButton,
                            QMessageBox)
from PyQt6.QtCore import Qt, QThread, QObject, pyqtSignal
from PyQt6.QtGui import QFont

from llm_helper.deep_seek_helper import get_word_meaning
from quest_generator import QuestGenerator

class WordTestApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("单词测试程序")
        self.setStyleSheet("""
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
        """)
        
        # 加载单词数据
        try:
            self.words_data = self.load_json_file('onlywords.json')
            if len(self.words_data) < 10:
                raise Exception("单词数据太少：需要至少10个单词")
            
            # 加载生词本
            try:
                with open('user/difficult_words.json', 'r', encoding='utf-8') as f:
                    self.difficult_words = json.load(f)
            except FileNotFoundError:
                self.difficult_words = {}
                
            # 加载已记住的单词
            try:
                with open('user/mastered_words.json', 'r', encoding='utf-8') as f:
                    self.mastered_words = json.load(f)
            except FileNotFoundError:
                self.mastered_words = []
        
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
            sys.exit(1)
            
        self.current_words = []
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
        
        # 开始新的测试
        self.start_new_test()
        
    def load_json_file(self, file_path):
        """从JSON文件中加载单词列表"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                words_list = json.load(f)
            
            if not isinstance(words_list, list) or not words_list:
                raise ValueError("文件格式不正确或为空")
            
            return words_list
        except json.JSONDecodeError:
            raise ValueError("JSON格式不正确")
        except IOError as e:
            raise IOError(f"无法读取文件：{e}")
        except Exception as e:
            raise Exception(f"加载单词数据时出错：{e}")
        
    def setup_gui(self):
        # 创建标题标签
        self.title_label = QLabel("英语单词测试")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.layout.addWidget(self.title_label)
        
        # 单词显示区域
        self.word_label = QLabel()
        self.word_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.word_label.setFont(QFont("Arial", 16))
        self.word_label.setWordWrap(True)
        self.word_label.setStyleSheet("""
            QLabel {
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                min-height: 100px;
            }
        """)
        self.layout.addWidget(self.word_label)
        
        # 答案输入区域
        input_layout = QHBoxLayout()
        
        self.answer_entry = QLineEdit()
        self.answer_entry.setPlaceholderText("请输入单词...")
        self.answer_entry.returnPressed.connect(self.check_answer)
        input_layout.addWidget(self.answer_entry)
        
        self.submit_btn = QPushButton("提交")
        self.submit_btn.clicked.connect(self.check_answer)
        input_layout.addWidget(self.submit_btn)
        
        self.dont_know_btn = QPushButton("不认识")
        self.dont_know_btn.setObjectName("dontKnowButton")
        self.dont_know_btn.clicked.connect(self.show_word_meaning)
        input_layout.addWidget(self.dont_know_btn)
        
        self.layout.addLayout(input_layout)
        
        # 进度和分数显示
        info_layout = QHBoxLayout()
        self.progress_label = QLabel()
        self.score_label = QLabel()
        info_layout.addWidget(self.progress_label)
        info_layout.addWidget(self.score_label)
        self.layout.addLayout(info_layout)
        
        # 统计信息显示
        stats_layout = QHBoxLayout()
        
        # 生词本统计
        self.difficult_words_label = QLabel()
        self.difficult_words_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_difficult_words_label()
        stats_layout.addWidget(self.difficult_words_label)
        
        # 已掌握单词统计
        self.mastered_words_label = QLabel()
        self.mastered_words_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_mastered_words_label()
        stats_layout.addWidget(self.mastered_words_label)
        
        self.layout.addLayout(stats_layout)
    
    def update_difficult_words_label(self):
        count = len(self.difficult_words)
        self.difficult_words_label.setText(f"生词本：{count}个")
        
    def update_mastered_words_label(self):
        count = len(self.mastered_words)
        total = len(self.words_data)
        percentage = (count / total * 100) if total > 0 else 0
        self.mastered_words_label.setText(f"已掌握：{count}/{total} ({percentage:.1f}%)")
    
    def show_word_meaning(self):
        if self.current_index >= len(self.current_words):
            return
            
        word = self.current_words[self.current_index]
        meaning = self.worker.get_word_meaning(word)

        # 添加到生词本
        self.difficult_words[word] = {
            "meaning": meaning,
            "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "review_count": 0
        }
        
        # 保存生词本
        with open('user/difficult_words.json', 'w', encoding='utf-8') as f:
            json.dump(self.difficult_words, f, ensure_ascii=False, indent=2)
        
        # 更新生词本统计
        self.update_difficult_words_label()
        
        # 显示单词的首字母
        QMessageBox.information(self, "单词", f"单词 {word} 已加入生词本")
        
        # 记录结果并进入下一个单词
        self.test_results.append({
            "word": word,
            "meaning": meaning,
            "user_answer": "不认识",
            "is_correct": False,
            "added_to_difficult": True
        })
        
        self.current_index += 1
        self.show_current_word()
    
    def start_new_test(self):
        # 从生词本和普通单词中各选择一部分
        
        # 从生词本中提取单词列表
        difficult_words_list = list(self.difficult_words.keys())
        regular_words_list = [word for word in self.words_data 
                            if word not in self.difficult_words]
        
        # 确定从每个来源选择多少个单词
        difficult_count = min(3, len(difficult_words_list))  # 生词本中选3个或更少
        regular_count = 10 - difficult_count  # 剩余的从普通单词中选择
        
        # 随机选择单词
        selected_difficult = random.sample(difficult_words_list, difficult_count) if difficult_count > 0 else []
        selected_regular = random.sample(regular_words_list, regular_count) if regular_count > 0 else []
        
        # 合并并打乱顺序
        self.current_words = selected_difficult + selected_regular
        random.shuffle(self.current_words)
        
        self.current_index = 0
        self.correct_count = 0
        self.test_results = []

        self.start_quest_task()

    def start_quest_task(self):
        # 创建线程和worker对象
        self.thread = QThread()
        self.worker = QuestGenerator()
        self.worker.moveToThread(self.thread)

        self.worker.add_words(self.current_words)

        # 将 Worker 移动到线程中
        self.thread.started.connect(self.worker.generate_quest)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # 启动线程
        self.thread.start()

    def update_progress(self, progress):
        if progress == 1:
            self.show_current_word()
        
    def show_current_word(self):
        if self.current_index < len(self.current_words):
            word = self.current_words[self.current_index]
            meaning = self.worker.get_word_meaning(word)
            hint = f"提示：单词以 {word[0].upper()} 开头，总长度为 {len(word)} 个字母"
            self.word_label.setText(f"{meaning}\n\n{hint}")
            self.progress_label.setText("进度：%d/10" % (self.current_index + 1))
            self.score_label.setText("当前得分：%d" % self.correct_count)
            self.answer_entry.clear()
            self.answer_entry.setFocus()
        else:
            self.save_results()
            self.show_final_score()
            
    def check_answer(self):
        if self.current_index >= len(self.current_words):
            return
            
        user_answer = self.answer_entry.text().strip().lower()
        word = self.current_words[self.current_index]
        meaning = self.worker.get_word_meaning(word)
        
        # 检查答案是否正确（完全匹配）
        is_correct = user_answer == word.lower()
        
        if is_correct:
            self.correct_count += 1
            self.answer_entry.setStyleSheet("background-color: #a8e6cf;")  # 绿色背景表示正确
            
            # 如果不在已掌握列表中，添加进去
            if word not in self.mastered_words:
                self.mastered_words.append(word)
                # 保存已掌握单词列表
                with open('user/mastered_words.json', 'w', encoding='utf-8') as f:
                    json.dump(self.mastered_words, f, ensure_ascii=False, indent=2)
                self.update_mastered_words_label()
            
            # 如果答对了生词本中的单词，增加复习次数
            if word in self.difficult_words:
                self.difficult_words[word]["review_count"] += 1
                # 如果复习次数达到3次，从生词本中移除
                if self.difficult_words[word]["review_count"] >= 3:
                    del self.difficult_words[word]
                    QMessageBox.information(self, "恭喜", f"单词 {word} 已经掌握，已从生词本中移除！")
                # 保存生词本
                with open('user/difficult_words.json', 'w', encoding='utf-8') as f:
                    json.dump(self.difficult_words, f, ensure_ascii=False, indent=2)
                self.update_difficult_words_label()
        else:
            self.answer_entry.setStyleSheet("background-color: #ffb3b3;")  # 红色背景表示错误
            # 显示答案时也只显示首字母
            QMessageBox.information(self, "答案", f"正确答案是：{word}")
        
        # 记录本次答题结果
        self.test_results.append({
            "word": word,
            "meaning": meaning,
            "user_answer": user_answer,
            "is_correct": is_correct,
            "added_to_difficult": False
        })
        
        # 延迟一下再显示下一个单词，让用户看到颜色反馈
        self.answer_entry.repaint()
        QApplication.processEvents()
        import time
        time.sleep(0.5)
        
        self.current_index += 1
        self.show_current_word()
        self.answer_entry.setStyleSheet("")  # 恢复默认样式
        
    def save_results(self):
        result_data = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "score": self.correct_count,
            "total": len(self.current_words),
            "details": self.test_results
        }
        
        try:
            # 读取现有结果
            try:
                with open('user/test_results.json', 'r', encoding='utf-8') as f:
                    all_results = json.load(f)
            except FileNotFoundError:
                all_results = []
                
            # 添加新的结果
            all_results.append(result_data)
            
            # 保存所有结果
            with open('user/test_results.json', 'w', encoding='utf-8') as f:
                json.dump(all_results, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            QMessageBox.warning(self, "警告", "保存结果时出错：" + str(e))
            
    def show_final_score(self):
        message = "测试完成！\n正确数量：%d/10\n得分：%d分" % (self.correct_count, self.correct_count * 10)
        reply = QMessageBox.question(self, "测试结果", message + "\n\n是否开始新的测试？",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.start_new_test()
        else:
            self.close()

def main():
    app = QApplication(sys.argv)
    window = WordTestApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
