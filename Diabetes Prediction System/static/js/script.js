/* ==========================================================
   Diabetes Prediction System
   script.js - Modern Interactive Engine
   ========================================================== */

document.addEventListener("DOMContentLoaded", function () {
    console.log("Diabetes Prediction System Loaded Successfully");

    /* ==========================================
       THEME TOGGLE ENGINE
       ========================================== */
    const themeToggleBtn = document.getElementById("themeToggleBtn");
    const themeToggleIcon = document.getElementById("themeToggleIcon");

    // Sync button icon on load based on current class
    function updateToggleIcon() {
        if (themeToggleIcon) {
            if (document.documentElement.classList.contains("dark-theme")) {
                themeToggleIcon.className = "bi bi-sun-fill";
            } else {
                themeToggleIcon.className = "bi bi-moon-fill";
            }
        }
    }
    
    // Initial sync
    updateToggleIcon();

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", function () {
            const isDark = document.documentElement.classList.toggle("dark-theme");
            localStorage.setItem("theme", isDark ? "dark" : "light");
            updateToggleIcon();
            
            // Dispatch a custom event so other components (like Chart.js) can react
            window.dispatchEvent(new Event("themeChanged"));
        });
    }

    /* ==========================================
       AGE CALCULATION
       ========================================== */
    const dob = document.getElementById("dob");
    if (dob) {
        dob.addEventListener("change", function () {
            const birthDate = new Date(this.value);
            const today = new Date();
            let age = today.getFullYear() - birthDate.getFullYear();
            const month = today.getMonth() - birthDate.getMonth();
            if (month < 0 || (month === 0 && today.getDate() < birthDate.getDate())) {
                age--;
            }
            const ageInput = document.getElementById("age");
            if (ageInput) {
                ageInput.value = age >= 0 ? age : 0;
            }
        });
    }

    /* ==========================================
       SHOW / HIDE PASSWORD
       ========================================== */
    const togglePassword = document.getElementById("togglePassword");
    if (togglePassword) {
        togglePassword.addEventListener("click", function () {
            const password = document.getElementById("password");
            if (password) {
                if (password.type === "password") {
                    password.type = "text";
                    this.classList.replace("bi-eye-slash", "bi-eye");
                } else {
                    password.type = "password";
                    this.classList.replace("bi-eye", "bi-eye-slash");
                }
            }
        });
    }

    /* ==========================================
       SIGNUP FORM CONFIRM PASSWORD & VALIDATION
       ========================================== */
    const signupForm = document.querySelector("form[action='/signup']");
    if (signupForm) {
        signupForm.addEventListener("submit", function (e) {
            const password = document.querySelector("input[name='password']");
            const confirmPassword = document.querySelector("input[name='confirm_password']");
            if (password && confirmPassword) {
                if (password.value !== confirmPassword.value) {
                    alert("Passwords do not match!");
                    e.preventDefault();
                }
            }
        });
    }

    /* ==========================================
       MOBILE NUMBER VALIDATION
       ========================================== */
    const mobile = document.querySelector("input[name='mobile']");
    if (mobile) {
        mobile.addEventListener("input", function () {
            this.value = this.value.replace(/\D/g, "");
            if (this.value.length > 10) {
                this.value = this.value.slice(0, 10);
            }
        });
    }

    /* ==========================================
       BMI VALIDATION
       ========================================== */
    const bmiInput = document.querySelector("input[name='bmi']");
    if (bmiInput) {
        bmiInput.addEventListener("input", function () {
            if (this.value < 0) {
                this.value = "";
            }
        });
    }

    /* ==========================================
       STAR RATING COMPONENT
       ========================================== */
    const starItems = document.querySelectorAll(".star-item");
    const ratingInput = document.getElementById("selectedRating");
    if (starItems.length > 0 && ratingInput) {
        starItems.forEach(star => {
            // Hover styling
            star.addEventListener("mouseover", function () {
                const hoverVal = parseInt(this.getAttribute("data-value"));
                highlightStars(hoverVal);
            });

            // Restore rating on mouse leave
            star.addEventListener("mouseleave", function () {
                const currentRating = parseInt(ratingInput.value) || 0;
                highlightStars(currentRating);
            });

            // Click to lock rating
            star.addEventListener("click", function () {
                const selectVal = parseInt(this.getAttribute("data-value"));
                ratingInput.value = selectVal;
                highlightStars(selectVal);
                
                // Update text description
                const ratingLabel = document.getElementById("ratingLabel");
                if (ratingLabel) {
                    const descriptions = {
                        1: "⭐ Poor",
                        2: "⭐⭐ Average",
                        3: "⭐⭐⭐ Good",
                        4: "⭐⭐⭐⭐ Very Good",
                        5: "⭐⭐⭐⭐⭐ Excellent"
                    };
                    ratingLabel.textContent = descriptions[selectVal] || "";
                }
            });
        });

        function highlightStars(count) {
            starItems.forEach(star => {
                const val = parseInt(star.getAttribute("data-value"));
                if (val <= count) {
                    star.classList.add("active");
                } else {
                    star.classList.remove("active");
                }
            });
        }
    }

    /* ==========================================
       TEXTAREA CHARACTER COUNT
       ========================================== */
    const textareas = document.querySelectorAll("textarea");
    textareas.forEach(textarea => {
        const countSpan = document.getElementById("charCount");
        textarea.addEventListener("input", function () {
            if (countSpan) {
                countSpan.textContent = this.value.length;
            }
            console.log("Characters: " + this.value.length);
        });
    });

    /* ==========================================
       CLINICAL INPUT LIVE COLOR-CODED VALIDATION
       ========================================== */
    const clinicalInputs = {
        pregnancies: { green: [0, 4], yellow: [5, 8] },
        glucose: { green: [0, 99], yellow: [100, 125] },
        blood_pressure: { green: [0, 79], yellow: [80, 89] },
        skin_thickness: { green: [10, 34], yellow: [35, 49] },
        insulin: { green: [15, 166], yellow: [167, 249] },
        bmi: { green: [0, 24.9], yellow: [25, 29.9] },
        pedigree: { green: [0, 0.499], yellow: [0.5, 0.799] }
    };

    Object.keys(clinicalInputs).forEach(fieldName => {
        const inputEl = document.querySelector(`input[name='${fieldName}']`);
        if (inputEl) {
            inputEl.addEventListener("input", function () {
                const val = parseFloat(this.value);
                if (isNaN(val) || this.value === "") {
                    this.className = "form-control-custom"; // Reset
                    return;
                }

                const thresholds = clinicalInputs[fieldName];
                
                // Reset classes
                this.classList.remove("border-success-custom", "border-warning-custom", "border-danger-custom");

                if (val >= thresholds.green[0] && val <= thresholds.green[1]) {
                    this.classList.add("border-success-custom");
                } else if (val >= thresholds.yellow[0] && val <= thresholds.yellow[1]) {
                    this.classList.add("border-warning-custom");
                } else {
                    this.classList.add("border-danger-custom");
                }
            });
        }
    });

    /* ==========================================
       PROFILE PHOTO LIVE PREVIEW
       ========================================== */
    const photoInput = document.querySelector("input[name='profile_photo']");
    const previewImg = document.querySelector(".profile-photo-container img");
    if (photoInput && previewImg) {
        photoInput.addEventListener("change", function () {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    previewImg.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    /* ==========================================
       LOADING ANIMATION FOR BUTTONS
       ========================================== */
    const submitButtons = document.querySelectorAll("button[type='submit']");
    submitButtons.forEach(btn => {
        btn.addEventListener("click", function () {
            // Only trigger if the form is actually valid
            const form = btn.closest("form");
            if (form && form.checkValidity()) {
                const originalText = btn.innerHTML;
                btn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Processing...`;
                btn.disabled = true;
                form.submit();
            }
        });
    });
});