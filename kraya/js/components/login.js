// Kraya Authentication Page Component (Login / Register / SMS OTP)
import { db } from '../db.js';
import { navigateToRoute } from '../app.js';

let loginMode = 'signin'; // signin, signup, phone_otp
let smsOtpSent = false;
let generatedOtp = '';

export function render(container, params) {
  // Check if already logged in, redirect to catalog or profile
  const user = db.getCurrentUser();
  if (user) {
    navigateToRoute('#profile');
    return;
  }
  
  renderForm(container);
}

function renderForm(container) {
  let innerHtml = '';
  
  if (loginMode === 'signin') {
    innerHtml = `
      <h2 style="font-size: 22px; font-weight: 800; margin-bottom: 8px; text-align: center;">Sign In to Kraya</h2>
      <p style="color: var(--text-muted); font-size: 13px; text-align: center; margin-bottom: 24px;">Access your orders, wishlist, and SuperCoins balance.</p>
      
      <form id="auth-signin-form" style="display: flex; flex-direction: column; gap: 16px;">
        <div class="form-group" style="margin-bottom:0;">
          <label class="form-label">Email Address</label>
          <input type="email" class="form-control" id="signin-email" placeholder="example@kraya.com" required value="pramoda@kraya.com">
        </div>
        
        <div class="form-group" style="margin-bottom:0;">
          <label class="form-label">Password</label>
          <input type="password" class="form-control" id="signin-password" placeholder="••••••••" required value="user123">
        </div>
        
        <button type="submit" class="btn-large btn-buy-now w-100" style="margin-top: 10px;">Sign In</button>
      </form>
      
      <div style="margin-top: 24px; text-align: center; font-size: 13px; color: var(--text-muted); display:flex; flex-direction:column; gap:12px;">
        <a href="javascript:void(0)" id="switch-to-otp" style="color: var(--secondary-color); font-weight: 600;">Or Login with Mobile OTP</a>
        <div>New to Kraya? <a href="javascript:void(0)" id="switch-to-signup" style="color: var(--primary-color); font-weight: 700;">Create an Account</a></div>
      </div>
    `;
  } else if (loginMode === 'signup') {
    innerHtml = `
      <h2 style="font-size: 22px; font-weight: 800; margin-bottom: 8px; text-align: center;">Create Account</h2>
      <p style="color: var(--text-muted); font-size: 13px; text-align: center; margin-bottom: 24px;">Join Kraya & get a <strong style="color: var(--success);">🎁 100 SuperCoins welcome bonus!</strong></p>
      
      <form id="auth-signup-form" style="display: flex; flex-direction: column; gap: 16px;">
        <div class="form-group" style="margin-bottom:0;">
          <label class="form-label">Full Name</label>
          <input type="text" class="form-control" id="signup-name" placeholder="Pramoda Kumar" required>
        </div>
        
        <div class="form-group" style="margin-bottom:0;">
          <label class="form-label">Email Address</label>
          <input type="email" class="form-control" id="signup-email" placeholder="name@email.com" required>
        </div>

        <div class="form-group" style="margin-bottom:0;">
          <label class="form-label">Mobile Number</label>
          <input type="text" class="form-control" id="signup-phone" placeholder="9876543210" maxlength="10" required>
        </div>
        
        <div class="form-group" style="margin-bottom:0;">
          <label class="form-label">Create Password</label>
          <input type="password" class="form-control" id="signup-password" placeholder="At least 6 characters" minlength="6" required>
        </div>
        
        <button type="submit" class="btn-large btn-buy-now w-100" style="margin-top: 10px;">Register & Claim Coins</button>
      </form>
      
      <div style="margin-top: 24px; text-align: center; font-size: 13px; color: var(--text-muted);">
        Already have an account? <a href="javascript:void(0)" id="switch-to-signin" style="color: var(--primary-color); font-weight: 700;">Sign In</a>
      </div>
    `;
  } else if (loginMode === 'phone_otp') {
    innerHtml = `
      <h2 style="font-size: 22px; font-weight: 800; margin-bottom: 8px; text-align: center;">OTP Login</h2>
      <p style="color: var(--text-muted); font-size: 13px; text-align: center; margin-bottom: 24px;">Enter your mobile number to receive a 4-digit verification code.</p>
      
      <form id="auth-otp-form" style="display: flex; flex-direction: column; gap: 16px;">
        <div class="form-group" style="margin-bottom:0;">
          <label class="form-label">Mobile Number</label>
          <div style="position: relative; display: flex; align-items: center;">
            <span style="position: absolute; left: 16px; font-weight: 700; color: var(--text-muted);">+91</span>
            <input type="text" class="form-control" id="otp-phone" style="padding-left: 56px;" placeholder="9876543210" maxlength="10" required ${smsOtpSent ? 'disabled' : ''}>
          </div>
        </div>
        
        ${smsOtpSent ? `
          <div style="background-color: var(--success-bg); color: var(--success); padding: 12px; border-radius: 6px; font-size: 12px; font-weight: 700; text-align: center; border: 1px solid rgba(3, 166, 133, 0.2);">
            💬 SMS Sent: Verification OTP is <strong>${generatedOtp}</strong>
          </div>
          <div class="form-group" style="margin-bottom:0;">
            <label class="form-label">Enter 4-Digit OTP Code</label>
            <input type="text" class="form-control" id="otp-code" placeholder="Enter code" maxlength="4" required style="text-align: center; font-size: 18px; font-weight: 800; letter-spacing: 8px;">
          </div>
        ` : ''}
        
        <button type="submit" class="btn-large btn-buy-now w-100" style="margin-top: 10px;">
          ${smsOtpSent ? 'Verify & Login' : 'Send Verification OTP'}
        </button>
      </form>
      
      <div style="margin-top: 24px; text-align: center; font-size: 13px; color: var(--text-muted);">
        <a href="javascript:void(0)" id="switch-to-signin" style="color: var(--primary-color); font-weight: 700;">Back to Email Login</a>
      </div>
    `;
  }
  
  container.innerHTML = `
    <div class="container" style="display: flex; align-items: center; justify-content: center; padding: 40px 0;">
      <div style="background-color: #fff; width: 440px; border-radius: 16px; padding: 36px; box-shadow: var(--shadow-lg); border: 1px solid var(--border-light);">
        ${innerHtml}
      </div>
    </div>
  `;
  
  wireUpAuthEvents(container);
}

function wireUpAuthEvents(container) {
  // Switche link bindings
  const signinBtn = document.getElementById("switch-to-signin");
  if (signinBtn) {
    signinBtn.addEventListener("click", () => {
      loginMode = 'signin';
      smsOtpSent = false;
      renderForm(container);
    });
  }
  
  const signupBtn = document.getElementById("switch-to-signup");
  if (signupBtn) {
    signupBtn.addEventListener("click", () => {
      loginMode = 'signup';
      renderForm(container);
    });
  }
  
  const otpBtn = document.getElementById("switch-to-otp");
  if (otpBtn) {
    otpBtn.addEventListener("click", () => {
      loginMode = 'phone_otp';
      smsOtpSent = false;
      renderForm(container);
    });
  }
  
  // Submit Sign In Form
  const signinForm = document.getElementById("auth-signin-form");
  if (signinForm) {
    signinForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const email = document.getElementById("signin-email").value.trim();
      const password = document.getElementById("signin-password").value;
      
      const ok = db.loginUser(email, password);
      if (ok) {
        // Successful login, trigger refresh and route to catalog or cart check page
        window.location.hash = '#profile';
        window.location.reload();
      } else {
        alert("Invalid Email or Password! Try pramoda@kraya.com / user123");
      }
    });
  }
  
  // Submit Sign Up Form
  const signupForm = document.getElementById("auth-signup-form");
  if (signupForm) {
    signupForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const name = document.getElementById("signup-name").value.trim();
      const email = document.getElementById("signup-email").value.trim();
      const phone = document.getElementById("signup-phone").value.trim();
      const password = document.getElementById("signup-password").value;
      
      const success = db.registerUser(name, email, password, phone);
      if (success) {
        alert("Welcome to Kraya! 100 Welcome SuperCoins have been credited to your account.");
        window.location.hash = '#profile';
        window.location.reload();
      } else {
        alert("An account with this email address already exists!");
      }
    });
  }
  
  // Submit OTP Form
  const otpForm = document.getElementById("auth-otp-form");
  if (otpForm) {
    otpForm.addEventListener("submit", (e) => {
      e.preventDefault();
      
      if (!smsOtpSent) {
        // Send SMS OTP process
        const phone = document.getElementById("otp-phone").value.trim();
        if (phone.length !== 10 || isNaN(phone)) {
          alert("Please enter a valid 10-digit mobile number!");
          return;
        }
        
        // Mock generation
        generatedOtp = Math.floor(1000 + Math.random() * 9000).toString();
        smsOtpSent = true;
        renderForm(container);
      } else {
        // Verify OTP code
        const codeInput = document.getElementById("otp-code").value.trim();
        if (codeInput === generatedOtp) {
          // Find or create account dynamically
          const phone = document.getElementById("otp-phone").value;
          const users = db.getUsers();
          let user = users.find(u => u.phone === phone);
          
          if (!user) {
            // Auto register
            const autoEmail = `${phone}@kraya.com`;
            db.registerUser(`User ${phone.slice(-4)}`, autoEmail, "otp_login_pass", phone);
          } else {
            // Log in
            db.loginUser(user.email, user.password);
          }
          
          alert("OTP verified successfully! Logged in.");
          window.location.hash = '#profile';
          window.location.reload();
        } else {
          alert("Incorrect verification code! Please check the mock SMS badge code and try again.");
        }
      }
    });
  }
}
