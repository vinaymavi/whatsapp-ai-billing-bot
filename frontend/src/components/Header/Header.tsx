import { Context } from "@/context/GlobalContext";
import { useContext, type FC } from "react";

export const Header: FC<{}> = () => {
  const { headerTitle } = useContext(Context);
  
  return (
    <header className="flex items-center justify-center bg-emerald-800  p-4 w-full">
      <h1 className="text-2xl text-neutral-100 uppercase">
        {headerTitle}
      </h1>
    </header>
  );
};

export default Header;
