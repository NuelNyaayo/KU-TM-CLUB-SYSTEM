document.addEventListener("DOMContentLoaded", function () {
    const links = document.querySelectorAll(".top-nav a");
    const notificationBtn = document.getElementById("navNotificationBtn");
    const bellIcon = document.querySelector(".top-nav-notification i"); // Select the bell icon
    const notificationBadge = document.getElementById("notification-badge"); // Notification count badge
    const currentPath = window.location.pathname; // Get current page path
    let activeLinkFound = false; // Flag to check if any link is active

    // Get the notification page URL from the button's data-url attribute
    const notificationPageUrl = notificationBtn.getAttribute("data-url");

    // Remove active class from all links
    links.forEach(link => link.classList.remove("active"));

    // Highlight active link
    links.forEach(link => {
        if (link.getAttribute("href") === currentPath) {
            link.classList.add("active");
            activeLinkFound = true; // Set flag to true when an active link is found
        }
    });

    // Check if we are on the notifications page
    if (currentPath === notificationPageUrl) {
        // Remove active class from all links to prevent "Home" from being selected
        links.forEach(link => link.classList.remove("active"));

        // Apply special styling to the notification button
        notificationBtn.style.backgroundColor = "gold";
        notificationBtn.style.color = "black";

        // Change bell icon color to gold
        if (bellIcon) {
            bellIcon.style.color = "gold";
        }

        // Hide notification badge when on the notifications page
        if (notificationBadge) {
            notificationBadge.style.display = "none";
        }

        activeLinkFound = true; // Set flag since notifications button is active
    } else {
        // Reset styles when navigating away
        notificationBtn.style.backgroundColor = "";
        notificationBtn.style.color = "";

        // Reset bell icon color
        if (bellIcon) {
            bellIcon.style.color = "";
        }

        // Show notification badge if there are unread notifications
        if (notificationBadge && notificationBadge.innerText !== "0") {
            notificationBadge.style.display = "block";
        }
    }

    // If no active link was found, set the dashboard (home) as default active
    if (!activeLinkFound) {
        const homeLink = document.querySelector(".top-nav a[href='/memb_dash/']");
        if (homeLink) {
            homeLink.classList.add("active");
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
