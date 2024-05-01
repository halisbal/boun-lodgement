import { Button } from "@material-tailwind/react";
import useAuth from "../hooks/useAuth";
import { Link } from "react-router-dom";

const AuthButtons = () => {
  const { isLoggedIn } = useAuth();

  if (!isLoggedIn) {
    return (
      <Link to="/login" className="text-lg text-black hover:text-gray-700 mr-4">
        Login
      </Link>
    );

  } else {
    return (
      <Button
        className="px-4 py-2" color="red" variant="outlined"
        onClick={() => {
          localStorage.removeItem("token");
          window.location.reload();
        }}
      >
        Logout
      </Button>
    );
  }
};

export default AuthButtons;
