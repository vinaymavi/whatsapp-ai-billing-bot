import { isValidLoginSession } from "@/util";
import { useEffect, type FC } from "react";
import { Outlet, useNavigate } from "react-router";

export const AuthLayout:FC<{}> = ()=>{
    const navigation = useNavigate();
    
    useEffect(()=>{
        if(!isValidLoginSession()){
            navigation('/?logout=true');
        }
    },[]);


    return(<>
    <Outlet/>
    </>
    )
}