import useAuth from "../hooks/useAuth";

const LogoutButton = () => {
  const { isLoggedIn } = useAuth();

  if (!isLoggedIn) {
    return null;
  } else {
    return (
      <button
        className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
        onClick={() => {
          localStorage.removeItem("token");
          window.location.reload();
        }}
      >
        Logout
      </button>
    );
  }
};

export default LogoutButton;
