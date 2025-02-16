document.addEventListener("DOMContentLoaded", function () {
    const links = document.querySelectorAll(".top-nav a");
    const currentPath = window.location.pathname; // Get current page path

    links.forEach(link => {
        link.classList.remove("active");

        // Set active link if href matches current path
        if (link.getAttribute("href") === currentPath) {
            link.classList.add("active");
        }

        // Store active tab in localStorage
        link.addEventListener("click", function () {
            localStorage.setItem("activeTab", this.getAttribute("href"));
        });
    });

    // If no active link, set default as "memb_dash"
    if (!document.querySelector(".top-nav a.active")) {
        document.querySelector(".top-nav a[href='/memb_dash/']").classList.add("active");
    }
});