import { useEffect } from "react";
import { Context } from "@/context/GlobalContext";
import { useContext } from "react";

export function Dashboard() {
  const { setHeaderTitle } = useContext(Context);
  useEffect(() => {
    setHeaderTitle?.("Admin Dashboard");
  }, [setHeaderTitle]);
  return (
    <div>
      <h1>Dashboard</h1>
    </div>
  );
}
