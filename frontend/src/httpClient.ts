export class HttpClient {
  private static instance: HttpClient;
  private static httpServer: string = import.meta.env.VITE_API_SERVER;

  private constructor() {
    if (!HttpClient.httpServer) {
      throw new Error(
        "API server URL is not defined in environment variables."
      );
    }
  }

  public static getInstance(): HttpClient {
    if (!HttpClient.instance) {
      HttpClient.instance = new HttpClient();
    }
    return HttpClient.instance;
  }

  private async get(
    url: string,
    headers: Record<string, string> = {}
  ): Promise<any> {
    const fetchOptions: RequestInit = {
      method: "GET",
      headers: { ...headers },
    };

    const resp = await fetch(`${HttpClient.httpServer}${url}`, fetchOptions);
    return await resp.json();
  }
  private async post(
    url: string,
    data: any,
    headers: Record<string, string> = {}
  ): Promise<any> {
    const isFormData =
      typeof FormData !== "undefined" && data instanceof FormData;
    const fetchOptions: RequestInit = {
      method: "POST",
      // When sending FormData, don't set Content-Type; the browser will add the correct
      // multipart/form-data boundary. For JSON, set Content-Type and stringify the body.
      headers: isFormData
        ? { ...headers }
        : { "Content-Type": "application/json", ...headers },
      body: isFormData ? data : JSON.stringify(data),
    };

    const resp = await fetch(`${HttpClient.httpServer}${url}`, fetchOptions);
    return await resp.json();
  }

  public async otp(data: { phone_number: string }): Promise<any> {
    const respData = await this.post("/api/admin/otp", data);
    return respData;
  }

  private async setAccessTokenTOLocalStorage(token: string): Promise<void> {
    localStorage.setItem("access_token", token);
  }

  public async verifyOtp(data: {
    phone_number: string;
    otp: string;
  }): Promise<any> {
    const form = new FormData();
    form.append("username", data.phone_number);
    form.append("password", data.otp);

    const respData = await this.post("/api/admin/token", form);
    this.setAccessTokenTOLocalStorage(respData.access_token);
    alert("OTP verified successfully!");
    return respData;
  }

  public async getRuns(): Promise<any> {
    const token = localStorage.getItem("access_token");
    if (!token) {
      throw new Error("Access token not found. Please log in.");
    }

    const headers = {
      Authorization: `Bearer ${token}`,
    };

    const respData = await this.get("/api/admin/runs", headers);
    return respData;
  }
}

export const httpClient = HttpClient.getInstance();
