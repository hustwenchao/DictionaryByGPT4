import json
from datetime import datetime
import os

class WordManager:
    def __init__(self):
        self.words_data = []
        self.difficult_words = {}
        self.mastered_words = []
        self.current_words = []
        self.load_data()

    def load_data(self):
        """加载所有单词数据"""
        try:
            self.words_data = self.load_json_file("onlywords.json")
            if len(self.words_data) < 10:
                raise Exception("单词数据太少：需要至少10个单词")

            # 加载生词本
            try:
                with open("user/difficult_words.json", "r", encoding="utf-8") as f:
                    self.difficult_words = json.load(f)
            except FileNotFoundError:
                self.difficult_words = {}

            # 加载已记住的单词
            try:
                with open("user/mastered_words.json", "r", encoding="utf-8") as f:
                    self.mastered_words = json.load(f)
            except FileNotFoundError:
                self.mastered_words = []

        except Exception as e:
            raise Exception(f"加载单词数据时出错：{e}")

    def load_json_file(self, file_path):
        """从JSON文件中加载单词列表"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
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

    def add_to_difficult_words(self, word, meaning):
        """添加单词到生词本"""
        self.difficult_words[word] = {
            "meaning": meaning,
            "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "review_count": 0,
        }
        self.save_difficult_words()

    def add_to_mastered_words(self, word):
        """添加单词到已掌握列表"""
        if word not in self.mastered_words:
            self.mastered_words.append(word)
            self.save_mastered_words()

    def increment_review_count(self, word):
        """增加生词复习次数"""
        if word in self.difficult_words:
            self.difficult_words[word]["review_count"] += 1
            if self.difficult_words[word]["review_count"] >= 3:
                del self.difficult_words[word]
                self.save_difficult_words()
                return True
            self.save_difficult_words()
        return False

    def save_difficult_words(self):
        """保存生词本"""
        os.makedirs("user", exist_ok=True)
        with open("user/difficult_words.json", "w", encoding="utf-8") as f:
            json.dump(self.difficult_words, f, ensure_ascii=False, indent=2)

    def save_mastered_words(self):
        """保存已掌握的单词"""
        os.makedirs("user", exist_ok=True)
        with open("user/mastered_words.json", "w", encoding="utf-8") as f:
            json.dump(self.mastered_words, f, ensure_ascii=False, indent=2)

    def save_test_results(self, result_data):
        """保存测试结果"""
        try:
            os.makedirs("user", exist_ok=True)
            # 读取现有结果
            try:
                with open("user/test_results.json", "r", encoding="utf-8") as f:
                    all_results = json.load(f)
            except FileNotFoundError:
                all_results = []

            # 添加新的结果
            all_results.append(result_data)

            # 保存所有结果
            with open("user/test_results.json", "w", encoding="utf-8") as f:
                json.dump(all_results, f, ensure_ascii=False, indent=2)

        except Exception as e:
            raise Exception(f"保存结果时出错：{e}")

    def get_difficult_words_count(self):
        """获取生词本中的单词数量"""
        return len(self.difficult_words)

    def get_mastered_words_stats(self):
        """获取已掌握单词的统计信息"""
        count = len(self.mastered_words)
        total = len(self.words_data)
        percentage = (count / total * 100) if total > 0 else 0
        return count, total, percentage
