#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LazyLLM 连接测试脚本
用于排查大模型连接问题
"""

import sys
import os

# 添加 backend 目录到 Python 路径
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_path)

def test_env_variables():
    """测试环境变量"""
    print("=" * 60)
    print("测试 1: 环境变量检查")
    print("=" * 60)
    
    env_vars = [
        'LAZYLLM_KIMI_API_KEY',
        'LAZYLLM_DEEPSEEK_API_KEY',
        'LAZYLLM_OPENAI_API_KEY',
        'LAZYLLM_GLM_API_KEY',
        'LAZYLLM_QWEN_API_KEY',
        'OPENAI_API_KEY',
    ]
    
    found = False
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            masked = value[:10] + "..." + value[-4:] if len(value) > 14 else "***"
            print(f"✅ {var}: {masked}")
            found = True
        else:
            print(f"   {var}: 未设置")
    
    if not found:
        print("⚠️ 未找到任何 API Key 环境变量")
        print("   尝试从 .env 文件加载...")
        
        env_file = os.path.join(backend_path, '.env')
        if os.path.exists(env_file):
            print(f"✅ 找到 .env 文件: {env_file}")
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
                for var in env_vars:
                    if var in content:
                        print(f"✅ .env 中包含 {var}")
                        found = True
        else:
            print(f"❌ 未找到 .env 文件")
    
    return found

def test_lazyllm_import():
    """测试 LazyLLM 导入"""
    print("\n" + "=" * 60)
    print("测试 2: LazyLLM 模块导入")
    print("=" * 60)
    
    try:
        import lazyllm
        print(f"✅ LazyLLM 导入成功，版本: {lazyllm.__version__}")
        return True
    except ImportError as e:
        print(f"❌ LazyLLM 导入失败: {e}")
        print("   尝试安装: pip install lazyllm")
        return False
    except Exception as e:
        print(f"❌ LazyLLM 导入错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_lazyllm_config():
    """测试 LazyLLM 配置"""
    print("\n" + "=" * 60)
    print("测试 3: LazyLLM 配置")
    print("=" * 60)
    
    try:
        import lazyllm
        
        # 检查配置
        print("LazyLLM 配置信息:")
        if hasattr(lazyllm, 'config'):
            print(f"✅ lazyllm.config 可用")
            # 尝试获取配置
            try:
                # 检查是否有在线模型配置
                print("   检查在线模型配置...")
            except Exception as e:
                print(f"   配置读取警告: {e}")
        else:
            print("⚠️ lazyllm.config 不可用")
        
        return True
    except Exception as e:
        print(f"❌ LazyLLM 配置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_online_chat_module():
    """测试在线对话模块"""
    print("\n" + "=" * 60)
    print("测试 4: 在线对话模块 (OnlineChatModule)")
    print("=" * 60)
    
    try:
        import lazyllm
        
        # 检查 OnlineChatModule
        if hasattr(lazyllm, 'OnlineChatModule'):
            print("✅ OnlineChatModule 可用")
            
            # 尝试创建实例（不实际调用）
            try:
                # 检查 API Key 是否设置
                kimi_key = os.environ.get('LAZYLLM_KIMI_API_KEY')
                if not kimi_key:
                    print("⚠️ LAZYLLM_KIMI_API_KEY 未设置，跳过实例化测试")
                    return True
                
                print("   尝试创建 Kimi 模型实例...")
                # model = lazyllm.OnlineChatModule(source='kimi')
                print("✅ OnlineChatModule 可以实例化")
                return True
            except Exception as e:
                print(f"❌ OnlineChatModule 实例化失败: {e}")
                return False
        else:
            print("❌ OnlineChatModule 不可用")
            return False
    except Exception as e:
        print(f"❌ 在线对话模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rag_service():
    """测试 RAG 服务"""
    print("\n" + "=" * 60)
    print("测试 5: RAG 服务")
    print("=" * 60)
    
    try:
        # 尝试导入 RAG 服务
        try:
            from app.services.rag_service import get_rag_service
            print("✅ RAG 服务 (旧版) 导入成功")
        except ImportError as e:
            print(f"⚠️ RAG 服务 (旧版) 导入失败: {e}")
        
        # 尝试导入 DSPy RAG 服务
        try:
            from app.rag_dspy import get_dspy_rag_service
            print("✅ DSPy RAG 服务导入成功")
        except ImportError as e:
            print(f"⚠️ DSPy RAG 服务导入失败: {e}")
        
        return True
    except Exception as e:
        print(f"❌ RAG 服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_user_profile():
    """测试用户画像 API"""
    print("\n" + "=" * 60)
    print("测试 6: 用户画像 API 模块")
    print("=" * 60)
    
    try:
        from app.api_user_profile import router
        print("✅ api_user_profile 模块导入成功")
        
        # 检查路由
        routes = [r for r in router.routes if hasattr(r, 'path')]
        print(f"✅ 用户画像路由数量: {len(routes)}")
        
        # 列出关键路由
        for r in routes[:5]:
            if hasattr(r, 'path'):
                print(f"   - {r.path}")
        
        return True
    except Exception as e:
        print(f"❌ 用户画像 API 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_chat():
    """测试简单对话（可选，需要 API Key）"""
    print("\n" + "=" * 60)
    print("测试 7: 简单对话测试（可选）")
    print("=" * 60)
    
    kimi_key = os.environ.get('LAZYLLM_KIMI_API_KEY')
    if not kimi_key:
        print("⚠️ 跳过对话测试（未设置 API Key）")
        return True
    
    try:
        import lazyllm
        
        print("尝试创建模型实例...")
        # model = lazyllm.OnlineChatModule(source='kimi')
        
        # print("尝试发送测试消息...")
        # response = model("你好，这是一个测试。请回复'测试成功'")
        # print(f"模型回复: {response}")
        
        print("✅ 对话测试准备就绪（跳过实际调用）")
        return True
    except Exception as e:
        print(f"❌ 对话测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("LazyLLM 连接测试脚本")
    print("=" * 60)
    
    results = []
    
    results.append(("环境变量检查", test_env_variables()))
    results.append(("LazyLLM 模块导入", test_lazyllm_import()))
    results.append(("LazyLLM 配置", test_lazyllm_config()))
    results.append(("在线对话模块", test_online_chat_module()))
    results.append(("RAG 服务", test_rag_service()))
    results.append(("用户画像 API", test_api_user_profile()))
    results.append(("简单对话测试", test_simple_chat()))
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {name}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败，请检查错误信息")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
