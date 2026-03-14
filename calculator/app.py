from flask import Flask, render_template, request, jsonify
import math
import re

app = Flask(__name__)


def factorial(n):
    """Factorial supporting non-negative integers."""
    n = int(n)
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    return math.factorial(n)


def cbrt(x):
    """Cube root."""
    return math.copysign(abs(x) ** (1/3), x)


def build_safe_env(angle_mode='deg'):
    """
    Build a safe evaluation environment with trig functions
    honouring DEG / RAD mode, plus common constants.
    """
    to_rad = (math.pi / 180) if angle_mode == 'deg' else 1

    env = {
        # Trig – input in degrees (converted) or radians
        'sin':   lambda x: math.sin(x * to_rad),
        'cos':   lambda x: math.cos(x * to_rad),
        'tan':   lambda x: math.tan(x * to_rad),
        # Inverse trig – output converted back to degrees if in deg mode
        'asin':  lambda x: math.degrees(math.asin(x)) if angle_mode == 'deg' else math.asin(x),
        'acos':  lambda x: math.degrees(math.acos(x)) if angle_mode == 'deg' else math.acos(x),
        'atan':  lambda x: math.degrees(math.atan(x)) if angle_mode == 'deg' else math.atan(x),
        # Logarithms
        'log':   math.log,          # natural log
        'log10': math.log10,        # base-10 log
        'log2':  math.log2,
        # Roots
        'sqrt':  math.sqrt,
        'cbrt':  cbrt,
        # Powers / exp
        'exp':   math.exp,
        'pow':   math.pow,
        # Absolute value
        'abs':   abs,
        # Factorial
        'factorial': factorial,
        # Rounding
        'floor': math.floor,
        'ceil':  math.ceil,
        'round': round,
        # Hyperbolic
        'sinh':  math.sinh,
        'cosh':  math.cosh,
        'tanh':  math.tanh,
        # Constants
        'pi':    math.pi,
        'e':     math.e,
        'tau':   math.tau,
        # Builtins blocked
        '__builtins__': {},
    }
    return env


def preprocess(expression: str) -> str:
    """
    Convert display symbols to valid Python/math expressions.
    """
    expr = expression
    expr = expr.replace('×', '*')
    expr = expr.replace('÷', '/')
    expr = expr.replace('−', '-')
    # Handle implicit multiplication before pi/e: 2pi → 2*pi, 3e → 3*e
    expr = re.sub(r'(\d)(pi|e\b|tau)', r'\1*\2', expr)
    # Handle ^ for exponentiation
    expr = expr.replace('^', '**')
    # Percentage: number% → number/100
    expr = re.sub(r'(\d+\.?\d*)%', r'(\1/100)', expr)
    return expr


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    data        = request.get_json()
    raw         = data.get('expression', '0')
    angle_mode  = data.get('angle_mode', 'deg')

    try:
        expression = preprocess(raw)
        env        = build_safe_env(angle_mode)
        result     = eval(expression, {"__builtins__": {}}, env)        # noqa: S307

        # Format result
        if isinstance(result, float):
            if math.isnan(result):
                return jsonify({'result': None, 'error': 'Not a number'})
            if math.isinf(result):
                return jsonify({'result': None, 'error': 'Infinity'})
            # Round to avoid floating-point noise
            result = round(result, 10)
            if result == int(result) and abs(result) < 1e15:
                result = int(result)

        return jsonify({'result': str(result), 'error': None})

    except ZeroDivisionError:
        return jsonify({'result': None, 'error': 'Division by zero'})
    except ValueError as exc:
        return jsonify({'result': None, 'error': str(exc)})
    except Exception:
        return jsonify({'result': None, 'error': 'Invalid expression'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
