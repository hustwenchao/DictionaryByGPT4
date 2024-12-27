# -*- coding: utf-8 -*-

import json

def convert_to_simple_json():
    """将gptwords.json里面的单词提取出来，存放到一个 onlywords.json 文件中"""
    try:
        # 读取原始文件
        words_dict = []
        with open('gptwords.json', 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    word_obj = json.loads(line.strip())
                    word = word_obj['word']
                    words_dict.append(word)                    
                except (json.JSONDecodeError, KeyError):
                    continue

        # 保存到新文件
        with open('onlywords.json', 'w', encoding='utf-8') as f:
            json.dump(words_dict, f, ensure_ascii=False, indent=2)
            
        print(f"成功转换 {len(words_dict)} 个单词到 onlywords.json")
        
    except Exception as e:
        print(f"转换过程中出错: {e}")

if __name__ == "__main__":
    convert_to_simple_json()
