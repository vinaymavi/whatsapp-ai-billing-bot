import { Context } from "@/context/GlobalContext";
import { isValidLoginSession } from "@/util";
import { useContext, useEffect, type FC } from "react";
import { Outlet, useNavigate } from "react-router";

export const AuthLayout: FC<{}> = () => {
  const navigation = useNavigate();
  const { setIsLogin } = useContext(Context);
  useEffect(() => {
    if (!isValidLoginSession()) {
      navigation("/?logout=true");
    }
    setIsLogin?.(true);
  }, []);

  return (
    <>
      <Outlet />
    </>
  );
};
