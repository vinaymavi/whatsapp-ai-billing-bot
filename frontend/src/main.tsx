import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Route, Routes, Navigate } from "react-router";
import "./index.css";
import App from "./App.tsx";
import { LoginForm } from "@components/LoginForm/LoginForm.tsx";
import { AuthLayout } from "@components/AuthLayout/AuthLayout.tsx";
import { Dashboard } from "@components/Dashboard/Dashboard.tsx";
import { GlobalContext } from "@/context/GlobalContext.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <GlobalContext>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/admin" replace />}></Route>
          <Route path="/admin" element={<App />}>
            <Route
              index
              element={
                <LoginForm
                  title="Welcome"
                  desc="Login to Admin seciton"
                  buttonLabel="Login"
                  inputPlaceholder="Admin #"
                />
              }
            />
            <Route path="/admin/dashboard" element={<AuthLayout />}>
              <Route index element={<Dashboard />} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </GlobalContext>
  </StrictMode>
);
