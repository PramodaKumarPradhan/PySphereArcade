// ── State ──────────────────────────────────────────────
let expression = '0';
let justCalculated  = false;
let angleMode       = 'deg';   // 'deg' or 'rad'
let memoryValue     = null;
let historyText     = '';

const displayEl  = document.getElementById('expression');
const previewEl  = document.getElementById('result-preview');
const historyEl  = document.getElementById('history-line');
const memDot     = document.getElementById('mem-indicator');

// ── Display ──────────────────────────────────────────────
function updateDisplay() {
    displayEl.textContent = expression;
    displayEl.classList.remove('sm','xs','xxs','error');
    const len = expression.length;
    if      (len > 22) displayEl.classList.add('xxs');
    else if (len > 16) displayEl.classList.add('xs');
    else if (len > 11) displayEl.classList.add('sm');
}

function setHistory(text) {
    historyText = text;
    historyEl.textContent = text;
}

// ── Appending values ──────────────────────────────────────
function appendToExpression(value) {
    if (event) addRipple(event);
    const ops = ['+','-','×','÷'];
    const isOp = ops.includes(value);

    if (justCalculated) {
        if (!isOp && value !== '^' && value !== '^2' && value !== '^3' && value !== '^(') {
            // Start fresh after =
            expression = value;
            justCalculated = false;
            updateDisplay();
            showLivePreview();
            return;
        }
        justCalculated = false;
    }

    if (expression === '0' && !isOp && value !== '.' && !value.startsWith('^')) {
        expression = value;
    } else if (value === '.') {
        const parts = expression.split(/[\+\-×÷\(]/);
        const last  = parts[parts.length - 1];
        if (last.includes('.')) return;
        expression += '.';
    } else if (isOp) {
        const last = expression.slice(-1);
        if (ops.includes(last)) expression = expression.slice(0, -1);
        expression += value;
        highlightOp(value);
    } else {
        expression += value;
    }

    updateDisplay();
    showLivePreview();
}

// ── Insert function like sin( ──────────────────────────────
function insertFunc(fn) {
    if (event) addRipple(event);
    if (justCalculated) { justCalculated = false; expression = '0'; }
    if (expression === '0') expression = fn;
    else expression += fn;
    updateDisplay();
    showLivePreview();
}

// ── Constants ─────────────────────────────────────────────
// pi and e are handled as text in expression; backend resolves them

// ── Calculate ─────────────────────────────────────────────
async function calculate() {
    if (event) addRipple(event);
    if (!expression || expression === '0') return;
    if (['+','-','×','÷'].includes(expression.slice(-1))) return;

    const equalsBtn = document.querySelector('.btn-equals');
    equalsBtn.classList.add('loading');
    equalsBtn.textContent = '';

    try {
        const resp = await fetch('/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ expression, angle_mode: angleMode })
        });
        const data = await resp.json();

        equalsBtn.classList.remove('loading');
        equalsBtn.textContent = '=';

        if (data.error) {
            showError(data.error);
        } else {
            setHistory(expression + ' =');
            previewEl.textContent = '';
            expression = data.result;
            justCalculated = true;
            clearOpHighlight();
            updateDisplay();
            popResult();
        }
    } catch {
        equalsBtn.classList.remove('loading');
        equalsBtn.textContent = '=';
        showError('Connection error');
    }
}

// ── Live preview ───────────────────────────────────────────
let previewTimer = null;
async function showLivePreview() {
    clearTimeout(previewTimer);
    previewTimer = setTimeout(async () => {
        if (expression === '0' || expression === '') { previewEl.textContent = ''; return; }
        const last = expression.slice(-1);
        if (['+','-','×','÷','('].includes(last) || last === '.') { previewEl.textContent = ''; return; }

        try {
            const resp = await fetch('/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ expression, angle_mode: angleMode })
            });
            const data = await resp.json();
            if (!data.error && data.result !== expression) {
                previewEl.textContent = '= ' + data.result;
            } else {
                previewEl.textContent = '';
            }
        } catch { previewEl.textContent = ''; }
    }, 180);
}

// ── Clear / Backspace ──────────────────────────────────────
function clearAll() {
    if (event) addRipple(event);
    expression = '0';
    justCalculated = false;
    previewEl.textContent = '';
    setHistory('');
    clearOpHighlight();
    updateDisplay();
    displayEl.classList.remove('error');
}

function backspace() {
    if (event) addRipple(event);
    if (justCalculated) { expression = '0'; justCalculated = false; updateDisplay(); previewEl.textContent = ''; return; }
    expression = expression.length <= 1 ? '0' : expression.slice(0, -1);
    updateDisplay();
    showLivePreview();
}

function toggleSign() {
    if (event) addRipple(event);
    if (expression === '0') return;
    expression = expression.startsWith('-') ? expression.slice(1) : '-' + expression;
    updateDisplay();
    showLivePreview();
}

// ── Angle mode ─────────────────────────────────────────────
function setAngleMode(mode) {
    angleMode = mode;
    document.getElementById('btn-deg').classList.toggle('active', mode === 'deg');
    document.getElementById('btn-rad').classList.toggle('active', mode === 'rad');
}

// ── Memory ─────────────────────────────────────────────────
function memoryStore() {
    if (event) addRipple(event);
    const val = parseFloat(previewEl.textContent.replace('= ','')) || parseFloat(expression);
    if (!isNaN(val)) {
        memoryValue = val;
        memDot.classList.add('active');
    }
}
function memoryRecall() {
    if (event) addRipple(event);
    if (memoryValue === null) return;
    if (justCalculated || expression === '0') expression = String(memoryValue);
    else expression += String(memoryValue);
    justCalculated = false;
    updateDisplay();
    showLivePreview();
}

// ── Operator highlight ─────────────────────────────────────
function highlightOp(op) {
    clearOpHighlight();
    const map = { '+':'+', '-':'−', '×':'×', '÷':'÷' };
    document.querySelectorAll('.btn-operator').forEach(b => {
        if (b.textContent.trim() === (map[op] || op)) b.classList.add('active');
    });
}
function clearOpHighlight() {
    document.querySelectorAll('.btn-operator').forEach(b => b.classList.remove('active'));
}

// ── Animations ─────────────────────────────────────────────
function popResult() {
    displayEl.classList.remove('pop');
    void displayEl.offsetWidth;
    displayEl.classList.add('pop');
    setTimeout(() => displayEl.classList.remove('pop'), 300);
}
function showError(msg) {
    displayEl.textContent = msg;
    displayEl.classList.add('error','shake');
    previewEl.textContent = '';
    expression = '0';
    justCalculated = false;
    clearOpHighlight();
    setTimeout(() => { displayEl.classList.remove('shake','error'); updateDisplay(); }, 2200);
}
function addRipple(e) {
    const btn = e?.currentTarget || e?.target;
    if (!btn?.classList?.contains('btn')) return;
    const r = document.createElement('span');
    r.className = 'ripple';
    const rect = btn.getBoundingClientRect();
    r.style.left = (e.clientX - rect.left) + 'px';
    r.style.top  = (e.clientY - rect.top)  + 'px';
    btn.appendChild(r);
    setTimeout(() => r.remove(), 550);
}

// ── Keyboard support ──────────────────────────────────────
document.addEventListener('keydown', e => {
    if (e.key >= '0' && e.key <= '9') appendToExpression(e.key);
    else if (e.key === '+') appendToExpression('+');
    else if (e.key === '-') appendToExpression('-');
    else if (e.key === '*') appendToExpression('×');
    else if (e.key === '/') { e.preventDefault(); appendToExpression('÷'); }
    else if (e.key === '.') appendToExpression('.');
    else if (e.key === '(') appendToExpression('(');
    else if (e.key === ')') appendToExpression(')');
    else if (e.key === 'Enter' || e.key === '=') calculate();
    else if (e.key === 'Backspace') backspace();
    else if (e.key === 'Escape') clearAll();
    else if (e.key === '^') appendToExpression('^');
});

// Init
updateDisplay();
