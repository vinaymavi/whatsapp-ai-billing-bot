import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router";
import "./index.css";
import App from "./App.tsx";
import { LoginForm } from "@components/LoginForm/LoginForm.tsx";
import { AuthLayout } from "@components/AuthLayout/AuthLayout.tsx";
import { Dashboard } from "@components/Dashboard/Dashboard.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />}>
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
          <Route path="/dashboard" element={<AuthLayout />}>
          <Route index element={<Dashboard/>}/>
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  </StrictMode>
);
