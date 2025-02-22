document.addEventListener("DOMContentLoaded", function () {
    const links = document.querySelectorAll(".top-nav a, ul a"); // Select all nav and sidebar links
    const notificationBtn = document.getElementById("navNotificationBtn");
    const bellIcon = document.querySelector(".top-nav-notification i"); // Bell icon
    const notificationBadge = document.getElementById("notification-badge"); // Notification count badge
    const currentPath = window.location.pathname; // Get current page path
    let activeLinkFound = false; // Flag to check if any link is active

    // Get the notification page URL from the button's data-url attribute
    const notificationPageUrl = notificationBtn.getAttribute("data-url");

    // Remove active class from all links and parent list items
    links.forEach(link => {
        link.classList.remove("active");
        link.parentElement.classList.remove("active"); // Remove active from parent <li>
    });

    // Highlight active link and apply breadcrumb format
    links.forEach(link => {
        if (link.getAttribute("href") === currentPath) {
            link.classList.add("active");
            link.parentElement.classList.add("active"); // Add active class to <li>
            activeLinkFound = true;

            // const parentMenuItem = link.closest("ul.submenu"); // Check if it's in a submenu
            // if (parentMenuItem) {
            //     const mainMenuItem = parentMenuItem.closest("li"); // Get parent <li>
            //     const mainMenuLink = mainMenuItem.querySelector("a"); // Get the main link text
                
            //     if (mainMenuLink) {
            //         // Modify parent menu to show breadcrumb-style text but keep active class styling unchanged
            //         mainMenuLink.innerHTML = `
            //             <i class="fa-solid fa-gear"></i> 
            //             <span>Settings</span> 
            //             <i class="fa-solid fa-angle-right style="font-size: 0.3em;"></i> 
            //             <span>Account</span>
            //         `;

            //         mainMenuItem.style.backgroundColor = "gold";
            //         mainMenuLink.style.color = "black";
            //         mainMenuLink.style.fontWeight = "bold";
            //         mainMenuItem.style.borderRadius = "0.7rem";
            //         mainMenuItem.style.margin = "0.3rem 0";
            //     }
            // }
        }
    });

    // Check if we are on the notifications page
    if (currentPath === notificationPageUrl) {
        links.forEach(link => link.classList.remove("active"));

        notificationBtn.style.backgroundColor = "gold";
        notificationBtn.style.color = "black";

        if (bellIcon) {
            bellIcon.style.color = "gold";
        }

        if (notificationBadge) {
            notificationBadge.style.display = "none";
        }

        activeLinkFound = true;
    } else {
        notificationBtn.style.backgroundColor = "";
        notificationBtn.style.color = "";

        if (bellIcon) {
            bellIcon.style.color = "";
        }

        if (notificationBadge && notificationBadge.innerText !== "0") {
            notificationBadge.style.display = "block";
        }
    }

    // If no active link was found, set the dashboard (home) as default active
    if (!activeLinkFound) {
        const homeLink = document.querySelector(".top-nav a[href='/memb_dash/']");
        if (homeLink) {
            homeLink.classList.add("active");
            homeLink.parentElement.classList.add("active"); // Also apply to parent <li>
        }
    }

    // Store active tab in localStorage
    links.forEach(link => {
        link.addEventListener("click", function () {
            localStorage.setItem("activeTab", this.getAttribute("href"));
        });
    });

    // Make the bell icon clickable
    if (bellIcon) {
        bellIcon.addEventListener("click", function () {
            window.location.href = notificationPageUrl;
        });
    }
});







document.addEventListener("DOMContentLoaded", function () {
    const navNotificationBtn = document.getElementById("navNotificationBtn");

    navNotificationBtn.addEventListener("click", function () {
        const notificationUrl = this.getAttribute("data-url");  // Get URL from button
        window.location.href = notificationUrl; // Redirect to notifications page
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const notificationBadge = document.getElementById("notification-badge");

    // Simulated unread count (Replace this with actual fetch request from backend)
    let unreadNotifications = 4; 

    // Update badge count
    function updateNotificationBadge(count) {
        if (count > 0) {
            notificationBadge.textContent = count;
            notificationBadge.style.display = "flex"; // Show the badge
        } else {
            notificationBadge.style.display = "none"; // Hide if no unread notifications
        }
    }

    updateNotificationBadge(unreadNotifications);

    // Example: Simulate marking notifications as read after 5 seconds
    // setTimeout(() => {
    //     unreadNotifications = 0; // Mark notifications as read
    //     updateNotificationBadge(unreadNotifications);
    // }, 5000);
});

document.addEventListener("DOMContentLoaded", function () {
    const markReadButtons = document.querySelectorAll(".mark-read");
    const markAllReadButton = document.getElementById("mark-all-read");
    const clearAllButton = document.getElementById("clear-all");
    const notificationList = document.getElementById("notification-list");
    const notificationBadge = document.getElementById("notification-badge");

    // Get the initial unread count based on existing unread notifications
    let unreadNotifications = document.querySelectorAll(".notification.unread").length;

    // Function to update the notification badge count
    function updateNotificationBadge(count) {
        if (count > 0) {
            notificationBadge.textContent = count;
            notificationBadge.style.display = "flex"; // Show the badge
        } else {
            notificationBadge.style.display = "none"; // Hide if no unread notifications
        }
    }

    // Initialize badge with the correct count
    updateNotificationBadge(unreadNotifications);

    // Mark a single notification as read
    markReadButtons.forEach(button => {
        button.addEventListener("click", function () {
            const notification = this.closest(".notification");
            notification.classList.remove("unread");
            this.remove(); // Remove the button after marking as read

            // Decrease unread count and update the badge
            unreadNotifications = Math.max(0, unreadNotifications - 1);
            updateNotificationBadge(unreadNotifications);
        });
    });

    // Mark all as read
    markAllReadButton.addEventListener("click", function () {
        document.querySelectorAll(".notification.unread").forEach(notification => {
            notification.classList.remove("unread");
            const button = notification.querySelector(".mark-read");
            if (button) button.remove();
        });

        // Set unread count to zero and update the badge
        unreadNotifications = 0;
        updateNotificationBadge(unreadNotifications);
    });

    // Clear all notifications
    clearAllButton.addEventListener("click", function () {
        notificationList.innerHTML = "<p>No notifications</p>";

        // Set unread count to zero and update the badge
        unreadNotifications = 0;
        updateNotificationBadge(unreadNotifications);
    });
});
