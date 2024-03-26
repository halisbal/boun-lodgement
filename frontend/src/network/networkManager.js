const BASE_URL = `${process.env.REACT_APP_BASE_ENDPOINT}`;

const request = async (endpoint, body = null) => {
  if (!endpoint) {
    throw new Error("Invalid endpoint key");
  }

  // Set the authorization header if the endpoint requires authentication
  if (endpoint.requiresAuth) {
    const accessToken = localStorage.getItem("accessToken");
    if (!accessToken) {
      throw new Error("Access token not found");
    }
    axiosInstance.defaults.headers.common["Authorization"] = `${accessToken}`;
  } else {
    delete axiosInstance.defaults.headers.common["Authorization"];
  }

  const config = {
    method: endpoint.method,
    url: endpoint.url,
    data: body,
  };
};
