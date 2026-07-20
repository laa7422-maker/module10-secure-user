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

      // Use the stored token to make an authenticated request,
      // confirming the JWT actually works end-to-end.
      await loadCurrentUser(data.access_token);
    } else {
      message.textContent = data.detail || "Invalid email or password.";
      message.classList.add("error");
    }
  } catch (err) {
    message.textContent = "Network error. Please try again.";
    message.classList.add("error");
  }
});

async function loadCurrentUser(token) {
  try {
    const meResponse = await fetch("/me", {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (meResponse.ok) {
      const me = await meResponse.json();
      message.textContent = `Login successful! Welcome, ${me.username}.`;
    }
    // If /me fails for any reason, we silently keep the plain
    // "Login successful!" message — the token itself is still valid
    // and stored, this call is just a demonstration of using it.
  } catch (err) {
    // Network issue on the /me call shouldn't undo a successful login.
  }
}
