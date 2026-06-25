import re

with open("c:/Users/JIGISHA GAJJAR/OneDrive/Desktop/ARISE/index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update appState
content = content.replace(
"""            filters: { search: '', category: 'all', shelf: 'all', analyticsPeriod: '7d', analyticsProduct: 'all', stockLevel: 'all', view: 'grid', analyticsTab: 'trend', demandView: 'day' },
            robot: { active: false, interval: null, currentTarget: null }""",
"""            filters: { search: '', category: 'all', shelf: 'all', analyticsPeriod: '7d', analyticsProduct: 'all', stockLevel: 'all', view: 'grid', analyticsTab: 'trend', demandView: 'day', dashTrendPeriod: '7d', productTrendPeriod: '30d' },
            currentProduct: null,
            robot: { active: false, interval: null, currentTarget: null }""")

# 2. Update pages
content = content.replace(
"""            procurement: renderProcurement,
            profile: renderProfile,
            settings: renderSettings
        };""",
"""            procurement: renderProcurement,
            profile: renderProfile,
            settings: renderSettings,
            product: renderProduct
        };""")

# 3. Update navigate initCharts execution
content = content.replace(
"""                if(path === 'dashboard' || path === 'analytics') initCharts(path);""",
"""                if(['dashboard', 'analytics', 'product'].includes(path)) initCharts(path);""")

# 4. Modify Dash Chart Header
content = content.replace(
"""                    <div class="card">
                        <div class="card-header">
                            <span class="card-title"><i data-lucide="line-chart"></i> Fleet Activity & Turnover Trend</span>
                        </div>
                        <div style="height: 300px; width: 100%;"><canvas id="dashTrendChart"></canvas></div>
                    </div>""",
"""                    <div class="card">
                        <div class="card-header" style="justify-content: space-between;">
                            <span class="card-title"><i data-lucide="line-chart"></i> Fleet Activity & Turnover Trend</span>
                            <select class="form-control" style="width: auto; padding: 2px 6px; font-size: 0.75rem;" onchange="appState.filters.dashTrendPeriod=this.value; initCharts('dashboard')">
                                <option value="7d" ${appState.filters.dashTrendPeriod==='7d'?'selected':''}>Last 7 Days</option>
                                <option value="30d" ${appState.filters.dashTrendPeriod==='30d'?'selected':''}>Last 1 Month</option>
                                <option value="1y" ${appState.filters.dashTrendPeriod==='1y'?'selected':''}>Last 1 Year</option>
                            </select>
                        </div>
                        <div style="height: 300px; width: 100%;"><canvas id="dashTrendChart"></canvas></div>
                    </div>""")

# 5. Extract and Replace openProductDetail and add renderProduct
match_detail = re.search(r'// --- PRODUCT DETAILS MODAL ---[\s\S]*?function adjustQty\(id, d\) \{', content)
if match_detail:
    new_detail = """// --- PRODUCT DETAILS PAGE ---
        function openProductDetail(id) {
            appState.currentProduct = id;
            navigate('product');
        }

        function renderProduct() {
            if(!appState.currentProduct) return `<div class="empty-state">No Sector/Product selected. Validate global index.</div>`;
            const item = appState.inventory.find(i=>i.id===appState.currentProduct);
            if(!item) return `<div class="empty-state">Product matrix disconnected.</div>`;
            const p = runPrediction(item);
            const pct = Math.round((item.qty/item.cap)*100);
            
            return `
                <div class="page-layout" style="grid-template-columns: 1fr; margin-bottom: 2rem;">
                    <button class="btn btn-outline mini-btn" onclick="window.history.back()" style="align-self: flex-start; margin-bottom:1.5rem;"><i data-lucide="arrow-left" style="width:14px; height: 14px;"></i> Array Return</button>
                    
                    <div class="card" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap: 1rem;">
                        <div style="display:flex; align-items:center; gap: 1.5rem;">
                            <div style="width: 60px; height: 60px; background: rgba(74, 222, 128, 0.1); border-radius: 8px; border: 1px solid var(--primary); display:flex; align-items:center; justify-content:center; font-size: 1.8rem; font-family:monospace; color:var(--primary); font-weight:bold;">${item.id}</div>
                            <div>
                                <p style="color:var(--primary); font-family:monospace; font-weight:700; font-size: 0.8rem; margin-bottom:0.2rem;">${item.rfid} | ${item.sku}</p>
                                <h2 style="font-size:1.8rem; margin-top:0; letter-spacing:-0.5px">${item.name}</h2>
                                <p style="color:var(--text-muted); font-size:0.9rem;">${item.category} • Supplier Array: ${item.supplier}</p>
                            </div>
                        </div>
                        <div style="display: flex; gap: 0.5rem;">
                            ${hasAccess('Manager') ? `<button class="btn btn-outline" onclick="adjustQty('${item.id}', 25)"><i data-lucide="plus"></i> Manual Intake (+25)</button>` : '<span style="font-size:0.8rem; color:var(--text-muted);"><i data-lucide="lock" style="width:12px;display:inline;"></i> L2 Auth Required</span>'}
                            <button class="btn btn-primary" onclick="reviewPO('${item.id}')"><i data-lucide="file-down"></i> Dispatch Priority PO</button>
                        </div>
                    </div>
                </div>
                
                <div class="grid-2-col" style="grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); margin-bottom: 2rem;">
                    <div class="card">
                        <p class="kpi-label">Sector Capacity Fill</p>
                        <p style="font-size:2.2rem; font-weight:800">${item.qty} <span style="font-size:1rem; color:var(--text-muted); font-weight:normal;">/ ${item.cap} Max</span></p>
                        <div style="width: 100%; height: 8px; background: var(--bg-body); border-radius:4px; overflow:hidden; margin-top: 0.8rem;">
                            <div style="width:${pct}%; background:var(--${pct < appState.settings.threshold ? 'warning' : 'success'}); height:100%;"></div>
                        </div>
                        <p style="font-weight:600; font-size:0.8rem; color:var(--${pct < appState.settings.threshold ? 'warning' : 'success'}); margin-top:0.8rem;">${pct}% Physical Utilization</p>
                    </div>
                    <div class="card">
                        <p class="kpi-label">Predicted Analytics Matrix</p>
                        <p style="font-size:2.2rem; font-weight:800">${p.demand} <span style="font-size:1rem; font-weight:normal; color:var(--text-muted)">/ day burn rate</span></p>
                        <p style="font-size:0.85rem; color:var(--text-muted); margin-top: 0.8rem;">Estimated Exhaustion in <span style="color:var(--${p.stockOut<5?'danger':'text-main'}); font-weight:700;">${p.stockOut} cycles</span></p>
                    </div>
                    <div class="card">
                        <p class="kpi-label">Total Asset Value</p>
                        <p style="font-size:2.2rem; font-weight:800; color: #cbd5e1;">$${(item.qty * item.price).toLocaleString()} <span style="font-size:1rem; color:var(--text-muted); font-weight:normal;">Total</span></p>
                        <p style="font-size:0.85rem; color:var(--text-muted); margin-top: 0.8rem;">Current Price Index: $${item.price} per unit</p>
                    </div>
                </div>

                <div class="card" style="margin-bottom: 1.5rem;">
                    <div class="card-header" style="justify-content: space-between;">
                        <span class="card-title"><i data-lucide="bar-chart-2"></i> Unit Turnover Velocity History</span>
                        <select class="form-control" style="width: auto; padding: 2px 6px; font-size: 0.75rem;" onchange="appState.filters.productTrendPeriod=this.value; initCharts('product')">
                            <option value="7d" ${appState.filters.productTrendPeriod==='7d'?'selected':''}>Last 7 Days</option>
                            <option value="30d" ${appState.filters.productTrendPeriod==='30d'?'selected':''}>Last 1 Month</option>
                            <option value="1y" ${appState.filters.productTrendPeriod==='1y'?'selected':''}>Last 1 Year</option>
                        </select>
                    </div>
                    <div style="height: 350px; width: 100%;"><canvas id="prodTrendChart"></canvas></div>
                </div>
            `;
        }

        function adjustQty(id, d) {"""
    
    content = content[:match_detail.start()] + new_detail + content[match_detail.end()-len('function adjustQty(id, d) {'):]

# 6. Update initCharts
initc_match = re.search(r"if\(page === 'dashboard'\) \{([\s\S]*?)const ctx = document.getElementById\('dashTrendChart'\);", content)
if initc_match:
    dash_chart_logic = """if(page === 'dashboard') {
                const p = appState.filters.dashTrendPeriod || '7d';
                let days = 7;
                if(p === '30d') days = 30;
                if(p === '1y') days = 365;
                for(let i=days-1; i>=0; i--) { labels.push(i+'d'); data.push(4000+Math.floor(Math.random()*800 + Math.sin(i/5)*500)); }
                
                const ctx = document.getElementById('dashTrendChart');"""
    content = content[:initc_match.start()] + dash_chart_logic + content[initc_match.end()-len("const ctx = document.getElementById('dashTrendChart');"):]

# Update elements:{point:{radius:0}} in dashboard chart
content = content.replace("options: { responsive:true, maintainAspectRatio:false, plugins: { legend: { display:false } }, scales: { y: { grid: { color: gc }, ticks: { color: tc } }, x: { grid: { display: false }, ticks: { color: tc } } } }", "options: { responsive:true, maintainAspectRatio:false, elements:{point:{radius: data.length > 60 ? 0 : 3}}, plugins: { legend: { display:false } }, scales: { y: { grid: { color: gc }, ticks: { color: tc } }, x: { grid: { display: false }, ticks: { color: tc, maxTicksLimit: 12 } } } }")

# Add chart rendering logic for 'product' view
prod_chart_append = """                }
            } else if (page === 'product') {
                const p = appState.filters.productTrendPeriod || '30d';
                let days = 30; if(p === '7d') days = 7; if(p === '1y') days = 365;
                const item = appState.inventory.find(i=>i.id===appState.currentProduct) || {cap: 1000};
                for(let i=days-1; i>=0; i--) { labels.push(i+'d'); data.push(Math.max(0, Math.floor(item.cap * 0.4 + Math.random() * (item.cap*0.3)))); }
                const ctx = document.getElementById('prodTrendChart');
                if(ctx) {
                    charts.trend = new Chart(ctx, { type: 'line', data: { labels, datasets: [{ label: 'Unit Drawdown', data, borderColor: 'var(--primary)', backgroundColor: 'rgba(74, 222, 128, 0.1)', fill: true, tension: 0.3 }] }, options: { responsive:true, maintainAspectRatio:false, elements:{point:{radius: days > 60 ? 0 : 4}}, plugins: { legend: { labels:{color: tc} } }, scales: { y: { grid: { color: gc }, ticks: { color: tc } }, x: { grid: { display: false }, ticks: { color: tc, maxTicksLimit: 12 } } } } });
                }
            }
        }"""
content = content.replace("                }\n            }\n        }", prod_chart_append)

# Delete modal structure from HTML
content = re.sub(r'<!-- PRODUCT MODAL -->[\s\S]*?<div class="modal-overlay" id="po-modal">', '<div class="modal-overlay" id="po-modal">', content)
#Wait, the modal in html was just `<div class="modal-overlay" id="detail-modal"> ... </div>` Let's do a strict replace
content = re.sub(r'<div class="modal-overlay" id="detail-modal">[\s\S]*?</div>\s*</div>', '', content)


with open("c:/Users/JIGISHA GAJJAR/OneDrive/Desktop/ARISE/index.html", "w", encoding="utf-8") as f:
    f.write(content)
