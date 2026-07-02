// =========================
// Mini HMS Main JS
// =========================

// Auto-hide alerts after 4 seconds
setTimeout(() => {
    let alerts = document.querySelectorAll(".alert");
    alerts.forEach(alert => {
        alert.style.transition = "0.5s";
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 500);
    });
}, 4000);


// Confirm delete actions
document.addEventListener("DOMContentLoaded", function () {
    const deleteButtons = document.querySelectorAll(".btn-danger");

    deleteButtons.forEach(btn => {
        btn.addEventListener("click", function (e) {
            let confirmAction = confirm("Are you sure you want to delete this?");
            if (!confirmAction) {
                e.preventDefault();
            }
        });
    });
});


// Table row highlight
document.querySelectorAll("tr").forEach(row => {
    row.addEventListener("mouseover", () => {
        row.style.backgroundColor = "#f1f3f5";
    });

    row.addEventListener("mouseout", () => {
        row.style.backgroundColor = "";
    });
});