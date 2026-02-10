#!/usr/bin/env python3
import sqlite3
import os

# 连接数据库
db_path = os.path.join(os.path.dirname(__file__), 'data', 'career_guidance.db')
print(f'Database path: {db_path}')
print(f'File exists: {os.path.exists(db_path)}')
print(f'File size: {os.path.getsize(db_path)} bytes')
print()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables in database:')
for t in tables:
    print(f'  - {t[0]}')
print()

# 查询用户画像 - 按完整度排序
if 'user_profiles' in [t[0] for t in tables]:
    cursor.execute('''
        SELECT user_id, nickname, holland_code, mbti_type, 
               career_path_preference, current_casve_stage,
               completeness_score, last_updated, value_priorities,
               ability_assessment, universal_skills, resilience_score
        FROM user_profiles
        ORDER BY completeness_score DESC, last_updated DESC
    ''')
    rows = cursor.fetchall()
    print(f'=== User Profiles ({len(rows)} records, sorted by completeness) ===')
    print()
    
    for row in rows:
        print(f'User ID: {row[0]}')
        print(f'  Nickname: {row[1]}')
        print(f'  Holland Code: {row[2]}')
        print(f'  MBTI Type: {row[3]}')
        print(f'  Career Path: {row[4]}')
        print(f'  CASVE Stage: {row[5]}')
        print(f'  Completeness: {row[6]}%')
        print(f'  Values: {row[8]}')
        print(f'  Abilities: {row[9]}')
        print(f'  Universal Skills: {row[10]}')
        print(f'  Resilience: {row[11]}')
        print(f'  Last Updated: {row[7]}')
        print()

# 查询更新日志
cursor.execute('''
    SELECT user_id, field_name, old_value, new_value, timestamp, update_type
    FROM user_profile_logs 
    ORDER BY timestamp DESC 
    LIMIT 15
''')
logs = cursor.fetchall()
print(f'=== Recent Update Logs ({len(logs)} records) ===')
for log in logs:
    print(f'{log[4]} | {log[0]} | [{log[5]}] {log[1]}: {log[2]} -> {log[3]}')

conn.close()
