export function isValidLoginSession(): boolean {
  const token = localStorage.getItem("access_token");
  // Here, you can add more checks like token expiration if needed
  return token !== null;
}
