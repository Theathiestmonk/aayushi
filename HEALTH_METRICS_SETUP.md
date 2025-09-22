# Health Metrics Integration Setup

This document explains how to set up and use the new health metrics tracking feature that connects the frontend dashboard with the backend database.

## Overview

The health metrics feature allows users to track:
- **Steps**: Daily step count with goal tracking
- **Sleep**: Hours of sleep with quality rating
- **Water Intake**: Daily water consumption in liters
- **Calories**: Calories eaten and burned
- **Macronutrients**: Carbs, protein, and fat tracking
- **Weight**: Current and target weight tracking

## Database Setup

### 1. Create the Database Table

Run the SQL script to create the `daily_health_metrics` table:

```bash
# Connect to your Supabase database and run:
psql -h your-supabase-host -U postgres -d postgres -f daily_health_metrics.sql
```

Or copy and paste the contents of `daily_health_metrics.sql` into your Supabase SQL editor.

### 2. Verify Table Creation

The table should include:
- User-specific data with RLS (Row Level Security)
- Daily tracking with unique constraints
- Comprehensive health metrics fields
- Automatic timestamp updates

## Backend API Endpoints

### Available Endpoints

1. **GET /api/v1/tracking/health-metrics**
   - Fetch today's health metrics for the current user
   - Returns default values if no data exists

2. **POST /api/v1/tracking/health-metrics**
   - Create or update health metrics for the current user
   - Supports partial updates

3. **GET /api/v1/tracking/health-metrics/history**
   - Fetch historical health metrics
   - Supports date range filtering and pagination

### Example API Usage

```javascript
// Fetch today's metrics
const response = await fetch('/api/v1/tracking/health-metrics', {
  headers: {
    'Authorization': `Bearer ${token}`,
  },
});

// Update steps
const updateResponse = await fetch('/api/v1/tracking/health-metrics', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    steps_today: 8500,
    water_intake_l: 1.8
  }),
});
```

## Frontend Integration

### Dashboard Updates

The dashboard now:
- Fetches real data from the API instead of using mock data
- Displays actual values from the database
- Includes interactive buttons to update metrics
- Falls back to mock data if API fails

### Interactive Features

Users can now:
- Click "+1K" to add 1000 steps
- Click "+0.5h" to add 30 minutes of sleep
- Click "+250ml" to add 250ml of water intake

### Data Flow

1. Dashboard loads → Fetches user profile
2. Dashboard loads → Fetches health metrics from API
3. User interacts → Updates metrics via API
4. Local state updates → UI reflects changes

## Testing

### Backend Testing

Run the test script to verify API endpoints:

```bash
cd backend
python test_health_metrics.py
```

Make sure to update the `TEST_USER_TOKEN` in the script with a valid authentication token.

### Frontend Testing

1. Start the frontend development server
2. Login with a valid user account
3. Navigate to the dashboard
4. Verify that real data is displayed
5. Test the interactive buttons to update metrics

## Configuration

### Environment Variables

Ensure these are set in your backend environment:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

### Database Permissions

The table uses Row Level Security (RLS) to ensure users can only access their own data. Make sure your Supabase project has RLS enabled.

## Troubleshooting

### Common Issues

1. **API Not Found (404)**
   - Ensure the tracking router is enabled in `api.py`
   - Check that the backend server is running

2. **Authentication Errors (401)**
   - Verify the user token is valid
   - Check that the user is properly authenticated

3. **Database Connection Errors (500)**
   - Verify Supabase credentials are correct
   - Check that the `daily_health_metrics` table exists

4. **Frontend Not Updating**
   - Check browser console for errors
   - Verify API responses are successful
   - Ensure the `updateHealthMetrics` function is working

### Debug Steps

1. Check backend logs for API errors
2. Verify database table structure
3. Test API endpoints with Postman or curl
4. Check frontend network tab for failed requests
5. Verify authentication tokens are valid

## Future Enhancements

Potential improvements:
- Real-time updates using WebSockets
- Data visualization charts
- Goal setting and achievement tracking
- Integration with fitness devices
- Mobile app support
- Data export functionality

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the API documentation
3. Check the backend logs
4. Verify database permissions and structure

