// 农业监控系统前端脚本
document.addEventListener('DOMContentLoaded', function() {
    // 初始化页面动画
    initializeAnimations();
    
    // 初始化图表
    initializeCharts();
    
    // 设置自动刷新
    setupAutoRefresh();
    
    // 初始化事件监听器
    setupEventListeners();
});

// 初始化页面动画
function initializeAnimations() {
    // 为卡片添加淡入动画
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
}

// 初始化图表
function initializeCharts() {
    // 如果Chart.js可用，初始化图表
    if (typeof Chart !== 'undefined') {
        initializeEnvironmentChart();
        initializePredictionChart();
    }
}

// 初始化环境数据图表
function initializeEnvironmentChart() {
    const ctx = document.getElementById('environmentChart');
    if (ctx) {
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '温度 (°C)',
                    data: [],
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.4
                }, {
                    label: '湿度 (%)',
                    data: [],
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// 初始化预测图表
function initializePredictionChart() {
    const ctx = document.getElementById('predictionChart');
    if (ctx) {
        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['蚜虫', '介壳虫', '红蜘蛛', '叶斑病', '白粉病', '锈病'],
                datasets: [{
                    label: '风险等级',
                    data: [0.7, 0.2, 0.3, 0.3, 0.6, 0.4],
                    borderColor: '#ffc107',
                    backgroundColor: 'rgba(255, 193, 7, 0.2)',
                    pointBackgroundColor: '#ffc107'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 1
                    }
                }
            }
        });
    }
}

// 设置自动刷新
function setupAutoRefresh() {
    // 每30秒刷新一次数据
    setInterval(function() {
        refreshData();
    }, 30000);
}

// 刷新数据
function refreshData() {
    // 刷新环境数据
    fetchEnvironmentData();
    
    // 刷新预测数据
    fetchPredictionData();
    
    // 更新最后更新时间
    updateLastUpdateTime();
}

// 获取环境数据
function fetchEnvironmentData() {
    fetch('/api/environmental-data')
        .then(response => response.json())
        .then(data => {
            updateEnvironmentDisplay(data);
        })
        .catch(error => {
            console.error('Error fetching environment data:', error);
        });
}

// 获取预测数据
function fetchPredictionData() {
    fetch('/api/predictions')
        .then(response => response.json())
        .then(data => {
            updatePredictionDisplay(data);
        })
        .catch(error => {
            console.error('Error fetching prediction data:', error);
        });
}

// 更新环境数据显示
function updateEnvironmentDisplay(data) {
    // 更新温度显示
    const tempElement = document.getElementById('currentTemp');
    if (tempElement && data.temperature) {
        tempElement.textContent = `${data.temperature[data.temperature.length - 1]}°C`;
    }
    
    // 更新湿度显示
    const humidityElement = document.getElementById('currentHumidity');
    if (humidityElement && data.humidity) {
        humidityElement.textContent = `${data.humidity[data.humidity.length - 1]}%`;
    }
}

// 更新预测数据显示
function updatePredictionDisplay(data) {
    // 更新风险等级
    const riskElement = document.getElementById('riskLevel');
    if (riskElement && data.risk_level) {
        riskElement.textContent = data.risk_level;
        riskElement.className = `badge bg-${getRiskColor(data.risk_level)}`;
    }
}

// 获取风险等级颜色
function getRiskColor(level) {
    switch(level) {
        case 'low': return 'success';
        case 'medium': return 'warning';
        case 'high': return 'danger';
        default: return 'secondary';
    }
}

// 更新最后更新时间
function updateLastUpdateTime() {
    const timeElement = document.getElementById('lastUpdate');
    if (timeElement) {
        timeElement.textContent = new Date().toLocaleTimeString();
    }
}

// 设置事件监听器
function setupEventListeners() {
    // 搜索功能
    const searchButton = document.getElementById('searchButton');
    if (searchButton) {
        searchButton.addEventListener('click', handleSearch);
    }
    
    // 刷新按钮
    const refreshButton = document.getElementById('refreshButton');
    if (refreshButton) {
        refreshButton.addEventListener('click', refreshData);
    }
    
    // 导出按钮
    const exportButton = document.getElementById('exportButton');
    if (exportButton) {
        exportButton.addEventListener('click', exportData);
    }
}

// 处理搜索
function handleSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        const query = searchInput.value.trim();
        if (query) {
            // 执行搜索逻辑
            console.log('搜索查询:', query);
        }
    }
}

// 导出数据
function exportData() {
    // 导出当前数据为CSV
    const data = getCurrentData();
    const csv = convertToCSV(data);
    downloadCSV(csv, 'agricultural_data.csv');
}

// 获取当前数据
function getCurrentData() {
    // 这里应该获取当前页面的数据
    return [];
}

// 转换为CSV格式
function convertToCSV(data) {
    if (!data || data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => row[header]).join(','))
    ].join('\n');
    
    return csvContent;
}

// 下载CSV文件
function downloadCSV(csvContent, filename) {
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

// 显示加载状态
function showLoading(element) {
    if (element) {
        element.innerHTML = '<div class="loading"><div class="spinner"></div>加载中...</div>';
    }
}

// 隐藏加载状态
function hideLoading(element, content) {
    if (element) {
        element.innerHTML = content;
    }
}

// 显示通知
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(notification, container.firstChild);
        
        // 自动隐藏通知
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// 格式化数字
function formatNumber(num, decimals = 2) {
    return parseFloat(num).toFixed(decimals);
}

// 格式化日期
function formatDate(date) {
    return new Date(date).toLocaleString('zh-CN');
}

// 工具函数：防抖
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