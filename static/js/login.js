const form = document.getElementById("login-form");
const message = document.getElementById("message");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  message.textContent = "";
  message.className = "message";

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  if (!email || !password) {
    message.textContent = "Please fill in both fields.";
    message.classList.add("error");
    return;
  }

  try {
    const response = await fetch("/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await response.json();

    if (response.ok) {
      localStorage.setItem("access_token", data.access_token);
      message.textContent = "Login successful!";
      message.classList.add("success");
    } else {
      message.textContent = data.detail || "Invalid email or password.";
      message.classList.add("error");
    }
  } catch (err) {
    message.textContent = "Network error. Please try again.";
    message.classList.add("error");
  }
});
