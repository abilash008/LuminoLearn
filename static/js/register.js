document.getElementById("registerForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    // Collect form data
    const username = document.getElementById("username").value;
    const email = document.getElementById("email").value;
    const role = document.getElementById("role").value;
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm_password").value;
    

    // Validate fields
    if (!username || !email || !password || !confirmPassword || !role) {
        alert("Please fill in all fields.");
        return;
    }


    if (password.length < 8) {
        e.preventDefault();
        alert("Password must be at least 8 characters long.");
    }

    if (password !== confirmPassword) {
        alert("Passwords do not match.");
        return;
    }


    // Send POST request to register API
    try {
        const response = await fetch("/users/register/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                username,
                email,
                password,
                confirm_password: confirmPassword,
                role,
            }),
        });

        const result = await response.json();

        if (result.status === "success") {
            alert("Registration successful!");
            window.location.href = "/users/login/"; // Redirect to login page after successful registration
        } else {
            alert(result.message); // Show error message
        }
    } catch (error) {
        console.error("Error:", error);
        alert("An error occurred. Please try again.");
    }
});
