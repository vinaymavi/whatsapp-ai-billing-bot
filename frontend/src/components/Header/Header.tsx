import type { FC } from "react";

export const Header: FC<{ title: string }> = ({ title }) => {
    return (
        <header className="flex items-center justify-center bg-emerald-800  p-4 w-full">
            <h1 className="text-2xl text-neutral-100 uppercase">{title}</h1>
        </header>
    );
};


export default Header;