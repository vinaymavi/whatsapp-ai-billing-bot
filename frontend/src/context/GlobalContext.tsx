import { createContext, useState, type FC, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

export interface ContextData {
  headerTitle: string;
  setHeaderTitle: (title: string) => void;
  isLogin: boolean;
  setIsLogin: (status: boolean) => void;
}

export const Context = createContext<Partial<ContextData>>({});

export const GlobalContext: FC<Props> = ({ children }: Props) => {
  const [headerTitle, setHeaderTitle] = useState<string>("");
  const [isLogin, setIsLogin] = useState<boolean>(false);

  const contextData = {
    headerTitle,
    setHeaderTitle,
    isLogin,
    setIsLogin,
  };

  return <Context.Provider value={contextData}>{children}</Context.Provider>;
};
