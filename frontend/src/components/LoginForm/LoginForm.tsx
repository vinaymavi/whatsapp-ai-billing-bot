import type { FC } from "react";
interface props {
  title: string;
  desc: string;
  inputPlaceholder: string;
  buttonLabel: string;
}
export const LoginForm: FC<props> = ({
  buttonLabel,
  desc,  
  inputPlaceholder,
  title,
}) => {
  return (    
    <>
    <style>
        {`
          @keyframes shadowPulse {
            0%, 100% { box-shadow: 0 25px 50px -12px rgba(20, 184, 166, 0.25); }
            50% { box-shadow: 0 35px 60px -12px rgba(20, 184, 166, 0.5); }
          }
          .shadow-pulse {
            animation: shadowPulse 2s ease-in-out infinite;
          }
        `}
      </style>
      <div className="flex max-w-2xl text-gray-800 items-center flex-col p-7 shadow-2xl shadow-teal-600 shadow-pulse">
        <h1 className="text-3xl pt-4">{title}</h1>
        <h5 className="text-l pt-0">{desc}</h5>
        <form role="form" className="flex flex-col items-center pt-4" action="" onSubmit={(e)=>{
            e.preventDefault();            
        }}>            
            <input className="input" id="mobile-num" type="text" placeholder={inputPlaceholder}/>
            <button type="submit" className="btn  mt-2 bg-teal-800 text-white hover:bg-teal-700">{buttonLabel}</button>
        </form>
      </div>
    </>
  );
};