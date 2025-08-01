const API_BASE_URL = "http://localhost:8000";  // Change to your actual backend URL

// Helper function to make requests
async function apiRequest(endpoint, method = "GET", data = null, token = null) {
  const headers = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const options = {
    method,
    headers,
  };
  if (data) {
    options.body = JSON.stringify(data);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
  const responseData = await response.json();

  if (!response.ok) {
    throw new Error(responseData.detail || "API request failed");
  }

  return responseData;
}

// ========== Auth APIs ==========

// Register a user
async function registerUser(formData) {
  return await apiRequest("/register", "POST", formData);
}

// Login
async function loginUser(formData) {
  return await apiRequest("/login", "POST", formData);
}

// Reset Password
async function resetPassword(data) {
  return await apiRequest("/reset-password", "POST", data);
}

// ========== Chat ==========

// Send user message to chatbot
async function sendChatMessage(message, token) {
  return await apiRequest("/chat", "POST", { message }, token);
}

// Get previous chats
async function getChatHistory(token) {
  return await apiRequest("/chat/history", "GET", null, token);
}
