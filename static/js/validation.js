// =========================
// FORM VALIDATION (Mini HMS)
// =========================

document.addEventListener("DOMContentLoaded", function () {

    // Validate empty inputs
    const forms = document.querySelectorAll("form");

    forms.forEach(form => {
        form.addEventListener("submit", function (e) {

            let inputs = form.querySelectorAll("input, textarea");
            let valid = true;

            inputs.forEach(input => {
                if (input.hasAttribute("required") && input.value.trim() === "") {
                    valid = false;
                    input.style.border = "2px solid red";
                } else {
                    input.style.border = "";
                }
            });

            if (!valid) {
                e.preventDefault();
                alert("Please fill all required fields.");
            }
        });
    });

});