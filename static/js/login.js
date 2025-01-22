document.getElementById("loginForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    // Basic validation
    if (!email || !password) {
        alert("Please fill in all fields!");
        return;
    }

    // Simulate sending data to the backend
    console.log("Logging in with:", { email, password });

    // Show a success message
    alert("Login successful!");
});


document.getElementById("loginForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    // Basic validation
    if (!email || !password) {
        alert("Please fill in all fields!");
        return;
    }

    // Get CSRF token from meta tag
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute("content");

    try {
        const response = await fetch("users/login/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken, // Include CSRF token
            },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message); // Show success message
            // Redirect to dashboard or any protected page
            window.location.href = "/dashboard/";
        } else {
            alert(data.message); // Show error message
        }
    } catch (error) {
        console.error("Error:", error);
        alert("An unexpected error occurred. Please try again later.");
    }
});
