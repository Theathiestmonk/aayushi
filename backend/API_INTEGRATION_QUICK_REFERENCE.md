# API Integration Quick Reference Guide

## 🚨 Quick Fixes for Common Issues

### Issue: "Profile data not found" with 200 OK
**Root Cause**: Data structure mismatch
**Quick Fix**: 
```python
# Change this:
return {"success": True, "data": profile_data}

# To this:
return {"success": True, "data": {"profile": profile_data}}
```

### Issue: 404 Not Found
**Root Cause**: Endpoint doesn't exist
**Quick Fix**: Add missing endpoint
```python
@app.get("/api/v1/your-endpoint")
async def your_function():
    return {"success": True, "data": your_data}
```

### Issue: CORS Error
**Root Cause**: Cross-origin request blocked
**Quick Fix**: Check CORS configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: 500 Internal Server Error
**Root Cause**: Server-side error
**Quick Fix**: Check server logs and fix syntax errors

---

## 🔍 Debugging Checklist

### 1. Check Network Tab
- [ ] Status is 200 OK
- [ ] Response contains expected data
- [ ] No CORS errors

### 2. Check Frontend Code
- [ ] API URL is correct
- [ ] Headers are set properly
- [ ] Data structure matches backend response

### 3. Check Backend Code
- [ ] Endpoint exists and is accessible
- [ ] Response structure matches frontend expectations
- [ ] No syntax errors
- [ ] Server is running

---

## 🛠️ Common Data Structure Fixes

### Frontend expects nested object
```python
# Wrong
{"success": True, "data": {"id": "123", "name": "John"}}

# Right
{"success": True, "data": {"profile": {"id": "123", "name": "John"}}}
```

### Field name mismatches
```python
# Wrong
{"height": 175, "weight": 70}

# Right
{"height_cm": 175.0, "weight_kg": 70.0}
```

### Data type mismatches
```python
# Wrong
{"age": "28", "bmi": "22.5"}

# Right
{"age": 28, "bmi": 22.5}
```

---

## 🧪 Testing Commands

### Test API endpoint
```bash
curl -X GET http://localhost:8000/api/v1/your-endpoint
```

### Test with Python
```python
import requests
response = requests.get('http://localhost:8000/api/v1/your-endpoint')
print(response.json())
```

### Check server status
```bash
netstat -an | findstr :8000
```

---

## 📋 Common Endpoints Template

```python
# Authentication
@app.post("/api/v1/auth/login")
async def login(request_data: dict):
    return {"success": True, "data": {"user_id": "123", "token": "abc"}}

# Profile
@app.get("/api/v1/profile")
async def get_profile():
    return {"success": True, "data": {"profile": profile_data}}

# Dashboard
@app.get("/api/v1/dashboard/metrics")
async def get_metrics():
    return {"success": True, "data": {"metrics": metrics_data}}

# Onboarding
@app.get("/api/v1/onboarding/status")
async def get_status():
    return {"success": True, "data": {"status": "completed"}}
```

---

## 🚀 Best Practices

1. **Always return consistent structure**:
   ```python
   return {"success": True, "message": "Success", "data": your_data}
   ```

2. **Use proper HTTP status codes**:
   - 200: Success
   - 400: Bad Request
   - 401: Unauthorized
   - 404: Not Found
   - 500: Internal Server Error

3. **Include error handling**:
   ```python
   try:
       # Your code
       return {"success": True, "data": result}
   except Exception as e:
       return {"success": False, "error": str(e)}
   ```

4. **Test endpoints before frontend integration**

5. **Use TypeScript interfaces for type safety**

---

## 📞 Emergency Fixes

### Server won't start
```bash
# Check for syntax errors
python -m py_compile main.py

# Kill existing processes
taskkill /f /im python.exe

# Restart server
python main.py
```

### Frontend shows old data
1. Hard refresh browser (Ctrl+F5)
2. Clear browser cache
3. Check if server restarted properly

### API returns wrong data
1. Check if you're hitting the right endpoint
2. Verify server logs
3. Test endpoint directly with curl/Postman

---

## 🎯 Remember

- **200 OK doesn't mean correct data structure**
- **Always check Network tab first**
- **Compare frontend expectations with backend response**
- **Test API endpoints directly**
- **Use consistent data structures**
