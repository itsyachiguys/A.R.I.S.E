import re

with open("c:/Users/JIGISHA GAJJAR/OneDrive/Desktop/ARISE/index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Expand initData
init_data_old = """        function initData() {
            let idCounter = 1620; 
            shelves.forEach(sLetter => {
                for (let i = 1; i <= 20; i++) {
                    const id = sLetter + i;
                    const cap = 150 + Math.floor(Math.random() * 150);
                    const qtyPct = [0, 5, 20, 55, 85, 95][Math.floor(Math.random() * 6)];
                    const qty = Math.floor((qtyPct / 100) * cap);
                    let history = Array.from({length:7}, () => Math.floor(Math.random() * 20));

                    appState.inventory.push({
                        id, sku: `SKU-${10000 + idCounter--}`, name: `${categories[Math.floor(Math.random()*3)]} Unit ${id}`,
                        qty, cap, category: categories[Math.floor(Math.random()*3)], history,
                        lastUpdated: new Date(Date.now() - Math.random() * 86400000).toLocaleString(),
                        supplier: suppliers[Math.floor(Math.random()*3)], price: Math.floor(Math.random() * 100) + 10, rfid: 'RFID-' + Math.random().toString(36).substr(2, 6).toUpperCase(),
                        scanned: false
                    });
                }
            });"""

init_data_new = """        function initData() {
            let idCounter = 1620; 
            appState.inventory = []; // flush
            shelves.forEach(aisle => {
                for (let shelf = 1; shelf <= 3; shelf++) {
                    for (let bin = 1; bin <= 7; bin++) {
                        const id = `${aisle}${shelf}-${bin}`;
                        const cap = 150 + Math.floor(Math.random() * 150);
                        const qtyPct = [0, 5, 20, 55, 85, 95][Math.floor(Math.random() * 6)];
                        const qty = Math.floor((qtyPct / 100) * cap);
                        let history = Array.from({length:7}, () => Math.floor(Math.random() * 20));

                        appState.inventory.push({
                            id, sku: `SKU-${10000 + idCounter--}`, name: `${categories[Math.floor(Math.random()*3)]} Module`,
                            qty, cap, category: categories[Math.floor(Math.random()*3)], history,
                            lastUpdated: new Date(Date.now() - Math.random() * 86400000).toLocaleString(),
                            supplier: suppliers[Math.floor(Math.random()*3)], price: Math.floor(Math.random() * 100) + 10, rfid: 'RFID-' + Math.random().toString(36).substr(2, 6).toUpperCase(),
                            scanned: false, aisle: aisle, shelf: shelf, bin: bin
                        });
                    }
                }
            });"""
content = content.replace(init_data_old, init_data_new)

# 2. Update renderRobotics Mapper layout
mapper_old = """                            <div style="display:grid; grid-template-columns: repeat(20, 1fr); gap: 4px; padding: 1.5rem 1rem; background: var(--bg-panel); border-radius: 8px; border: 1px solid var(--border);">
                                ${appState.inventory.map(i => {
                                    const isTarget = appState.robot.currentTarget === i.id;
                                    let bg = 'var(--bg-body)'; let op = 0.3;
                                    if(i.scanned) {
                                        const pct = (i.qty/i.cap)*100;
                                        bg = `var(--${pct < appState.settings.threshold ? (pct===0?'danger':'warning') : 'success'})`;
                                        op = 0.8;
                                    }
                                    if(isTarget) { bg = 'var(--primary)'; op = 1; }
                                    return `<div id="rbt-map-${i.id}" style="aspect-ratio: 1; border-radius: 4px; background: ${bg}; ${isTarget ? 'box-shadow: 0 0 12px var(--primary); transform: scale(1.3); animation: pulse 1s infinite; z-index:10; position:relative;' : 'transition: background 0.3s;'} border: 1px solid var(--border); opacity: ${op}; cursor:help;" title="Sector ${i.id}${i.scanned?` | Verified Stock: ${i.qty}/${i.cap}`:' | Status: Unverified'}"></div>`;
                                }).join('')}
                            </div>"""

mapper_new = """                            <div style="display:flex; flex-direction:column; gap: 1.5rem; padding: 1.5rem 1rem; background: var(--bg-panel); border-radius: 8px; border: 1px solid var(--border);">
                                ${['A', 'B', 'C'].map(aisle => `
                                    <div class="aisle-block" style="background: var(--bg-body); padding: 1rem; border-radius: 8px; border: 1px solid var(--border);">
                                        <h4 style="margin-bottom:0.8rem; color:var(--text-main); font-size: 0.9rem;"><i data-lucide="align-justify" style="width:14px;display:inline;"></i> Warehouse Aisle ${aisle}</h4>
                                        <div style="display:flex; flex-direction:column; gap: 0.8rem;">
                                            ${[1, 2, 3].map(shelf => `
                                                <div style="display:flex; gap: 0.5rem; align-items:center;">
                                                    <span style="font-size:0.75rem; color:var(--text-muted); font-family:monospace; min-width:60px;">SHELF ${shelf}</span>
                                                    <div style="display:grid; grid-template-columns: repeat(7, 1fr); gap: 6px; flex-grow:1;">
                                                        ${appState.inventory.filter(i => i.aisle === aisle && i.shelf === shelf).map(i => {
                                                            const isTarget = appState.robot.currentTarget === i.id;
                                                            let bg = 'var(--bg-panel)'; let op = 0.3;
                                                            if(i.scanned) {
                                                                const pct = (i.qty/i.cap)*100;
                                                                bg = `var(--${pct < appState.settings.threshold ? (pct===0?'danger':'warning') : 'success'})`;
                                                                op = 0.8;
                                                            }
                                                            if(isTarget) { bg = 'var(--primary)'; op = 1; }
                                                            return `<div id="rbt-map-${i.id}" style="height: 18px; border-radius: 3px; background: ${bg}; ${isTarget ? 'box-shadow: 0 0 8px var(--primary); transform: scale(1.2); animation: pulse 1s infinite; z-index:10; position:relative;' : 'transition: background 0.3s;'} border: 1px solid var(--border); opacity: ${op}; cursor:help;" title="ID: ${i.id}${i.scanned?` | Stock: ${i.qty}/${i.cap}`:' | Unverified'}"></div>`;
                                                        }).join('')}
                                                    </div>
                                                </div>
                                            `).join('')}
                                        </div>
                                    </div>
                                `).join('')}
                            </div>"""

content = content.replace(mapper_old, mapper_new)

# 3. Update renderGrid (Inventory visual grid layout)
grid_old_match = re.search(r"function renderGrid\(data, grouped = true\) \{([\s\S]*?)\} else \{([\s\S]*?)\} return html;\}", content)

grid_new = """function renderGrid(data, grouped = true) {
            let html = '';
            if(!grouped) {
                html += '<div class="shelf-grid" style="grid-template-columns: repeat(auto-fill, minmax(30px, 1fr)); gap:6px;">';
                data.forEach(i => {
                    const pct = (i.qty/i.cap)*100;
                    let color = 'success';
                    if(pct===0) color='danger'; else if(pct < appState.settings.threshold) color='warning';
                    html += `<div class="box bg-${color}" onclick="openProductDetail('${i.id}')" title="${i.id} - ${i.name} (${i.qty}/${i.cap})"></div>`;
                });
                html += '</div>';
            } else {
                ['A', 'B', 'C'].forEach(aisle => {
                    const aisleData = data.filter(i=>i.aisle === aisle);
                    if(aisleData.length === 0) return;
                    html += `<div class="shelf-row" style="background:var(--bg-body); padding:1rem; border-radius:8px; border:1px solid var(--border); margin-bottom:1rem; flex-direction:column; align-items:stretch;">
                                <div class="shelf-label" style="text-align:left; padding-left:0; border-bottom:1px solid var(--border); padding-bottom:0.5rem; margin-bottom:1rem; writing-mode: horizontal-tb; transform:none; width:auto; color:var(--primary); font-weight:700;"><i data-lucide="layers" style="width:16px;height:16px;display:inline;vertical-align:middle;"></i> Aisle ${aisle}</div>`;
                    
                    [1, 2, 3].forEach(shelf => {
                        const shelfData = aisleData.filter(i=>i.shelf === shelf);
                        if(shelfData.length === 0) return;
                        html += `<div style="display:flex; gap:1rem; align-items:center; margin-bottom: 0.5rem;">
                                    <span style="font-size:0.75rem; color:var(--text-muted); font-family:monospace; min-width:60px;">SHELF ${shelf}</span>
                                    <div class="shelf-grid" style="grid-template-columns: repeat(7, 1fr); flex-grow:1; gap:6px;">`;
                        
                        shelfData.forEach(i => {
                            const pct = (i.qty/i.cap)*100;
                            let color = 'success';
                            if(pct===0) color='danger'; else if(pct < appState.settings.threshold) color='warning';
                            html += `<div class="box bg-${color}" onclick="openProductDetail('${i.id}')" title="${i.id} - ${i.name} (${i.qty}/${i.cap})" style="height:25px; border-radius:4px;"></div>`;
                        });
                        html += `</div></div>`;
                    });
                    html += `</div>`;
                });
            }
            return html;
        }"""
        
if grid_old_match:
    match_str = grid_old_match.group(0)
    # The regex group matched all the way to `return html;}`
    # but since it's tricky, we'll use string replacement for the exact extracted text
    pass

# We will just replace it via regex substitute safely
content = re.sub(r'function renderGrid\(data, grouped = true\) \{[\s\S]*?return html;\s*\}', grid_new, content)

with open("c:/Users/JIGISHA GAJJAR/OneDrive/Desktop/ARISE/index.html", "w", encoding="utf-8") as f:
    f.write(content)
