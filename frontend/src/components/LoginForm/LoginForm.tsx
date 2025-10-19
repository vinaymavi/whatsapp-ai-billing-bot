import { useState, type FC } from "react";

import {httpClient} from '@/httpClient';
interface props {
  title: string;
  desc: string;
  inputPlaceholder: string;
  buttonLabel: string;
}

const countryCodes = [
  { code: "+1", country: "USA/Canada", value: "1" },  
  { code: "+91", country: "India", value: "91" },  
];

export const LoginForm: FC<props> = ({
  buttonLabel,
  desc,
  inputPlaceholder,
  title,
}) => {
  const [phone, setPhone] = useState<string>("");
  const [otp, setOtp] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [touched, setTouched] = useState<boolean>(false);
  const [selectedCountry, setSelectedCountry] = useState<any>(countryCodes[0]);
  const [formStep, setFormStep] = useState<"phone" | "otp" | 'optverified'>("phone");

  // Basic E.164-like validation: optional leading +, country code cannot start with 0,
  // total digits between 8 and 15. This is intentionally simple and avoids adding
  // an external lib; replace with libphonenumber if stricter validation is needed.
  const validatePhoneNumber = (value: string) => {
    const cleaned = value.replace(/\s+/g, "");
    const re = /^\+?[1-9]\d{7,14}$/;
    return re.test(cleaned);
  };

  const generateOtp = async (phoneNumber: string) => {
    await httpClient.otp({phone_number: `${selectedCountry.value}${phoneNumber}`});
    setFormStep("otp");
  }


  const validateOtp = async (phoneNumber: string, otp: string) => {
    await httpClient.verifyOtp({phone_number: `${selectedCountry.value}${phoneNumber}`, otp});
    setFormStep("optverified");
  }
  

      
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
        <form
          role="form"
          className="flex flex-col items-center pt-4"
          action=""
          onSubmit={(e) => {
            e.preventDefault();
            setTouched(true);
            if (!validatePhoneNumber(phone)) {
              setError(
                "Please enter a valid phone number including country code (e.g. +1234567890)"
              );
              return;
            }

            if(formStep==="phone"){
              generateOtp(phone);
            } else if(formStep==="otp"){
              validateOtp(phone, otp);
            }
          }}
        >
          <div className="join">
            <div className="join-item">
              <details className="dropdown">
                <summary className="btn m-1"> {selectedCountry.country} ({selectedCountry.code})</summary>
                <ul className="menu dropdown-content bg-base-100 rounded-box z-1 w-52 p-2 shadow-sm">
                  {countryCodes.map((cc) => (
                    <li key={cc.code}>
                      <a
                        onClick={() => setSelectedCountry(cc)}
                      >
                        {cc.country} ({cc.code})
                      </a>
                    </li>
                  ))}
                </ul>
              </details>
            </div>
            <div className="join-item">
              <input
                className="input"
                id="mobile-num"
                name="mobile"
                type="tel"
                inputMode="tel"
                disabled={formStep !== "phone"}
                placeholder={inputPlaceholder}
                value={phone}
                aria-invalid={!!error}
                aria-describedby={error ? "mobile-num-error" : undefined}
                onChange={(e) => {
                  const v = e.target.value;
                  setPhone(v);
                  if (touched) {
                    if (!v) setError("Phone number is required");
                    else if (!validatePhoneNumber(v))
                      setError("Invalid phone number");
                    else setError(null);
                  }
                }}
                onBlur={() => {
                  setTouched(true);
                  if (!phone) setError("Phone number is required");
                  else if (!validatePhoneNumber(phone))
                    setError("Invalid phone number");
                  else setError(null);
                }}
              />

              {error && (
                <div
                  id="mobile-num-error"
                  className="text-sm text-red-600 mt-2"
                  role="alert"
                >
                  {error}
                </div>
              )}
            </div>
          </div>
           <input type='number' className="input mt-4" placeholder="Enter OTP" disabled={formStep !== "otp"} value={otp} onChange={(e)=>setOtp(e.target.value)}  />
          <button
            type="submit"
            className="btn mt-2 bg-teal-800 text-white hover:bg-teal-700 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={!phone || !!error}
          >
            {buttonLabel}
          </button>
        </form>
      </div>
    </>
  );
};
