
        /* 
        ================================================================
        3. JAVASCRIPT LOGIC (PRODUCTION-GRADE ERP SIMULATION)
        ================================================================
        */

        // --- A. STATE MANAGEMENT ---
        let state = {
            inventory: [],
            alerts: [],
            logs: [],
            settings: { threshold: 20, role: 'Admin', leadTime: 3, growthFactor: 1.15 },
            pagination: { page: 1, pageSize: 12 }
        };

        const shelves = ['A', 'B', 'C'];
        const categories = ['Electronics', 'Grocery', 'Furniture'];
        const suppliers = ['Global Logistics', 'Nexus Parts', 'EcoSupply Co'];
        let searchTimer = null;
        let charts = {};

        // --- A.1 LOGGING UTILS ---
        function logActivity(msg) {
            state.logs.unshift({ msg, time: new Date().toLocaleTimeString() });
            if(state.logs.length > 5) state.logs.pop();
            console.log(`[ERP_LOG]: ${msg}`);
        }

        // --- B. AUTH & PERMISSIONS ---
        function updateRole(role) {
            state.settings.role = role;
            spawnToast({ type: 'info', text: `Role switched to ${role}` });
            document.getElementById('profile-modal-role').innerText = role;
            logActivity(`Changed role to ${role}`);
            updateDashboard();
        }

        function hasAccess(level) {
            const roles = { 'Admin': 3, 'Manager': 2, 'Staff': 1 };
            return roles[state.settings.role] >= roles[level];
        }

        function openProfilePanel() {
            document.getElementById('profile-menu').style.display = 'none';
            const logContainer = document.getElementById('profile-activity');
            logContainer.innerHTML = state.logs.length 
                ? state.logs.map(l => `<p><strong style="color: var(--primary)">[${l.time}]</strong> ${l.msg}</p>`).join('')
                : '<p style="color:var(--text-muted)">No recent activity.</p>';
            document.getElementById('profile-modal').style.display = 'flex';
        }

        // --- C. SIMULATED DATA ENGINE (API LAYER) ---
        const API = {
            getInventory: (q = '', cat = 'all', page = 1) => {
                let filtered = state.inventory;
                if(q) {
                    const lq = q.toLowerCase();
                    filtered = filtered.filter(i => i.name.toLowerCase().includes(lq) || i.sku.toLowerCase().includes(lq) || i.id.toLowerCase().includes(lq));
                }
                if(cat !== 'all') filtered = filtered.filter(i => i.category === cat);
                
                const start = (page - 1) * state.pagination.pageSize;
                return {
                    data: filtered.slice(start, start + state.pagination.pageSize),
                    total: filtered.length,
                    pages: Math.ceil(filtered.length / state.pagination.pageSize)
                };
            },
            getStockDistribution: () => {
                let dist = {};
                categories.forEach(c => dist[c] = state.inventory.filter(i => i.category === c).length);
                return dist;
            },
            getShelfUtilization: () => {
                let util = {};
                shelves.forEach(s => {
                    const shelfItems = state.inventory.filter(i => i.id.startsWith(s));
                    const totalCap = shelfItems.reduce((a, b) => a + b.cap, 0);
                    const usedCap = shelfItems.reduce((a, b) => a + b.qty, 0);
                    util[s] = totalCap > 0 ? Math.round((usedCap / totalCap) * 100) : 0;
                });
                return util;
            },
            search: (term) => {
                const results = [];
                const lterm = term.toLowerCase();
                state.inventory.filter(i => i.name.toLowerCase().includes(lterm) || i.sku.toLowerCase().includes(lterm)).slice(0, 5).forEach(i => {
                    results.push({ type: 'product', name: i.name, id: i.id });
                });
                shelves.filter(s => s.toLowerCase() === lterm).forEach(s => {
                    results.push({ type: 'shelf', name: `Shelf ${s}`, id: s });
                });
                return results;
            },
            getLowStock: () => state.inventory.filter(i => (i.qty / i.cap) * 100 < state.settings.threshold && i.qty > 0),
            getEmptySlots: () => state.inventory.filter(i => i.qty === 0),
            getRestockList: () => state.inventory.filter(i => i.qty < runPrediction(i).demand * state.settings.leadTime).map(i => {
                let p = runPrediction(i);
                return { ...i, restockQty: Math.max(50, Math.ceil((p.demand * state.settings.leadTime * 2) - i.qty)) };
            }),
            getAlerts: () => state.alerts
        };

        // --- D. INITIALIZATION ---
        function init() {
            logActivity("System Initialized");
            
            // Generate Production-Like Dataset
            let idCounter = 1620; 
            shelves.forEach(sLetter => {
                for (let i = 1; i <= 20; i++) {
                    const id = sLetter + i;
                    const cap = 150 + Math.floor(Math.random() * 150);
                    const qtyPct = [0, 5, 20, 55, 85, 95][Math.floor(Math.random() * 6)];
                    const qty = Math.floor((qtyPct / 100) * cap);
                    let history = [];
                    for(let j=0; j<7; j++) history.push(Math.floor(Math.random() * 20));

                    state.inventory.push({
                        id, sku: `SKU-${10000 + idCounter--}`, name: `${categories[Math.floor(Math.random()*3)]} Unit ${id}`,
                        qty, cap, category: categories[Math.floor(Math.random()*3)], history,
                        lastUpdated: new Date(Date.now() - Math.random() * 86400000).toLocaleString(),
                        supplier: suppliers[Math.floor(Math.random()*3)], price: Math.floor(Math.random() * 100) + 10, rfid: 'RFID-' + Math.random().toString(36).substr(2, 6).toUpperCase()
                    });
                }
            });

            // Populate Product Selector
            const prodSelect = document.getElementById('analytics-product');
            state.inventory.forEach(i => {
                const opt = document.createElement('option');
                opt.value = i.id;
                opt.text = i.name;
                prodSelect.appendChild(opt);
            });

            renderGrid();
            updateDashboard();
            updateAnalytics();
            lucide.createIcons();
            
            setInterval(syncAnalytics, 15000);
            setInterval(processLiveAlerts, 10000);
        }

        function syncAnalytics() {
            updateAnalytics();
            const syncEl = document.getElementById('last-sync');
            if(syncEl) syncEl.innerText = new Date().toLocaleTimeString();
        }

        // --- E. CORE LOGIC ---
        function runPrediction(item) {
            const avg = item.history.reduce((a,b)=>a+b, 0) / 7;
            const seasonal = avg * state.settings.growthFactor;
            const stockOut = seasonal > 0 ? Math.floor(item.qty / seasonal) : 'INF';
            return { demand: seasonal.toFixed(1), stockOut, trend: item.history[6] > item.history[0] ? 'up' : 'down' };
        }

        function processLiveAlerts() {
            const utils = API.getShelfUtilization();
            Object.keys(utils).forEach(s => {
                if(utils[s] > 80 && !state.alerts.find(a => a.text.includes(`High Usage on Shelf ${s}`) && a.status === 'Active')) {
                    const alert = { type: 'warning', priority: 'High', text: `CRITICAL: High Usage on Shelf ${s} (${utils[s]}%)`, time: new Date().toLocaleTimeString(), status: 'Active' };
                    state.alerts.unshift(alert);
                    spawnToast({ type: 'critical', text: `Shelf ${s} over 80% capacity!` });
                }
            });

            state.inventory.forEach(item => {
                const pct = (item.qty / item.cap) * 100;
                if(pct < state.settings.threshold && !state.alerts.find(a => a.id === item.id && a.status === 'Active')) {
                    const alert = { id: item.id, type: pct === 0 ? 'danger' : 'warning', priority: pct === 0 ? 'High' : 'Medium', text: `${pct === 0 ? 'EMPTY' : 'LOW STOCK'}: Sector ${item.id}`, time: new Date().toLocaleTimeString(), status: 'Active' };
                    state.alerts.unshift(alert);
                }
            });
            updateDashboard();
        }

        function updateDashboard() {
            const totalQty = state.inventory.reduce((a,b)=>a+b.qty, 0);
            const lowCount = API.getLowStock().length;
            const emptyCount = API.getEmptySlots().length;
            const restockCount = API.getRestockList().length;
            const avgDemand = (state.inventory.reduce((a, b) => a + parseFloat(runPrediction(b).demand), 0) / state.inventory.length).toFixed(1);

            const safeSetText = (id, val) => { const el = document.getElementById(id); if(el) el.innerText = val; };
            safeSetText('stat-total', totalQty.toLocaleString());
            safeSetText('stat-low', lowCount);
            safeSetText('stat-empty', emptyCount);
            safeSetText('stat-demand', avgDemand);
            safeSetText('stat-restock', restockCount);
            
            const activeCount = state.alerts.filter(a => a.status === 'Active').length;
            safeSetText('stat-alerts', activeCount);
            safeSetText('notif-badge', activeCount);

            renderAlertDropdown();
            renderDistributionAndUtilizationCharts();
        }

        // --- F. DYNAMIC ANALYTICS & CHARTS ---
        function updateAnalytics() {
            const prodId = document.getElementById('analytics-product').value;
            const timeFilter = document.getElementById('analytics-time').value;
            
            let days = timeFilter === '7d' ? 7 : (timeFilter === '1m' ? 30 : 365);
            let labels = [];
            let data = [];
            let totalSales = 0;
            let avgInv = 0;

            if (prodId === 'all') {
                for(let i=days-1; i>=0; i--) {
                    labels.push(new Date(Date.now() - i*86400000).toLocaleDateString('en-US',{month:'short', day:'numeric'}));
                    data.push(4200 + Math.floor(Math.random()*600));
                }
                totalSales = Math.floor(Math.random() * 5000 * (days/7));
                avgInv = 4400;
            } else {
                const item = state.inventory.find(i=>i.id===prodId);
                for(let i=days-1; i>=0; i--) {
                    labels.push(new Date(Date.now() - i*86400000).toLocaleDateString('en-US',{month:'short', day:'numeric'}));
                    data.push(item.cap - Math.floor(Math.random() * 20));
                }
                totalSales = Math.floor(Math.random() * 200 * (days/7));
                avgInv = item.qty || 1;
            }

            const turnover = (totalSales / avgInv).toFixed(2);
            const velocity = (totalSales / days).toFixed(1);

            document.getElementById('metric-turnover').innerText = turnover;
            document.getElementById('metric-velocity').innerText = `${velocity}/d`;
            document.getElementById('metric-movement').innerText = totalSales;
            document.getElementById('trend-period-label').innerText = `(${timeFilter})`;

            if(charts.trend) charts.trend.destroy();
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            const colors = { grid: isDark ? '#334155' : '#e2e8f0', text: isDark ? '#94a3b8' : '#64748b' };
            
            charts.trend = new Chart(document.getElementById('trendChart'), {
                type: 'line', 
                data: { labels, datasets: [{ label: prodId==='all'?'Global Inventory':'Stock Level', data, borderColor: '#3b82f6', tension: 0.4, fill: true, backgroundColor: 'rgba(59,130,246,0.1)' }] },
                options: { plugins: { legend: { display:false } }, scales: { y: { grid: { color: colors.grid }, ticks: { color: colors.text } }, x: { grid: { display: false }, ticks: { color: colors.text } } } }
            });
        }

        function renderDistributionAndUtilizationCharts() {
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            const colors = { grid: isDark ? '#334155' : '#e2e8f0', text: isDark ? '#94a3b8' : '#64748b' };
            const distData = API.getStockDistribution();
            if(charts.dist) charts.dist.destroy();
            charts.dist = new Chart(document.getElementById('distChart'), {
                type: 'doughnut', 
                data: { labels: Object.keys(distData), datasets: [{ data: Object.values(distData), backgroundColor: ['#3b82f6', '#22c55e', '#f59e0b'] }] },
                options: { cutout: '75%', plugins: { legend: { position: 'bottom', labels: { color: colors.text, boxWidth: 10, padding: 15 } } }, onClick: (evt, active) => { if(active.length > 0) { document.getElementById('cat-filter').value = categories[active[0].index]; applyFilters(); } } }
            });

            const utilData = API.getShelfUtilization();
            if(charts.util) charts.util.destroy();
            charts.util = new Chart(document.getElementById('utilChart'), {
                type: 'bar',
                data: { labels: Object.keys(utilData), datasets: [{ label: 'Utilization %', data: Object.values(utilData), backgroundColor: Object.values(utilData).map(v => v > 80 ? '#ef4444' : '#3b82f6') }] },
                options: { plugins: { legend: { display: false } }, scales: { y: { max: 100, grid: { color: colors.grid }, ticks: { color: colors.text } }, x: { grid: { display: false }, ticks: { color: colors.text } } }, onClick: (evt, active) => { if(active.length > 0) { document.getElementById('shelf-filter').value = shelves[active[0].index]; applyFilters(); } } }
            });
        }

        // --- G. Purchase Order Logic Component (jsPDF) ---
        function generatePOData(items) {
            const poNumber = "PO-" + Date.now();
            let total = 0;
            const formattedItems = items.map(item => {
                const qty = item.restockQty || Math.max(50, item.cap - item.qty);
                const price = item.price || 25;
                total += qty * price;
                return { name: item.name, sku: item.sku, qty, price, total: qty * price };
            });
            return {
                poNumber, date: new Date().toLocaleDateString(),
                supplier: items.length === 1 ? items[0].supplier : "A.R.I.S.E Central Procurement",
                warehouse: "Facility Sector Alpha",
                items: formattedItems,
                subTotal: total, tax: total * 0.1, finalTotal: total * 1.1
            };
        }

        function buildPOText(poData) {
            let txt = `PURCHASE ORDER\n======================================================\n`;
            txt += `PO Number:  ${poData.poNumber}\nDate:       ${poData.date}\nSupplier:   ${poData.supplier}\nWarehouse:  ${poData.warehouse}\n\n`;
            txt += `ITEMS:\n------------------------------------------------------\n`;
            txt += `SKU       | Description             | Qty | Price | Total\n`;
            txt += `------------------------------------------------------\n`;
            poData.items.forEach(i => { txt += `${i.sku.padEnd(9)} | ${i.name.padEnd(23)} | ${i.qty.toString().padEnd(3)} | $${i.price.toString().padEnd(4)} | $${i.total.toFixed(2)}\n`; });
            txt += `------------------------------------------------------\n`;
            txt += `Subtotal: $${poData.subTotal.toFixed(2)}\nTax(10%): $${poData.tax.toFixed(2)}\nTotal:    $${poData.finalTotal.toFixed(2)}\n\n`;
            txt += `TERMS & CONDITIONS:\n- Delivery within 7 business days.\n- Payment Net 30.\n- Standard return policy applies.\n`;
            return txt;
        }

        function createPDF(poData) {
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            doc.setFontSize(22); doc.text("PURCHASE ORDER", 20, 20);
            doc.setFontSize(12); doc.text(`PO Number: ${poData.poNumber}`, 20, 35); doc.text(`Date: ${poData.date}`, 20, 42); doc.text(`Supplier: ${poData.supplier}`, 20, 49); doc.text(`Warehouse: ${poData.warehouse}`, 20, 56);
            doc.setLineWidth(0.5); doc.line(20, 62, 190, 62);
            doc.setFont("helvetica", "bold"); doc.text("SKU", 20, 70); doc.text("Description", 50, 70); doc.text("Qty", 130, 70); doc.text("Price", 150, 70); doc.text("Total", 175, 70); doc.setFont("helvetica", "normal");
            
            let y = 80;
            poData.items.forEach(i => {
                if (y > 270) { doc.addPage(); y = 20; }
                doc.text(i.sku, 20, y); doc.text(i.name.substring(0, 30), 50, y); doc.text(i.qty.toString(), 130, y); doc.text(`$${i.price}`, 150, y); doc.text(`$${i.total.toFixed(2)}`, 175, y);
                y += 8;
            });
            doc.line(20, y+5, 190, y+5); y += 15;
            if (y > 270) { doc.addPage(); y = 20; }
            doc.setFont("helvetica", "bold"); doc.text(`Subtotal: $${poData.subTotal.toFixed(2)}`, 130, y); doc.text(`Tax (10%): $${poData.tax.toFixed(2)}`, 130, y+8); doc.text(`Total: $${poData.finalTotal.toFixed(2)}`, 130, y+16);
            y += 30;
            if (y > 270) { doc.addPage(); y = 20; }
            doc.setFontSize(10); doc.text("Terms & Conditions:", 20, y); doc.setFont("helvetica", "normal");
            doc.text("- Delivery within 7 business days.", 20, y+6); doc.text("- Payment Net 30.", 20, y+12); doc.text("- Standard return policy applies.", 20, y+18);
            return doc;
        }

        let currentPOData = null;

        function reviewPO(id) {
            const item = state.inventory.find(i=>i.id===id);
            currentPOData = generatePOData([item]);
            document.getElementById('po-preview-content').innerText = buildPOText(currentPOData);
            document.getElementById('po-download-btn').onclick = () => downloadPOFromData(currentPOData);
            document.getElementById('po-modal').style.display = 'flex';
        }

        function downloadPO(id) {
            const item = state.inventory.find(i=>i.id===id);
            downloadPOFromData(generatePOData([item]));
        }

        function reviewCombinedPO() {
            const items = API.getRestockList();
            if(items.length === 0) return spawnToast({type:'warning', text:'No items to order.'});
            currentPOData = generatePOData(items);
            document.getElementById('po-preview-content').innerText = buildPOText(currentPOData);
            document.getElementById('po-download-btn').onclick = () => downloadPOFromData(currentPOData);
            document.getElementById('po-modal').style.display = 'flex';
        }

        function downloadCombinedPO() {
            const items = API.getRestockList();
            if(items.length === 0) return spawnToast({type:'warning', text:'No items to order.'});
            downloadPOFromData(generatePOData(items));
        }

        function downloadPOFromData(data) {
            const doc = createPDF(data);
            doc.save(`${data.poNumber}.pdf`);
            spawnToast({type:'success', text:`${data.poNumber}.pdf Generated`});
            logActivity(`Generated PO ${data.poNumber}`);
            closeModal('po-modal');
        }

        // --- H. HEADER & NAVIGATION LOGIC ---
        function handleGlobalSearch(term) {
            const dropdown = document.getElementById('search-dropdown');
            if(!term) { dropdown.style.display = 'none'; return; }
            clearTimeout(searchTimer);
            searchTimer = setTimeout(() => {
                const results = API.search(term);
                if(results.length === 0) { dropdown.innerHTML = '<div class="search-result-item">No results found</div>'; }
                else {
                    dropdown.innerHTML = results.map(r => `
                        <div class="search-result-item" onclick="handleSearchAction('${r.type}', '${r.id}')">
                            <span>${r.name}</span>
                            <span class="result-type">${r.type}</span>
                        </div>
                    `).join('');
                }
                dropdown.style.display = 'flex';
            }, 300);
        }

        function handleSearchAction(type, id) {
            document.getElementById('search-dropdown').style.display = 'none';
            document.getElementById('global-search').value = '';
            if(type === 'product') openDetailById(id);
            else {
                document.getElementById('shelf-filter').value = id;
                applyFilters();
                window.scrollTo({ top: document.getElementById('warehouse-floor').offsetTop - 100, behavior: 'smooth' });
            }
        }

        function toggleProfileDropdown() {
            const menu = document.getElementById('profile-menu');
            menu.style.display = menu.style.display === 'flex' ? 'none' : 'flex';
        }

        window.onclick = function(e) {
            if(!e.target.closest('.search-container')) document.getElementById('search-dropdown').style.display = 'none';
            if(!e.target.closest('#profile-trigger')) document.getElementById('profile-menu').style.display = 'none';
        }

        // --- I. COMPONENT RENDERING ---
        function renderGrid(data = state.inventory) {
            const floor = document.getElementById('warehouse-floor');
            floor.innerHTML = '';
            shelves.forEach(sLetter => {
                const shelfBlock = document.createElement('div');
                shelfBlock.className = 'shelf-block';
                shelfBlock.innerHTML = `<div class="shelf-title"><i data-lucide="layers"></i> Shelf ${sLetter}</div>`;
                const boxGrid = document.createElement('div');
                boxGrid.className = 'box-grid';
                data.filter(item => item.id.startsWith(sLetter)).forEach(item => {
                    const pct = (item.qty/item.cap)*100;
                    let color = 'bg-full';
                    if(pct === 0) color = 'bg-empty';
                    else if(pct < state.settings.threshold) color = 'bg-critical';
                    else if(pct < 70) color = 'bg-low';

                    const box = document.createElement('div');
                    box.className = `shelf-box ${color}`;
                    box.onclick = () => openDetail(item);
                    box.innerHTML = `<div class="box-id">${item.id}</div><div class="box-pct">${Math.round(pct)}% Full</div>`;
                    boxGrid.appendChild(box);
                });
                shelfBlock.appendChild(boxGrid);
                floor.appendChild(shelfBlock);
            });
            lucide.createIcons();
        }

        function openDetailById(id) { openDetail(state.inventory.find(i => i.id === id)); }
        function openDetail(item) {
            const modal = document.getElementById('detail-modal');
            const container = document.getElementById('modal-data');
            const p = runPrediction(item);
            const pct = Math.round((item.qty/item.cap)*100);
            container.innerHTML = `
                <div style="margin-bottom:2rem">
                    <p style="color:var(--primary); font-family:monospace; font-weight:700">${item.rfid} | ${item.sku}</p>
                    <h2 style="font-size:2rem; margin-top:0.5rem; letter-spacing:-1px">${item.name}</h2>
                    <p style="color:var(--text-muted)">${item.category} • Supplier: ${item.supplier}</p>
                </div>
                <div class="grid-2" style="margin-bottom:2rem">
                    <div class="kpi-card" style="background:var(--bg-body); border-left:5px solid var(--primary)">
                        <p class="kpi-label">Current Quantity</p>
                        <p style="font-size:1.5rem; font-weight:800">${item.qty} Units</p>
                        <p style="font-weight:600; color:${pct < state.settings.threshold ? 'var(--danger)' : 'var(--success)'}">${pct}% Full</p>
                    </div>
                    <div class="kpi-card" style="background:var(--bg-body)">
                        <p class="kpi-label">7-Day Forecast</p>
                        <p style="font-size:1.2rem; font-weight:800">${p.demand} / day</p>
                        <p style="font-size:0.9rem; color:var(--text-muted)">Stock-out in ${p.stockOut} days</p>
                    </div>
                </div>
                <div style="display:flex; justify-content: space-between; align-items:center;">
                    ${hasAccess('Manager') ? `<button class="btn btn-primary" onclick="adjustQty('${item.id}', 25)"><i data-lucide="plus"></i> Add 25</button>` : '<div></div>'}
                    <div class="action-cell">
                        <button class="btn btn-outline" onclick="reviewPO('${item.id}')"><i data-lucide="file-text"></i> Review PO</button>
                        <button class="btn btn-primary" onclick="downloadPO('${item.id}')"><i data-lucide="download"></i> Download</button>
                    </div>
                </div>
            `;
            modal.style.display = 'flex';
            lucide.createIcons();
        }

        // --- J. MODAL PANELS (TABLE DATA) ---
        function showListModal(html) { document.getElementById('list-modal-data').innerHTML = html; document.getElementById('list-modal').style.display = 'flex'; lucide.createIcons(); }
        
        function openInventoryPanel(page = 1) {
            const res = API.getInventory('', document.getElementById('cat-filter').value, page);
            showListModal(`
                <div class="panel-header"><h2 class="panel-title">Master Inventory</h2> <button class="btn btn-outline" onclick="exportData()"><i data-lucide="download"></i> Export CSV</button></div>
                <div class="data-table-container"><table class="data-table">
                    <thead><tr><th>Product</th><th>SKU</th><th>Quantity</th><th>Location</th><th>Action</th></tr></thead>
                    <tbody>${res.data.map(i => `<tr><td>${i.name}</td><td>${i.sku}</td><td><strong>${i.qty}</strong> / ${i.cap}</td><td>Shelf ${i.id}</td><td><button class="btn btn-outline mini-btn" onclick="openDetailById('${i.id}')">View</button></td></tr>`).join('')}</tbody>
                </table></div>
                <div class="pagination"><span class="page-info">Page ${page} of ${res.pages}</span> <button class="btn btn-outline mini-btn" ${page===1?'disabled':''} onclick="openInventoryPanel(${page-1})">Prev</button> <button class="btn btn-outline mini-btn" ${page===res.pages?'disabled':''} onclick="openInventoryPanel(${page+1})">Next</button></div>
            `);
        }

        function openLowStockPanel() {
            const items = API.getLowStock();
            showListModal(`<div class="panel-header"><h2 class="panel-title">Critical Levels</h2></div><div class="data-table-container"><table class="data-table"><thead><tr><th>Product</th><th>Count</th><th>Action</th></tr></thead><tbody>${items.map(i => `<tr><td>${i.name}</td><td>${i.qty}</td><td class="action-cell"><button class="btn btn-outline mini-btn" onclick="reviewPO('${i.id}')">Review PO</button> <button class="btn btn-primary mini-btn" onclick="downloadPO('${i.id}')"><i data-lucide="download" style="width:14px; height:14px"></i></button></td></tr>`).join('')}</tbody></table></div>`);
        }

        function openEmptyShelvesPanel() {
            const slots = API.getEmptySlots();
            showListModal(`<div class="panel-header"><h2 class="panel-title">Unoccupied Slots</h2></div><div class="data-table-container"><table class="data-table"><thead><tr><th>Slot</th><th>Location</th></tr></thead><tbody>${slots.map(s => `<tr><td><strong>${s.id}</strong></td><td>Shelf ${s.id[0]}</td></tr>`).join('')}</tbody></table></div>`);
        }

        function openAlertsPanel() {
            const alerts = state.alerts.filter(a => a.status === 'Active');
            showListModal(`<div class="panel-header"><h2 class="panel-title">System Alerts</h2></div><div class="data-table-container"><table class="data-table"><thead><tr><th>Priority</th><th>Message</th><th>Action</th></tr></thead><tbody>${alerts.map((a,idx) => `<tr><td><span class="status-pill status-${a.type==='danger'?'danger':'warning'}">${a.priority}</span></td><td>${a.text}</td><td><button class="btn btn-primary mini-btn" onclick="resolveAlert(${idx})">Resolve</button></td></tr>`).join('')}</tbody></table></div>`);
        }

        function openDemandPanel() {
            const items = state.inventory.slice(0, 10).map(i => ({...i, p: runPrediction(i)})).sort((a,b)=>b.p.demand - a.p.demand);
            showListModal(`<div class="panel-header"><h2 class="panel-title">Forecasting Analytics</h2></div><div class="data-table-container"><table class="data-table"><thead><tr><th>Product</th><th>Demand Prediction</th><th>Stock-Out Risk</th></tr></thead><tbody>${items.map(i => `<tr><td>${i.name}</td><td><strong>${i.p.demand}</strong> per day</td><td><span class="status-pill ${parseFloat(i.p.stockOut)<5?'status-danger':'status-success'}">${i.p.stockOut} Days</span></td></tr>`).join('')}</tbody></table></div>`);
        }

        function openRestockPanel() {
            const list = API.getRestockList();
            showListModal(`<div class="panel-header"><h2 class="panel-title">Restock Queue</h2><div class="action-cell"><button class="btn btn-outline" onclick="reviewCombinedPO()"><i data-lucide="file-text" style="width:16px;height:16px"></i> Review All</button> <button class="btn btn-primary" onclick="downloadCombinedPO()"><i data-lucide="download" style="width:16px;height:16px"></i> Order All</button></div></div><div class="data-table-container"><table class="data-table"><thead><tr><th>Product</th><th>Current</th><th>Required</th><th>Action</th></tr></thead><tbody>${list.map(i => `<tr><td>${i.name}</td><td>${i.qty}</td><td><strong>${i.restockQty}</strong></td><td class="action-cell"><button class="btn btn-outline mini-btn" onclick="reviewPO('${i.id}')">Review</button><button class="btn btn-primary mini-btn" onclick="downloadPO('${i.id}')"><i data-lucide="download" style="width:14px; height:14px"></i></button></td></tr>`).join('')}</tbody></table></div>`);
        }

        // --- K. GENERAL UTILITIES ---
        function resolveAlert(idx) { state.alerts[idx].status = 'Resolved'; logActivity(`Resolved alert regarding ${state.alerts[idx].id||'global system'}`); updateDashboard(); openAlertsPanel(); spawnToast({type:'info', text:'Archived.'}); }
        function applyFilters() { let res = state.inventory; const c = document.getElementById('cat-filter').value; const s = document.getElementById('shelf-filter').value; if(c!=='all') res = res.filter(i=>i.category===c); if(s!=='all') res = res.filter(i=>i.id.startsWith(s)); renderGrid(res); }
        function adjustQty(id, d) { const item = state.inventory.find(i=>i.id===id); item.qty = Math.min(item.cap, Math.max(0, item.qty+d)); logActivity(`Manual adjustment on ${item.name} (${d<0?d:'+'+d})`); updateDashboard(); renderGrid(); openDetail(item); }
        function toggleTheme() { const h = document.documentElement; const t = h.getAttribute('data-theme') === 'dark' ? 'light' : 'dark'; h.setAttribute('data-theme', t); document.getElementById('theme-icon').setAttribute('data-lucide', t==='dark'?'sun':'moon'); updateDashboard(); lucide.createIcons(); }
        function openSettings() { document.getElementById('settings-modal').style.display = 'flex'; }
        function closeModal(id) { document.getElementById(id).style.display = 'none'; }
        function closeDetail() { document.getElementById('detail-modal').style.display = 'none'; }
        function updateThreshold(v) { state.settings.threshold = parseInt(v); logActivity(`Updated Low Stock Threshold to ${v}%`); updateDashboard(); renderGrid(); }
        function toggleNotifications() { const p = document.getElementById('notif-panel'); p.style.display = p.style.display === 'block'?'none':'block'; }
        function clearAlerts() { state.alerts = state.alerts.filter(a=>a.status === 'Active'); updateDashboard(); }
        
        function renderAlertDropdown() {
            const list = document.getElementById('notif-list');
            if(!list) return;
            const active = state.alerts.filter(a => a.status === 'Active');
            list.innerHTML = active.length ? '' : '<p style="text-align:center; padding:1.5rem; color:var(--text-muted); font-size:0.8rem">No alerts</p>';
            active.slice(0, 5).forEach(a => { list.innerHTML += `<div class="notif-item" onclick="openAlertsPanel()"><strong>${a.priority}</strong>: ${a.text}</div>`; });
        }

        function spawnToast({type, text}) {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = 'toast';
            const colors = { 'critical': 'var(--danger)', 'warning': 'var(--warning)', 'info': 'var(--primary)', 'success': 'var(--success)' };
            toast.style.borderLeftColor = colors[type];
            toast.innerHTML = `<p style="font-weight:700; font-size:0.75rem; color:${colors[type]}">${type.toUpperCase()}</p><p style="font-size:0.85rem;">${text}</p>`;
            container.appendChild(toast);
            setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 500); }, 4000);
        }

        function exportData() { spawnToast({ type: 'info', text: 'Report exported successfully.' }); logActivity('Initiated CSV Data Export'); }

        // --- L. ROBOT SIMULATION ---
        let robotActive = false;
        let robotInterval = null;

        function toggleRobot() {
            robotActive = !robotActive;
            const btnText = document.getElementById('robot-btn-text');
            const toggleBtn = document.getElementById('robot-toggle');
            const badge = document.getElementById('robot-status-badge');
            
            if (robotActive) {
                btnText.innerText = 'Disengage Scanner';
                toggleBtn.className = 'btn btn-outline';
                toggleBtn.style.color = 'var(--danger)';
                toggleBtn.style.borderColor = 'var(--danger)';
                
                badge.className = 'status-pill status-success';
                badge.innerHTML = '<span class="blink">●</span> ACTIVE';
                
                logToRobotConsole('[SYS] Activating autonomous scanning protocol...', 'info');
                robotInterval = setInterval(simulateRobotScan, 4000);
            } else {
                btnText.innerText = 'Engage Scanner';
                toggleBtn.className = 'btn btn-primary';
                toggleBtn.style.color = '';
                toggleBtn.style.borderColor = '';
                
                badge.className = 'status-pill status-warning';
                badge.innerHTML = '<span class="blink">●</span> STANDBY';
                
                logToRobotConsole('[SYS] Robot operations suspended.', 'warning');
                clearInterval(robotInterval);
                
                document.getElementById('sensor-mq135').innerText = '---';
                document.getElementById('sensor-mq135-volt').innerText = '-- V';
                document.getElementById('sensor-distance').innerHTML = '--- <span style="font-size:1rem;">cm</span>';
                document.getElementById('sensor-location').innerText = 'Targeting: None';
            }
        }

        function logToRobotConsole(msg, type = 'normal') {
            const consoleDiv = document.getElementById('robot-console');
            const line = document.createElement('div');
            line.className = 'robot-console-line';
            if (type === 'alert' || type === 'danger') line.classList.add('robot-console-alert');
            else if (type === 'warning') { line.style.color = '#f59e0b'; line.style.borderLeftColor = '#f59e0b'; }
            else if (type === 'info') { line.style.color = '#64748b'; line.style.borderLeftColor = '#64748b'; }
            
            const ts = new Date().toLocaleTimeString('en-US', { hour12: false, hour: "numeric", minute: "numeric", second: "numeric" });
            line.innerText = `[${ts}] ${msg}`;
            
            consoleDiv.appendChild(line);
            if(consoleDiv.children.length > 5) {
                consoleDiv.removeChild(consoleDiv.firstChild);
            }
        }

        function simulateRobotScan() {
            // 1. Target a random shelf location
            const targetIndex = Math.floor(Math.random() * state.inventory.length);
            const item = state.inventory[targetIndex];
            
            document.getElementById('sensor-location').innerText = `Targeting: Shelf ${item.id}`;
            
            // 2. Ultrasonic Sensor (Distance inversely proportional to Qty)
            // Simulating shelf logic: Distance decreases as stock increases.
            // Say max distance from front is 120cm (empty), min distance is 20cm (full).
            let isFull = Math.random() > 0.6; 
            let distance = isFull ? Math.floor(Math.random() * 30 + 20) : Math.floor(Math.random() * 50 + 70); // cm
            
            document.getElementById('sensor-distance').innerHTML = `${distance} <span style="font-size:1rem;">cm</span>`;
            
            let estimatedQty = Math.floor(item.cap * ((120 - distance) / 100)); // Cap mapping
            if (estimatedQty < 0) estimatedQty = 0;
            if (estimatedQty > item.cap) estimatedQty = item.cap;
            
            let oldQty = item.qty;
            item.qty = estimatedQty;
            
            // Update the array object memory
            state.inventory[targetIndex].qty = estimatedQty;
            
            logToRobotConsole(`Scanning Sector ${item.id} -> US Dist: ${distance}cm -> Estimated Stock: ${estimatedQty}/${item.cap}`);
            
            // 3. MQ135 Gas Sensor Logic
            let gasValue = Math.floor(Math.random() * 40 + 10); // Normal range
            let gasAlert = false; 
            if(Math.random() > 0.85) { 
                gasValue = Math.floor(Math.random() * 30 + 55); 
            }
            if(gasValue > 50) gasAlert = true;

            let voltage = (gasValue * (5.0 / 1023.0)).toFixed(2);
            
            document.getElementById('sensor-mq135').innerText = gasValue;
            document.getElementById('sensor-mq135-volt').innerText = `${voltage} V`;
            if (gasAlert) {
                document.getElementById('sensor-mq135').style.color = 'var(--danger)';
            } else {
                document.getElementById('sensor-mq135').style.color = '';
            }
            
            // Trigger algorithms based on findings
            if (gasAlert) {
                logToRobotConsole(`CRITICAL: Gas breach detected at ${item.id} (Val: ${gasValue})!`, 'alert');
                if(!state.alerts.find(a => a.id === `GAS_${item.id}` && a.status === 'Active')) {
                    const alert = { id: `GAS_${item.id}`, type: 'danger', priority: 'Critical', text: `⚠️ MQ135 GAS LEAK at ${item.id}. Measured: ${gasValue} (${voltage}V)`, time: new Date().toLocaleTimeString(), status: 'Active' };
                    state.alerts.unshift(alert);
                    spawnToast({ type: 'critical', text: `ROBOT ALERT: Gas Leak at Sector ${item.id}` });
                    logActivity(`Robot detected gas leak at ${item.id}`);
                }
            }
            
            // Highlight a difference in stock if significant
            if(Math.abs(estimatedQty - oldQty) > 30) {
                spawnToast({ type: 'info', text: `ROBOT: Stock updated for ${item.id} from ${oldQty} to ${estimatedQty}.`});
                logActivity(`Robot mapped new stock for ${item.id}: ${estimatedQty} units`);
            }

            // Sync visual components and run algorithms
            updateDashboard();
            renderGrid();
        }

        window.onload = init;
    