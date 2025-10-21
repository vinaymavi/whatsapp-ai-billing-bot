import { Context } from "@/context/GlobalContext";
import { useContext, type FC } from "react";
import { NavLink } from "react-router";
export const Header: FC<{}> = () => {
  const { headerTitle, isLogin } = useContext(Context);

  return (
    <header className="flex items-center justify-center bg-emerald-800  p-4 w-full">
      {isLogin ? (
        <div className="join join-vertical lg:join-horizontal">
          {/* Anchor Button: /admin/dashboard */}
          <NavLink
            to="/admin/dashboard"
            className={({ isActive }) => `${isActive ? "bg-emerald-600" : ""}`}
          >
            {({ isActive }) => (
              <button
                className={`btn join-item ${
                  isActive ? "btn-active bg-emerald-600" : ""
                }`}
              >
                Runs
              </button>
            )}
          </NavLink>
          {/* Anchor Button: /admin/prepare-jobs */}
          <NavLink
            to="/admin/prepare-jobs"
            className={({ isActive }) => `${isActive ? "bg-emerald-600" : ""}`}
          >
            {({ isActive }) => (
              <button
                className={`btn join-item ${
                  isActive ? "btn-active bg-emerald-600" : ""
                }`}
              >
                Prepare Jobs+
              </button>
            )}
          </NavLink>
          {/* Anchor Button: /admin/settings */}
          <NavLink
            to="/admin/settings"
            className={({ isActive }) => `${isActive ? "bg-emerald-600" : ""}`}
          >
            {({ isActive }) => (
              <button
                className={`btn join-item ${
                  isActive ? "btn-active bg-emerald-600" : ""
                }`}
              >
                Settings
              </button>
            )}
          </NavLink>
        </div>
      ) : (
        <h1 className="text-2xl text-neutral-100 uppercase">{headerTitle}</h1>
      )}
    </header>
  );
};

export default Header;
