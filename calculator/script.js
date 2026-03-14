// ─────────────────────────────────────────────────────────────────────────────
//  Pure JS Scientific Calculator  –  no backend required
// ─────────────────────────────────────────────────────────────────────────────

// ── State ─────────────────────────────────────────────────────────────────────
let expression    = '0';
let justCalculated = false;
let angleMode      = 'deg';
let memoryValue    = null;

const displayEl = document.getElementById('expression');
const previewEl = document.getElementById('result-preview');
const historyEl = document.getElementById('history-line');
const memDot    = document.getElementById('mem-indicator');

// ── Safe Math evaluator ───────────────────────────────────────────────────────
function factorial(n) {
    n = Math.round(n);
    if (n < 0 || n > 170) throw new Error('Out of range');
    if (n === 0 || n === 1) return 1;
    let r = 1;
    for (let i = 2; i <= n; i++) r *= i;
    return r;
}

function cbrt(x)   { return Math.cbrt(x); }
function log10(x)  { return Math.log10(x); }
function log(x)    { return Math.log(x); }   // natural log
function log2(x)   { return Math.log2(x); }
function sqrt(x)   { return Math.sqrt(x); }
function abs(x)    { return Math.abs(x); }
function exp(x)    { return Math.exp(x); }
function fac(x)    { return factorial(x); }

// Trig wrappers that honour DEG / RAD mode
function toRad(x)  { return angleMode === 'deg' ? x * (Math.PI / 180) : x; }
function toDeg(x)  { return angleMode === 'deg' ? x * (180 / Math.PI) : x; }

function sin(x)    { return Math.sin(toRad(x)); }
function cos(x)    { return Math.cos(toRad(x)); }
function tan(x)    { return Math.tan(toRad(x)); }
function asin(x)   { return toDeg(Math.asin(x)); }
function acos(x)   { return toDeg(Math.acos(x)); }
function atan(x)   { return toDeg(Math.atan(x)); }
function sinh(x)   { return Math.sinh(x); }
function cosh(x)   { return Math.cosh(x); }
function tanh(x)   { return Math.tanh(x); }

const PI  = Math.PI;
const E   = Math.E;
const TAU = Math.PI * 2;

/** Preprocess display expression → valid JS expression */
function preprocess(expr) {
    return expr
        .replace(/×/g,  '*')
        .replace(/÷/g,  '/')
        .replace(/−/g,  '-')
        .replace(/\^/g, '**')
        .replace(/(\d)(PI|E|TAU)/g, '$1*$2')   // implicit mult: 2PI → 2*PI
        .replace(/(\d+\.?\d*)%/g, '($1/100)'); // percentage
}

/** Evaluate expression string; returns { result, error } */
function safeEval(raw) {
    try {
        const js = preprocess(raw);
        // Build a function with all math helpers in scope
        const fn = new Function(
            'sin','cos','tan','asin','acos','atan',
            'sinh','cosh','tanh',
            'log','log10','log2','sqrt','cbrt','abs','exp','fac','factorial',
            'PI','E','TAU',
            `"use strict"; return (${js});`
        );
        const val = fn(
            sin, cos, tan, asin, acos, atan,
            sinh, cosh, tanh,
            log, log10, log2, sqrt, cbrt, abs, exp, fac, factorial,
            PI, E, TAU
        );
        if (typeof val !== 'number' || isNaN(val)) return { result: null, error: 'Not a number' };
        if (!isFinite(val)) return { result: null, error: val > 0 ? '+Infinity' : '-Infinity' };

        let result = parseFloat(val.toPrecision(12));
        if (result === Math.trunc(result) && Math.abs(result) < 1e15) result = Math.trunc(result);
        return { result: String(result), error: null };
    } catch (e) {
        if (e.message.includes('zero') || e.message.includes('Infinity')) return { result: null, error: 'Division by zero' };
        return { result: null, error: 'Invalid expression' };
    }
}

// ── Display ───────────────────────────────────────────────────────────────────
function updateDisplay() {
    displayEl.textContent = expression;
    displayEl.classList.remove('sm','xs','xxs','error');
    const len = expression.length;
    if      (len > 24) displayEl.classList.add('xxs');
    else if (len > 18) displayEl.classList.add('xs');
    else if (len > 12) displayEl.classList.add('sm');
}

function setHistory(text) { historyEl.textContent = text; }

// ── Live preview ──────────────────────────────────────────────────────────────
let previewTimer = null;
function showLivePreview() {
    clearTimeout(previewTimer);
    previewTimer = setTimeout(() => {
        if (expression === '0') { previewEl.textContent = ''; return; }
        const last = expression.slice(-1);
        if (['+','-','×','÷','('].includes(last) || last === '.') { previewEl.textContent = ''; return; }
        const { result, error } = safeEval(expression);
        if (!error && result !== expression) {
            previewEl.textContent = '= ' + result;
        } else {
            previewEl.textContent = '';
        }
    }, 120);
}

// ── Append value ──────────────────────────────────────────────────────────────
function appendToExpression(value) {
    if (typeof event !== 'undefined' && event) addRipple(event);
    const ops = ['+','-','×','÷'];
    const isOp = ops.includes(value);

    if (justCalculated) {
        // After = : if digit/open-paren → start fresh; if operator → chain
        if (!isOp && value !== '^' && !value.startsWith('^')) {
            expression = (value === '.') ? '0.' : value;
            justCalculated = false;
            updateDisplay(); showLivePreview(); return;
        }
        justCalculated = false;
    }

    if (expression === '0' && !isOp && value !== '.' && !value.startsWith('^')) {
        expression = value;
    } else if (value === '.') {
        const parts = expression.split(/[\+\-×÷\(]/);
        if (parts[parts.length - 1].includes('.')) return;
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

// ── Insert function e.g. sin( ─────────────────────────────────────────────────
function insertFunc(fn) {
    if (typeof event !== 'undefined' && event) addRipple(event);
    if (justCalculated) { justCalculated = false; expression = fn; }
    else                { expression = (expression === '0') ? fn : expression + fn; }
    updateDisplay();
    showLivePreview();
}

// ── Calculate ─────────────────────────────────────────────────────────────────
function calculate() {
    if (typeof event !== 'undefined' && event) addRipple(event);
    if (!expression || expression === '0') return;
    const last = expression.slice(-1);
    if (['+','-','×','÷'].includes(last)) return;

    const { result, error } = safeEval(expression);
    if (error) {
        showError(error);
    } else {
        setHistory(expression + '  =');
        previewEl.textContent = '';
        expression = result;
        justCalculated = true;
        clearOpHighlight();
        updateDisplay();
        popResult();
    }
}

// ── Control buttons ───────────────────────────────────────────────────────────
function clearAll() {
    if (typeof event !== 'undefined' && event) addRipple(event);
    expression = '0'; justCalculated = false;
    previewEl.textContent = ''; setHistory('');
    clearOpHighlight(); updateDisplay();
    displayEl.classList.remove('error');
}

function backspace() {
    if (typeof event !== 'undefined' && event) addRipple(event);
    if (justCalculated) { expression = '0'; justCalculated = false; updateDisplay(); previewEl.textContent = ''; return; }
    expression = expression.length <= 1 ? '0' : expression.slice(0, -1);
    updateDisplay(); showLivePreview();
}

function toggleSign() {
    if (typeof event !== 'undefined' && event) addRipple(event);
    if (expression === '0') return;
    expression = expression.startsWith('-') ? expression.slice(1) : '-' + expression;
    updateDisplay(); showLivePreview();
}

// ── Angle mode ────────────────────────────────────────────────────────────────
function setAngleMode(mode) {
    angleMode = mode;
    document.getElementById('btn-deg').classList.toggle('active', mode === 'deg');
    document.getElementById('btn-rad').classList.toggle('active', mode === 'rad');
}

// ── Memory ────────────────────────────────────────────────────────────────────
function memoryStore() {
    if (typeof event !== 'undefined' && event) addRipple(event);
    const preview = previewEl.textContent.replace('= ', '');
    const val = parseFloat(preview) || parseFloat(expression);
    if (!isNaN(val)) { memoryValue = val; memDot.classList.add('active'); }
}
function memoryRecall() {
    if (typeof event !== 'undefined' && event) addRipple(event);
    if (memoryValue === null) return;
    const mv = String(memoryValue);
    if (justCalculated || expression === '0') expression = mv;
    else expression += mv;
    justCalculated = false; updateDisplay(); showLivePreview();
}

// ── Operator highlight ────────────────────────────────────────────────────────
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

// ── Animations ────────────────────────────────────────────────────────────────
function popResult() {
    displayEl.classList.remove('pop');
    void displayEl.offsetWidth;
    displayEl.classList.add('pop');
    setTimeout(() => displayEl.classList.remove('pop'), 320);
}
function showError(msg) {
    displayEl.textContent = msg; displayEl.classList.add('error','shake');
    previewEl.textContent = '';
    expression = '0'; justCalculated = false; clearOpHighlight();
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
    setTimeout(() => r.remove(), 560);
}

// ── Keyboard ──────────────────────────────────────────────────────────────────
document.addEventListener('keydown', e => {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    const k = e.key;
    if (k >= '0' && k <= '9') { appendToExpression(k); return; }
    const map = { '+':'+', '-':'-', '*':'×', 'x':'×', '/':'÷', '.':'.', '(':' (', ')':')', '^':'^' };
    if (map[k]) { if (k === '/') e.preventDefault(); appendToExpression(map[k]); return; }
    if (k === 'Enter' || k === '=') calculate();
    else if (k === 'Backspace')     backspace();
    else if (k === 'Escape')        clearAll();
    else if (k === 'p' || k === 'P') appendToExpression('PI');
    else if (k === 'e')             appendToExpression('E');
});

// init
updateDisplay();
