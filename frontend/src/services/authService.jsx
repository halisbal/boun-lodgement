//const BASE_ENDPOINT = import.meta.env.VITE_BASE_ENDPOINT;
const BASE_ENDPOINT = "http://127.0.0.1:8080";
const login = async (username, password) => {
  try {
    const response = await fetch(`${BASE_ENDPOINT}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username: username, password: password }),
    });
    const data = await response.json();
    if (response.ok) {
      localStorage.setItem("token", data.token);
      return true;
    }
  } catch (error) {
    console.error(error);
    return false;
  }
};

const getUserInfo = async () => {
  try {
    const token = localStorage.getItem("token");
    const response = await fetch(`${BASE_ENDPOINT}/getuserinfo`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await response.json();
    if (response.ok) {
      return data;
    } else {
      throw new Error(data.message || "Failed to get user info");
    }
  } catch (error) {
    console.error(error);
    return null;
  }
};

const logout = () => {
  localStorage.removeItem("token");
};

const getToken = () => {
  return localStorage.getItem("token");
};

export default { login, logout, getToken, getUserInfo };
