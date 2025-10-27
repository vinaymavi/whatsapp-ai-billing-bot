# Update file

curl -X POST \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiU3VwZXIgQWRtaW4iLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NjE2NTY4ODR9.8yTazwqvPw_1OyJTIn1iObeShmJSXaWS9wTjrYBTu0U" \
  -F "file=@1D99A-89B85-A71BD-BA2B5.pdf" \
  http://localhost:8000/api/admin/batch
