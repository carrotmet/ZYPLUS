// 强制清除缓存的版本检查
// 如果看到这个错误，说明浏览器加载的是旧版本的api-service.js
// 解决方法：Ctrl+Shift+R 强制刷新页面，或清除浏览器缓存

// 版本标识 - 2026-01-29
const APP_VERSION = '2026-01-29-fix-v2';

console.log('[App] Version:', APP_VERSION);

// 检查 _convertToCamelCase 是否正确工作
function testCamelCase() {
    const testData = {
        major_categories: [
            {
                name: '测试类',
                majors: [
                    { name: '测试专业', main_courses: ['课程1', '课程2'] }
                ]
            }
        ]
    };
    
    // 转换
    const result = window.apiService._convertToCamelCase(testData);
    
    console.log('[Test] Original keys:', Object.keys(testData));
    console.log('[Test] Converted keys:', Object.keys(result));
    console.log('[Test] majorCategories exists:', 'majorCategories' in result);
    console.log('[Test] majors in category:', result.major_categories ? 'exists but wrong' : 'not found');
    console.log('[Test] majors in category:', result.majorCategories ? 'exists and correct' : 'not found');
    
    if (result.majorCategories && result.majorCategories[0].majors) {
        console.log('[Test] majors in first category:', result.majorCategories[0].majors);
    }
}

// 在控制台运行测试
window.testCamelCase = testCamelCase;
