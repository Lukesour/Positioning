/**
 * 智能留学选校规划系统 V1.5 - 前端JavaScript
 */

// 全局变量
let selectedCountries = [];
let targetMajors = [];
let practicalExperiences = [];
let configOptions = {};
let autocompleteOptions = {};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    loadConfigOptions();
    loadAutocompleteOptions();
    initializeForm();
    initializeCountrySelection();
    initializeExperienceManager();
    initializeTargetMajors();
    initializeSelectionFactors();
    initializeAutocomplete();
    initializeFormValidation();
    initializeStandardizedTests(); // V1.6.1 新增
});

/**
 * 加载配置选项
 */
async function loadConfigOptions() {
    try {
        const response = await fetch('/api/v1/config/options');
        configOptions = await response.json();
    } catch (error) {
        console.error('加载配置选项失败:', error);
        // 使用默认配置
        configOptions = {
            popular_universities: ['北京大学', '清华大学', '复旦大学'],
            popular_majors: ['计算机科学', '软件工程', '数据科学']
        };
    }
}

/**
 * 加载自动补全选项
 */
async function loadAutocompleteOptions() {
    try {
        const response = await fetch('/api/v1/autocomplete-options');
        autocompleteOptions = await response.json();
        console.log(`自动补全选项加载成功: ${autocompleteOptions.total_universities} 所院校, ${autocompleteOptions.total_majors} 个专业`);
    } catch (error) {
        console.error('加载自动补全选项失败:', error);
        // 使用默认配置
        autocompleteOptions = {
            universities: ['北京大学', '清华大学', '复旦大学', '上海交通大学', '浙江大学'],
            majors: ['计算机科学与技术', '软件工程', '电子信息工程', '机械工程', '金融学']
        };
    }
}

/**
 * 初始化表单
 */
function initializeForm() {
    const form = document.getElementById('schoolPlanningForm');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // 验证表单
        if (!validateForm()) {
            return;
        }
        
        // 提交表单
        submitForm();
    });
}

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
            
            // 验证表单
            validateForm();
        });
    });
}

/**
 * 初始化实践经历管理
 */
function initializeExperienceManager() {
    const addBtn = document.getElementById('add-experience-btn');
    const container = document.getElementById('experiences-container');
    
    addBtn.addEventListener('click', function() {
        addExperienceItem();
    });
}

/**
 * 添加实践经历项目
 */
function addExperienceItem(data = null) {
    const container = document.getElementById('experiences-container');
    const index = practicalExperiences.length;
    
    const experienceData = data || {
        organization: '',
        position: '',
        start_date: '',
        end_date: '',
        description: ''
    };
    
    const itemHtml = `
        <div class="dynamic-item" data-index="${index}">
            <button type="button" class="remove-btn" onclick="removeExperienceItem(${index})">×</button>
            <div class="row">
                <div class="col-md-6">
                    <div class="form-group">
                        <label class="form-label">公司/机构名称</label>
                        <input type="text" class="form-control experience-org" 
                               placeholder="如：腾讯科技" value="${experienceData.organization}">
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="form-group">
                        <label class="form-label">职位/角色</label>
                        <input type="text" class="form-control experience-position" 
                               placeholder="如：软件开发实习生" value="${experienceData.position}">
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <div class="form-group">
                        <label class="form-label">开始时间</label>
                        <input type="month" class="form-control experience-start" value="${experienceData.start_date}">
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="form-group">
                        <label class="form-label">结束时间</label>
                        <input type="month" class="form-control experience-end" value="${experienceData.end_date}">
                    </div>
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">核心职责与成果</label>
                <textarea class="form-control experience-desc" rows="3" 
                          placeholder="建议使用点句式，量化成果更佳，如：优化算法使系统响应速度提升 20%。">${experienceData.description}</textarea>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', itemHtml);
    practicalExperiences.push(experienceData);
    
    // 添加事件监听器
    const newItem = container.lastElementChild;
    addExperienceEventListeners(newItem, index);
}

/**
 * 为实践经历项目添加事件监听器
 */
function addExperienceEventListeners(item, index) {
    const inputs = item.querySelectorAll('input, textarea');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            updateExperienceData(index);
        });
    });
}

/**
 * 更新实践经历数据
 */
function updateExperienceData(index) {
    const item = document.querySelector(`[data-index="${index}"]`);
    if (!item) return;
    
    practicalExperiences[index] = {
        organization: item.querySelector('.experience-org').value,
        position: item.querySelector('.experience-position').value,
        start_date: item.querySelector('.experience-start').value,
        end_date: item.querySelector('.experience-end').value,
        description: item.querySelector('.experience-desc').value
    };
}

/**
 * 删除实践经历项目
 */
function removeExperienceItem(index) {
    const item = document.querySelector(`[data-index="${index}"]`);
    if (item) {
        item.remove();
        practicalExperiences.splice(index, 1);
        
        // 重新索引
        updateExperienceIndexes();
    }
}

/**
 * 更新实践经历索引
 */
function updateExperienceIndexes() {
    const items = document.querySelectorAll('#experiences-container .dynamic-item');
    items.forEach((item, index) => {
        item.setAttribute('data-index', index);
        const removeBtn = item.querySelector('.remove-btn');
        removeBtn.setAttribute('onclick', `removeExperienceItem(${index})`);
    });
}

/**
 * 初始化意向专业管理
 */
function initializeTargetMajors() {
    const input = document.getElementById('target-major-input');
    const list = document.getElementById('target-majors-list');
    const hiddenInput = document.getElementById('target_majors');
    
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            addTargetMajor(this.value.trim());
            this.value = '';
        }
    });
    
    // 使列表可排序
    makeSortable(list, updateTargetMajorsOrder);
}

/**
 * 添加意向专业
 */
function addTargetMajor(major) {
    if (!major || targetMajors.includes(major) || targetMajors.length >= 5) {
        return;
    }
    
    targetMajors.push(major);
    renderTargetMajors();
    updateTargetMajorsHidden();
    validateForm();
}

/**
 * 渲染意向专业列表
 */
function renderTargetMajors() {
    const list = document.getElementById('target-majors-list');
    list.innerHTML = '';
    
    targetMajors.forEach((major, index) => {
        const item = document.createElement('div');
        item.className = 'sortable-item';
        item.draggable = true;
        item.innerHTML = `
            <span><i class="fas fa-grip-vertical drag-handle"></i>${major}</span>
            <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeTargetMajor(${index})">
                <i class="fas fa-times"></i>
            </button>
        `;
        list.appendChild(item);
    });
}

/**
 * 删除意向专业
 */
function removeTargetMajor(index) {
    targetMajors.splice(index, 1);
    renderTargetMajors();
    updateTargetMajorsHidden();
    validateForm();
}

/**
 * 更新意向专业顺序
 */
function updateTargetMajorsOrder() {
    const items = document.querySelectorAll('#target-majors-list .sortable-item');
    const newOrder = [];
    
    items.forEach(item => {
        const text = item.querySelector('span').textContent.replace('', '').trim();
        newOrder.push(text);
    });
    
    targetMajors = newOrder;
    updateTargetMajorsHidden();
}

/**
 * 更新意向专业隐藏字段
 */
function updateTargetMajorsHidden() {
    const hiddenInput = document.getElementById('target_majors');
    hiddenInput.value = JSON.stringify(targetMajors);
}

/**
 * V1.6.1 新增：初始化标化成绩复选框逻辑
 */
function initializeStandardizedTests() {
    // 语言成绩复选框
    const languageCheckbox = document.getElementById('has_language_score');
    const languageInput = document.getElementById('language_score_text');
    
    if (languageCheckbox && languageInput) {
        languageCheckbox.addEventListener('change', function() {
            languageInput.disabled = !this.checked;
            if (!this.checked) {
                languageInput.value = '';
            }
        });
    }
    
    // GRE/GMAT成绩复选框
    const greCheckbox = document.getElementById('has_gre_score');
    const greInput = document.getElementById('gre_score_text');
    
    if (greCheckbox && greInput) {
        greCheckbox.addEventListener('change', function() {
            greInput.disabled = !this.checked;
            if (!this.checked) {
                greInput.value = '';
            }
        });
    }
}

/**
 * 初始化选校因素
 */
function initializeSelectionFactors() {
    const container = document.getElementById('selection-factors-container');
    const hiddenInput = document.getElementById('school_selection_factors');
    const enableCheckbox = document.getElementById('enable_selection_factors');
    
    // V1.6.1 更新：添加总开关逻辑
    if (enableCheckbox) {
        enableCheckbox.addEventListener('change', function() {
            if (this.checked) {
                container.classList.remove('disabled-sorting');
                // 启用拖拽排序
                makeSortable(container, updateSelectionFactors);
            } else {
                container.classList.add('disabled-sorting');
                // 清空选校偏好数据
                hiddenInput.value = '';
            }
        });
    }
}

/**
 * 更新选校因素 (V1.6.1 更新)
 */
function updateSelectionFactors() {
    const container = document.getElementById('selection-factors-container');
    const enableCheckbox = document.getElementById('enable_selection_factors');
    const hiddenInput = document.getElementById('school_selection_factors');
    
    // 只有在启用排序时才收集数据
    if (enableCheckbox && enableCheckbox.checked) {
        const items = container.querySelectorAll('.sortable-item');
        const selectedFactors = [];
        
        items.forEach(item => {
            selectedFactors.push(item.dataset.factor);
        });
        
        hiddenInput.value = JSON.stringify(selectedFactors);
    } else {
        hiddenInput.value = '';
    }
}

/**
 * 初始化自动补全功能
 */
function initializeAutocomplete() {
    // 院校自动补全 - 使用数据库数据
    setupAutocomplete('undergrad_school', 'school-suggestions', 'universities', true);
    
    // 专业自动补全 - 使用数据库数据
    setupAutocomplete('major', 'major-suggestions', 'majors', true);
    setupAutocomplete('target-major-input', 'target-major-suggestions', 'majors', true);
}

/**
 * 设置自动补全
 */
function setupAutocomplete(inputId, suggestionsId, dataKey, useDatabase = false) {
    const input = document.getElementById(inputId);
    const suggestions = document.getElementById(suggestionsId);
    
    if (!input || !suggestions) return;
    
    input.addEventListener('input', function() {
        const value = this.value.toLowerCase().trim();
        if (value.length < 1) {
            suggestions.style.display = 'none';
            return;
        }
        
        // 选择数据源
        let data = [];
        if (useDatabase && autocompleteOptions[dataKey]) {
            data = autocompleteOptions[dataKey];
        } else if (configOptions[dataKey]) {
            data = configOptions[dataKey];
        }
        
        // 过滤匹配项
        const filtered = data.filter(item => 
            item.toLowerCase().includes(value)
        ).slice(0, 8); // 限制显示8个建议
        
        if (filtered.length === 0) {
            suggestions.style.display = 'none';
            return;
        }
        
        // 构建建议列表
        suggestions.innerHTML = '';
        filtered.forEach(item => {
            const div = document.createElement('div');
            div.className = 'autocomplete-suggestion';
            
            // 高亮匹配的文本
            const regex = new RegExp(`(${value})`, 'gi');
            const highlightedText = item.replace(regex, '<strong>$1</strong>');
            div.innerHTML = highlightedText;
            
            div.addEventListener('click', function() {
                input.value = item;
                suggestions.style.display = 'none';
                
                // 触发input事件以更新验证状态
                input.dispatchEvent(new Event('input'));
                
                // 特殊处理意向专业输入
                if (inputId === 'target-major-input') {
                    addTargetMajor(item);
                    input.value = '';
                }
            });
            suggestions.appendChild(div);
        });
        
        suggestions.style.display = 'block';
    });
    
    // 键盘导航支持
    let selectedIndex = -1;
    input.addEventListener('keydown', function(e) {
        const suggestionItems = suggestions.querySelectorAll('.autocomplete-suggestion');
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedIndex = Math.min(selectedIndex + 1, suggestionItems.length - 1);
            updateSelection(suggestionItems, selectedIndex);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedIndex = Math.max(selectedIndex - 1, -1);
            updateSelection(suggestionItems, selectedIndex);
        } else if (e.key === 'Enter' && selectedIndex >= 0) {
            e.preventDefault();
            suggestionItems[selectedIndex].click();
        } else if (e.key === 'Escape') {
            suggestions.style.display = 'none';
            selectedIndex = -1;
        }
    });
    
    // 更新选中状态
    function updateSelection(items, index) {
        items.forEach((item, i) => {
            if (i === index) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }
    
    // 点击外部隐藏建议
    document.addEventListener('click', function(e) {
        if (!input.contains(e.target) && !suggestions.contains(e.target)) {
            suggestions.style.display = 'none';
            selectedIndex = -1;
        }
    });
}

/**
 * 使元素可排序
 */
function makeSortable(container, callback) {
    let draggedElement = null;
    
    // 确保所有sortable-item都有draggable属性
    const items = container.querySelectorAll('.sortable-item');
    items.forEach(item => {
        item.draggable = true;
        item.style.cursor = 'move';
    });
    
    container.addEventListener('dragstart', function(e) {
        if (e.target.classList.contains('sortable-item')) {
            draggedElement = e.target;
            e.target.style.opacity = '0.5';
            e.dataTransfer.effectAllowed = 'move';
        }
    });
    
    container.addEventListener('dragend', function(e) {
        if (e.target.classList.contains('sortable-item')) {
            e.target.style.opacity = '';
            draggedElement = null;
        }
    });
    
    container.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    });
    
    container.addEventListener('dragenter', function(e) {
        e.preventDefault();
    });
    
    container.addEventListener('drop', function(e) {
        e.preventDefault();
        
        if (draggedElement && e.target !== draggedElement) {
            // 找到最近的sortable-item
            let dropTarget = e.target;
            while (dropTarget && !dropTarget.classList.contains('sortable-item')) {
                dropTarget = dropTarget.parentElement;
            }
            
            if (dropTarget && dropTarget.classList.contains('sortable-item')) {
                const rect = dropTarget.getBoundingClientRect();
                const midpoint = rect.top + rect.height / 2;
                
                if (e.clientY < midpoint) {
                    container.insertBefore(draggedElement, dropTarget);
                } else {
                    container.insertBefore(draggedElement, dropTarget.nextSibling);
                }
                
                if (callback) callback();
            }
        }
    });
}

/**
 * 初始化表单验证
 */
function initializeFormValidation() {
    const form = document.getElementById('schoolPlanningForm');
    const submitBtn = document.getElementById('submit-btn');
    
    // 监听所有必填字段的变化
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        field.addEventListener('input', validateForm);
        field.addEventListener('change', validateForm);
    });
    
    // 初始验证
    validateForm();
}

/**
 * 验证表单
 */
function validateForm() {
    const form = document.getElementById('schoolPlanningForm');
    const submitBtn = document.getElementById('submit-btn');
    
    // 检查必填字段
    const requiredFields = [
        'undergrad_school',
        'school_tier', 
        'major',
        'gpa',
        'target_degree'
    ];
    
    let isValid = true;
    
    // 检查基本必填字段
    for (const fieldId of requiredFields) {
        const field = document.getElementById(fieldId);
        if (!field || !field.value.trim()) {
            isValid = false;
            break;
        }
    }
    
    // 检查国家选择
    if (selectedCountries.length === 0) {
        isValid = false;
    }
    
    // 检查意向专业
    if (targetMajors.length === 0) {
        isValid = false;
    }
    
    // 更新提交按钮状态
    if (isValid) {
        submitBtn.classList.add('enabled');
        submitBtn.disabled = false;
    } else {
        submitBtn.classList.remove('enabled');
        submitBtn.disabled = true;
    }
    
    return isValid;
}

/**
 * 收集表单数据
 */
function collectFormData() {
    // 解析语言成绩
    const languageScoreText = document.getElementById('language_score_text').value;
    let languageTest = '暂无';
    let languageScore = null;
    
    if (languageScoreText) {
        if (languageScoreText.toLowerCase().includes('toefl')) {
            languageTest = '托福';
            const match = languageScoreText.match(/(\d+(?:\.\d+)?)/);
            if (match) languageScore = parseFloat(match[1]);
        } else if (languageScoreText.toLowerCase().includes('ielts')) {
            languageTest = '雅思';
            const match = languageScoreText.match(/(\d+(?:\.\d+)?)/);
            if (match) languageScore = parseFloat(match[1]);
        }
    }
    
    // 解析GRE成绩
    const greScoreText = document.getElementById('gre_score_text').value;
    let greScore = null;
    if (greScoreText) {
        const match = greScoreText.match(/(\d+)/);
        if (match) greScore = parseInt(match[1]);
    }
    
    return {
        // 基本字段
        undergrad_school: document.getElementById('undergrad_school').value,
        school_tier: document.getElementById('school_tier').value,
        major: document.getElementById('major').value,
        gpa: document.getElementById('gpa').value,
        language_test: languageTest,
        language_score: languageScore,
        gre_score: greScore,
        target_degree: document.getElementById('target_degree').value,
        target_countries: selectedCountries,
        target_major: targetMajors[0] || '', // 保持向后兼容
        
        // V1.5 新增字段
        major_gpa: document.getElementById('major_gpa').value || null,
        exchange_experience: document.getElementById('exchange_experience').value === 'true',
        prerequisite_courses: document.getElementById('prerequisite_courses').value || null,
        practical_experiences: practicalExperiences.filter(exp => 
            exp.organization || exp.position || exp.description
        ),
        achievements: document.getElementById('achievements').value || null,
        target_majors: targetMajors,
        post_graduation_plan: document.getElementById('post_graduation_plan').value || null,
        school_selection_factors: JSON.parse(document.getElementById('school_selection_factors').value || '[]'),
        
        // V1.6.1 新增字段
        major_ranking: document.getElementById('major_ranking').value || null,
        budget: document.getElementById('budget').value || null
    };
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
        
        console.log('提交的表单数据:', formData);
        
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
        showError('提交失败: ' + error.message);
        hideLoading();
    }
}

/**
 * 显示加载状态
 */
function showLoading() {
    document.getElementById('formSection').style.display = 'none';
    document.getElementById('loadingSection').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';
}

/**
 * 隐藏加载状态
 */
function hideLoading() {
    document.getElementById('loadingSection').style.display = 'none';
}

/**
 * 显示结果
 */
function showResults(data) {
    hideLoading();
    
    document.getElementById('formSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'block';
    
    // 显示AI分析
    const analysisContent = document.getElementById('analysisContent');
    analysisContent.innerHTML = `
        <div class="mb-3">
            <h5>优势分析</h5>
            <p>${data.analysis_report.strengths}</p>
                </div>
        <div class="mb-3">
            <h5>劣势分析</h5>
            <p>${data.analysis_report.weaknesses}</p>
        </div>
        <div>
            <h5>提升建议</h5>
            <p>${data.analysis_report.suggestions}</p>
        </div>
    `;
    
    // 显示学校推荐
    const recommendationsContent = document.getElementById('recommendationsContent');
    let recommendationsHtml = '';
    
    const recommendations = data.analysis_report.recommendations;
    if (recommendations.reach && recommendations.reach.length > 0) {
        recommendationsHtml += '<h5>冲刺院校 (Reach)</h5>';
        recommendations.reach.forEach(school => {
            recommendationsHtml += `
                    <div class="school-recommendation">
                    <h6>${school.university}</h6>
                    <p><strong>项目:</strong> ${school.program}</p>
                    <p><strong>推荐理由:</strong> ${school.reason}</p>
                    </div>
                `;
            });
    }
    
    if (recommendations.target && recommendations.target.length > 0) {
        recommendationsHtml += '<h5>核心院校 (Target)</h5>';
        recommendations.target.forEach(school => {
            recommendationsHtml += `
                <div class="school-recommendation">
                    <h6>${school.university}</h6>
                    <p><strong>项目:</strong> ${school.program}</p>
                    <p><strong>推荐理由:</strong> ${school.reason}</p>
                </div>
            `;
        });
    }
    
    if (recommendations.safety && recommendations.safety.length > 0) {
        recommendationsHtml += '<h5>保底院校 (Safety)</h5>';
        recommendations.safety.forEach(school => {
            recommendationsHtml += `
                <div class="school-recommendation">
                    <h6>${school.university}</h6>
                    <p><strong>项目:</strong> ${school.program}</p>
                    <p><strong>推荐理由:</strong> ${school.reason}</p>
                </div>
            `;
        });
    }
    
    recommendationsContent.innerHTML = recommendationsHtml;
    
    // 显示相似案例
    const casesContent = document.getElementById('casesContent');
    let casesHtml = '';
    
    data.matched_cases.slice(0, 10).forEach(case_item => {
        casesHtml += `
                <div class="case-card">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6>${case_item.university}</h6>
                    <span class="similarity-score">${case_item.similarity_score ? case_item.similarity_score.toFixed(1) : 'N/A'}% 匹配</span>
                </div>
                <p><strong>项目:</strong> ${case_item.program}</p>
                <p><strong>背景:</strong> ${case_item.undergrad_school_tier || '未知'} ${case_item.undergrad_major || '未知专业'}</p>
                <p><strong>成绩:</strong> GPA ${case_item.gpa_scale_4 || 'N/A'}/4.0, ${case_item.language_type || ''} ${case_item.language_score || 'N/A'}</p>
            </div>
        `;
    });
    
    casesContent.innerHTML = casesHtml;
}

/**
 * 显示错误信息
 */
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    const formSection = document.getElementById('formSection');
    formSection.insertBefore(errorDiv, formSection.firstChild);
    
    // 3秒后自动移除错误信息
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 3000);
}

/**
 * 重置表单
 */
function resetForm() {
    // 重置所有变量
    selectedCountries = [];
    targetMajors = [];
    practicalExperiences = [];
    
    // 重置表单
    document.getElementById('schoolPlanningForm').reset();
    
    // 清除动态内容
    document.getElementById('experiences-container').innerHTML = '';
    document.getElementById('target-majors-list').innerHTML = '';
    
    // 重置国家选择
    document.querySelectorAll('.country-tag').forEach(tag => {
        tag.classList.remove('selected');
    });
    
    // 重置选校因素
    document.querySelectorAll('.factor-checkbox').forEach(checkbox => {
        checkbox.checked = false;
    });
    
    // 显示表单，隐藏结果
    document.getElementById('formSection').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('loadingSection').style.display = 'none';
    
    // 重新验证表单
    validateForm();
}