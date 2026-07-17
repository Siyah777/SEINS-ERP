document.addEventListener("DOMContentLoaded", function () {

    function aplicarLayout() {

        document.cookie = "jazzy_menu=closed;path=/;SameSite=Strict";
        document.body.classList.add("sidebar-collapse");

        const header = document.querySelector(".app-header");
        const main = document.querySelector(".app-main");
        const sidebar = document.querySelector(".app-sidebar");

        if (header && main) {
            header.style.position = "fixed";
            header.style.top = "0";
            header.style.left = "0";
            header.style.right = "0";
            header.style.zIndex = "1060";

            main.style.paddingTop = `${header.offsetHeight}px`;
        }

        if (sidebar) {
            sidebar.style.zIndex = "1061";
        }
    }

    aplicarLayout();

});

// Cerrar el sidebar al hacer clic fuera de él
document.addEventListener("click", function (e) {

    const sidebar = document.querySelector(".app-sidebar");
    const toggle = document.querySelector('[data-lte-toggle="sidebar"]');

    if (!sidebar || !toggle) return;

    // No cerrar si se hace clic en el botón hamburguesa
    if (toggle.contains(e.target)) return;

    // No cerrar si el clic fue dentro del sidebar
    if (sidebar.contains(e.target)) return;

    // Si está abierto, cerrarlo
    if (document.body.classList.contains("sidebar-open")) {
        document.body.classList.remove("sidebar-open");
        document.body.classList.add("sidebar-collapse");
        document.cookie = "jazzy_menu=closed;path=/;SameSite=Strict";
    }

});

if (sidebar && header) {
    sidebar.style.height = `calc(100vh - ${header.offsetHeight}px)`;
    sidebar.style.marginTop = `${header.offsetHeight}px`;
    sidebar.style.overflowY = "auto";
    sidebar.style.overscrollBehavior = "contain";
}