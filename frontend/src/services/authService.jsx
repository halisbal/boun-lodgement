//const BASE_ENDPOINT = import.meta.env.VITE_BASE_ENDPOINT;
const BASE_ENDPOINT = import.meta.env.VITE_BASE_ENDPOINT;
const login = async (username, password) => {
  try {
    const response = await fetch(
      `${BASE_ENDPOINT}/api/auth/login/
    `,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email: username, password: password }),
      }
    );
    const data = await response.json();
    if (response.ok) {
      console.log(response, "authservice login response object");
      console.log(data, "authservice login data object");
      localStorage.setItem("token", data.token);
      return true;
    }
    return false;
  } catch (error) {
    console.error(error, "Failed to login authservice login");
    return false;
  }
};

const getUserInfo = async () => {
  try {
    const token = localStorage.getItem("token");
    const response = await fetch(`${BASE_ENDPOINT}/api/auth/me/`, {
      headers: {
        Authorization: `Token ${token}`,
      },
    });

    if (response.ok) {
      const data = response.json();
      return data;
    } else {
      console.log("Failed to get user info from authservice getUserInfo");
      return null;
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
