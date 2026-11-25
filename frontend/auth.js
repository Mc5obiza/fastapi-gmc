const API_BASE_URL = "http://127.0.0.1:8000";
const ACCESS_TOKEN_KEY = "gmc_access_token";
const authForm = document.querySelector("#auth-form");
const errorElement = document.querySelector("#auth-error");
const submitButton = authForm.querySelector('button[type="submit"]');

function getErrorMessage(body, status) {
  if (typeof body?.detail === "string") {
    return body.detail;
  }
  if (Array.isArray(body?.detail)) {
    return body.detail.map((item) => item.msg).filter(Boolean).join(" ");
  }
  return `The request failed (HTTP ${status}). Please try again.`;
}

authForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorElement.textContent = "";
  submitButton.disabled = true;
  authForm.setAttribute("aria-busy", "true");

  const formData = new FormData(authForm);
  const password = formData.get("password");
  const payload = {
    email: formData.get("email").trim(),
    password,
  };
  if (authForm.dataset.endpoint === "/auth/register") {
    payload.confirm_password = password;
  }

  try {
    const response = await fetch(`${API_BASE_URL}${authForm.dataset.endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await response.json().catch(() => null);
    if (!response.ok) {
      throw new Error(getErrorMessage(body, response.status));
    }
    if (typeof body?.access_token !== "string" || !body.access_token) {
      throw new Error("The server did not return an access token. Please try again.");
    }

    localStorage.setItem(ACCESS_TOKEN_KEY, body.access_token);
    window.location.replace("index.html");
  } catch (error) {
    errorElement.textContent = error instanceof TypeError
      ? "Unable to connect to the server. Check that the backend is running, then try again."
      : error.message;
    console.error("Authentication request failed.", error);
  } finally {
    submitButton.disabled = false;
    authForm.removeAttribute("aria-busy");
  }
});
