import re

with open("c:/Users/JIGISHA GAJJAR/OneDrive/Desktop/ARISE/index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update appState
content = content.replace(
"""        const appState = {
            currentPage: "dashboard",
            inventory: [],
            logs: [],
            alerts: [],
            settings: { threshold: 20, role: 'Admin', leadTime: 3, growthFactor: 1.15, alertsEnabled: true },
            filters: { search: '', category: 'all', shelf: 'all', analyticsPeriod: '7d', analyticsProduct: 'all' },
            robot: { active: false, interval: null }
        };""",
"""        const appState = {
            currentPage: "dashboard",
            inventory: [],
            logs: [],
            alerts: [],
            settings: { threshold: 20, role: 'Admin', leadTime: 3, growthFactor: 1.15, alertsEnabled: true },
            filters: { search: '', category: 'all', shelf: 'all', analyticsPeriod: '7d', analyticsProduct: 'all', stockLevel: 'all', view: 'grid', analyticsTab: 'trend', demandView: 'day' },
            robot: { active: false, interval: null, currentTarget: null }
        };""")

# 2. Update navigate
content = content.replace(
"""        function navigate(path) {
            if(!pages[path]) path = "dashboard";
            appState.currentPage = path;""",
"""        function navigate(path, params={}) {
            if(!pages[path]) path = "dashboard";
            appState.currentPage = path;
            
            if(params.stockLevel) appState.filters.stockLevel = params.stockLevel;
            else if (path === 'inventory' && !params.keepFilters) appState.filters.stockLevel = 'all';

            if(params.view) appState.filters.view = params.view;
            if(params.analyticsTab) appState.filters.analyticsTab = params.analyticsTab;""")

# 3. Modify renderDashboard string
dash_match = re.search(r'function renderDashboard\(\) \{[\s\S]*?return `([\s\S]*?)<div class="grid-2-col">', content)
if dash_match:
    dash_logic = """        function renderDashboard() {
            const totQty = appState.inventory.reduce((a,b)=>a+b.qty,0);
            const lowCount = appState.inventory.filter(i => (i.qty/i.cap)*100 < appState.settings.threshold && i.qty > 0).length;
            const empty = appState.inventory.filter(i=>i.qty===0).length;
            const avgDemand = (appState.inventory.reduce((a,b)=>a+parseFloat(runPrediction(b).demand),0)/appState.inventory.length);
            const alertsCount = appState.alerts.filter(a=>!a.resolved).length;
            
            let dLabel = 'Day', dMult = 1;
            if(appState.filters.demandView === 'week') { dLabel = 'Week'; dMult = 7; }
            if(appState.filters.demandView === 'month') { dLabel = 'Month'; dMult = 30; }
            const demandValue = (avgDemand * dMult).toFixed(1);

            return `
                <div class="kpi-row">
                    <div class="kpi-card" onclick="navigate('inventory', {view: 'table', keepFilters:false})">
                        <i data-lucide="boxes" class="kpi-icon" style="color: var(--primary)"></i>
                        <p class="kpi-label">Total Inventory</p>
                        <div class="kpi-value">${totQty.toLocaleString()}</div>
                    </div>
                    <div class="kpi-card" onclick="navigate('inventory', {stockLevel: 'low', keepFilters:true})">
                        <i data-lucide="alert-circle" class="kpi-icon" style="color: var(--warning)"></i>
                        <p class="kpi-label">Low Stock</p>
                        <div class="kpi-value" style="color: var(--warning)">${lowCount}</div>
                    </div>
                    <div class="kpi-card" onclick="navigate('inventory', {stockLevel: 'empty', keepFilters:true})">
                        <i data-lucide="layers" class="kpi-icon" style="color: var(--danger)"></i>
                        <p class="kpi-label">Empty Shelves</p>
                        <div class="kpi-value" style="color: var(--danger)">${empty}</div>
                    </div>
                    <div class="kpi-card" onclick="document.getElementById('notif-trigger').click()">
                        <i data-lucide="activity" class="kpi-icon" style="color: var(--critical)"></i>
                        <p class="kpi-label">Active Alerts</p>
                        <div class="kpi-value" style="color: var(--critical)">${alertsCount}</div>
                    </div>
                    <div class="kpi-card">
                        <i data-lucide="trending-up" class="kpi-icon" style="color: var(--primary)"></i>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                            <p class="kpi-label" style="margin-bottom:0; cursor:pointer;" onclick="navigate('analytics')">Avg Demand</p>
                            <div style="display:flex; gap:4px; position:relative; z-index:10;">
                                <button class="mini-btn ${appState.filters.demandView==='day'?'btn-primary':'btn-outline'}" style="padding:2px 4px;font-size:0.6rem" onclick="event.stopPropagation(); appState.filters.demandView='day'; navigate('dashboard')">D</button>
                                <button class="mini-btn ${appState.filters.demandView==='week'?'btn-primary':'btn-outline'}" style="padding:2px 4px;font-size:0.6rem" onclick="event.stopPropagation(); appState.filters.demandView='week'; navigate('dashboard')">W</button>
                                <button class="mini-btn ${appState.filters.demandView==='month'?'btn-primary':'btn-outline'}" style="padding:2px 4px;font-size:0.6rem" onclick="event.stopPropagation(); appState.filters.demandView='month'; navigate('dashboard')">M</button>
                            </div>
                        </div>
                        <div class="kpi-value">${demandValue} <span style="font-size:0.8rem;color:var(--text-muted);font-weight:normal">/ ${dLabel}</span></div>
                    </div>
                </div>
                <!-- split -->
                <div class="grid-2-col">`
"""
    
    content = content[:dash_match.start()] + dash_logic + content[dash_match.end()-len('<div class="grid-2-col">'):]

# 4. Modify renderInventory
inv_start = content.find("function renderInventory() {")
inv_end = content.find("function renderGrid(data, grouped = true) {")

new_inv = """        function renderInventory() {
            let list = appState.inventory;
            if(appState.filters.category !== 'all') list = list.filter(i => i.category === appState.filters.category);
            if(appState.filters.shelf !== 'all') list = list.filter(i => i.id.startsWith(appState.filters.shelf));
            if(appState.filters.stockLevel === 'low') list = list.filter(i => { const p=(i.qty/i.cap)*100; return p > 0 && p < appState.settings.threshold; });
            if(appState.filters.stockLevel === 'empty') list = list.filter(i => i.qty === 0);

            const tableHtml = `
                <div class="table-responsive">
                    <table class="data-table">
                        <thead><tr><th>Sector ID</th><th>SKU & Tag</th><th>Product Name</th><th>Category</th><th>Stock Level</th><th>Action</th></tr></thead>
                        <tbody>
                            ${list.map(i => {
                                const pct = Math.round((i.qty/i.cap)*100);
                                let color = 'success';
                                if(pct===0) color='danger'; else if(pct < appState.settings.threshold) color='warning';
                                return `
                                <tr>
                                    <td><strong>${i.id}</strong></td>
                                    <td><div style="font-family:monospace; color:var(--text-muted)">${i.sku}<br>${i.rfid}</div></td>
                                    <td>${i.name}</td>
                                    <td>${i.category}</td>
                                    <td>
                                        <div style="display:flex; align-items:center; gap:0.5rem">
                                            <div style="width: 60px; height: 6px; background: var(--bg-body); border-radius:3px; overflow:hidden;">
                                                <div style="width:${pct}%; background:var(--${color}); height:100%;"></div>
                                            </div>
                                            <span><strong>${i.qty}</strong><span style="color:var(--text-muted)">/${i.cap}</span></span>
                                        </div>
                                    </td>
                                    <td><button class="btn btn-outline mini-btn" onclick="openProductDetail('${i.id}')">Inspect</button></td>
                                </tr>`;
                            }).join('')}
                        </tbody>
                    </table>
                </div>
            `;

            return `
                <div class="page-layout">
                    <!-- Main Inventory View -->
                    <div>
                        <div class="tabs">
                            <div class="tab-item ${appState.filters.view === 'grid' ? 'active' : ''}" onclick="appState.filters.view='grid'; navigate('inventory', {view: 'grid', keepFilters:true})">Grid View Mapping</div>
                            <div class="tab-item ${appState.filters.view === 'table' ? 'active' : ''}" onclick="appState.filters.view='table'; navigate('inventory', {view: 'table', keepFilters:true})">Detailed Table View</div>
                        </div>
                        
                        <div class="warehouse-wrapper" style="display:${appState.filters.view === 'grid' ? 'block' : 'none'};">
                            ${list.length === 0 ? '<div class="empty-state">No matching sectors found.</div>' : renderGrid(list, true)}
                        </div>
                        <div class="table-wrapper" style="display:${appState.filters.view === 'table' ? 'block' : 'none'};">
                            ${list.length === 0 ? '<div class="empty-state">No matching sectors found.</div>' : tableHtml}
                        </div>
                    </div>
                    
                    <!-- Advanced Filters Panel -->
                    <div class="card">
                        <h3 style="font-size:1rem; margin-bottom:1.5rem; border-bottom:1px solid var(--border); padding-bottom:0.8rem;">Filter Controls</h3>
                        
                        <div class="form-group">
                            <label class="form-label">Stock Status</label>
                            <select class="form-control" onchange="appState.filters.stockLevel=this.value; navigate('inventory', {keepFilters:true})">
                                <option value="all" ${appState.filters.stockLevel==='all'?'selected':''}>All Sectors</option>
                                <option value="low" ${appState.filters.stockLevel==='low'?'selected':''}>Low Stock</option>
                                <option value="empty" ${appState.filters.stockLevel==='empty'?'selected':''}>Empty Shelves</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Category</label>
                            <select class="form-control" onchange="appState.filters.category=this.value; navigate('inventory', {keepFilters:true})">
                                <option value="all" ${appState.filters.category==='all'?'selected':''}>All Categories</option>
                                <option value="Electronics" ${appState.filters.category==='Electronics'?'selected':''}>Electronics</option>
                                <option value="Grocery" ${appState.filters.category==='Grocery'?'selected':''}>Grocery</option>
                                <option value="Furniture" ${appState.filters.category==='Furniture'?'selected':''}>Furniture</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Sector Region</label>
                            <select class="form-control" onchange="appState.filters.shelf=this.value; navigate('inventory', {keepFilters:true})">
                                <option value="all" ${appState.filters.shelf==='all'?'selected':''}>All Regions</option>
                                <option value="A" ${appState.filters.shelf==='A'?'selected':''}>Sector A</option>
                                <option value="B" ${appState.filters.shelf==='B'?'selected':''}>Sector B</option>
                                <option value="C" ${appState.filters.shelf==='C'?'selected':''}>Sector C</option>
                            </select>
                        </div>
                        <button class="btn btn-outline" style="width:100%" onclick="appState.filters.category='all'; appState.filters.shelf='all'; appState.filters.stockLevel='all'; navigate('inventory')">Reset Controls</button>
                        
                        <div style="margin-top: 2rem; border-top:1px solid var(--border); padding-top:1rem;">
                            <h4 style="font-size:0.8rem; color:var(--text-muted); margin-bottom:1rem; text-transform:uppercase;">Bulk Actions</h4>
                            <button class="btn btn-outline" style="width:100%; margin-bottom:0.5rem;" onclick="spawnToast('info', 'Data Exported to CSV')"><i data-lucide="download"></i> Export Displayed</button>
                        </div>
                    </div>
                </div>
            `;
        }
"""
content = content[:inv_start] + new_inv + content[inv_end:]

# 5. Modify renderAnalytics
an_start = content.find("function renderAnalytics() {")
an_end = content.find("function renderRobotics() {")

new_an = """        function renderAnalytics() {
            const isCap = appState.filters.analyticsTab === 'capacity';
            return `
                <div class="tabs">
                    <div class="tab-item ${!isCap?'active':''}" onclick="navigate('analytics', {analyticsTab: 'trend'})">Trend Forecasts</div>
                    <div class="tab-item ${isCap?'active':''}" onclick="navigate('analytics', {analyticsTab: 'capacity'})">Capacity Reports</div>
                </div>
                <div class="card" style="margin-bottom:1.5rem;">
                     <div class="card-header" style="border:none; padding:0; margin:0;">
                        <h3 class="card-title">Parameter Controller</h3>
                        <div style="display:flex; gap:1rem;">
                             <select class="form-control" id="a-product" onchange="appState.filters.analyticsProduct=this.value; initCharts('analytics');" style="width:200px; padding:0.4rem;">
                                <option value="all">Global Array</option>
                                ${appState.inventory.map(i => `<option value="${i.id}" ${appState.filters.analyticsProduct===i.id?'selected':''}>${i.name}</option>`).join('')}
                            </select>
                            <select class="form-control" id="a-period" onchange="appState.filters.analyticsPeriod=this.value; initCharts('analytics');" style="width:150px; padding:0.4rem;">
                                <option value="7d" ${appState.filters.analyticsPeriod==='7d'?'selected':''}>Last 7 Days</option>
                                <option value="30d" ${appState.filters.analyticsPeriod==='30d'?'selected':''}>Last 30 Days</option>
                            </select>
                        </div>
                     </div>
                </div>

                <div class="grid-2-col" style="${isCap?'display:none;':''}">
                    <div class="card">
                        <div class="card-header"><span class="card-title">Velocity & Demand Prediction</span></div>
                        <div style="height: 350px; width: 100%;"><canvas id="an-trendChart"></canvas></div>
                    </div>
                    <div class="card">
                        <div class="card-header"><span class="card-title">Category Distribution</span></div>
                        <div style="height: 350px; width: 100%; display:flex; justify-content:center;"><canvas id="an-distChart"></canvas></div>
                    </div>
                </div>

                <div class="grid-2-col" style="${!isCap?'display:none;':''}">
                    <div class="card">
                        <div class="card-header"><span class="card-title">Facility Capacity Overview</span></div>
                        <div style="height: 350px; width: 100%;"><canvas id="an-capChart"></canvas></div>
                    </div>
                    <div class="card">
                        <div class="card-header"><span class="card-title">Top Filled Sectors</span></div>
                        <div class="table-responsive">
                            <table class="data-table">
                                <thead><tr><th>Sector</th><th>Stock</th><th>%</th></tr></thead>
                                <tbody>
                                    ${[...appState.inventory].sort((a,b)=>(b.qty/b.cap)-(a.qty/a.cap)).slice(0,5).map(i=>{
                                        const p = Math.round((i.qty/i.cap)*100);
                                        return `<tr><td>${i.id}</td><td>${i.qty}</td><td><span style="color:var(--${p>90?'danger':(p<appState.settings.threshold?'warning':'success')})">${p}%</span></td></tr>`;
                                    }).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
        }
"""
content = content[:an_start] + new_an + content[an_end:]


# 6. Modify renderRobotics
rob_start = content.find("function renderRobotics() {")
rob_end = content.find("function renderProcurement() {")

new_rob = """        function renderRobotics() {
            const r = appState.robot;
            return `
                <div class="card" style="margin-bottom:1.5rem; display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <h2 style="margin-bottom:0.3rem;">Fleet Command Node</h2>
                        <p style="color:var(--text-muted); font-size:0.85rem;">Manage autonomous scanning drones. ID: RBT-09X</p>
                    </div>
                    <button class="btn btn-${r.active?'danger':'primary'}" id="rbt-toggle" onclick="toggleRobot()">
                        <i data-lucide="power"></i> ${r.active?'Disengage Network':'Initialize Scanners'}
                    </button>
                </div>

                <div class="page-layout">
                    <!-- Stream & Map -->
                    <div>
                        <div class="card robot-panel" style="margin-bottom:1.5rem;">
                            <div class="robot-glow"></div>
                            <div class="card-header" style="position:relative; z-index:2;">
                                <span class="card-title"><i data-lucide="terminal"></i> Live Telemetry Stream</span>
                                <span id="rbt-badge" class="status-pill status-${r.active?'success':'warning'}"><span class="blink">●</span> ${r.active?'ONLINE':'STANDBY'}</span>
                            </div>
                            <div style="background:#000; border:1px solid var(--border); border-radius: 8px; padding: 1rem; height: 200px; display:flex; flex-direction:column; position:relative; z-index:2;">
                                <div id="robot-console" style="flex:1; overflow:hidden; display:flex; flex-direction:column; justify-content:flex-end; font-size:0.8rem;">
                                    <div class="robot-console-line" style="color: #94a3b8; border-color: #94a3b8;">[SYS] Connection established.</div>
                                </div>
                            </div>
                        </div>

                        <div class="card">
                            <div class="card-header"><span class="card-title"><i data-lucide="map"></i> Automated Warehouse Mapper</span></div>
                            <div style="display:grid; grid-template-columns: repeat(15, 1fr); gap: 6px; padding: 1.5rem 1rem; background: var(--bg-panel); border-radius: 8px; border: 1px solid var(--border);">
                                ${appState.inventory.map(i => {
                                    const isTarget = appState.robot.currentTarget === i.id;
                                    return `<div id="rbt-map-${i.id}" style="aspect-ratio: 1; border-radius: 4px; background: ${isTarget ? 'var(--primary)' : 'var(--bg-body)'}; ${isTarget ? 'box-shadow: 0 0 12px var(--primary); transform: scale(1.3); animation: pulse 1s infinite;' : 'transition: background 0.3s;'} border: 1px solid var(--border); opacity: ${isTarget?1:0.5};" title="Sector ${i.id}"></div>`;
                                }).join('')}
                            </div>
                            <style>@keyframes pulse { 0% { opacity: 1; transform: scale(1.3); } 50% { opacity: 0.6; transform: scale(1); } 100% { opacity: 1; transform: scale(1.3); } }</style>
                        </div>
                    </div>

                    <!-- Sensor Arrays -->
                    <div style="display:flex; flex-direction:column; gap:1.5rem;">
                        <div class="card">
                            <div class="card-header"><span class="card-title" style="font-size:0.85rem;"><i data-lucide="flame" style="color:var(--warning)"></i> MQ135 Air Quality Node</span></div>
                            <div style="text-align:center; padding: 1rem 0;">
                                <p id="sns-mq" style="font-size: 3rem; font-weight:800; line-height:1; font-family:monospace;">---</p>
                                <p id="sns-mq-v" style="color:var(--text-muted); font-size:0.8rem; margin-top:0.5rem; font-family:monospace;">0.00 V</p>
                            </div>
                        </div>
                        <div class="card">
                            <div class="card-header"><span class="card-title" style="font-size:0.85rem;"><i data-lucide="radar" style="color:var(--primary)"></i> LIDAR/Ultrasonic Mesh</span></div>
                            <div style="text-align:center; padding: 1rem 0;">
                                <p id="sns-dist" style="font-size: 3rem; font-weight:800; line-height:1; font-family:monospace;">---<span style="font-size:1.2rem;">cm</span></p>
                                <p id="sns-loc" style="color:var(--primary); font-size:0.8rem; margin-top:0.5rem; font-weight:600;">Target: None</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
"""
content = content[:rob_start] + new_rob + content[rob_end:]

# 7. Modify simulateScan
scan_start = content.find("function simulateScan() {")
scan_end = content.find("function logToConsole(msg, type='info') {")

new_scan = """        function simulateScan() {
            const item = appState.inventory[Math.floor(Math.random() * appState.inventory.length)];
            let isFull = Math.random() > 0.6; 
            let dist = isFull ? Math.floor(Math.random() * 30 + 20) : Math.floor(Math.random() * 50 + 70); 
            
            // Map ultrasonic distance to stock logically
            let simulatedQty = Math.floor(item.cap * (1 - Math.min(1, Math.max(0, (dist - 20) / 100))));
            item.qty = simulatedQty;

            let gas = Math.floor(Math.random() * 40 + 10);
            if(Math.random() > 0.9) gas = Math.floor(Math.random() * 40 + 60);

            // Visual tracking for the Robot Map
            if (appState.robot.currentTarget) {
               const oldCell = document.getElementById('rbt-map-' + appState.robot.currentTarget);
               if(oldCell) { oldCell.style.background = 'var(--bg-body)'; oldCell.style.boxShadow = 'none'; oldCell.style.transform = 'scale(1)'; oldCell.style.animation = 'none'; oldCell.style.opacity = '0.5'; }
            }
            appState.robot.currentTarget = item.id;

            if(appState.currentPage === 'robotics') {
                const newCell = document.getElementById('rbt-map-' + item.id);
                if(newCell) { newCell.style.background = 'var(--primary)'; newCell.style.boxShadow = '0 0 12px var(--primary)'; newCell.style.transform = 'scale(1.3)'; newCell.style.animation = 'pulse 1s infinite'; newCell.style.opacity = '1'; }

                document.getElementById('sns-loc').innerText = `Target: Sector ${item.id}`;
                document.getElementById('sns-dist').innerHTML = `${dist}<span style="font-size:1.2rem;">cm</span>`;
                document.getElementById('sns-mq').innerText = gas;
                document.getElementById('sns-mq-v').innerText = (gas * (5/1023)).toFixed(2) + ' V';
                document.getElementById('sns-mq').style.color = gas > 50 ? 'var(--danger)' : '';
                
                logToConsole(`[SCN] Target ${item.id} -> US:${dist}cm -> QTY updated to ${simulatedQty}`);
                if(gas > 50) {
                    logToConsole(`[ALRT] CRITICAL GAS LEAK Sector ${item.id}`, 'alert');
                }
            }

            if(gas > 50) {
                spawnToast('critical', `Gas spike detected at Sector ${item.id}`);
            }
            
            processAlerts(); // Checks new values for alerts
        }

"""
content = content[:scan_start] + new_scan + content[scan_end:]

# 8. Modify initCharts to add capacity chart
charts_start = content.find("function initCharts(page) {")
charts_end = content.find("function toggleRobot() {")

new_charts = """        function initCharts(page) {
            let labels=[], data=[];
            if (charts.trend) charts.trend.destroy();
            if (charts.dist) charts.dist.destroy();
            if (charts.cap) charts.cap.destroy();

            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            const tc = isDark ? '#94a3b8' : '#475569';
            const gc = isDark ? '#1d3326' : '#e2e8f0';

            if(page === 'dashboard') {
                for(let i=6; i>=0; i--) { labels.push(new Date(Date.now()-i*86400000).toLocaleDateString('en-US',{day:'numeric',month:'short'})); data.push(4000+Math.floor(Math.random()*800)); }
                const ctx = document.getElementById('dashTrendChart');
                if(ctx) {
                    charts.trend = new Chart(ctx, { type: 'line', data: { labels, datasets: [{ data, borderColor: 'var(--primary)', backgroundColor: 'rgba(74, 222, 128, 0.1)', fill: true, tension: 0.4 }] }, options: { responsive:true, maintainAspectRatio:false, plugins: { legend: { display:false } }, scales: { y: { grid: { color: gc }, ticks: { color: tc } }, x: { grid: { display: false }, ticks: { color: tc } } } } });
                }

                const ctxU = document.getElementById('dashUtilChart');
                if(ctxU) {
                    let utilData = Object.fromEntries(shelves.map(s => {
                        const items = appState.inventory.filter(i=>i.id.startsWith(s));
                        return [s, Math.round((items.reduce((a,b)=>a+b.qty,0) / items.reduce((a,b)=>a+b.cap,0))*100)];
                    }));
                    charts.dist = new Chart(ctxU, { type: 'bar', data: { labels: Object.keys(utilData), datasets: [{ data: Object.values(utilData), backgroundColor: Object.values(utilData).map(v => v > 80 ? '#ef4444' : '#22c55e'), borderRadius: 4 }] }, options: { responsive:true, maintainAspectRatio:false, plugins: { legend: { display:false } }, scales: { y: { max: 100, grid: { color: gc }, ticks: { color: tc } }, x: { grid: { display: false }, ticks: { color: tc } } } } });
                }
            } else if (page === 'analytics') {
                if(appState.filters.analyticsTab === 'trend') {
                    const p = appState.filters.analyticsPeriod;
                    const days = p === '7d' ? 7 : 30;
                    for(let i=days-1; i>=0; i--) { labels.push(i+'d'); data.push(Math.floor(Math.random()*400)); }
                    
                    const ctx = document.getElementById('an-trendChart');
                    if(ctx) charts.trend = new Chart(ctx, { type: 'line', data: { labels, datasets: [{ label: 'Movement', data, borderColor: 'var(--primary)', tension: 0.3 }] }, options: { responsive:true, maintainAspectRatio:false, elements:{point:{radius:0}} } });

                    const ctxD = document.getElementById('an-distChart');
                    if(ctxD) {
                        let distData = Object.fromEntries(categories.map(c => [c, appState.inventory.filter(i=>i.category===c).reduce((a,b)=>a+b.qty,0)]));
                        charts.dist = new Chart(ctxD, { type: 'doughnut', data: { labels: Object.keys(distData), datasets: [{ data: Object.values(distData), backgroundColor: ['#4ade80', '#22c55e', '#166534'], borderWidth:0 }] }, options: { responsive:true, maintainAspectRatio:false, cutout:'75%', plugins: { legend: { position: 'bottom', labels: {color: tc} } } } });
                    }
                } else {
                    const ctxC = document.getElementById('an-capChart');
                    if(ctxC) {
                        let capDataMax = Object.fromEntries(shelves.map(s => [s, appState.inventory.filter(i=>i.id.startsWith(s)).reduce((a,b)=>a+b.cap,0)]));
                        let capDataCur = Object.fromEntries(shelves.map(s => [s, appState.inventory.filter(i=>i.id.startsWith(s)).reduce((a,b)=>a+b.qty,0)]));
                        charts.cap = new Chart(ctxC, {
                            type: 'bar',
                            data: {
                                labels: Object.keys(capDataMax),
                                datasets: [
                                    { label: 'Active Inventory', data: Object.values(capDataCur), backgroundColor: '#4ade80', borderRadius: 4 },
                                    { label: 'Empty Capacity', data: Object.keys(capDataMax).map(s => capDataMax[s] - capDataCur[s]), backgroundColor: isDark ? '#1d3326' : '#e2e8f0', borderRadius: 4 }
                                ]
                            },
                            options: { responsive:true, maintainAspectRatio:false, plugins: { legend: { labels: {color: tc} } }, scales: { x: { stacked: true, grid:{display:false}, ticks:{color:tc} }, y: { stacked: true, grid:{color:gc}, ticks:{color:tc} } } }
                        });
                    }
                }
            }
        }

"""
content = content[:charts_start] + new_charts + content[charts_end:]

with open("c:/Users/JIGISHA GAJJAR/OneDrive/Desktop/ARISE/index.html", "w", encoding="utf-8") as f:
    f.write(content)
