// ── Elements ─────────────────────────────────────────────────────────────
const ipInput = document.getElementById('ipInput');
const btnScan = document.getElementById('btnScan');
const btnClear = document.getElementById('btnClear');
const btnMyIP = document.getElementById('btnMyIP');
const resultPanel = document.getElementById('resultPanel');
const emptyState = document.getElementById('emptyState');
const tabs = document.querySelectorAll('.tab');
const tabPanes = document.querySelectorAll('.tab-pane');
const toastEl = document.getElementById('toast');
const bulkInput = document.getElementById('bulkInput');
const btnBulkScan = document.getElementById('btnBulkScan');

// ── State ────────────────────────────────────────────────────────────────
let currentData = null;
let mapPin = null;
let mapInstance = null;

const API_BASE = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost' 
    ? 'http://127.0.0.1:5001' 
    : '';

// Initialize Map
function initMap() {
    if (mapInstance) return;
    mapInstance = L.map('map', { zoomControl: false }).setView([20, 0], 2);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(mapInstance);
    L.control.zoom({ position: 'bottomright' }).addTo(mapInstance);
}

// ── Navigation (Tabs) ────────────────────────────────────────────────────
tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tabPanes.forEach(p => p.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(`tab-${tab.dataset.tab}`).classList.add('active');
        if (tab.dataset.tab === 'history') loadHistory();
    });
});

// ── Search Input Logic ───────────────────────────────────────────────────
ipInput.addEventListener('input', () => {
    btnClear.style.display = ipInput.value ? 'block' : 'none';
});

btnClear.addEventListener('click', () => {
    ipInput.value = '';
    btnClear.style.display = 'none';
    ipInput.focus();
    emptyState.style.display = 'block';
    resultPanel.style.display = 'none';
});

ipInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') performScan(ipInput.value.trim());
});

btnScan.addEventListener('click', () => {
    performScan(ipInput.value.trim());
});

btnMyIP.addEventListener('click', async () => {
    ipInput.value = '';
    btnClear.style.display = 'none';
    btnMyIP.style.opacity = '0.7';
    btnMyIP.innerHTML = 'Detecting...';
    try {
        const res = await fetch(`${API_BASE}/api/myip`);
        const data = await res.json();
        if (data.error) throw new Error(data.error);
        ipInput.value = data.ip;
        btnClear.style.display = 'block';
        displayResults(data);
    } catch (err) {
        showToast(err.message || 'Failed to detect IP', true);
    } finally {
        btnMyIP.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 1 0 0 20A10 10 0 0 0 12 2z"/><path d="M12 8v4l3 3"/></svg>My IP';
        btnMyIP.style.opacity = '1';
    }
});

// Quick tags
window.quickScan = (ip) => {
    ipInput.value = ip;
    btnClear.style.display = 'block';
    performScan(ip);
};

// ── Main Scan Logic ──────────────────────────────────────────────────────
async function performScan(ip) {
    if (!ip) {
        showToast('Please enter an IP address', true);
        return;
    }
    
    btnScan.classList.add('loading');
    emptyState.style.display = 'none';
    resultPanel.style.opacity = '0.5';

    try {
        const res = await fetch(`${API_BASE}/api/lookup?ip=${encodeURIComponent(ip)}`);
        const data = await res.json();
        
        if (data.error) throw new Error(data.error);
        
        displayResults(data);
        saveToHistory(data);
    } catch (err) {
        showToast(err.message || 'Scan failed', true);
        emptyState.style.display = 'block';
        resultPanel.style.display = 'none';
    } finally {
        btnScan.classList.remove('loading');
        resultPanel.style.opacity = '1';
    }
}

// ── Display Data ─────────────────────────────────────────────────────────
function displayResults(data) {
    currentData = data;
    emptyState.style.display = 'none';
    resultPanel.style.display = 'flex';
    
    // Header
    document.getElementById('resIP').textContent = data.ip;
    document.getElementById('resFlag').textContent = getFlagEmoji(data.country_code);
    document.getElementById('resHostname').textContent = data.hostname || 'No hostname';
    
    // Tags
    const tagsEl = document.getElementById('resTags');
    tagsEl.innerHTML = '';
    if (data.is_hosting) tagsEl.innerHTML += `<span class="ip-tag tag-hosting">Data Center/Hosting</span>`;
    if (data.is_proxy) tagsEl.innerHTML += `<span class="ip-tag tag-proxy">Proxy/VPN</span>`;
    if (data.is_mobile) tagsEl.innerHTML += `<span class="ip-tag tag-mobile">Mobile Network</span>`;
    if (!data.is_hosting && !data.is_proxy && !data.is_mobile) {
         tagsEl.innerHTML += `<span class="ip-tag tag-clean">Residential / Clean</span>`;
    }

    // Location
    document.getElementById('resCity').textContent = data.city;
    document.getElementById('resRegion').textContent = `${data.region} (${data.region_code})`;
    document.getElementById('resCountry').textContent = `${data.country} (${data.country_code})`;
    document.getElementById('resCont').textContent = data.continent;
    document.getElementById('resZip').textContent = data.zip || '—';
    document.getElementById('resLatLon').textContent = `${data.lat}, ${data.lon}`;
    document.getElementById('resTZ').textContent = data.timezone;
    
    // Network
    document.getElementById('resISP').textContent = data.isp;
    document.getElementById('resOrg').textContent = data.org;
    document.getElementById('resASN').textContent = data.asn;
    document.getElementById('resASName').textContent = data.asn_name;
    document.getElementById('resHostname2').textContent = data.hostname;

    // Map Update
    initMap();
    document.getElementById('mapCoords').textContent = `${data.lat.toFixed(4)}°, ${data.lon.toFixed(4)}°`;
    if (mapPin) mapInstance.removeLayer(mapPin);
    
    const icon = L.divIcon({
        className: 'custom-pin',
        html: `<svg width="32" height="32" viewBox="0 0 24 24" fill="#6366f1" stroke="#fff" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3" fill="#fff"/></svg>`,
        iconSize: [32, 32],
        iconAnchor: [16, 32]
    });
    
    mapPin = L.marker([data.lat, data.lon], {icon}).addTo(mapInstance);
    mapInstance.flyTo([data.lat, data.lon], 11, { duration: 1.5 });

    // Render Business Circles
    renderBusinessCircles(data);
}

function renderBusinessCircles(data) {
    const parent = document.getElementById('bizCircles');
    parent.innerHTML = '';
    
    const metrics = [
        { label: 'Network Class', val: data.is_hosting ? 'Datacenter' : data.is_mobile ? 'Cellular' : 'Residential', icon: '<path d="M5 12h14M12 5v14"/>', color: 'var(--acc1)', pct: 100 },
        { label: 'Risk Profile', val: data.is_proxy ? 'Elevated' : 'Standard', icon: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>', color: data.is_proxy ? 'var(--err)' : 'var(--ok)', pct: data.is_proxy? 80 : 20 },
        { label: 'Distance (Est)', val: (Math.abs(data.utc_offset) / 3600) + ' hrs', icon: '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>', color: 'var(--acc3)', pct: 60 }
    ];

    metrics.forEach(m => {
        const c = 2 * Math.PI * 34; // r=34
        const offset = c - (m.pct / 100) * c;
        parent.innerHTML += `
            <div class="biz-circle">
                <div class="circle-ring">
                    <svg class="ring-svg" viewBox="0 0 76 76">
                        <circle class="ring-track" cx="38" cy="38" r="34"></circle>
                        <circle class="ring-fill" cx="38" cy="38" r="34" stroke="${m.color}" stroke-dasharray="${c}" stroke-dashoffset="${offset}"></circle>
                    </svg>
                    <div class="circle-icon" style="color: ${m.color}">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">${m.icon}</svg>
                    </div>
                </div>
                <div style="display:flex;flex-direction:column;gap:4px">
                    <span class="biz-circle-label">${m.label}</span>
                    <span class="biz-circle-value">${m.val}</span>
                </div>
            </div>
        `;
    });
}

// ── Bulk Scan ────────────────────────────────────────────────────────────
bulkInput.addEventListener('input', () => {
    const lines = bulkInput.value.split('\\n').map(x=>x.trim()).filter(x=>x);
    document.getElementById('bulkCount').textContent = `${lines.length} IP${lines.length===1?'':'s'}`;
});

btnBulkScan.addEventListener('click', async () => {
    const ips = bulkInput.value.split('\\n').map(x=>x.trim()).filter(x=>x);
    if (!ips.length) return showToast('Enter at least 1 IP', true);
    if (ips.length > 20) return showToast('Maximum 20 IPs allowed in bulk', true);

    btnBulkScan.disabled = true;
    document.getElementById('bulkProgress').style.display = 'block';
    const resArea = document.getElementById('bulkResults');
    resArea.innerHTML = '';
    
    document.getElementById('progressFill').style.width = '10%';
    document.getElementById('progressText').textContent = 'Connecting via API...';

    try {
        const res = await fetch(`${API_BASE}/api/bulk`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ips })
        });
        const data = await res.json();
        
        document.getElementById('progressFill').style.width = '100%';
        document.getElementById('progressText').textContent = 'Scan Complete';
        setTimeout(() => { document.getElementById('bulkProgress').style.display = 'none'; }, 1500);

        if (data.error) throw new Error(data.error);

        data.results.forEach(val => {
            const html = val.error 
                ? `<div class="bulk-result-row"><span class="bulk-row-ip">${val.ip}</span><span class="bulk-row-err">${val.error}</span></div>`
                : `<div class="bulk-result-row" onclick="quickScan('${val.ip}')" style="cursor:pointer" title="Click for deep scan">
                     <span class="bulk-row-ip">${val.ip}</span>
                     <span class="bulk-row-info">${val.isp} / ${val.org}</span>
                     <span class="bulk-row-country">${getFlagEmoji(val.country_code)} ${val.city}, ${val.country}</span>
                   </div>`;
            resArea.innerHTML += html;
        });

    } catch (err) {
        showToast(err.message, true);
        document.getElementById('bulkProgress').style.display = 'none';
    } finally {
        btnBulkScan.disabled = false;
    }
});

// ── Actions & Exports ────────────────────────────────────────────────────
document.getElementById('btnCopyJSON').addEventListener('click', () => {
    if (!currentData) return;
    navigator.clipboard.writeText(JSON.stringify(currentData, null, 2)).then(() => showToast('Copied JSON to clipboard!'));
});

document.getElementById('btnExportCSV').addEventListener('click', () => {
    if (!currentData) return;
    const keys = Object.keys(currentData);
    const vals = Object.values(currentData).map(v => `"${String(v).replace(/"/g, '""')}"`);
    const csv = `${keys.join(',')}\\n${vals.join(',')}`;
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ipscope_${currentData.ip.replace(/\\./g, '_')}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('CSV Exported!');
});

// ── Helpers ──────────────────────────────────────────────────────────────
function getFlagEmoji(countryCode) {
    if (!countryCode || countryCode.length !== 2) return '🌐';
    const codePoints = countryCode.toUpperCase().split('').map(char =>  127397 + char.charCodeAt());
    return String.fromCodePoint(...codePoints);
}

function showToast(msg, isErr = false) {
    toastEl.textContent = msg;
    toastEl.className = `toast show ${isErr?'error':'success'}`;
    setTimeout(() => { toastEl.className = 'toast'; }, 3000);
}

// ── History ──────────────────────────────────────────────────────────────
function saveToHistory(data) {
    let hist = JSON.parse(localStorage.getItem('ipScopeHist') || '[]');
    hist = hist.filter(h => h.ip !== data.ip);
    hist.unshift({
        ip: data.ip,
        loc: `${data.city}, ${data.country}`,
        flag: getFlagEmoji(data.country_code),
        time: new Date().toLocaleString()
    });
    if (hist.length > 50) hist.pop();
    localStorage.setItem('ipScopeHist', JSON.stringify(hist));
}

function loadHistory() {
    const hist = JSON.parse(localStorage.getItem('ipScopeHist') || '[]');
    const parent = document.getElementById('historyList');
    document.getElementById('histCount').textContent = `${hist.length} entries`;
    
    if (!hist.length) {
        parent.innerHTML = `<div class="history-empty">No scans yet.</div>`;
        return;
    }
    
    parent.innerHTML = hist.map(h => `
        <div class="hist-row" onclick="quickScan('${h.ip}')">
            <span class="hist-flag">${h.flag}</span>
            <div><div class="hist-ip">${h.ip}</div><div class="hist-loc">${h.loc}</div></div>
            <span class="hist-time">${h.time}</span>
        </div>
    `).join('');
}

document.getElementById('btnClearHist').addEventListener('click', () => {
    localStorage.removeItem('ipScopeHist');
    loadHistory();
    showToast('History cleared');
});

// Setup
document.getElementById('footerYear').textContent = new Date().getFullYear();
