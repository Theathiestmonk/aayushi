# Diet Plan Cleanup Functionality

## Overview

This document describes the new diet plan cleanup functionality that automatically removes old diet plans when creating new ones, preventing duplicate entries in the database.

## Problem Solved

Previously, when users generated new diet plans, old plans would remain in the database, leading to:
- Multiple 30-day plans for the same user
- Confusion about which plan is current
- Unnecessary database storage
- Potential conflicts in meal tracking

## Solution

The system now automatically cleans up existing diet plans before creating new ones using a three-tier approach:

1. **Primary**: Force clear ALL existing data (nuclear option)
2. **Fallback**: Regular deletion if force clear fails
3. **Last Resort**: Archiving if deletion fails

## Implementation Details

### 1. Automatic Cleanup in Diet Planner Agent

The `DietPlannerAgent` now automatically cleans up existing diet plans before creating new ones:

```python
# Clean up existing diet plans before creating new ones
# Use the nuclear option to ensure ALL data is completely cleared
force_clear_result = await supabase_manager.force_clear_all_user_data(user_id)

if force_clear_result["success"]:
    deleted_plans = force_clear_result.get("deleted_plans", 0)
    deleted_daily_plans = force_clear_result.get("deleted_daily_plans", 0)
    deleted_meals = force_clear_result.get("deleted_meals", 0)
    deleted_food_items = force_clear_result.get("deleted_food_items", 0)
    logger.info(f"✅ Force cleared {deleted_plans} diet plans, {deleted_daily_plans} daily plans, {deleted_meals} meals, {deleted_food_items} food items")
else:
    # Try regular deletion as fallback
    delete_result = await supabase_manager.delete_all_user_diet_plans(user_id)
```

### 2. New Supabase Manager Methods

#### `force_clear_all_user_data(user_id)`
- **Nuclear option**: Completely removes ALL diet-related data for a user
- Manually deletes diet_plans, daily_plans, meals, and food_items
- Ensures no data remains in the database
- Returns detailed counts of deleted records

#### `delete_all_user_diet_plans(user_id)`
- Deletes all diet plans for a user
- Uses cascade deletion for related records (daily_plans, meals, food_items)
- Returns count of deleted plans

#### `archive_user_diet_plans(user_id)`
- Changes status of active diet plans to 'completed'
- Preserves data for historical analysis
- Returns count of archived plans

#### `verify_user_data_cleared(user_id)`
- Verifies that all diet-related data has been completely cleared
- Returns counts of any remaining records
- Useful for confirming cleanup success

#### `has_existing_diet_plans(user_id)`
- Checks if user has any existing diet plans
- Returns boolean result

#### `get_diet_plan_count(user_id)`
- Returns count of existing diet plans
- Useful for frontend warnings

#### `delete_diet_plan(plan_id)`
- Deletes a specific diet plan by ID
- Used by the delete API endpoint

### 3. New API Endpoints

#### `GET /diet-plans/check-existing`
- Check if user has existing diet plans
- Returns boolean result

#### `GET /diet-plans/count`
- Get count of user's diet plans
- Returns numeric count

#### `POST /diet-plans/force-clear`
- **Nuclear option**: Force clear ALL diet data for a user
- Completely removes all plans, daily plans, meals, and food items
- Use with caution - this is irreversible

#### `POST /diet-plans/archive-existing`
- Manually archive existing diet plans
- Useful for frontend-initiated cleanup

#### `GET /diet-plans/verify-clear`
- Verify that all diet data has been cleared
- Returns counts of any remaining records

#### `DELETE /diet-plans/{plan_id}`
- Delete a specific diet plan
- Now fully implemented (was placeholder)

## Database Schema Changes

No schema changes required. The existing `status` field in the `diet_plans` table is used for archiving:

- `active`: Current diet plan
- `completed`: Archived diet plan
- `paused`: Paused diet plan

## Usage Examples

### Frontend Integration

```typescript
// Check if user has existing plans before generating new ones
const checkResult = await api.get('/diet-plans/check-existing');
if (checkResult.has_existing_plans) {
  // Show warning about replacing existing plan
  const confirmed = await showConfirmationDialog(
    "You already have a diet plan. Generating a new one will replace it. Continue?"
  );
  if (!confirmed) return;
}

// Generate new diet plan (cleanup happens automatically)
const result = await api.post('/diet-plans/generate', requestData);
```

### Manual Cleanup

```typescript
// Manually archive existing plans
await api.post('/diet-plans/archive-existing');

// Check plan count
const countResult = await api.get('/diet-plans/count');
console.log(`User has ${countResult.count} diet plans`);
```

## Benefits

1. **Guaranteed Clean Slate**: Users always start with completely fresh data
2. **No More Duplicates**: Users always have only one active diet plan
3. **Complete Data Removal**: All old data is completely cleared from Supabase
4. **Automatic Cleanup**: No manual intervention required
5. **Multiple Fallback Strategies**: Three-tier cleanup approach ensures success
6. **Verification**: Can verify that data has been completely cleared
7. **Frontend Control**: APIs for manual cleanup when needed

## Testing

Run the test script to verify functionality:

```bash
cd backend
python test_diet_plan_cleanup.py
```

## Error Handling

The system gracefully handles cleanup failures:

- If archiving fails, falls back to deletion
- If both fail, continues with plan creation
- Logs all cleanup attempts for debugging
- Returns detailed error messages

## Monitoring

Monitor cleanup operations through logs:

```
🧹 Cleaning up existing diet plans for user: user-123
💥 Force clearing ALL existing diet data to ensure completely clean slate...
💥 Force clearing ALL diet data for user: user-123
🗑️ Force deleting diet plan: plan-123
   🗑️ Deleted 30 daily plans for diet plan: plan-123
   🗑️ Deleted 90 meals for daily plan: daily-456
   🗑️ Deleted 450 food items for meal: meal-789
✅ Successfully deleted diet plan: plan-123
💥 Force clear completed for user: user-123
   - Deleted 2 diet plans
   - Deleted 60 daily plans
   - Deleted 180 meals
   - Deleted 900 food items
✅ Force cleared 2 diet plans, 60 daily plans, 180 meals, 900 food items
✅ Diet plan created with ID: plan-456
```

## Future Enhancements

1. **Configurable Cleanup Strategy**: Allow users to choose between archiving and deletion
2. **Retention Policies**: Automatically delete very old archived plans
3. **Bulk Operations**: API endpoints for bulk cleanup operations
4. **Audit Trail**: Track all cleanup operations for compliance

## Security Considerations

- All cleanup operations respect Row Level Security (RLS)
- Users can only clean up their own diet plans
- Service role key bypasses RLS for backend operations
- All operations are logged for audit purposes
