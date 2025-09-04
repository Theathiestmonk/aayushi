# Frontend-Backend Integration Troubleshooting Guide

## 🚨 Common Error: "Profile data not found" despite 200 OK API response

### Problem Description
- **Symptom**: Frontend displays error message "Profile data not found" or "Error Loading Profile"
- **API Status**: Backend returns 200 OK with data
- **Root Cause**: Data structure mismatch between frontend expectations and backend response

---

## 🔍 Step-by-Step Debugging Process

### Step 1: Check Network Tab
1. Open Chrome DevTools (F12)
2. Go to Network tab
3. Filter by "Fetch/XHR"
4. Look for your API call (e.g., `/api/v1/onboarding/profile`)
5. Check if status is 200 OK
6. Click on the request to see response body

**Expected Result**: Status 200, response contains data
**If Not**: Backend issue - check server logs

### Step 2: Analyze Frontend Code
Look for how the frontend processes the API response:

```typescript
// Example from Profile.tsx
const response = await fetch('/api/v1/onboarding/profile', {
  headers: { 'Authorization': `Bearer ${token}` }
});

const data = await response.json();
if (data.success && data.data.profile) {  // ← Check this condition
  setProfile(data.data.profile);
} else {
  throw new Error('Profile data not found');
}
```

**Key Questions**:
- What structure does the frontend expect?
- Is it looking for `data.data.profile` or `data.data`?
- Are field names matching exactly?

### Step 3: Compare Data Structures

#### Frontend Expects:
```json
{
  "success": true,
  "data": {
    "profile": {
      "id": "user-123",
      "full_name": "Amit Tiwari",
      "age": 28,
      "height_cm": 175.0,
      "weight_kg": 70.0
      // ... more fields
    }
  }
}
```

#### Backend Returns (Wrong):
```json
{
  "success": true,
  "data": {
    "id": "user-123",
    "full_name": "Amit Tiwari",
    "age": 28,
    "height_cm": 175.0,
    "weight_kg": 70.0
    // ... more fields (missing 'profile' wrapper)
  }
}
```

### Step 4: Fix Backend Response Structure

```python
# WRONG - Direct data return
@app.get("/api/v1/onboarding/profile")
async def get_onboarding_profile():
    return {
        "success": True,
        "data": {
            "id": "user-123",
            "full_name": "Amit Tiwari",
            # ... profile fields directly
        }
    }

# CORRECT - Nested profile object
@app.get("/api/v1/onboarding/profile")
async def get_onboarding_profile():
    return {
        "success": True,
        "data": {
            "profile": {  # ← Add this wrapper
                "id": "user-123",
                "full_name": "Amit Tiwari",
                # ... profile fields
            }
        }
    }
```

---

## 🛠️ Common Fixes

### Fix 1: Data Structure Mismatch
**Problem**: Frontend expects nested object, backend returns flat object
**Solution**: Wrap data in expected structure

```python
# Before
return {"success": True, "data": profile_data}

# After
return {"success": True, "data": {"profile": profile_data}}
```

### Fix 2: Field Name Mismatches
**Problem**: Frontend expects `height_cm` but backend returns `height`
**Solution**: Match exact field names

```python
# Before
"height": 175

# After
"height_cm": 175.0
```

### Fix 3: Data Type Mismatches
**Problem**: Frontend expects number but backend returns string
**Solution**: Ensure correct data types

```python
# Before
"age": "28"  # String

# After
"age": 28    # Number
```

### Fix 4: Missing Required Fields
**Problem**: Frontend expects fields that don't exist in response
**Solution**: Add all required fields with appropriate defaults

```python
# Add missing fields
"onboarding_completed": True,
"created_at": "2024-01-01T00:00:00Z",
"updated_at": "2024-01-01T00:00:00Z"
```

---

## 🧪 Testing Your Fix

### 1. Test API Directly
```bash
curl -X GET http://localhost:8000/api/v1/onboarding/profile
```

### 2. Test with Python
```python
import requests
response = requests.get('http://localhost:8000/api/v1/onboarding/profile')
print('Status:', response.status_code)
data = response.json()
print('Success:', data['success'])
print('Has profile:', 'profile' in data['data'])
```

### 3. Check Frontend Console
- Open DevTools Console
- Look for JavaScript errors
- Check if data is being processed correctly

---

## 📋 Checklist for Frontend-Backend Integration

### Backend Checklist
- [ ] API endpoint returns 200 OK
- [ ] Response has correct structure (`data.profile` vs `data`)
- [ ] All required fields are present
- [ ] Field names match frontend expectations
- [ ] Data types are correct (numbers, strings, arrays)
- [ ] No syntax errors in code
- [ ] Server is running and accessible

### Frontend Checklist
- [ ] API call URL is correct
- [ ] Headers are properly set (Authorization, Content-Type)
- [ ] Response processing logic matches backend structure
- [ ] Error handling is implemented
- [ ] Loading states are managed
- [ ] No JavaScript errors in console

---

## 🚀 Prevention Tips

### 1. Use TypeScript Interfaces
```typescript
interface ApiResponse {
  success: boolean;
  data: {
    profile: UserProfile;
  };
}

interface UserProfile {
  id: string;
  full_name: string;
  age: number;
  height_cm: number;
  weight_kg: number;
  // ... other fields
}
```

### 2. Document API Contracts
Create clear documentation of expected request/response formats.

### 3. Use API Testing Tools
- Postman for manual testing
- Jest/Testing Library for automated tests
- Swagger/OpenAPI for documentation

### 4. Implement Proper Error Handling
```typescript
try {
  const response = await fetch('/api/v1/onboarding/profile');
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  const data = await response.json();
  if (!data.success || !data.data?.profile) {
    throw new Error('Invalid response structure');
  }
  setProfile(data.data.profile);
} catch (error) {
  console.error('Profile fetch error:', error);
  setError(error.message);
}
```

---

## 🔧 Quick Debug Commands

### Check if server is running
```bash
netstat -an | findstr :8000
```

### Test API endpoint
```bash
curl -X GET http://localhost:8000/api/v1/onboarding/profile
```

### Check server logs
```bash
# Look at terminal where server is running
# Check for error messages
```

### Restart server
```bash
# Stop server (Ctrl+C)
# Start server
python main.py
```

---

## 📞 When to Ask for Help

1. **API returns 500 error** - Backend server issue
2. **API returns 404 error** - Endpoint doesn't exist
3. **CORS errors** - Cross-origin request blocked
4. **Authentication errors** - Token/authorization issues
5. **Data structure still wrong** - Need to compare frontend/backend code

---

## 🎯 Summary

The most common cause of "Profile data not found" with 200 OK response is a **data structure mismatch**. The frontend expects data in a specific format, but the backend returns it differently. Always:

1. Check the Network tab first
2. Compare frontend expectations with backend response
3. Ensure exact field name and structure matches
4. Test API endpoints directly
5. Use proper error handling and logging

Remember: **The API can return 200 OK but still have the wrong data structure!**
