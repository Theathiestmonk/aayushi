-- Comprehensive User Profile Schema for AI Dietitian System
-- This table stores sensitive health and personal information
-- Access is restricted through Row Level Security (RLS)

-- Create the profiles table with all onboarding fields
CREATE TABLE IF NOT EXISTS user_profiles (
    -- Core identification (linked to auth.users)
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Basic Information
    full_name TEXT NOT NULL,
    age INTEGER CHECK (age > 0 AND age < 150),
    gender TEXT CHECK (gender IN ('male', 'female', 'other')),
    height_cm DECIMAL(5,2) CHECK (height_cm > 0 AND height_cm < 300),
    weight_kg DECIMAL(5,2) CHECK (weight_kg > 0 AND weight_kg < 500),
    contact_number TEXT,
    email TEXT NOT NULL,
    emergency_contact_name TEXT,
    emergency_contact_number TEXT,
    occupation TEXT CHECK (occupation IN ('student', 'professional', 'homemaker', 'retired', 'other')),
    occupation_other TEXT,
    
    -- Medical & Health History
    medical_conditions JSONB DEFAULT '[]', -- Array of conditions
    medications_supplements JSONB DEFAULT '[]', -- Array of medications
    surgeries_hospitalizations TEXT,
    food_allergies JSONB DEFAULT '[]', -- Array of allergies
    family_history JSONB DEFAULT '[]', -- Array of family conditions
    
    -- Lifestyle & Habits
    daily_routine TEXT CHECK (daily_routine IN ('sedentary', 'moderately_active', 'highly_active')),
    sleep_hours TEXT CHECK (sleep_hours IN ('<5', '5-6', '7-8', '>8')),
    alcohol_consumption BOOLEAN DEFAULT FALSE,
    alcohol_frequency TEXT,
    smoking BOOLEAN DEFAULT FALSE,
    stress_level TEXT CHECK (stress_level IN ('low', 'moderate', 'high')),
    physical_activity_type TEXT,
    physical_activity_frequency TEXT,
    physical_activity_duration TEXT,
    
    -- Eating Habits
    breakfast_habits TEXT,
    lunch_habits TEXT,
    dinner_habits TEXT,
    snacks_habits TEXT,
    beverages_habits TEXT,
    meal_timings TEXT CHECK (meal_timings IN ('regular', 'irregular')),
    food_preference TEXT CHECK (food_preference IN ('vegetarian', 'vegan', 'non_vegetarian', 'eggetarian')),
    cultural_restrictions TEXT,
    eating_out_frequency TEXT CHECK (eating_out_frequency IN ('rare', 'weekly', '2-3_times_week', 'daily')),
    daily_water_intake TEXT CHECK (daily_water_intake IN ('<1L', '1-2L', '2-3L', '>3L')),
    common_cravings JSONB DEFAULT '[]', -- Array of cravings
    
    -- Goals & Expectations
    primary_goals JSONB DEFAULT '[]', -- Array of goals
    specific_health_concerns TEXT,
    past_diets TEXT,
    progress_pace TEXT CHECK (progress_pace IN ('gradual', 'moderate', 'aggressive')),
    
    -- Measurements & Tracking
    current_weight_kg DECIMAL(5,2) CHECK (current_weight_kg > 0 AND current_weight_kg < 500),
    waist_circumference_cm DECIMAL(5,2) CHECK (waist_circumference_cm > 0 AND waist_circumference_cm < 200),
    bmi DECIMAL(4,2) CHECK (bmi > 0 AND bmi < 100),
    weight_trend TEXT CHECK (weight_trend IN ('increased', 'decreased', 'stable')),
    blood_reports JSONB DEFAULT '[]', -- Array of available reports
    
    -- Personalization & Motivation
    loved_foods TEXT,
    disliked_foods TEXT,
    cooking_facilities JSONB DEFAULT '[]', -- Array of facilities
    who_cooks TEXT CHECK (who_cooks IN ('self', 'family_member', 'cook_helper')),
    budget_flexibility TEXT CHECK (budget_flexibility IN ('limited', 'flexible', 'high')),
    motivation_level INTEGER CHECK (motivation_level >= 1 AND motivation_level <= 10),
    support_system TEXT CHECK (support_system IN ('strong', 'moderate', 'weak')),
    
    -- System fields
    onboarding_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Data protection and privacy
    data_encryption_level TEXT DEFAULT 'standard',
    last_data_access TIMESTAMP WITH TIME ZONE,
    data_access_log JSONB DEFAULT '[]'
);

-- Create indexes for performance (only on non-sensitive fields)
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_user_profiles_onboarding_completed ON user_profiles(onboarding_completed);
CREATE INDEX IF NOT EXISTS idx_user_profiles_created_at ON user_profiles(created_at);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_user_profiles_updated_at 
    BEFORE UPDATE ON user_profiles 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) - CRITICAL FOR DATA PROTECTION
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own profile
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = id);

-- Policy: Users can only update their own profile
CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = id);

-- Policy: Users can only insert their own profile
CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Policy: Users can only delete their own profile
CREATE POLICY "Users can delete own profile" ON user_profiles
    FOR DELETE USING (auth.uid() = id);

-- Create a view for basic profile info (non-sensitive data only)
CREATE OR REPLACE VIEW public_profile_view AS
SELECT 
    id,
    full_name,
    age,
    gender,
    height_cm,
    weight_kg,
    food_preference,
    daily_routine,
    primary_goals,
    onboarding_completed,
    created_at
FROM user_profiles;

-- Grant permissions
GRANT SELECT ON public_profile_view TO authenticated;
GRANT ALL ON user_profiles TO authenticated;

-- Create audit log table for data access tracking
CREATE TABLE IF NOT EXISTS profile_access_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    profile_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    access_type TEXT NOT NULL CHECK (access_type IN ('view', 'update', 'create', 'delete')),
    accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,
    accessed_by UUID REFERENCES auth.users(id) ON DELETE CASCADE
);

-- Enable RLS on audit log
ALTER TABLE profile_access_log ENABLE ROW LEVEL SECURITY;

-- Policy for audit log
CREATE POLICY "Users can view own access logs" ON profile_access_log
    FOR SELECT USING (auth.uid() = user_id);

-- Function to log profile access
CREATE OR REPLACE FUNCTION log_profile_access(
    p_profile_id UUID,
    p_access_type TEXT,
    p_ip_address INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO profile_access_log (user_id, profile_id, access_type, ip_address, user_agent)
    VALUES (auth.uid(), p_profile_id, p_access_type, p_ip_address, p_user_agent);
    
    -- Update last_data_access in user_profiles
    UPDATE user_profiles 
    SET last_data_access = NOW(),
        data_access_log = COALESCE(data_access_log, '[]'::jsonb) || 
                         jsonb_build_object(
                             'timestamp', NOW(),
                             'access_type', p_access_type,
                             'ip_address', p_ip_address
                         )
    WHERE id = p_profile_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION log_profile_access(UUID, TEXT, INET, TEXT) TO authenticated;

