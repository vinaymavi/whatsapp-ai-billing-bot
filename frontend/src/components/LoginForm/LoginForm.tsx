import { useState, type FC } from "react";
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
  const [phone, setPhone] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [touched, setTouched] = useState<boolean>(false);

  // Basic E.164-like validation: optional leading +, country code cannot start with 0,
  // total digits between 8 and 15. This is intentionally simple and avoids adding
  // an external lib; replace with libphonenumber if stricter validation is needed.
  const validatePhoneNumber = (value: string) => {
    const cleaned = value.replace(/\s+/g, "");
    const re = /^\+?[1-9]\d{7,14}$/;
    return re.test(cleaned);
  };
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
              setError("Please enter a valid phone number including country code (e.g. +1234567890)");
              return;
            }

            // Phone is valid — proceed with whatever the parent should do next.
            // For now we simply log it; replace with a callback prop if needed.
            console.log("Submitting phone:", phone);
          }}
        >
          <input
            className="input"
            id="mobile-num"
            name="mobile"
            type="tel"
            inputMode="tel"
            placeholder={inputPlaceholder}
            value={phone}
            aria-invalid={!!error}
            aria-describedby={error ? "mobile-num-error" : undefined}
            onChange={(e) => {
              const v = e.target.value;
              setPhone(v);
              if (touched) {
                if (!v) setError("Phone number is required");
                else if (!validatePhoneNumber(v)) setError("Invalid phone number");
                else setError(null);
              }
            }}
            onBlur={() => {
              setTouched(true);
              if (!phone) setError("Phone number is required");
              else if (!validatePhoneNumber(phone)) setError("Invalid phone number");
              else setError(null);
            }}
          />

          {error && (
            <div id="mobile-num-error" className="text-sm text-red-600 mt-2" role="alert">
              {error}
            </div>
          )}

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