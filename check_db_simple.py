#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单数据库查看工具 - 输出到文件避免编码问题
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from app.database import SessionLocal, engine
from sqlalchemy import inspect, text


def list_tables():
    """列出所有表"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("Database Tables:")
    print("-" * 50)
    
    categories = {
        'Core Data': ['disciplines', 'major_categories', 'majors', 'occupations', 'major_occupations', 'career_paths'],
        'User': ['users'],
        'User Profile': ['user_profiles', 'user_conversations', 'user_profile_logs', 'user_career_path_recommendations'],
        'Experience': ['personal_experiences', 'experience_shares'],
    }
    
    for cat, table_list in categories.items():
        print(f"\n{cat}:")
        for t in table_list:
            if t in tables:
                db = SessionLocal()
                count = db.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
                db.close()
                print(f"  - {t:<35} ({count} records)")


def export_table(table_name, output_file=None):
    """导出表数据到文件或打印"""
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    col_names = [c['name'] for c in columns]
    
    db = SessionLocal()
    result = db.execute(text(f"SELECT * FROM {table_name} LIMIT 100"))
    rows = result.fetchall()
    db.close()
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Table: {table_name}\n")
            f.write(f"Columns: {', '.join(col_names)}\n")
            f.write(f"Total: {len(rows)} records (showing max 100)\n")
            f.write("=" * 80 + "\n\n")
            
            for i, row in enumerate(rows, 1):
                f.write(f"Record #{i}:\n")
                for name, val in zip(col_names, row):
                    if val is not None:
                        val_str = str(val)[:200]  # 限制长度
                        f.write(f"  {name}: {val_str}\n")
                f.write("\n")
        print(f"Data exported to: {output_file}")
    else:
        # 简单打印
        print(f"\nTable: {table_name}")
        print(f"Columns: {', '.join(col_names)}")
        print(f"Records: {len(rows)}")
        
        for row in rows[:5]:
            print("-" * 50)
            for name, val in zip(col_names, row):
                if val is not None:
                    val_str = str(val)[:100]
                    print(f"  {name}: {val_str}")


def show_user_profiles():
    """显示用户画像"""
    db = SessionLocal()
    
    # 用户画像列表
    result = db.execute(text("""
        SELECT user_id, nickname, holland_code, mbti_type, 
               current_casve_stage, completeness_score
        FROM user_profiles 
        LIMIT 10
    """))
    rows = result.fetchall()
    
    print("\n" + "=" * 80)
    print("User Profiles")
    print("=" * 80)
    
    if not rows:
        print("No user profiles found.")
    else:
        for row in rows:
            print(f"\nUser ID: {row[0]}")
            print(f"  Nickname: {row[1] or 'N/A'}")
            print(f"  Holland: {row[2] or 'N/A'}")
            print(f"  MBTI: {row[3] or 'N/A'}")
            print(f"  CASVE Stage: {row[4]}")
            print(f"  Completeness: {row[5]}%")
    
    # 对话统计
    result = db.execute(text("""
        SELECT user_id, COUNT(*) as cnt 
        FROM user_conversations 
        GROUP BY user_id 
        ORDER BY cnt DESC 
        LIMIT 10
    """))
    conv_rows = result.fetchall()
    
    print("\n" + "=" * 80)
    print("Conversation Stats (Top 10)")
    print("=" * 80)
    for row in conv_rows:
        print(f"  {row[0]}: {row[1]} messages")
    
    db.close()


def show_schema(table_name):
    """显示表结构"""
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    
    print(f"\nSchema: {table_name}")
    print("-" * 60)
    print(f"{'Column':<25} {'Type':<20} {'Nullable':<10}")
    print("-" * 60)
    for col in columns:
        name = col['name']
        col_type = str(col['type'])
        nullable = 'YES' if col.get('nullable', True) else 'NO'
        print(f"{name:<25} {col_type:<20} {nullable:<10}")


def main():
    if len(sys.argv) < 2:
        list_tables()
        return
    
    arg = sys.argv[1]
    
    if arg == 'profile':
        show_user_profiles()
    elif arg == 'schema' and len(sys.argv) > 2:
        show_schema(sys.argv[2])
    elif arg == 'export' and len(sys.argv) > 2:
        table = sys.argv[2]
        outfile = sys.argv[3] if len(sys.argv) > 3 else f"{table}_export.txt"
        export_table(table, outfile)
    else:
        # 查看表数据
        export_table(arg)


if __name__ == '__main__':
    main()
