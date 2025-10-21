import { Context } from "@/context/GlobalContext";
import { useContext, type FC } from "react";
import { NavLink } from "react-router";
export const Header: FC<{}> = () => {
  const { headerTitle, isLogin } = useContext(Context);

  return (
    <header className="flex items-center justify-center bg-emerald-800  p-4 w-full">
      {isLogin ? (
        <div className="join join-vertical lg:join-horizontal">
          <NavLink to="/admin/dashboard">
            <button className="btn join-item">Runs</button>
          </NavLink>
          <NavLink to="/admin/prepare-jobs">
            <button className="btn join-item">Prepare Jobs+</button>
          </NavLink>
          <NavLink to="/admin/settings">
            <button className="btn join-item">Settings</button>
          </NavLink>
        </div>
      ) : (
        <h1 className="text-2xl text-neutral-100 uppercase">{headerTitle}</h1>
      )}
    </header>
  );
};

export default Header;
