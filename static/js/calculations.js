document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("access_token");
  const message = document.getElementById("message");

  // Guard: no token means no business being on this page.
  if (!token) {
    window.location.href = "login.html";
    return;
  }

  const form = document.getElementById("calc-form");
  const calcIdInput = document.getElementById("calc-id");
  const aInput = document.getElementById("a");
  const bInput = document.getElementById("b");
  const typeInput = document.getElementById("type");
  const submitBtn = document.getElementById("submit-btn");
  const cancelEditBtn = document.getElementById("cancel-edit-btn");
  const tableBody = document.getElementById("calc-table-body");
  const logoutBtn = document.getElementById("logout-btn");

  logoutBtn.addEventListener("click", () => {
    localStorage.removeItem("access_token");
    window.location.href = "login.html";
  });

  function showMessage(text, isError = false) {
    message.textContent = text;
    message.className = isError ? "message error" : "message success";
  }

  function resetForm() {
    calcIdInput.value = "";
    form.reset();
    submitBtn.textContent = "Add Calculation";
    cancelEditBtn.style.display = "none";
  }

  cancelEditBtn.addEventListener("click", resetForm);

  // ---------- BROWSE ----------
  async function loadCalculations() {
    try {
      const response = await fetch("/calculations/", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.status === 401) {
        // Token expired or invalid — send the user back to login.
        localStorage.removeItem("access_token");
        window.location.href = "login.html";
        return;
      }

      const calculations = await response.json();
      renderTable(calculations);
    } catch (err) {
      showMessage("Network error loading calculations.", true);
    }
  }

  function renderTable(calculations) {
    tableBody.innerHTML = "";

    calculations.forEach((calc) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${calc.a}</td>
        <td>${calc.b}</td>
        <td>${calc.type}</td>
        <td>${calc.result ?? "—"}</td>
        <td>${new Date(calc.created_at).toLocaleString()}</td>
        <td>
          <button class="edit-btn" data-id="${calc.id}">Edit</button>
          <button class="delete-btn" data-id="${calc.id}">Delete</button>
        </td>
      `;
      tableBody.appendChild(row);
    });

    attachRowListeners(calculations);
  }

  function attachRowListeners(calculations) {
    document.querySelectorAll(".edit-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const calc = calculations.find((c) => c.id === Number(btn.dataset.id));
        startEdit(calc);
      });
    });

    document.querySelectorAll(".delete-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        deleteCalculation(Number(btn.dataset.id));
      });
    });
  }

  // ---------- EDIT (populate form) ----------
  function startEdit(calc) {
    calcIdInput.value = calc.id;
    aInput.value = calc.a;
    bInput.value = calc.b;
    typeInput.value = calc.type;
    submitBtn.textContent = "Update Calculation";
    cancelEditBtn.style.display = "inline-block";
  }

  // ---------- ADD / EDIT (shared submit) ----------
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      a: parseFloat(aInput.value),
      b: parseFloat(bInput.value),
      type: typeInput.value,
    };

    const calcId = calcIdInput.value;
    const isEdit = Boolean(calcId);

    try {
      const response = await fetch(
        isEdit ? `/calculations/${calcId}` : "/calculations/",
        {
          method: isEdit ? "PUT" : "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(payload),
        }
      );

      const data = await response.json();

      if (response.ok) {
        showMessage(isEdit ? "Calculation updated!" : "Calculation added!");
        resetForm();
        loadCalculations();
      } else {
        showMessage(data.detail || "Something went wrong.", true);
      }
    } catch (err) {
      showMessage("Network error. Please try again.", true);
    }
  });

  // ---------- DELETE ----------
  async function deleteCalculation(id) {
    if (!confirm("Delete this calculation?")) return;

    try {
      const response = await fetch(`/calculations/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.status === 204) {
        showMessage("Calculation deleted.");
        loadCalculations();
      } else {
        const data = await response.json();
        showMessage(data.detail || "Delete failed.", true);
      }
    } catch (err) {
      showMessage("Network error. Please try again.", true);
    }
  }

  // ---------- INITIAL LOAD ----------
  loadCalculations();
});
