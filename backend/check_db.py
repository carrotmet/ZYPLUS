#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查数据库表和内容"""

import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'), override=True)

from app.database import SessionLocal, DATABASE_FILE
from sqlalchemy import text
from app import models

print("=" * 60)
print("数据库检查工具")
print("=" * 60)
print(f"\n数据库文件: {DATABASE_FILE}")

session = SessionLocal()

# 1. 列出所有表
print("\n【数据库表列表】")
result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
tables = [row[0] for row in result]
for table in tables:
    print(f"  - {table}")

# 2. 查看 user_profiles 表（结构化信息主要存储在这里）
if 'user_profiles' in tables:
    print("\n【user_profiles 表 - 用户画像结构化信息】")
    result = session.execute(text("SELECT * FROM user_profiles LIMIT 5"))
    columns = result.keys()
    rows = result.fetchall()
    print(f"字段: {', '.join(columns)}")
    print(f"记录数: {len(rows)}")
    for row in rows:
        print(f"\n用户ID: {row.user_id}")
        print(f"  - 昵称: {row.nickname}")
        print(f"  - 霍兰德代码: {row.holland_code}")
        print(f"  - MBTI: {row.mbti_type}")
        print(f"  - 价值观: {row.value_priorities}")
        print(f"  - 能力评估: {row.ability_assessment}")
        print(f"  - 路径偏好: {row.career_path_preference}")
        print(f"  - 完整度: {row.completeness_score}%")

# 3. 查看 conversation_history 表（对话历史）
if 'conversation_history' in tables:
    print("\n【conversation_history 表 - 对话历史】")
    result = session.execute(text("SELECT COUNT(*) as cnt FROM conversation_history"))
    count = result.fetchone()[0]
    print(f"总记录数: {count}")
    
    if count > 0:
        result = session.execute(text("SELECT * FROM conversation_history ORDER BY timestamp DESC LIMIT 10"))
        print("\n最近10条对话记录:")
        for row in result:
            print(f"  [{row.timestamp}] {row.message_role}: {row.message_content[:50]}...")

# 4. 查看 users 表（用户账号信息）
if 'users' in tables:
    print("\n【users 表 - 用户账号信息】")
    result = session.execute(text("SELECT id, username, nickname, user_profile_id, created_at FROM users"))
    for row in result:
        print(f"  用户: {row.username} (ID:{row.id}), 画像ID: {row.user_profile_id}")

session.close()
print("\n" + "=" * 60)
print("检查完成")
print("=" * 60)
