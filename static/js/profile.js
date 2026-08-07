const token = localStorage.getItem("access_token");

// Guard: no token means no business being on this page.
if (!token) {
  window.location.href = "login.html";
}

const profileForm = document.getElementById("update-profile-form");
const profileMessage = document.getElementById("profile-message");
const passwordForm = document.getElementById("password-form");
const passwordMessage = document.getElementById("password-message");
const logoutBtn = document.getElementById("logout-btn");
const fullNameInput = document.getElementById("full-name");

// Prefill the full_name field using the existing /me endpoint.
async function loadProfile() {
  try {
    const res = await fetch("/me", {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) {
      const me = await res.json();
      fullNameInput.value = me.full_name || "";
    }
  } catch (err) {
    // Non-fatal: form just stays blank if this fails.
  }
}
loadProfile();

// Helper: FastAPI/Pydantic 422 errors return detail as an array of
// objects, not a plain string. 401s return a plain string. Handle both.
function extractErrorMessage(data, fallback) {
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail) && data.detail[0]?.msg) {
    return data.detail[0].msg;
  }
  return fallback;
}

profileForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  profileMessage.textContent = "";
  profileMessage.className = "message";

  try {
    const response = await fetch("/users/me", {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ full_name: fullNameInput.value.trim() }),
    });
    const data = await response.json();

    if (response.ok) {
      profileMessage.textContent = "Profile updated successfully!";
      profileMessage.classList.add("success");
    } else {
      profileMessage.textContent = extractErrorMessage(data, "Update failed.");
      profileMessage.classList.add("error");
    }
  } catch (err) {
    profileMessage.textContent = "Network error. Please try again.";
    profileMessage.classList.add("error");
  }
});

passwordForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  passwordMessage.textContent = "";
  passwordMessage.className = "message";

  const currentPassword = document.getElementById("current-password").value;
  const newPassword = document.getElementById("new-password").value;
  const confirmNewPassword = document.getElementById("confirm-new-password").value;

  if (newPassword !== confirmNewPassword) {
    passwordMessage.textContent = "New passwords do not match.";
    passwordMessage.classList.add("error");
    return;
  }

  try {
    const response = await fetch("/users/me/password", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });
    const data = await response.json();

    if (response.ok) {
      passwordMessage.textContent = "Password changed successfully!";
      passwordMessage.classList.add("success");
      passwordForm.reset();
    } else {
      passwordMessage.textContent = extractErrorMessage(data, "Password change failed.");
      passwordMessage.classList.add("error");
    }
  } catch (err) {
    passwordMessage.textContent = "Network error. Please try again.";
    passwordMessage.classList.add("error");
  }
});

logoutBtn.addEventListener("click", () => {
  localStorage.removeItem("access_token");
  window.location.href = "login.html";
});
