export class HttpClient {
    private static instance: HttpClient;
    private static httpServer: string = import.meta.env.VITE_API_SERVER
    
    private constructor() {
        if(!HttpClient.httpServer){
            throw new Error("API server URL is not defined in environment variables.");
        }
     }

    public static getInstance(): HttpClient {
        if (!HttpClient.instance) {
            HttpClient.instance = new HttpClient();
        }
        return HttpClient.instance;
    }

    private async post(url: string, data: any, headers: Record<string, string> = {}): Promise<any> {
        const isFormData = typeof FormData !== 'undefined' && data instanceof FormData;
        const fetchOptions: RequestInit = {
            method: 'POST',
            // When sending FormData, don't set Content-Type; the browser will add the correct
            // multipart/form-data boundary. For JSON, set Content-Type and stringify the body.
            headers: isFormData ? { ...headers } : { 'Content-Type': 'application/json', ...headers },
            body: isFormData ? data : JSON.stringify(data),
        };

        return fetch(`${HttpClient.httpServer}${url}`, fetchOptions)
            .then((resp) => resp.json())
            .then((data) => data)
            .catch((error) => {
                console.error('HTTP POST Error:', error);
                throw error;
            });
    }

    public async otp(data: { phone_number: string }): Promise<any> {
        const respData = await this.post('/api/admin/otp', data);
        return respData;
    }

    public async verifyOtp(data: { phone_number: string; otp: string }): Promise<any> {
        const form = new FormData();
        form.append('username', data.phone_number);
        form.append('password', data.otp);

        const respData = await this.post('/api/admin/token', form);
        return respData;
    }
}

export const httpClient = HttpClient.getInstance();

