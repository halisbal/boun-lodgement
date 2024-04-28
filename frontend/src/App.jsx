import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import HomePage from "./components/HomePage";
import LoginPage from "./components/LoginPage";
import { Link } from "react-router-dom";
import { ProtectedRoute } from "./routes/ProtectedRoute";
import { AuthProvider } from "./contexts/AuthContext";
import LoggedInHeader from "./components/LoggedInHeader";
import ListLodgementsPage from "./components/ListLodgementsPage";
import AuthButtons from "./components/AuthButtons";
const queryClient = new QueryClient({
  defaultOptions: {
    staleTime: Infinity,
    cacheTime: Infinity,
  },
});

const App = () => {



  return (
    <AuthProvider>
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          <header className="bg-gray-800 text-white p-4">
            <nav className="flex justify-between items-center">
              <Link
                to="/home"
                className="text-xl font-semibold hover:text-gray-300"
              >
                <img
                  src="/boun_logo.svg"
                  alt="Bogazici University Logo"
                  className="h-8 w-auto"
                />
              </Link>

              <LoggedInHeader>
                <Link to="/logdements" className="text-lg hover:text-gray-300 mr-4">
                  Lodgements
                </Link>
              </LoggedInHeader>


              <div className="flex items-center">
                <AuthButtons />
              </div>
            </nav>
          </header>

          <Routes>
            <Route
              path="/home"
              element={
                <ProtectedRoute>
                  <HomePage />
                </ProtectedRoute>
              }
            ></Route>
            <Route path="/" element={<LoginPage />}></Route>
            <Route
              path="/logdements"
              element={
                <ProtectedRoute>
                  <ListLodgementsPage />
                </ProtectedRoute>
              }
            ></Route>
            <Route path="/login" element={<LoginPage />}></Route>
          </Routes>
        </QueryClientProvider>
      </BrowserRouter>
    </AuthProvider>
  );
};

const container = document.getElementById("root");
const root = createRoot(container);
root.render(<App />);
