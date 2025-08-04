/**
 * 智能留学选校规划系统 - 前端JavaScript
 */

// 全局变量
let selectedCountries = [];

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeCountrySelection();
    initializeForm();
    loadSystemStats();
});

/**
 * 初始化国家选择功能
 */
function initializeCountrySelection() {
    const countryTags = document.querySelectorAll('.country-tag');
    const hiddenInput = document.getElementById('target_countries');
    
    countryTags.forEach(tag => {
        tag.addEventListener('click', function() {
            const country = this.dataset.country;
            
            if (this.classList.contains('selected')) {
                // 取消选择
                this.classList.remove('selected');
                selectedCountries = selectedCountries.filter(c => c !== country);
            } else {
                // 选择
                this.classList.add('selected');
                selectedCountries.push(country);
            }
            
            // 更新隐藏输入框
            hiddenInput.value = selectedCountries.join(',');
            
            // 验证至少选择一个国家
            if (selectedCountries.length === 0) {
                hiddenInput.setCustomValidity('请至少选择一个意向国家/地区');
            } else {
                hiddenInput.setCustomValidity('');
            }
        });
    });
}

/**
 * 初始化表单
 */
function initializeForm() {
    const form = document.getElementById('schoolPlanningForm');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // 验证表单
        if (!form.checkValidity()) {
            form.classList.add('was-validated');
            return;
        }
        
        // 验证国家选择
        if (selectedCountries.length === 0) {
            showError('请至少选择一个意向国家/地区');
            return;
        }
        
        // 提交表单
        submitForm();
    });
    
    // 语言考试类型变化时的处理
    const languageTest = document.getElementById('language_test');
    const languageScore = document.getElementById('language_score');
    
    languageTest.addEventListener('change', function() {
        if (this.value === '暂无') {
            languageScore.disabled = true;
            languageScore.value = '';
            languageScore.required = false;
        } else {
            languageScore.disabled = false;
            languageScore.required = true;
        }
    });
}

/**
 * 提交表单
 */
async function submitForm() {
    try {
        // 显示加载状态
        showLoading();
        
        // 收集表单数据
        const formData = collectFormData();
        
        // 发送请求
        const response = await fetch('/api/v1/school-planning', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || '请求失败');
        }
        
        const result = await response.json();
        
        // 显示结果
        showResults(result);
        
    } catch (error) {
        console.error('提交失败:', error);
        hideLoading();
        showError('生成报告失败: ' + error.message);
    }
}

/**
 * 收集表单数据
 */
function collectFormData() {
    const languageScore = document.getElementById('language_score').value;
    const greScore = document.getElementById('gre_score').value;
    
    return {
        undergrad_school: document.getElementById('undergrad_school').value.trim(),
        school_tier: document.getElementById('school_tier').value,
        major: document.getElementById('major').value.trim(),
        gpa: document.getElementById('gpa').value.trim(),
        language_test: document.getElementById('language_test').value,
        language_score: languageScore ? parseFloat(languageScore) : null,
        gre_score: greScore ? parseInt(greScore) : null,
        target_degree: document.getElementById('target_degree').value,
        target_countries: selectedCountries,
        target_major: document.getElementById('target_major').value.trim()
    };
}

/**
 * 显示加载状态
 */
function showLoading() {
    document.getElementById('formSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('loadingSection').style.display = 'block';
}

/**
 * 隐藏加载状态
 */
function hideLoading() {
    document.getElementById('loadingSection').style.display = 'none';
    document.getElementById('formSection').style.display = 'block';
}

/**
 * 显示结果
 */
function showResults(data) {
    document.getElementById('loadingSection').style.display = 'none';
    document.getElementById('formSection').style.display = 'none';
    
    // 渲染分析报告
    renderAnalysisReport(data.analysis_report);
    
    // 渲染学校推荐
    renderRecommendations(data.analysis_report.recommendations);
    
    // 渲染相似案例
    renderCases(data.matched_cases);
    
    document.getElementById('resultsSection').style.display = 'block';
    
    // 滚动到结果区域
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
}

/**
 * 渲染分析报告
 */
function renderAnalysisReport(report) {
    const content = document.getElementById('analysisContent');
    
    content.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h5><i class="fas fa-thumbs-up text-success me-2"></i>您的优势</h5>
                <div class="p-3 bg-light rounded">
                    ${formatText(report.strengths)}
                </div>
            </div>
            <div class="col-md-6">
                <h5><i class="fas fa-exclamation-triangle text-warning me-2"></i>需要改进</h5>
                <div class="p-3 bg-light rounded">
                    ${formatText(report.weaknesses)}
                </div>
            </div>
        </div>
        <div class="mt-4">
            <h5><i class="fas fa-lightbulb text-info me-2"></i>提升建议</h5>
            <div class="p-3 bg-light rounded">
                ${formatText(report.suggestions)}
            </div>
        </div>
    `;
}

/**
 * 渲染学校推荐
 */
function renderRecommendations(recommendations) {
    const content = document.getElementById('recommendationsContent');
    
    const categories = [
        { key: 'reach', title: '冲刺院校', icon: 'fas fa-rocket', color: 'danger' },
        { key: 'target', title: '核心院校', icon: 'fas fa-bullseye', color: 'primary' },
        { key: 'safety', title: '保底院校', icon: 'fas fa-shield-alt', color: 'success' }
    ];
    
    let html = '<div class="row">';
    
    categories.forEach(category => {
        const schools = recommendations[category.key] || [];
        
        html += `
            <div class="col-md-4">
                <h5><i class="${category.icon} text-${category.color} me-2"></i>${category.title}</h5>
                <div class="recommendations-list">
        `;
        
        if (schools.length > 0) {
            schools.forEach(school => {
                html += `
                    <div class="school-recommendation">
                        <h6 class="mb-1">${school.university}</h6>
                        <p class="mb-1 text-muted small">${school.program}</p>
                        <p class="mb-0 small">${school.reason}</p>
                    </div>
                `;
            });
        } else {
            html += '<p class="text-muted">暂无推荐</p>';
        }
        
        html += '</div></div>';
    });
    
    html += '</div>';
    content.innerHTML = html;
}

/**
 * 渲染相似案例
 */
function renderCases(cases) {
    const content = document.getElementById('casesContent');
    
    if (!cases || cases.length === 0) {
        content.innerHTML = '<p class="text-muted">暂无相似案例</p>';
        return;
    }
    
    let html = '<div class="row">';
    
    cases.slice(0, 12).forEach(caseItem => {  // 只显示前12个案例
        html += `
            <div class="col-md-6 col-lg-4">
                <div class="case-card">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="mb-0">${caseItem.university}</h6>
                        ${caseItem.similarity_score ? 
                            `<span class="similarity-score">${caseItem.similarity_score.toFixed(1)}</span>` : 
                            ''
                        }
                    </div>
                    <p class="mb-2 text-primary small">${caseItem.program}</p>
                    <div class="case-details small text-muted">
                        <div><strong>本科:</strong> ${caseItem.undergrad_school || 'N/A'}</div>
                        <div><strong>专业:</strong> ${caseItem.undergrad_major || 'N/A'}</div>
                        <div><strong>GPA:</strong> ${caseItem.gpa_scale_4 ? caseItem.gpa_scale_4 + '/4.0' : 'N/A'}</div>
                        <div><strong>语言:</strong> ${formatLanguageScore(caseItem)}</div>
                        ${caseItem.gre_score ? `<div><strong>GRE:</strong> ${caseItem.gre_score}</div>` : ''}
                    </div>
                    ${caseItem.original_url ? 
                        `<a href="${caseItem.original_url}" target="_blank" class="btn btn-sm btn-outline-primary mt-2">
                            <i class="fas fa-external-link-alt me-1"></i>查看详情
                        </a>` : 
                        ''
                    }
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    
    if (cases.length > 12) {
        html += `<div class="text-center mt-3">
            <p class="text-muted">还有 ${cases.length - 12} 个相似案例...</p>
        </div>`;
    }
    
    content.innerHTML = html;
}

/**
 * 格式化语言成绩
 */
function formatLanguageScore(caseItem) {
    if (caseItem.language_type && caseItem.language_score) {
        return `${caseItem.language_type} ${caseItem.language_score}`;
    }
    return 'N/A';
}

/**
 * 格式化文本（处理换行等）
 */
function formatText(text) {
    if (!text) return '';
    return text.replace(/\n/g, '<br>');
}

/**
 * 显示错误信息
 */
function showError(message) {
    // 移除现有的错误信息
    const existingError = document.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // 创建错误信息元素
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-circle me-2"></i>
        ${message}
    `;
    
    // 插入到表单前面
    const formSection = document.getElementById('formSection');
    formSection.insertBefore(errorDiv, formSection.firstChild);
    
    // 3秒后自动移除
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.remove();
        }
    }, 5000);
}

/**
 * 重置表单
 */
function resetForm() {
    // 隐藏结果，显示表单
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('formSection').style.display = 'block';
    
    // 重置表单数据
    document.getElementById('schoolPlanningForm').reset();
    
    // 重置国家选择
    selectedCountries = [];
    document.querySelectorAll('.country-tag').forEach(tag => {
        tag.classList.remove('selected');
    });
    document.getElementById('target_countries').value = '';
    
    // 重置语言成绩输入框状态
    document.getElementById('language_score').disabled = false;
    document.getElementById('language_score').required = false;
    
    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * 加载系统统计信息
 */
async function loadSystemStats() {
    try {
        const response = await fetch('/api/v1/cases/count');
        if (response.ok) {
            const data = await response.json();
            console.log(`系统已收录 ${data.total_cases} 个成功案例`);
        }
    } catch (error) {
        console.log('加载统计信息失败:', error);
    }
}

/**
 * 工具函数：防抖
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}