const form = document.getElementById("register-form");
const message = document.getElementById("message");

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  message.textContent = "";
  message.className = "message";

  const username = document.getElementById("username").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const confirmPassword = document.getElementById("confirm_password").value;

  if (!isValidEmail(email)) {
    message.textContent = "Please enter a valid email address.";
    message.classList.add("error");
    return;
  }
  if (password.length < 8) {
    message.textContent = "Password must be at least 8 characters long.";
    message.classList.add("error");
    return;
  }
  if (password !== confirmPassword) {
    message.textContent = "Passwords do not match.";
    message.classList.add("error");
    return;
  }

  try {
    const response = await fetch("/users/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password }),
    });
    const data = await response.json();

    if (response.ok) {
      message.textContent = "Registration successful! Redirecting to login...";
      message.classList.add("success");
      setTimeout(() => (window.location.href = "/static/login.html"), 1200);
    } else {
      message.textContent = data.detail || "Registration failed.";
      message.classList.add("error");
    }
  } catch (err) {
    message.textContent = "Network error. Please try again.";
    message.classList.add("error");
  }
});
