# -*- coding: utf-8 -*-
"""
批量运行所有学科门类初始化脚本
"""

import sys
import os

backend_path = 'D:/github.com/carrotmet/zyplusv2/backend'
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
os.chdir(backend_path)

# 导入所有初始化模块
from app import (
    init_03_law,
    init_04_education,
    init_05_literature_chinese,
    init_05_literature_foreign_a,
    init_05_literature_foreign_b,
    init_06_history,
    init_07_science,
    init_08_engineering_a,
    init_08_engineering_b,
    init_09_agriculture,
    init_10_medicine,
    init_12_management,
    init_13_art,
)

def run_all():
    print("=" * 60)
    print("批量初始化所有学科门类数据")
    print("=" * 60)
    
    scripts = [
        ("03 法学", init_03_law.init_law_data),
        ("04 教育学", init_04_education.init_education_data),
        ("05 文学-中国语言文学与新闻传播", init_05_literature_chinese.init_literature_chinese_data),
        ("05 文学-外国语言文学A", init_05_literature_foreign_a.init_literature_foreign_a_data),
        ("05 文学-外国语言文学B", init_05_literature_foreign_b.init_literature_foreign_b_data),
        ("06 历史学", init_06_history.init_history_data),
        ("07 理学", init_07_science.init_science_data),
        ("08 工学-A部分", init_08_engineering_a.init_engineering_a_data),
        ("08 工学-B部分", init_08_engineering_b.init_engineering_b_data),
        ("09 农学", init_09_agriculture.init_data),
        ("10 医学", init_10_medicine.init_data),
        ("12 管理学", init_12_management.init_data),
        ("13 艺术学", init_13_art.init_data),
    ]
    
    success_count = 0
    fail_count = 0
    
    for name, init_func in scripts:
        print(f"\n{'='*60}")
        print(f"正在初始化: {name}")
        print('='*60)
        try:
            init_func()
            success_count += 1
            print(f"[成功] {name} 初始化完成")
        except Exception as e:
            fail_count += 1
            print(f"[失败] {name} 初始化出错: {e}")
    
    print("\n" + "=" * 60)
    print("初始化汇总")
    print("=" * 60)
    print(f"成功: {success_count} 个")
    print(f"失败: {fail_count} 个")
    print(f"总计: {len(scripts)} 个")
    print("=" * 60)

if __name__ == "__main__":
    run_all()
