import useAuth from "../hooks/useAuth";
import { Link } from "react-router-dom";

const AuthButtons = () => {
  const { isLoggedIn } = useAuth();

  if (!isLoggedIn) {
    return (
      <Link to="/login" className="text-lg hover:text-gray-300 mr-4">
        Login
      </Link>
    );

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

export default AuthButtons;
