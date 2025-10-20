import ErrorBoundary from "@components/ErrorBoundary/ErrorBoundary";
import "./App.css";
import Header from "./components/Header/Header";
import { Outlet } from "react-router";
function App() {
  return (
    <ErrorBoundary>
      <div className="flex flex-col items-center justify-center">
        <Header />
        <Outlet />
      </div>
    </ErrorBoundary>
  );
}

export default App;
