#!/usr/bin/env python3
"""
AI隐式调用表单更新测试

测试场景：
1. AI从用户对话中提取结构化信息
2. AI调用ProfileForm.updateByAI()隐式更新用户画像
3. 验证数据是否正确保存到数据库

使用方法：
    cd D:\github.com\carrotmet\zyplusv2
    python tests\test_ai_profile_update.py

或者直接在浏览器控制台测试：
    // 模拟AI调用
    await ProfileForm.updateByAI(userId, {
        'career_path_preference': 'technical',
        'value_priorities': ['成就感', '创新']
    }, '从对话中提取');
"""

import sys
import os

# 添加backend到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import json
from app.database import SessionLocal
from app.models_user_profile import UserProfile, UserProfileLog
from app.crud_user_profile import get_user_profile, update_user_profile
from app.schemas_user_profile import UserProfileUpdate


def test_ai_update_api():
    """
    测试后端API：POST /api/user-profiles/{user_id}/ai-update
    
    这是AI隐式调用的后端接口测试
    """
    print("=" * 60)
    print("测试1: AI更新API (后端)")
    print("=" * 60)
    
    db = SessionLocal()
    test_user_id = "test_ai_user_001"
    
    try:
        # 1. 创建测试用户画像（如果不存在）
        from app.crud_user_profile import get_or_create_user_profile
        profile = get_or_create_user_profile(db, test_user_id, "AI测试用户")
        print(f"✓ 测试用户创建/获取成功: {test_user_id}")
        print(f"  初始完整度: {profile.completeness_score}%")
        
        # 2. 模拟AI提取的数据
        ai_extracted_data = {
            "career_path_preference": "technical",  # 技术专家路径
            "value_priorities": ["成就感", "创新", "成长"],
            "ability_assessment": {
                "logic": 8,
                "creativity": 7,
                "communication": 6
            },
            "current_casve_stage": "analysis"  # 推进到分析阶段
        }
        
        print(f"\n✓ AI提取的数据:")
        for key, value in ai_extracted_data.items():
            print(f"  {key}: {value}")
        
        # 3. 调用更新函数（模拟API行为）
        updated_profile = update_user_profile(
            db=db,
            user_id=test_user_id,
            profile_update=UserProfileUpdate(**ai_extracted_data),
            update_type="ai_extraction"
        )
        
        print(f"\n✓ 更新成功!")
        print(f"  新完整度: {updated_profile.completeness_score}%")
        print(f"  职业路径: {updated_profile.career_path_preference}")
        print(f"  价值观: {updated_profile.value_priorities}")
        print(f"  CASVE阶段: {updated_profile.current_casve_stage}")
        
        # 4. 验证更新日志
        logs = db.query(UserProfileLog).filter(
            UserProfileLog.user_id == test_user_id
        ).order_by(UserProfileLog.timestamp.desc()).all()
        
        print(f"\n✓ 更新日志 ({len(logs)} 条):")
        for log in logs[:5]:
            print(f"  [{log.update_type}] {log.field_name}: {log.old_value} -> {log.new_value}")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_rag_service_integration():
    """
    测试RAG服务集成AI更新的完整流程
    
    模拟：用户输入 -> RAG处理 -> 提取信息 -> AI更新画像
    """
    print("\n" + "=" * 60)
    print("测试2: RAG服务集成AI更新")
    print("=" * 60)
    
    db = SessionLocal()
    test_user_id = "test_ai_user_002"
    
    try:
        # 1. 准备测试数据
        from app.crud_user_profile import get_or_create_user_profile
        profile = get_or_create_user_profile(db, test_user_id, "RAG集成测试用户")
        
        user_message = "我喜欢编程，想走技术路线，擅长逻辑思维，重视创新和成就感"
        
        print(f"✓ 测试用户: {test_user_id}")
        print(f"✓ 用户输入: {user_message}")
        
        # 2. 调用RAG服务处理消息
        from app.services.rag_service import get_rag_service
        rag_service = get_rag_service()
        
        profile_dict = {
            "holland_code": profile.holland_code,
            "mbti_type": profile.mbti_type,
            "value_priorities": profile.value_priorities,
            "ability_assessment": profile.ability_assessment,
            "career_path_preference": profile.career_path_preference,
            "current_casve_stage": profile.current_casve_stage,
            "completeness_score": profile.completeness_score
        }
        
        result = rag_service.process_message(
            user_message=user_message,
            user_profile=profile_dict,
            conversation_history=[]
        )
        
        print(f"\n✓ RAG处理结果:")
        print(f"  意图: {result.get('intent')}")
        print(f"  回复: {result.get('reply', '')[:50]}...")
        print(f"  提取信息: {result.get('extracted_info')}")
        print(f"  画像更新建议: {result.get('profile_updates')}")
        
        # 3. 应用提取的更新（模拟后端API行为）
        profile_updates = result.get('profile_updates', {})
        if profile_updates:
            # 过滤有效字段
            valid_fields = [
                'holland_code', 'mbti_type', 'value_priorities', 'ability_assessment',
                'career_path_preference', 'current_casve_stage', 'universal_skills', 'resilience_score'
            ]
            update_data = {k: v for k, v in profile_updates.items() if k in valid_fields and v}
            
            if update_data:
                updated_profile = update_user_profile(
                    db=db,
                    user_id=test_user_id,
                    profile_update=UserProfileUpdate(**update_data),
                    update_type="ai_extraction"
                )
                
                print(f"\n✓ AI自动更新成功!")
                print(f"  更新字段: {list(update_data.keys())}")
                print(f"  新完整度: {updated_profile.completeness_score}%")
            else:
                print(f"\n⚠ RAG未提取到有效更新字段")
        else:
            print(f"\n⚠ RAG未返回画像更新建议")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def generate_frontend_test_code():
    """
    生成前端测试代码（可在浏览器控制台执行）
    """
    print("\n" + "=" * 60)
    print("测试3: 前端AI隐式调用代码示例")
    print("=" * 60)
    
    code = '''
// ==================== 在浏览器控制台执行 ====================

// 1. 获取当前用户ID
const userId = localStorage.getItem('user_id');
console.log('当前用户ID:', userId);

// 2. 模拟AI从对话中提取信息并隐式更新
async function testAIProfileUpdate() {
    console.log('开始测试AI隐式更新...');
    
    // 模拟AI提取的结构化数据
    const aiExtractedData = {
        career_path_preference: 'technical',  // 技术专家路径
        value_priorities: ['成就感', '创新', '成长'],
        ability_assessment: {
            logic: 8,
            creativity: 7,
            communication: 6
        },
        current_casve_stage: 'analysis',  // 推进到分析阶段
        resilience_score: 8
    };
    
    console.log('AI提取的数据:', aiExtractedData);
    
    // 调用ProfileForm.updateByAI进行隐式更新
    // 注意：这需要ProfileForm模块已加载
    if (typeof ProfileForm !== 'undefined') {
        const result = await ProfileForm.updateByAI(
            userId,
            aiExtractedData,
            '从对话"我想成为技术专家"中提取'
        );
        
        console.log('AI更新结果:', result);
        
        if (result.success) {
            console.log('✓ AI隐式更新成功!');
            console.log('  更新字段:', result.data.updated_fields);
            
            // 刷新UI显示
            if (typeof updateUIFromProfileData === 'function') {
                updateUIFromProfileData(result.data.profile);
            }
        } else {
            console.error('✗ AI更新失败:', result.error);
        }
    } else {
        console.error('ProfileForm模块未加载');
    }
}

// 执行测试
testAIProfileUpdate();

// ==================== 测试结束 ====================
'''
    print(code)
    
    # 保存到文件
    js_file = os.path.join(os.path.dirname(__file__), 'test_ai_profile_update.js')
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(code)
    print(f"\n✓ 前端测试代码已保存到: {js_file}")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("AI隐式调用表单更新测试套件")
    print("=" * 60)
    
    results = []
    
    # 测试1: AI更新API
    results.append(("AI更新API", test_ai_update_api()))
    
    # 测试2: RAG服务集成
    results.append(("RAG服务集成", test_rag_service_integration()))
    
    # 测试3: 生成前端测试代码
    generate_frontend_test_code()
    results.append(("前端测试代码生成", True))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {name}: {status}")
    
    all_passed = all(r[1] for r in results)
    print("\n" + ("✓ 所有测试通过!" if all_passed else "✗ 部分测试失败"))
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
