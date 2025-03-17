document.addEventListener("DOMContentLoaded", function () {
    let menuItems = document.querySelectorAll(".side-panel ul li a");

    // **Clear localStorage if the user just logged in or registered**
    if (document.cookie.includes("clear_cache=true")) {
        localStorage.removeItem("activeTab");  // Remove stored active tab
        document.cookie = "clear_cache=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";  // Clear the cookie
    }

    // Get the default tab URL from the first menu item
    let defaultTab = menuItems.length > 0 ? menuItems[0].getAttribute("href") : "/leader_dash/";

    // Get the last active tab from localStorage, or fallback to default
    let activeTab = localStorage.getItem("activeTab") || defaultTab;

    function setActiveTab(tabHref) {
        // Remove 'active' class from all menu items
        menuItems.forEach(item => item.parentElement.classList.remove("active"));

        // Find the menu item that matches the stored URL and add 'active' class
        let activeItem = [...menuItems].find(item => item.getAttribute("href") === tabHref);

        if (activeItem) {
            activeItem.parentElement.classList.add("active");
        } else {
            // If no active tab is found, default to the first menu item
            menuItems[0].parentElement.classList.add("active");
        }
    }

    // Ensure the active tab is selected on first-time page load
    setActiveTab(activeTab);

    // Redirect only if the current path is different from activeTab and it's valid
    if (window.location.pathname !== activeTab && window.location.pathname !== "/") {
        let validTab = [...menuItems].some(item => item.getAttribute("href") === activeTab);
        if (validTab) {
            window.location.href = activeTab;
        }
    }

    // Handle menu item clicks
    menuItems.forEach(item => {
        item.addEventListener("click", function (event) {
            event.preventDefault();

            let selectedTab = this.getAttribute("href");

            // Store the selected tab in localStorage
            localStorage.setItem("activeTab", selectedTab);

            // Update the active tab styling
            setActiveTab(selectedTab);

            // Redirect to the selected tab
            window.location.href = selectedTab;
        });
    });
});
