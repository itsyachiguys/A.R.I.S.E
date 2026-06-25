import re

# We will generate a complete new index.html with SPA state-based rendering.

html_content = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A.R.I.S.E | Smart Warehouse Dashboard v2.1</title>
    
    <!-- LIBRARIES -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --primary: #4ade80; /* Bright Green */
            --primary-dark: #22c55e;
            --success: #22c55e;
            --warning: #facc15;
            --danger: #f87171;
            --critical: #ef4444;
            --bg-body: #050a08; 
            --bg-card: #0d1b14; 
            --bg-panel: #14281d;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border: #1d3326;
            --shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
            --sidebar-width: 260px;
            --radius-md: 12px;
            --radius-lg: 16px;
        }

        [data-theme="light"] {
            --primary: #16a34a; 
            --primary-dark: #15803d;
            --success: #16a34a;
            --warning: #d97706;
            --danger: #dc2626;
            --critical: #b91c1c;
            --bg-body: #f0fdf4; 
            --bg-card: #ffffff; 
            --bg-panel: #f8fafc;
            --text-main: #0f172a;
            --text-muted: #475569;
            --border: #e2e8f0;
            --shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background: var(--bg-body); color: var(--text-main); display: flex; height: 100vh; overflow: hidden; transition: background 0.3s, color 0.3s; }

        /* SIDEBAR */
        .sidebar {
            width: var(--sidebar-width);
            background: var(--bg-card);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            padding: 1.5rem 1rem;
            z-index: 100;
            transition: all 0.3s ease;
        }
        .logo-container {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 2.5rem;
            padding-left: 0.5rem;
        }
        .logo { font-weight: 800; font-size: 1.5rem; color: var(--text-main); letter-spacing: -0.5px; }
        .logo span { color: var(--primary); }

        .nav-label { font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: var(--text-muted); letter-spacing: 1px; margin: 1.5rem 0 0.5rem 0.5rem; }
        .nav-item { display: flex; align-items: center; gap: 12px; padding: 0.8rem 1rem; border-radius: var(--radius-md); color: var(--text-main); text-decoration: none; cursor: pointer; transition: all 0.2s; margin-bottom: 0.3rem; }
        .nav-item:hover, .nav-item.active { background: rgba(74, 222, 128, 0.1); color: var(--primary); }
        .nav-item i { width: 18px; height: 18px; }

        /* MAIN CONTENT AREA */
        .main-wrapper { flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative; }

        /* HEADER */
        header { padding: 1.2rem 2rem; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border); background: var(--bg-body); position: relative; z-index: 50; }
        
        .header-content { display: flex; align-items: center; gap: 2rem; flex: 1; }
        .breadcrumb { display: flex; align-items: center; gap: 0.5rem; color: var(--text-muted); font-size: 0.85rem; font-weight: 600; text-transform: uppercase; }
        .breadcrumb span.active { color: var(--primary); }
        
        /* Search Bar Fix */
        .search-container { position: relative; width: 400px; display: flex; align-items: center; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-md); transition: border-color 0.2s; overflow: hidden; padding: 0 1rem; height: 42px;}
        .search-container:focus-within { border-color: var(--primary); }
        .search-icon { color: var(--text-muted); width: 18px; display: flex; align-items: center; justify-content: center; }
        .search-container input { width: 100%; border: none; background: transparent; color: var(--text-main); outline: none; padding: 0 0.8rem; font-size: 0.85rem; height: 100%; }
        .search-filter-icon { color: var(--text-muted); width: 18px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: color 0.2s; }
        .search-filter-icon:hover { color: var(--primary); }

        .header-actions { display: flex; align-items: center; gap: 1.5rem; }
        .icon-btn { cursor: pointer; color: var(--text-muted); background: none; border: none; position: relative; transition: color 0.2s; display: flex; align-items: center; justify-content: center; padding:0; height:24px; width:24px;}
        .icon-btn:hover { color: var(--text-main); }
        .badge { position: absolute; top: -6px; right: -6px; background: var(--critical); color: white; font-size: 0.65rem; font-weight: 700; width: 16px; height: 16px; display: flex; align-items: center; justify-content: center; border-radius: 50%; }
        .profile-btn { width: 40px; height: 40px; border-radius: 50%; background: var(--bg-panel); color: var(--primary); border: 1px solid var(--border); display: flex; align-items: center; justify-content: center; font-weight: 700; cursor: pointer; }

        /* MAIN SCROLLABLE AREA */
        main { padding: 2rem; flex: 1; overflow-y: auto; overflow-x: hidden; position: relative; }

        /* PAGE TRANSITIONS */
        .page-view { animation: fadeIn 0.3s ease forwards; display: none; }
        .page-view.active { display: block; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        /* STANDARDIZED UI ELEMENTS */
        .btn { padding: 0.6rem 1.2rem; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem; border: 1px solid transparent; font-size: 0.85rem; }
        .btn-primary { background: rgba(74, 222, 128, 0.15); color: var(--primary); border-color: rgba(74, 222, 128, 0.3); }
        .btn-primary:hover { background: rgba(74, 222, 128, 0.25); border-color: var(--primary); transform: translateY(-1px); }
        .btn-danger { background: rgba(239, 68, 68, 0.15); color: var(--danger); border-color: rgba(239, 68, 68, 0.3); }
        .btn-danger:hover { background: rgba(239, 68, 68, 0.25); border-color: var(--danger); }
        .btn-outline { background: transparent; border-color: var(--border); color: var(--text-main); }
        .btn-outline:hover { background: var(--bg-panel); }
        .mini-btn { padding: 0.4rem 0.8rem; font-size: 0.75rem; border-radius: 6px; }

        .form-group { margin-bottom: 1.2rem; }
        .form-label { display: block; font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.5rem; font-weight: 600; }
        .form-control { width: 100%; padding: 0.7rem; border: 1px solid var(--border); border-radius: 8px; background: var(--bg-panel); color: var(--text-main); font-size: 0.85rem; outline: none; transition: border 0.2s; }
        .form-control:focus { border-color: var(--primary); }

        .card { background: var(--bg-card); padding: 1.5rem; border-radius: var(--radius-lg); border: 1px solid var(--border); box-shadow: var(--shadow); position: relative; overflow: hidden; }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.2rem; border-bottom: 1px solid var(--border); padding-bottom: 0.8rem; }
        .card-title { font-size: 1rem; font-weight: 600; color: var(--text-main); display: flex; align-items: center; gap: 0.5rem; }

        /* KPIs */
        .kpi-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.2rem; margin-bottom: 2rem; }
        .kpi-card { background: var(--bg-card); padding: 1.2rem; border-radius: var(--radius-lg); border: 1px solid var(--border); box-shadow: var(--shadow); cursor: pointer; transition: transform 0.2s, border-color 0.2s; position: relative; overflow: hidden; }
        .kpi-card:hover { transform: translateY(-3px); border-color: var(--primary-dark); }
        .kpi-label { font-size: 0.75rem; color: var(--text-muted); font-weight: 600; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.5px; }
        .kpi-value { font-size: 1.6rem; font-weight: 700; color: var(--text-main); }
        .kpi-icon { position: absolute; top: 1.2rem; right: 1.2rem; opacity: 0.2; width: 28px; height: 28px; }

        /* LAYOUT GRIDS */
        .grid-2-col { display: grid; grid-template-columns: 2fr 1fr; gap: 1.5rem; }
        .grid-3-col { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1.5rem; }
        .page-layout { display: grid; grid-template-columns: 3fr 1fr; gap: 1.5rem; align-items: start; }

        /* WAREHOUSE GRID */
        .warehouse-container { display: flex; flex-direction: column; gap: 1.5rem; }
        .shelf-block { background: var(--bg-panel); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.2rem; }
        .shelf-title { font-weight: 700; margin-bottom: 1rem; color: var(--text-muted); display: flex; align-items: center; gap: 0.5rem; font-size: 0.9rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }
        .box-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 1rem; }
        .shelf-box { aspect-ratio: 1.2; padding: 0.8rem; border-radius: 8px; cursor: pointer; transition: all 0.2s; display: flex; flex-direction: column; justify-content: space-between; color: #fff; position: relative; overflow: hidden; border: 1px solid rgba(255,255,255,0.1); }
        .shelf-box::before { content: ''; position: absolute; top:0; left:0; width:100%; height:100%; background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(0,0,0,0) 100%); pointer-events: none; }
        .shelf-box:hover { transform: scale(1.05); filter: brightness(1.1); }
        .box-id { font-weight: 800; font-size: 1rem; z-index: 1; }
        .box-pct { font-size: 0.7rem; font-weight: 600; background: rgba(0,0,0,0.4); padding: 2px 6px; border-radius: 4px; align-self: flex-start; z-index: 1; backdrop-filter: blur(2px); }

        .bg-full { background: #166534; } 
        .bg-low { background: #b45309; }  
        .bg-critical { background: #991b1b; } 
        .bg-empty { background: #7f1d1d; border: 1px dashed var(--danger); animation: flash 2s infinite; }
        @keyframes flash { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }

        /* DATA TABLES */
        .table-responsive { overflow-x: auto; border-radius: var(--radius-md); border: 1px solid var(--border); background: var(--bg-card); }
        .data-table { width: 100%; border-collapse: collapse; text-align: left; }
        .data-table th { padding: 1rem; border-bottom: 2px solid var(--border); color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; font-weight: 700; background: var(--bg-panel); white-space: nowrap; }
        .data-table td { padding: 1rem; border-bottom: 1px solid var(--border); font-size: 0.85rem; vertical-align: middle; }
        .data-table tr:hover td { background: rgba(255,255,255,0.02); }
        .data-table tr:last-child td { border-bottom: none; }

        /* STATUS PILLS */
        .status-pill { padding: 4px 10px; border-radius: 20px; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; display: inline-flex; align-items: center; gap: 4px;}
        .status-success { background: rgba(34, 197, 94, 0.1); color: var(--success); border: 1px solid rgba(34, 197, 94, 0.3); }
        .status-warning { background: rgba(245, 158, 11, 0.1); color: var(--warning); border: 1px solid rgba(245, 158, 11, 0.3); }
        .status-danger { background: rgba(239, 68, 68, 0.1); color: var(--danger); border: 1px solid rgba(239, 68, 68, 0.3); }

        /* ROBOTICS PANEL */
        .robot-panel { position: relative; }
        .robot-glow { position: absolute; top: -50%; right: -20%; width: 200px; height: 200px; background: rgba(74, 222, 128, 0.1); filter: blur(60px); pointer-events: none; }
        .robot-console-line { margin: 2px 0; border-left: 2px solid var(--primary); padding-left: 8px; animation: slideInX 0.2s; font-family: monospace; }
        .robot-console-alert { color: var(--danger); border-left-color: var(--danger); }
        @keyframes slideInX { from { transform: translateX(-10px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }

        /* DROPDOWNS & MODALS */
        .dropdown { position: absolute; top: 120%; right: 0; width: 320px; background: var(--bg-panel); border: 1px solid var(--border); border-radius: var(--radius-md); box-shadow: var(--shadow); padding: 1rem; display: none; z-index: 1001; opacity: 0; transform: translateY(-10px); transition: opacity 0.2s, transform 0.2s; }
        .dropdown.show { display: block; opacity: 1; transform: translateY(0); }
        
        /* Notifications Panel inner */
        .notif-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 0.8rem; margin-bottom: 0.8rem; font-size: 0.9rem; font-weight: 600; }
        .notif-list { max-height: 250px; overflow-y: auto; display: flex; flex-direction: column; gap: 0.5rem; }
        .notif-item { padding: 0.8rem; border-radius: 8px; font-size: 0.8rem; border: 1px solid var(--border); background: var(--bg-card); display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; }
        .notif-item:hover { border-color: var(--primary); }
        .notif-item.read { opacity: 0.6; }
        
        .search-results-dropdown { left: 0; right: auto; width: 100%; top: calc(100% + 5px); }
        .search-result-item { padding: 0.7rem 1rem; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: space-between; font-size: 0.85rem; }
        .search-result-item:hover { background: var(--bg-panel); color: var(--primary); }

        .modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.7); display: none; justify-content: center; align-items: center; z-index: 2000; backdrop-filter: blur(4px); }
        .modal-overlay.active { display: flex; }
        .modal-content { background: var(--bg-panel); width: 90%; max-width: 600px; border-radius: var(--radius-lg); padding: 2rem; position: relative; border: 1px solid var(--border); box-shadow: 0 25px 50px -12px rgba(0,0,0,0.8); animation: zoomIn 0.2s; }
        .modal-close { position: absolute; top: 1.5rem; right: 1.5rem; font-size: 1.5rem; cursor: pointer; color: var(--text-muted); transition: color 0.2s; display:flex; align-items:center; justify-content:center; width: 30px; height: 30px; border-radius: 50%; background: var(--bg-card); border: 1px solid var(--border); }
        .modal-close:hover { color: var(--danger); border-color: var(--danger); }
        @keyframes zoomIn { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }

        /* TOAST */
        #toast-container { position: fixed; bottom: 2rem; right: 2rem; z-index: 9999; display: flex; flex-direction: column; gap: 0.8rem; }
        .toast { padding: 1rem 1.5rem; border-radius: var(--radius-md); background: var(--bg-panel); border: 1px solid var(--border); box-shadow: var(--shadow); border-left: 4px solid var(--primary); animation: slideInUp 0.3s forwards; max-width: 350px; }
        @keyframes slideInUp { from { transform: translateY(100%); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

        /* SCROLLBAR */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

        .empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 3rem; color: var(--text-muted); gap: 1rem; }
        
        /* Tabs */
        .tabs { display: flex; gap: 1rem; border-bottom: 1px solid var(--border); margin-bottom: 1.5rem; }
        .tab-item { padding: 0.8rem 1rem; cursor: pointer; border-bottom: 2px solid transparent; font-size: 0.9rem; font-weight: 600; color: var(--text-muted); transition: all 0.2s; }
        .tab-item:hover { color: var(--text-main); }
        .tab-item.active { color: var(--primary); border-bottom-color: var(--primary); }
    </style>
</head>
<body>
    <!-- SIDEBAR NAVIGATION -->
    <aside class="sidebar">
        <div class="logo-container">
            <div class="logo">A.R.I.S.E<span>.</span></div>
        </div>
        
        <p class="nav-label">General Mode</p>
        <a class="nav-item active" data-path="dashboard"><i data-lucide="layout-dashboard"></i> Dashboard</a>
        <a class="nav-item" data-path="inventory"><i data-lucide="box"></i> Inventory Engine</a>
        <a class="nav-item" data-path="analytics"><i data-lucide="line-chart"></i> Analytics Hub</a>
        <a class="nav-item" data-path="robotics"><i data-lucide="cpu"></i> Robotics Control</a>
        
        <p class="nav-label">Management</p>
        <a class="nav-item" data-path="procurement"><i data-lucide="file-text"></i> Procurement</a>
        
        <div style="margin-top: auto;">
            <a class="nav-item" data-path="settings"><i data-lucide="settings"></i> Settings</a>
            <a class="nav-item" data-path="profile"><i data-lucide="user"></i> My Profile</a>
        </div>
    </aside>

    <div class="main-wrapper">
        <!-- HEADER -->
        <header>
            <div class="header-content">
                <div class="breadcrumb">
                    <span id="bc-main">A.R.I.S.E</span> / <span id="bc-current" class="active">Dashboard</span>
                </div>
                
                <div class="search-container">
                    <i data-lucide="search" class="search-icon"></i>
                    <input type="text" id="global-search" placeholder="Search products, regions, skus...">
                    <i data-lucide="sliders-horizontal" class="search-filter-icon" title="Advanced Search"></i>
                    <div class="dropdown search-results-dropdown" id="search-dropdown"></div>
                </div>
            </div>
            
            <div class="header-actions">
                <div style="position: relative;">
                    <button class="icon-btn" id="notif-trigger">
                        <i data-lucide="bell"></i>
                        <span class="badge" id="notif-badge" style="display:none;">0</span>
                    </button>
                    <div class="dropdown" id="notif-panel">
                        <div class="notif-header">
                            <span>Notifications</span>
                            <div style="display:flex; gap: 0.5rem;">
                                <button class="btn btn-outline mini-btn" id="btn-mark-read">Mark Read</button>
                                <button class="btn btn-danger mini-btn" id="btn-clear-notif"><i data-lucide="trash-2" style="width:12px;height:12px;"></i> Clear</button>
                            </div>
                        </div>
                        <div class="notif-list" id="notif-list">
                            <!-- Injected -->
                        </div>
                    </div>
                </div>
                
                <button class="icon-btn" id="theme-toggle" title="Toggle Theme">
                    <i data-lucide="sun" id="theme-icon"></i>
                </button>

                <div class="profile-btn" data-path="profile">AD</div>
            </div>
        </header>

        <!-- SPA MAINFRAME -->
        <main id="app-content">
            <!-- Dynamic Content Injected Here -->
        </main>
    </div>

    <!-- GLOBAL MODALS -->
    <!-- Product Detail Modal Side Drawer replacement (but functioning as centered modal for now) -->
    <div class="modal-overlay" id="detail-modal">
        <div class="modal-content" id="modal-data">
            <!-- Content -->
        </div>
    </div>
    
    <!-- Procurement PO Preview Modal -->
    <div class="modal-overlay" id="po-modal">
        <div class="modal-content" style="max-width: 700px;">
            <div class="modal-close" onclick="document.getElementById('po-modal').classList.remove('active')"><i data-lucide="x"></i></div>
            <h2 style="margin-bottom: 1.5rem; border-bottom: 1px solid var(--border); padding-bottom:1rem; font-size:1.2rem;">Review Procurement Order</h2>
            <div id="po-preview-content" style="background: var(--bg-body); padding: 1.5rem; border-radius: 8px; font-family: monospace; font-size: 0.8rem; line-height: 1.5; white-space: pre-wrap; margin-bottom: 1.5rem; max-height: 50vh; overflow-y: auto; border: 1px solid var(--border);"></div>
            <div style="display: flex; gap: 1rem; justify-content: flex-end;">
                <button class="btn btn-outline" onclick="document.getElementById('po-modal').classList.remove('active')">Cancel</button>
                <button class="btn btn-primary" id="po-download-btn"><i data-lucide="download"></i> Download PDF</button>
            </div>
        </div>
    </div>

    <!-- Confirmation Modal -->
    <div class="modal-overlay" id="confirm-modal">
        <div class="modal-content" style="max-width: 400px; text-align:center; padding: 2.5rem;">
            <i data-lucide="alert-triangle" style="width: 48px; height: 48px; color: var(--warning); margin: 0 auto 1.5rem auto;"></i>
            <h3 style="margin-bottom: 0.5rem;" id="confirm-title">Are you sure?</h3>
            <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 2rem;" id="confirm-text">This action cannot be undone.</p>
            <div style="display: flex; gap: 1rem; justify-content: center;">
                <button class="btn btn-outline" onclick="document.getElementById('confirm-modal').classList.remove('active')">Cancel</button>
                <button class="btn btn-danger" id="confirm-action-btn">Confirm</button>
            </div>
        </div>
    </div>

    <!-- TOASTS -->
    <div id="toast-container"></div>

    <!-- APP LOGIC -->
    <script>
        // --- STATE MANAGEMENT ---
        const appState = {
            currentPage: "dashboard",
            inventory: [],
            logs: [],
            alerts: [],
            settings: { threshold: 20, role: 'Admin', leadTime: 3, growthFactor: 1.15, alertsEnabled: true },
            filters: { search: '', category: 'all', shelf: 'all', analyticsPeriod: '7d', analyticsProduct: 'all' },
            robot: { active: false, interval: null }
        };

        const shelves = ['A', 'B', 'C'];
        const categories = ['Electronics', 'Grocery', 'Furniture'];
        const suppliers = ['Global Logistics', 'Nexus Parts', 'EcoSupply Co'];
        let charts = {};

        // --- CORE UTILITIES ---
        function generateID() { return Math.random().toString(36).substr(2, 9); }
        function spawnToast(type, text) {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = 'toast';
            const colors = { critical: 'var(--danger)', warning: 'var(--warning)', info: 'var(--primary)', success: 'var(--success)' };
            toast.style.borderLeftColor = colors[type] || colors.info;
            toast.innerHTML = `<p style="font-weight:700; font-size:0.75rem; color:${colors[type]}">${type.toUpperCase()}</p><p style="font-size:0.85rem;">${text}</p>`;
            container.appendChild(toast);
            setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }, 3000);
        }
        function logActivity(msg) {
            appState.logs.unshift({ msg, time: new Date().toLocaleTimeString() });
            if(appState.logs.length > 50) appState.logs.pop();
            console.log(`[ERP_LOG]: ${msg}`);
        }
        function hasAccess(level) {
            const roles = { 'Admin': 3, 'Manager': 2, 'Staff': 1 };
            return roles[appState.settings.role] >= roles[level];
        }

        // --- MOCK DATA ENGINE ---
        function initData() {
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
                        supplier: suppliers[Math.floor(Math.random()*3)], price: Math.floor(Math.random() * 100) + 10, rfid: 'RFID-' + Math.random().toString(36).substr(2, 6).toUpperCase()
                    });
                }
            });

            // Initial Alerts
            processAlerts();
            logActivity("System Core Booted & Inventory Loaded");
        }

        function runPrediction(item) {
            const avg = item.history.reduce((a,b)=>a+b, 0) / 7;
            const seasonal = avg * appState.settings.growthFactor;
            const stockOut = seasonal > 0 ? Math.floor(item.qty / seasonal) : 999;
            return { demand: seasonal.toFixed(1), stockOut, restockQty: Math.max(50, Math.ceil((seasonal * appState.settings.leadTime * 2) - item.qty)) };
        }

        // --- NOTIFICATIONS & ALERTS ---
        function processAlerts() {
            if(!appState.settings.alertsEnabled) return;
            
            // Check Low Stock
            appState.inventory.forEach(item => {
                const pct = (item.qty / item.cap) * 100;
                if(pct < appState.settings.threshold) {
                    const existing = appState.alerts.find(a => a.itemId === item.id && !a.resolved);
                    if(!existing) {
                        appState.alerts.unshift({ id: generateID(), itemId: item.id, type: pct === 0 ? 'critical' : 'warning', text: `${pct === 0 ? 'EMPTY' : 'LOW STOCK'}: Sector ${item.id}`, time: new Date().toLocaleTimeString(), resolved: false, read: false });
                    }
                }
            });
            updateNotifUI();
        }

        function updateNotifUI() {
            const list = document.getElementById('notif-list');
            const badge = document.getElementById('notif-badge');
            const activeAlerts = appState.alerts.filter(a => !a.resolved);
            const unreadCount = activeAlerts.filter(a => !a.read).length;
            
            if(unreadCount > 0) {
                badge.style.display = 'flex';
                badge.innerText = unreadCount;
            } else {
                badge.style.display = 'none';
            }

            if(activeAlerts.length === 0) {
                list.innerHTML = '<div class="empty-state" style="padding: 1.5rem;"><i data-lucide="check-circle" style="width:30px;height:30px"></i> All clear.</div>';
            } else {
                list.innerHTML = activeAlerts.map(a => `
                    <div class="notif-item ${a.read ? 'read' : ''}" data-id="${a.id}">
                        <div style="flex:1">
                            <p style="font-weight:600; color: var(--${a.type==='critical'?'danger':'warning'});">${a.text}</p>
                            <p style="font-size:0.7rem; color:var(--text-muted); margin-top:2px;">${a.time}</p>
                        </div>
                        <button class="btn btn-outline mini-btn" onclick="resolveAlert('${a.id}')" style="padding:4px;"><i data-lucide="check" style="width:14px;height:14px"></i></button>
                    </div>
                `).join('');
            }
            lucide.createIcons();
        }

        function resolveAlert(id) {
            const a = appState.alerts.find(a => a.id === id);
            if(a) { a.resolved = true; a.read = true; updateNotifUI(); }
        }

        document.getElementById('btn-mark-read').addEventListener('click', () => {
            appState.alerts.forEach(a => a.read = true);
            updateNotifUI();
        });

        document.getElementById('btn-clear-notif').addEventListener('click', () => {
            document.getElementById('confirm-title').innerText = "Clear All Alerts?";
            document.getElementById('confirm-text').innerText = "This will permanently archive all current system notifications.";
            document.getElementById('confirm-modal').classList.add('active');
            
            document.getElementById('confirm-action-btn').onclick = () => {
                appState.alerts = appState.alerts.filter(a => a.resolved); // Keep resolved history, clear active
                appState.alerts.forEach(a => { a.resolved = true; a.read = true; }); // Mark everything resolved
                updateNotifUI();
                spawnToast('success', 'Alerts cleared.');
                document.getElementById('confirm-modal').classList.remove('active');
            };
        });

        // --- SPA ROUTING ---
        const pages = {
            dashboard: renderDashboard,
            inventory: renderInventory,
            analytics: renderAnalytics,
            robotics: renderRobotics,
            procurement: renderProcurement,
            profile: renderProfile,
            settings: renderSettings
        };

        function navigate(path) {
            if(!pages[path]) path = "dashboard";
            appState.currentPage = path;
            
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            const activeNav = document.querySelector(`.nav-item[data-path="${path}"]`);
            if(activeNav) activeNav.classList.add('active');
            
            document.getElementById('bc-current').innerText = path.charAt(0).toUpperCase() + path.slice(1);
            
            // Re-render Main Content Container
            const main = document.getElementById('app-content');
            main.innerHTML = `<div class="empty-state"><i data-lucide="loader-2" class="blink"></i> Loading module...</div>`;
            lucide.createIcons();
            
            setTimeout(() => {
                const markup = pages[path]();
                main.innerHTML = `<div class="page-view active">${markup}</div>`;
                if(path === 'dashboard' || path === 'analytics') initCharts(path);
                lucide.createIcons();
            }, 100);
            
            // Sync URL hash without jumping
            history.pushState(null, null, `#${path}`);
            logActivity(`Navigated to ${path}`);
        }

        // Add Listeners
        document.querySelectorAll('[data-path]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                navigate(link.getAttribute('data-path'));
            });
        });

        window.addEventListener('popstate', () => {
            let hash = window.location.hash.replace('#', '');
            navigate(hash || 'dashboard');
        });

        // --- PAGE RENDER FUNCTIONS ---

        function renderDashboard() {
            const totQty = appState.inventory.reduce((a,b)=>a+b.qty,0);
            const lowCount = appState.inventory.filter(i => (i.qty/i.cap)*100 < appState.settings.threshold && i.qty > 0).length;
            const empty = appState.inventory.filter(i=>i.qty===0).length;
            const avgDemand = (appState.inventory.reduce((a,b)=>a+parseFloat(runPrediction(b).demand),0)/appState.inventory.length).toFixed(1);
            const alertsCount = appState.alerts.filter(a=>!a.resolved).length;
            
            return `
                <div class="kpi-row">
                    <div class="kpi-card" onclick="navigate('inventory')">
                        <i data-lucide="boxes" class="kpi-icon" style="color: var(--primary)"></i>
                        <p class="kpi-label">Total Inventory</p>
                        <div class="kpi-value">${totQty.toLocaleString()}</div>
                    </div>
                    <div class="kpi-card" onclick="navigate('inventory')">
                        <i data-lucide="alert-circle" class="kpi-icon" style="color: var(--warning)"></i>
                        <p class="kpi-label">Low Stock</p>
                        <div class="kpi-value" style="color: var(--warning)">${lowCount}</div>
                    </div>
                    <div class="kpi-card" onclick="navigate('inventory')">
                        <i data-lucide="layers" class="kpi-icon" style="color: var(--danger)"></i>
                        <p class="kpi-label">Empty Shelves</p>
                        <div class="kpi-value" style="color: var(--danger)">${empty}</div>
                    </div>
                    <div class="kpi-card" onclick="document.getElementById('notif-trigger').click()">
                        <i data-lucide="activity" class="kpi-icon" style="color: var(--critical)"></i>
                        <p class="kpi-label">Active Alerts</p>
                        <div class="kpi-value" style="color: var(--critical)">${alertsCount}</div>
                    </div>
                    <div class="kpi-card" onclick="navigate('analytics')">
                        <i data-lucide="trending-up" class="kpi-icon" style="color: var(--primary)"></i>
                        <p class="kpi-label">Avg Demand / Day</p>
                        <div class="kpi-value">${avgDemand}</div>
                    </div>
                </div>

                <div class="grid-2-col">
                    <div class="card">
                        <div class="card-header">
                            <span class="card-title"><i data-lucide="line-chart"></i> Fleet Activity & Turnover Trend</span>
                        </div>
                        <div style="height: 300px; width: 100%;"><canvas id="dashTrendChart"></canvas></div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <span class="card-title"><i data-lucide="pie-chart"></i> Sector Utilization</span>
                        </div>
                        <div style="height: 250px; width: 100%; display:flex; justify-content:center;"><canvas id="dashUtilChart"></canvas></div>
                    </div>
                </div>
                
                <div class="card" style="margin-top: 1.5rem;">
                    <div class="card-header">
                        <span class="card-title"><i data-lucide="layout-grid"></i> Overview Map (Random Sector Snapshot)</span>
                        <button class="btn btn-outline mini-btn" onclick="navigate('inventory')">View Full Grid</button>
                    </div>
                    <div class="warehouse-container">
                        ${renderGrid(appState.inventory.slice(0, 16), false)}
                    </div>
                </div>
            `;
        }

        function renderInventory() {
            // Apply Filters
            let list = appState.inventory;
            if(appState.filters.category !== 'all') list = list.filter(i => i.category === appState.filters.category);
            if(appState.filters.shelf !== 'all') list = list.filter(i => i.id.startsWith(appState.filters.shelf));

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
                            <div class="tab-item active">Grid View Mapping</div>
                            <div class="tab-item" onclick="document.querySelector('.warehouse-wrapper').style.display='none'; document.querySelector('.table-wrapper').style.display='block'; this.parentNode.children[0].classList.remove('active'); this.classList.add('active');">Detailed Table View</div>
                            <div class="tab-item" onclick="document.querySelector('.warehouse-wrapper').style.display='block'; document.querySelector('.table-wrapper').style.display='none'; this.parentNode.children[1].classList.remove('active'); this.classList.add('active');" style="display:none;" id="trigger-grid">Grid</div> <!-- hack for simple tab -->
                        </div>
                        
                        <div class="warehouse-wrapper">
                            ${renderGrid(list, true)}
                        </div>
                        <div class="table-wrapper" style="display:none;">
                            ${tableHtml}
                        </div>
                    </div>
                    
                    <!-- Advanced Filters Panel -->
                    <div class="card">
                        <h3 style="font-size:1rem; margin-bottom:1.5rem; border-bottom:1px solid var(--border); padding-bottom:0.8rem;">Filter Controls</h3>
                        
                        <div class="form-group">
                            <label class="form-label">Category</label>
                            <select class="form-control" onchange="appState.filters.category=this.value; navigate('inventory')">
                                <option value="all" ${appState.filters.category==='all'?'selected':''}>All Categories</option>
                                <option value="Electronics" ${appState.filters.category==='Electronics'?'selected':''}>Electronics</option>
                                <option value="Grocery" ${appState.filters.category==='Grocery'?'selected':''}>Grocery</option>
                                <option value="Furniture" ${appState.filters.category==='Furniture'?'selected':''}>Furniture</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Sector</label>
                            <select class="form-control" onchange="appState.filters.shelf=this.value; navigate('inventory')">
                                <option value="all" ${appState.filters.shelf==='all'?'selected':''}>All Regions</option>
                                <option value="A" ${appState.filters.shelf==='A'?'selected':''}>Sector A</option>
                                <option value="B" ${appState.filters.shelf==='B'?'selected':''}>Sector B</option>
                                <option value="C" ${appState.filters.shelf==='C'?'selected':''}>Sector C</option>
                            </select>
                        </div>
                        <button class="btn btn-outline" style="width:100%" onclick="appState.filters.category='all'; appState.filters.shelf='all'; navigate('inventory')">Reset</button>
                        
                        <div style="margin-top: 2rem; border-top:1px solid var(--border); padding-top:1rem;">
                            <h4 style="font-size:0.8rem; color:var(--text-muted); margin-bottom:1rem; text-transform:uppercase;">Bulk Actions</h4>
                            <button class="btn btn-outline" style="width:100%; margin-bottom:0.5rem;" onclick="spawnToast('info', 'Data Exported to CSV')"><i data-lucide="download"></i> Export Displayed</button>
                        </div>
                    </div>
                </div>
            `;
        }

        function renderGrid(data, grouped = true) {
            if(!grouped) {
                return `<div class="box-grid">
                    ${data.map(item => generateBoxHtml(item)).join('')}
                </div>`;
            }
            
            let html = '';
            shelves.forEach(sLetter => {
                const shelfData = data.filter(i => i.id.startsWith(sLetter));
                if(shelfData.length === 0) return;
                html += `
                <div class="shelf-block">
                    <div class="shelf-title"><i data-lucide="layers"></i> Sector ${sLetter}</div>
                    <div class="box-grid">
                        ${shelfData.map(item => generateBoxHtml(item)).join('')}
                    </div>
                </div>`;
            });
            return html;
        }

        function generateBoxHtml(item) {
            const pct = (item.qty/item.cap)*100;
            let color = 'bg-full';
            if(pct === 0) color = 'bg-empty';
            else if(pct < appState.settings.threshold) color = 'bg-critical';
            else if(pct < 70) color = 'bg-low';

            return `<div class="shelf-box ${color}" onclick="openProductDetail('${item.id}')">
                <div class="box-id">${item.id}</div>
                <div class="box-pct">${Math.round(pct)}% Full</div>
            </div>`;
        }

        function renderAnalytics() {
            return `
                <div class="tabs">
                    <div class="tab-item active">Trend Forecasts</div>
                    <div class="tab-item" onclick="spawnToast('info', 'Module in development')">Capacity Reports</div>
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

                <div class="grid-2-col">
                    <div class="card">
                        <div class="card-header"><span class="card-title">Velocity & Demand Prediction</span></div>
                        <div style="height: 350px; width: 100%;"><canvas id="an-trendChart"></canvas></div>
                    </div>
                    <div class="card">
                        <div class="card-header"><span class="card-title">Category Distribution</span></div>
                        <div style="height: 350px; width: 100%; display:flex; justify-content:center;"><canvas id="an-distChart"></canvas></div>
                    </div>
                </div>
            `;
        }

        function renderRobotics() {
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
                            <div style="background:#000; border:1px solid var(--border); border-radius: 8px; padding: 1rem; height: 300px; display:flex; flex-direction:column; position:relative; z-index:2;">
                                <div id="robot-console" style="flex:1; overflow:hidden; display:flex; flex-direction:column; justify-content:flex-end; font-size:0.8rem;">
                                    <div class="robot-console-line" style="color: #94a3b8; border-color: #94a3b8;">[SYS] Connection established.</div>
                                </div>
                            </div>
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

        function renderProcurement() {
            const list = appState.inventory.map(i => ({...i, p: runPrediction(i)})).filter(i => i.qty < i.p.demand * appState.settings.leadTime);
            
            return `
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title"><i data-lucide="file-text"></i> Restock Generation Queue</h3>
                        <div style="display:flex; gap:1rem;">
                            <button class="btn btn-outline" onclick="reviewCombinedPO()"><i data-lucide="eye"></i> Master Audit</button>
                            <button class="btn btn-primary" onclick="downloadCombinedPO()"><i data-lucide="file-down"></i> Dispatch All POs</button>
                        </div>
                    </div>
                    
                    ${list.length === 0 ? '<div class="empty-state"><i data-lucide="check-circle" style="width:48px;height:48px;color:var(--success)"></i><p>Inventory levels optimal. No restock needed.</p></div>' : `
                    <div class="table-responsive">
                        <table class="data-table">
                            <thead><tr><th>Target Asset</th><th>Current Stock</th><th>Lead Restock Qty</th><th>Supplier</th><th>Action</th></tr></thead>
                            <tbody>
                                ${list.map(i => `
                                <tr>
                                    <td><strong>${i.name}</strong><br><span style="font-size:0.7rem; color:var(--text-muted)">Sector ${i.id}</span></td>
                                    <td><span style="color:var(--danger); font-weight:700;">${i.qty}</span></td>
                                    <td><strong>+${i.p.restockQty}</strong></td>
                                    <td>${i.supplier}</td>
                                    <td>
                                        <div style="display:flex; gap:0.5rem;">
                                            <button class="btn btn-outline mini-btn" onclick="reviewPO('${i.id}')">View</button>
                                            <button class="btn btn-primary mini-btn" onclick="downloadPO('${i.id}')"><i data-lucide="download" style="width:14px;height:14px"></i></button>
                                        </div>
                                    </td>
                                </tr>`).join('')}
                            </tbody>
                        </table>
                    </div>`}
                </div>
            `;
        }

        function renderProfile() {
            return `
                <div class="page-layout">
                    <div class="card">
                        <div class="card-header"><span class="card-title"><i data-lucide="shield"></i> Session Activity Log</span></div>
                        <div class="table-responsive">
                            <table class="data-table">
                                <thead><tr><th>Timestamp</th><th>Action Record</th></tr></thead>
                                <tbody>
                                    ${appState.logs.length === 0 ? '<tr><td colspan="2" style="text-align:center; color:var(--text-muted);">No activity logged in current session.</td></tr>' : 
                                      appState.logs.map(l => `<tr><td style="white-space:nowrap; color:var(--text-muted); font-size:0.75rem;">${l.time}</td><td>${l.msg}</td></tr>`).join('')
                                    }
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    <div style="display:flex; flex-direction:column; gap:1.5rem;">
                        <div class="card" style="text-align: center; padding: 3rem 1.5rem;">
                            <div class="profile-btn" style="width: 90px; height: 90px; font-size: 2.5rem; margin: 0 auto 1.5rem auto;">AD</div>
                            <h2 style="font-size: 1.5rem; margin-bottom:0.2rem;">System Admin</h2>
                            <span class="status-pill status-info" style="margin-bottom:1rem; border-color:var(--primary); color:var(--primary);">Clearance: ${appState.settings.role}</span>
                            <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 1rem;"><i data-lucide="mail" style="display:inline; width:14px; position:relative; top:2px;"></i> admin@core.arise.net</p>
                            
                            <button class="btn btn-outline" style="width:100%; margin-top:2rem;" onclick="spawnToast('warning', 'LDAP Sync Required for Password change')">Change Password</button>
                            <button class="btn btn-danger" style="width:100%; margin-top:.5rem;" onclick="location.reload()">Terminate Session</button>
                        </div>
                    </div>
                </div>
            `;
        }

        function renderSettings() {
            return `
                <div class="page-layout">
                    <div style="display:flex; flex-direction:column; gap:1.5rem;">
                        <div class="card">
                            <div class="card-header"><span class="card-title"><i data-lucide="sliders"></i> ERP Engine Configuration</span></div>
                            <div class="grid-2-col">
                                <div class="form-group">
                                    <label class="form-label">Global Low-Stock Threshold (%)</label>
                                    <input type="number" class="form-control" value="${appState.settings.threshold}" onchange="appState.settings.threshold=parseInt(this.value); logActivity('Updated threshold to '+this.value+'%'); processAlerts(); spawnToast('success', 'Threshold Saved')">
                                    <p style="font-size:0.7rem; color:var(--text-muted); margin-top:4px;">Engine fires alerts when sectors dip below capacity percentage.</p>
                                </div>
                                <div class="form-group">
                                    <label class="form-label">Estimated Lead Time (Days)</label>
                                    <input type="number" class="form-control" value="${appState.settings.leadTime}" onchange="appState.settings.leadTime=parseInt(this.value); logActivity('Lead time adjusted to '+this.value); spawnToast('success', 'Lead Time Saved')">
                                </div>
                            </div>
                            <div class="form-group" style="max-width:50%;">
                                <label class="form-label">Seasonal Growth Factor Baseline</label>
                                <input type="number" step="0.01" class="form-control" value="${appState.settings.growthFactor}" onchange="appState.settings.growthFactor=parseFloat(this.value); spawnToast('success', 'AI Baseline Shifted')">
                            </div>
                        </div>
                        
                        <div class="card">
                            <div class="card-header"><span class="card-title"><i data-lucide="bell"></i> Alert System Rules</span></div>
                            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;">
                                <div>
                                    <p style="font-weight:600; font-size:0.9rem;">Master Diagnostic Alerts</p>
                                    <p style="font-size:0.75rem; color:var(--text-muted);">Enable or disable background daemon alerts for stock and sensors.</p>
                                </div>
                                <button class="btn btn-${appState.settings.alertsEnabled?'primary':'outline'}" onclick="appState.settings.alertsEnabled=!appState.settings.alertsEnabled; navigate('settings'); spawnToast('info', 'Alert system toggled')">${appState.settings.alertsEnabled?'Enabled':'Disabled'}</button>
                            </div>
                        </div>
                    </div>
                
                    <div class="card">
                        <div class="card-header"><span class="card-title"><i data-lucide="shield-check"></i> Role Simulation</span></div>
                        <p style="font-size:0.8rem; color:var(--text-muted); margin-bottom:1rem; line-height:1.5;">Temporarily downgrade your session access level to test visual gates.</p>
                        
                        <div class="form-group">
                            <label class="form-label">Current Role</label>
                            <select class="form-control" onchange="appState.settings.role=this.value; spawnToast('warning', 'Role Shifted to ' + this.value); logActivity('Shifted role to '+this.value)">
                                <option value="Admin" ${appState.settings.role==='Admin'?'selected':''}>Admin (L3)</option>
                                <option value="Manager" ${appState.settings.role==='Manager'?'selected':''}>Manager (L2)</option>
                                <option value="Staff" ${appState.settings.role==='Staff'?'selected':''}>Staff (L1)</option>
                            </select>
                        </div>
                        
                        <div style="margin-top: 2rem; background: var(--bg-panel); border:1px solid var(--border); padding: 1rem; border-radius: 8px;">
                            <p style="font-size:0.75rem; font-weight: 700; color:var(--text-muted);">CORE DB STATUS</p>
                            <p style="font-size: 0.85rem; margin-top:5px; font-family:monospace;">Node: ARISE-SYS-90X <br> Active Sectors: ${appState.inventory.length}</p>
                        </div>
                    </div>
                </div>
            `;
        }

        // --- PRODUCT DETAILS MODAL ---
        function openProductDetail(id) {
            const item = appState.inventory.find(i=>i.id===id);
            if(!item) return;
            const p = runPrediction(item);
            const pct = Math.round((item.qty/item.cap)*100);
            
            const content = `
                <div class="modal-close" onclick="document.getElementById('detail-modal').classList.remove('active')"><i data-lucide="x"></i></div>
                <div style="margin-bottom:1.5rem">
                    <p style="color:var(--primary); font-family:monospace; font-weight:700">${item.rfid} | ${item.sku}</p>
                    <h2 style="font-size:1.8rem; margin-top:0.3rem; letter-spacing:-0.5px">${item.name}</h2>
                    <p style="color:var(--text-muted); font-size:0.9rem;">${item.category} • Supplier: ${item.supplier}</p>
                </div>
                <div class="grid-2-col" style="margin-bottom:2rem; display:grid; grid-template-columns:1fr 1fr;">
                    <div style="background:var(--bg-body); padding:1.2rem; border-radius:8px; border-left:4px solid var(--primary)">
                        <p class="kpi-label" style="font-size:0.65rem;">Current Capacity</p>
                        <p style="font-size:1.4rem; font-weight:800">${item.qty} <span style="font-size:0.9rem; color:var(--text-muted); font-weight:normal;">/ ${item.cap}</span></p>
                        <p style="font-weight:600; font-size:0.8rem; color:var(--${pct < appState.settings.threshold ? 'warning' : 'success'})">${pct}% Full</p>
                    </div>
                    <div style="background:var(--bg-body); padding:1.2rem; border-radius:8px; border:1px solid var(--border);">
                        <p class="kpi-label" style="font-size:0.65rem;">Predicted Analytics</p>
                        <p style="font-size:1.2rem; font-weight:800">${p.demand} <span style="font-size:0.8rem; font-weight:normal;">/ day</span></p>
                        <p style="font-size:0.8rem; color:var(--text-muted)">Stock-out in <span style="color:var(--${p.stockOut<5?'danger':'text-main'}); font-weight:700;">${p.stockOut} days</span></p>
                    </div>
                </div>
                <div style="display:flex; justify-content: space-between; align-items:center;">
                    <div>
                    ${hasAccess('Manager') ? `<button class="btn btn-outline" onclick="adjustQty('${item.id}', 25)"><i data-lucide="plus"></i> Log Intake (+25)</button>` : '<span style="font-size:0.8rem; color:var(--text-muted);"><i data-lucide="lock" style="width:12px;display:inline;"></i> Auth Required for Intake</span>'}
                    </div>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn btn-outline" onclick="reviewPO('${item.id}')">Generate PO</button>
                    </div>
                </div>
            `;
            document.getElementById('modal-data').innerHTML = content;
            document.getElementById('detail-modal').classList.add('active');
            lucide.createIcons();
        }

        function adjustQty(id, d) { 
            const item = appState.inventory.find(i=>i.id===id); 
            item.qty = Math.min(item.cap, Math.max(0, item.qty+d)); 
            logActivity(`Manual intake (+${d}) logged for ${item.name}`); 
            spawnToast('success', 'Database updated manually.');
            if(appState.currentPage === 'inventory') navigate('inventory'); // Fresh render
            openProductDetail(id); // refresh modal
            processAlerts();
        }

        // --- CHARTS INITIALIZATION ---
        function initCharts(page) {
            let labels=[], data=[];
            if (charts.trend) charts.trend.destroy();
            if (charts.dist) charts.dist.destroy();

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
            }
        }

        // --- ROBOT SIMULATION ---
        function toggleRobot() {
            appState.robot.active = !appState.robot.active;
            navigate('robotics'); // Re-renders the component natively based on state
            
            if(appState.robot.active) {
                logActivity("Robotics array engaged");
                appState.robot.interval = setInterval(simulateScan, 3000);
            } else {
                logActivity("Robotics array suspended");
                clearInterval(appState.robot.interval);
            }
        }

        function simulateScan() {
            if(appState.currentPage !== 'robotics') return; // Only process UI updates if viewing page
            
            const item = appState.inventory[Math.floor(Math.random() * appState.inventory.length)];
            let isFull = Math.random() > 0.6; 
            let dist = isFull ? Math.floor(Math.random() * 30 + 20) : Math.floor(Math.random() * 50 + 70); 
            let gas = Math.floor(Math.random() * 40 + 10);
            if(Math.random() > 0.9) gas = Math.floor(Math.random() * 40 + 60);

            document.getElementById('sns-loc').innerText = `Target: Sector ${item.id}`;
            document.getElementById('sns-dist').innerHTML = `${dist}<span style="font-size:1.2rem;">cm</span>`;
            document.getElementById('sns-mq').innerText = gas;
            document.getElementById('sns-mq-v').innerText = (gas * (5/1023)).toFixed(2) + ' V';
            document.getElementById('sns-mq').style.color = gas > 50 ? 'var(--danger)' : '';
            
            logToConsole(`[SCN] Targeting ${item.id} -> US:${dist}cm -> Gas:${gas}`);

            if(gas > 50) {
                spawnToast('critical', `Gas spike detected at Sector ${item.id}`);
                logToConsole(`[ALRT] CRITICAL GAS LEAK Sector ${item.id}`, 'alert');
            }
        }

        function logToConsole(msg, type='info') {
            const el = document.getElementById('robot-console');
            if(!el) return;
            const line = document.createElement('div');
            line.className = 'robot-console-line';
            if(type === 'alert') line.classList.add('robot-console-alert');
            line.innerText = msg;
            el.appendChild(line);
            if(el.children.length > 8) el.removeChild(el.firstChild);
        }

        // --- PROCUREMENT (JSPDF) ---
        function generatePOData(items) {
            const num = "PO-" + Date.now();
            let total = 0;
            const fmt = items.map(i => {
                const q = i.p?.restockQty || 50; const p = i.price || 25; total += q*p;
                return { name: i.name, sku: i.sku, q, p, t: q*p };
            });
            return { num, date: new Date().toLocaleDateString(), sup: items.length===1?items[0].supplier:"Central A.R.I.S.E Req", items: fmt, sub: total, tax: total*0.1, tot: total*1.1 };
        }
        function buildPOText(d) {
            let t=`PURCHASE ORDER\n===========================\nNumber: ${d.num}\nDate: ${d.date}\nSupplier: ${d.sup}\n\nITEMS:\n---------------------------\n`;
            d.items.forEach(i => t += `${i.sku.padEnd(9)} | ${i.name.padEnd(20)} | Qty:${i.q.toString().padEnd(3)} | $${i.p.toString().padEnd(3)} | $${i.t.toFixed(2)}\n`);
            t+=`---------------------------\nSubtotal: $${d.sub.toFixed(2)}\nTax: $${d.tax.toFixed(2)}\nTotal: $${d.tot.toFixed(2)}\n`;
            return t;
        }
        function reviewPO(id) {
            const item = appState.inventory.find(i=>i.id===id);
            const d = generatePOData([item]);
            document.getElementById('po-preview-content').innerText = buildPOText(d);
            document.getElementById('po-download-btn').onclick = () => { spawnToast('success', 'PO Dispatched.'); document.getElementById('po-modal').classList.remove('active'); };
            document.getElementById('po-modal').classList.add('active');
        }
        function reviewCombinedPO() {
            const list = appState.inventory.map(i => ({...i, p: runPrediction(i)})).filter(i => i.qty < i.p.demand * appState.settings.leadTime);
            if(list.length===0) return spawnToast('warning', 'No automated targets found.');
            const d = generatePOData(list);
            document.getElementById('po-preview-content').innerText = buildPOText(d);
            document.getElementById('po-download-btn').onclick = () => { spawnToast('success', 'Master PO Dispatched.'); document.getElementById('po-modal').classList.remove('active'); };
            document.getElementById('po-modal').classList.add('active');
        }
        function downloadPO() { spawnToast('success', 'PDF generation simulated offline.'); }
        function downloadCombinedPO() { spawnToast('success', 'Bulk PDF generation simulated offline.'); }

        // --- GLOBAL UI INTERACTIONS ---
        document.getElementById('theme-toggle').addEventListener('click', () => {
            const h = document.documentElement; const t = h.getAttribute('data-theme')==='dark'?'light':'dark';
            h.setAttribute('data-theme', t); document.getElementById('theme-icon').setAttribute('data-lucide', t==='dark'?'sun':'moon');
            lucide.createIcons();
            if(appState.currentPage === 'dashboard' || appState.currentPage === 'analytics') initCharts(appState.currentPage);
        });

        // Search Bar logic
        let searchTimer;
        document.getElementById('global-search').addEventListener('input', (e) => {
            const v = e.target.value.toLowerCase(); const dd = document.getElementById('search-dropdown');
            if(!v) { dd.classList.remove('show'); return; }
            clearTimeout(searchTimer);
            searchTimer = setTimeout(() => {
                const res = appState.inventory.filter(i=>i.name.toLowerCase().includes(v) || i.sku.toLowerCase().includes(v)).slice(0,5);
                if(res.length===0) { dd.innerHTML = '<div style="padding:1rem;color:var(--text-muted);text-align:center;">No match found in DB</div>'; }
                else {
                    dd.innerHTML = res.map(i=>`<div class="search-result-item" onclick="openProductDetail('${i.id}')"><div><span style="font-weight:600">${i.name}</span> <span style="font-size:0.7rem; color:var(--text-muted); margin-left:5px;">Sector ${i.id}</span></div> <i data-lucide="arrow-up-right" style="width:14px;"></i></div>`).join('');
                }
                lucide.createIcons();
                dd.classList.add('show');
            }, 200);
        });

        // Hide dropdowns on outside click
        document.addEventListener('click', (e) => {
            if(!e.target.closest('.search-container')) document.getElementById('search-dropdown').classList.remove('show');
            if(!e.target.closest('#notif-trigger') && !e.target.closest('#notif-panel')) document.getElementById('notif-panel').classList.remove('show');
        });
        
        document.getElementById('notif-trigger').addEventListener('click', () => {
            document.getElementById('notif-panel').classList.toggle('show');
        });

        // Initialize App
        window.addEventListener('DOMContentLoaded', () => {
            initData();
            
            // Extract hash on load if present
            let hash = window.location.hash.replace('#', '');
            if(hash === '') hash = 'dashboard';
            navigate(hash);
        });
    </script>
</body>
</html>
"""

with open('c:/Users/JIGISHA GAJJAR/OneDrive/Desktop/ARISE/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
