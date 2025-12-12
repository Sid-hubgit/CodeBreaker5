const modeBtn = document.getElementById("mode-btn");
const submitBtn = document.getElementById("submit-btn");
const confirmPass = document.getElementById("confirm-password");
const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password");
const formTitle = document.getElementById("form-title");
const logDiv = document.getElementById("log");

let mode = "login"; // current mode

// --- Utilities ---
function clearInputs() {
  usernameInput.value = "";
  passwordInput.value = "";
  confirmPass.value = "";
}

function showLog(msg, color = "red") {
  logDiv.textContent = msg;
  logDiv.style.color = color;
}

function clearLog() {
  logDiv.textContent = "";
}

// --- LocalStorage helpers ---
function getUsers() {
  try {
    return JSON.parse(localStorage.getItem("users")) || {};
  } catch {
    return {};
  }
}

function saveUser(username, password) {
  const users = getUsers();
  users[username] = password;
  localStorage.setItem("users", JSON.stringify(users));
}

function checkUser(username, password) {
  const users = getUsers();
  return users.hasOwnProperty(username) && users[username] === password;
}

// --- Mode toggle ---
modeBtn.addEventListener("click", () => {
  clearInputs();
  clearLog();

  if (mode === "login") {
    mode = "signup";
    formTitle.textContent = "Signup";
    confirmPass.style.display = "block";
    submitBtn.textContent = "Signup";
    modeBtn.textContent = "Switch to Login";
  } else {
    mode = "login";
    formTitle.textContent = "Login";
    confirmPass.style.display = "none";
    submitBtn.textContent = "Login";
    modeBtn.textContent = "Switch to Signup";
  }
});

// --- Submission ---
submitBtn.addEventListener("click", () => {
  const username = usernameInput.value.trim();
  const password = passwordInput.value.trim();
  const confirmPassword = confirmPass.value.trim();

  if (username === "" || password === "" || (mode === "signup" && confirmPassword === "")) {
    showLog("Input is empty");
    return;
  }

  if (mode === "signup") {
    if (password !== confirmPassword) {
      showLog("Passwords do not match");
      return;
    }

    const users = getUsers();
    if (users.hasOwnProperty(username)) {
      showLog("Username already exists");
      return;
    }

    saveUser(username, password);
    showLog("Signup successful!", "green");
    clearInputs();
  } else {
    if (!checkUser(username, password)) {
      showLog("Invalid username or password");
      return;
    }

    showLog("Login successful!", "green");
    clearInputs();
  }
});
