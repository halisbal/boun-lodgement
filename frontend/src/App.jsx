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
import ApplyPage from "./components/ApplyPage";
import ListApplicationsPage from "./components/ListApplicationsPage";
import ApplicationDetailPage from "./components/ApplicationDetailPage";
import EditInventoryPage from "./components/EditInventoryPage";
import ManagerHeader from "./components/ManagerHeader";
import ManageApplicationsPage from "./components/ManageApplicationsPage";
import ManageApplicationsDetail from "./components/ManageApplicationsDetail";
import ManageUsers from "./components/ManageUsers";
const queryClient = new QueryClient({
  defaultOptions: {
    staleTime: 0,
    cacheTime: 0,
  },
});

const App = () => {



  return (
    <AuthProvider>
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          <header className="bg-white-900 text-white p-4">
            <nav className="">
              <div className="container mx-auto flex justify-between items-center">
                <div className="flex items-center">
                  <Link to="/home" className="mx-4"> <img src="/boun_logo.svg" alt="Bogazici University Logo" className="h-8 w-auto" /> </Link>
                  <LoggedInHeader>
                    <Link to="/logdements" className="text-lg mx-4 text-black hover:text-gray-700 mr-4"> Lodgements </Link>
                  </LoggedInHeader>
                  <LoggedInHeader>
                    <Link to="/apply" className="text-lg mx-4 text-black hover:text-gray-700 mr-4"> Apply </Link>
                  </LoggedInHeader>
                  <LoggedInHeader>
                    <Link to="/my-applications" className="text-lg mx-4 text-black hover:text-gray-700 mr-4"> My Applications </Link>
                  </LoggedInHeader>
                  <ManagerHeader>
                    <Link to="/edit-inventory" className="text-lg mx-4 text-black hover:text-gray-700 mr-4"> Edit Inventory </Link>
                  </ManagerHeader>
                  <ManagerHeader>
                    <Link to="/manage-applications" className="text-lg mx-4 text-black hover:text-gray-700 mr-4"> Manage Applications </Link>
                  </ManagerHeader>
                  <ManagerHeader>
                    <Link to="/manage-users" className="text-lg mx-4 text-black hover:text-gray-700 mr-4"> Manage Users </Link>
                  </ManagerHeader>
                </div>
                <div>
                  <div className="flex items-center">
                    <AuthButtons />
                  </div>
                </div>
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
            <Route
              path="/apply"
              element={
                <ProtectedRoute>
                  <ApplyPage />
                </ProtectedRoute>
              }
            ></Route>
            <Route
              path="/my-applications"
              element={
                <ProtectedRoute>
                  <ListApplicationsPage />
                </ProtectedRoute>
              }
            ></Route>
            <Route path="/login" element={<LoginPage />}></Route>
            <Route path="/application/:id" element={<ApplicationDetailPage />}></Route>
            <Route path="/edit-inventory" element={<EditInventoryPage />}></Route>
            <Route path="/manage-applications" element={<ManageApplicationsPage />}></Route>
            <Route path="/manage-application-detail/:id" element={<ManageApplicationsDetail />}></Route>
            <Route path="/manage-users" element={<ManageUsers />}></Route>
            <Route path="*" element={<div>Not Found</div>}></Route>
          </Routes>
        </QueryClientProvider>
      </BrowserRouter>
    </AuthProvider>
  );
};

const container = document.getElementById("root");
const root = createRoot(container);
root.render(<App />);
