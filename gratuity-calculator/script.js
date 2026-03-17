document.addEventListener('DOMContentLoaded', () => {
    const calculateBtn = document.getElementById('calculate-btn');
    const salaryInput = document.getElementById('salary');
    const yearsInput = document.getElementById('years');
    const monthsInput = document.getElementById('months');
    
    // Result elements
    const resultsSection = document.getElementById('results');
    const totalGratuityEl = document.getElementById('total-gratuity');
    const taxFreeAmountEl = document.getElementById('tax-free-amount');
    const taxableAmountEl = document.getElementById('taxable-amount');
    const effectiveTenureEl = document.getElementById('effective-tenure');
    const eligibilityWarning = document.getElementById('eligibility-warning');

    // Constants
    const TAX_FREE_LIMIT_INR = 2000000; // 20 Lakhs

    calculateBtn.addEventListener('click', () => {
        calculateGratuity();
    });

    const formatINR = (number) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(number);
    };

    const validateInputs = () => {
        const salary = parseFloat(salaryInput.value);
        const years = parseInt(yearsInput.value) || 0;
        const months = parseInt(monthsInput.value) || 0;

        if (isNaN(salary) || salary <= 0) {
            alert('Please enter a valid Last Drawn Salary.');
            salaryInput.focus();
            return false;
        }

        if (years === 0 && months === 0) {
            alert('Please enter your tenure (Years and/or Months).');
            yearsInput.focus();
            return false;
        }

        if (months > 11 || months < 0) {
            alert('Months should be between 0 and 11.');
            monthsInput.focus();
            return false;
        }

        return { salary, years, months };
    };

    const calculateGratuity = () => {
        const inputs = validateInputs();
        if (!inputs) return;

        const { salary, years, months } = inputs;
        const isCovered = document.querySelector('input[name="is-covered"]:checked').value === 'yes';

        let effectiveYears = 0;
        let gratuityAmount = 0;

        if (isCovered) {
            // Covered under Act
            // If months > 6, it is rounded up to the next year
            effectiveYears = years + (months > 6 ? 1 : 0);
            
            // Formula: (15 * Salary * Tenure) / 26
            gratuityAmount = Math.round((15 * salary * effectiveYears) / 26);
        } else {
            // Not Covered under Act
            // Only completed years are considered. Months are ignored.
            effectiveYears = years;
            
            // Formula: (15 * Salary * Tenure) / 30 (Since month is considered 30 days)
            gratuityAmount = Math.round((15 * salary * effectiveYears) / 30);
        }

        // Show eligibility warning if continuous service is less than 5 years (roughly 60 months)
        const totalMonths = (years * 12) + months;
        if (totalMonths < 56) { // ~4 years 8 months is sometimes considered 5, but let's warn for < 56 months
            eligibilityWarning.classList.remove('hidden');
        } else {
            eligibilityWarning.classList.add('hidden');
        }

        // Handle case where effectiveYears is 0 for Not Covered < 1 year
        if (effectiveYears === 0) {
            gratuityAmount = 0;
        }

        // Tax calculation section
        let taxFreeAmount = Math.min(gratuityAmount, TAX_FREE_LIMIT_INR);
        let taxableAmount = Math.max(0, gratuityAmount - TAX_FREE_LIMIT_INR);

        // Update UI
        totalGratuityEl.textContent = formatINR(gratuityAmount);
        taxFreeAmountEl.textContent = formatINR(taxFreeAmount);
        taxableAmountEl.textContent = formatINR(taxableAmount);
        
        effectiveTenureEl.textContent = `${effectiveYears} Year${effectiveYears !== 1 ? 's' : ''}`;

        // Add some animation
        resultsSection.classList.remove('hidden');
        resultsSection.style.opacity = '0';
        
        setTimeout(() => {
            resultsSection.style.transition = 'opacity 0.4s ease';
            resultsSection.style.opacity = '1';
        }, 50);

        // Scroll to results smoothly if needed
        setTimeout(() => {
            const resultsPosition = resultsSection.getBoundingClientRect().top + window.scrollY;
            if (resultsPosition > window.innerHeight - 100) {
                window.scrollTo({
                    top: resultsPosition,
                    behavior: 'smooth'
                });
            }
        }, 100);
    };

    // Add enter key support
    const inputs = [salaryInput, yearsInput, monthsInput];
    inputs.forEach(input => {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                calculateGratuity();
            }
        });
    });
});
