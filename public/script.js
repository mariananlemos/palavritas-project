// State variables
let datasets = {};
let activeTab = 'overview';
let charts = {};

// Colors for charts
const chartColors = {
    yellow: '#FFC80A',
    yellowLight: 'rgba(255, 200, 10, 0.2)',
    darkYellow: '#CC9C00',
    gray: '#9CA3AF',
    lightGray: '#F3F4F6',
    card: '#FFFFFF',
    border: '#E5E7EB',
    gridColor: '#F3F4F6',
    text: '#374151',
    white: '#FFFFFF',
    dark: '#0D0D0D',
    red: '#EF4444',
    emerald: '#10B981',
    blue: '#3B82F6',
    purple: '#8B5CF6'
};

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    loadAllData();
});

// Load all JSON datasets
async function loadAllData() {
    try {
        const [overall, cleaning, newsletter, hourly, device, demographics, words, streaks, foodDelivery] = await Promise.all([
            fetch('data/overall.json').then(r => r.json()),
            fetch('data/cleaning.json').then(r => r.json()),
            fetch('data/newsletter.json').then(r => r.json()),
            fetch('data/hourly.json').then(r => r.json()),
            fetch('data/device.json').then(r => r.json()),
            fetch('data/demographics.json').then(r => r.json()),
            fetch('data/words.json').then(r => r.json()),
            fetch('data/streaks.json').then(r => r.json()),
            fetch('data/food_delivery.json').then(r => r.json())
        ]);

        datasets = { overall, cleaning, newsletter, hourly, device, demographics, words, streaks, foodDelivery };
        
        // Populate DOM elements
        populateOverviewKPIs();
        populateCleaningLogs();
        populateWordsTable();
        
        // Initialize charts
        initNewsletterChart();
        initHourlyChart();
        initDemographicsChart();
        
        console.log("All data loaded and visualizations initialized.");
    } catch (error) {
        console.error("Error loading JSON datasets:", error);
    }
}

// Switch between tabs
function switchTab(tabId) {
    activeTab = tabId;
    
    // Hide all panes
    document.querySelectorAll('.tab-pane').forEach(el => el.classList.add('hidden'));
    
    // Show selected pane
    document.getElementById(`tab-content-${tabId}`).classList.remove('hidden');
    
    // Reset sidebar buttons classes
    document.querySelectorAll('aside nav button').forEach(btn => {
        btn.className = "w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left font-medium transition-all duration-200 text-tnGray hover:text-tnDark hover:bg-tnBorder";
    });
    
    // Set active button class
    document.getElementById(`btn-${tabId}`).className = "w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left font-medium transition-all duration-200 bg-tnYellow text-tnDark";
    
    // Update titles
    const titleMap = {
        'overview': { title: 'Visão Geral', sub: 'Resumo geral das métricas do produto e limpeza de dados.' },
        'newsletter': { title: 'Efeito Newsletter', sub: 'O impacto de abrir a newsletter na vitória e na retenção D30.' },
        'hourly': { title: 'Horários & Hábitos', sub: 'Análise temporal e mapeamento de hábitos do usuário.' },
        'demographics': { title: 'Perfil Demográfico', sub: 'Análise de segmentação de perfil socioeconômico contra a atividade D30.' },
        'words': { title: 'Palavras & Dificuldade', sub: 'Identificação de bugs de conteúdo e relevância de palavras na retenção.' }
    };
    
    document.getElementById('tab-title').innerText = titleMap[tabId].title;
    document.getElementById('tab-subtitle').innerText = titleMap[tabId].sub;

    // Close sidebar on mobile after choosing a tab
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
    if (sidebar && sidebar.classList.contains('translate-x-0')) {
        sidebar.classList.remove('translate-x-0');
        sidebar.classList.add('-translate-x-full');
        if (backdrop) backdrop.classList.add('hidden');
    }
}

// Populate OVERVIEW KPIs
function populateOverviewKPIs() {
    const o = datasets.overall;
    document.getElementById('kpi-sessions').innerText = o.total_sessions.toLocaleString('pt-BR');
    document.getElementById('kpi-users').innerText = o.total_users.toLocaleString('pt-BR');
    document.getElementById('kpi-win-rate').innerText = `${o.win_rate_pct}%`;
    document.getElementById('kpi-d1').innerText = `${o.d1_retention_pct}%`;
    document.getElementById('kpi-d30').innerText = `${o.d30_active_pct}%`;
}

// Populate OVERVIEW Cleaning Diagnostics
function populateCleaningLogs() {
    const c = datasets.cleaning;
    document.getElementById('clean-raw-sessions').innerText = c.raw_records.sessions.toLocaleString('pt-BR');
    document.getElementById('clean-removed-attempts').innerText = `-${c.anomalies_removed.invalid_sessions_attempts_count.toLocaleString('pt-BR')}`;
    document.getElementById('clean-removed-results').innerText = `-${c.anomalies_removed.missing_results_sessions_count.toLocaleString('pt-BR')}`;
    document.getElementById('clean-device-fixes').innerText = c.standardizations.device_casing_fixes.toLocaleString('pt-BR');
    document.getElementById('clean-delivery-fixes').innerText = c.standardizations.delivery_boolean_fixes.toLocaleString('pt-BR');
    document.getElementById('clean-final-sessions').innerText = c.cleaned_records.sessions.toLocaleString('pt-BR');
}

// Populate Words tab table
function populateWordsTable() {
    const words = datasets.words;
    const body = document.getElementById('words-table-body');
    body.innerHTML = '';
    
    // We will show the top 5 hardest and top 5 easiest
    const hardest = words.slice(0, 5);
    const easiest = words.slice(-5).reverse();
    
    const displayWords = [
        ...hardest.map((w, idx) => ({ ...w, type: 'Difícil', rank: idx + 1 })),
        ...easiest.map((w, idx) => ({ ...w, type: 'Fácil', rank: idx + 1 }))
    ];
    
    displayWords.forEach((w) => {
        const row = document.createElement('tr');
        row.className = "border-b border-tnBorder hover:bg-[#F9FAFB]";
        
        const badgeColor = w.type === 'Difícil' ? 'bg-red-50 text-red-600 border border-red-100' : 'bg-emerald-50 text-emerald-600 border border-emerald-100';
        
        row.innerHTML = `
            <td class="py-4 px-4 font-semibold text-tnGray">#${w.rank} ${w.type}</td>
            <td class="py-4 px-4 font-bold text-tnDark tracking-wide">${w.word}</td>
            <td class="py-4 px-4 text-right">
                <span class="px-2.5 py-1 rounded-full text-xs font-semibold ${badgeColor}">
                    ${w.win_rate.toFixed(1)}%
                </span>
            </td>
            <td class="py-4 px-4 text-right font-medium text-tnDark">${w.avg_attempts.toFixed(2)}</td>
            <td class="py-4 px-4 text-right font-semibold text-tnGray">${w.active_d30.toFixed(1)}%</td>
        `;
        body.appendChild(row);
    });
}

// Newsletter Chart init
function initNewsletterChart() {
    const ctx = document.getElementById('chart-newsletter').getContext('2d');
    const data = datasets.newsletter.by_open_before_game;
    
    // Group: 0 -> false (Não abriu), 1 -> true (Abriu)
    // We want to show Win Rate, D1 Retention, D30 Active
    const labels = ['Taxa de Vitória (%)', 'Retenção D1 (%)', 'Ativo D30 (%)'];
    
    const noOpen = data.find(d => !d.newsletter_open_before_game);
    const openBefore = data.find(d => d.newsletter_open_before_game);
    
    charts.newsletter = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Não abriu a newsletter',
                    data: [noOpen.win_rate, noOpen.played_next_day, noOpen.active_d30],
                    backgroundColor: chartColors.gray,
                    borderRadius: 8
                },
                {
                    label: 'Abriu a newsletter antes de jogar',
                    data: [openBefore.win_rate, openBefore.played_next_day, openBefore.active_d30],
                    backgroundColor: chartColors.yellow,
                    borderRadius: 8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: chartColors.text, font: { family: 'Outfit', size: 12 } }
                },
                tooltip: {
                    backgroundColor: chartColors.card,
                    borderColor: chartColors.border,
                    borderWidth: 1,
                    titleColor: chartColors.dark,
                    bodyColor: chartColors.text
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: chartColors.text, font: { family: 'Outfit' } }
                },
                y: {
                    max: 100,
                    grid: { color: chartColors.gridColor },
                    ticks: { color: chartColors.text, font: { family: 'Outfit' } }
                }
            }
        }
    });
}

// Hourly Chart init
function initHourlyChart() {
    const ctx = document.getElementById('chart-hourly').getContext('2d');
    const data = datasets.hourly.by_hour;
    
    const labels = data.map(d => `${d.session_hour.toString().padStart(2, '0')}h`);
    const sessions = data.map(d => d.sessions);
    const activeD30 = data.map(d => d.active_d30);
    
    charts.hourly = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Número de Partidas (Eixo Esq.)',
                    data: sessions,
                    borderColor: chartColors.gray,
                    backgroundColor: 'rgba(138, 138, 138, 0.1)',
                    yAxisID: 'y',
                    fill: true,
                    tension: 0.3,
                    borderWidth: 2
                },
                {
                    label: 'Ativos D30 (%) (Eixo Dir.)',
                    data: activeD30,
                    borderColor: chartColors.yellow,
                    backgroundColor: 'transparent',
                    yAxisID: 'y1',
                    fill: false,
                    tension: 0.3,
                    borderWidth: 3,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: chartColors.text, font: { family: 'Outfit', size: 12 } }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: chartColors.text, font: { family: 'Outfit' } }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    grid: { color: chartColors.gridColor },
                    ticks: { color: chartColors.text }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: { drawOnChartArea: false },
                    ticks: { color: chartColors.yellow, callback: (v) => `${v}%` },
                    min: 20,
                    max: 45
                }
            }
        }
    });
}

// Demographics Chart init
function initDemographicsChart() {
    const ctx = document.getElementById('chart-demographics').getContext('2d');
    
    charts.demographics = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Ativos D30 (%)',
                data: [],
                backgroundColor: chartColors.yellowLight,
                borderColor: chartColors.yellow,
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: chartColors.text, font: { family: 'Outfit', size: 11 } }
                },
                y: {
                    min: 0,
                    max: 45,
                    grid: { color: chartColors.gridColor },
                    ticks: { color: chartColors.text, callback: (v) => `${v}%` }
                }
            }
        }
    });
    
    // Trigger initial render
    updateDemographicsChart();
}

// Update Demographics Chart based on dropdown selection
function updateDemographicsChart() {
    const select = document.getElementById('demo-select');
    const value = select.value;
    const selectedText = select.options[select.selectedIndex].text;
    
    const demoData = datasets.demographics[value];
    const groupData = demoData.data;
    const pValue = demoData.stats.p_value;
    
    // Sort so chart looks clean
    groupData.sort((a, b) => b.active_d30 - a.active_d30);
    
    const labels = groupData.map(d => d[value]);
    const d30Values = groupData.map(d => d.active_d30);
    
    // Update chart
    charts.demographics.data.labels = labels;
    charts.demographics.data.datasets[0].data = d30Values;
    charts.demographics.update();
    
    // Update text
    document.getElementById('demo-chart-title').innerText = `Retenção D30 por ${selectedText}`;
    
    const sigElement = document.getElementById('demo-chart-sig');
    sigElement.innerText = `p-value: ${pValue.toFixed(4)} (${pValue < 0.05 ? 'Significativo' : 'Não Significativo'})`;
    sigElement.className = `text-xs font-semibold ${pValue < 0.05 ? 'text-emerald-600' : 'text-tnGray'}`;
}

// Toggle mobile sidebar
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
    if (!sidebar) return;
    
    if (sidebar.classList.contains('-translate-x-full')) {
        sidebar.classList.remove('-translate-x-full');
        sidebar.classList.add('translate-x-0');
        if (backdrop) backdrop.classList.remove('hidden');
    } else {
        sidebar.classList.remove('translate-x-0');
        sidebar.classList.add('-translate-x-full');
        if (backdrop) backdrop.classList.add('hidden');
    }
}
