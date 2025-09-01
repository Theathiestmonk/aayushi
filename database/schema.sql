-- AI Dietitian Agent System Database Schema
-- This file contains all the necessary tables for the multi-agent system

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table (clients)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE,
    gender VARCHAR(20),
    height_cm DECIMAL(5,2),
    weight_kg DECIMAL(5,2),
    activity_level VARCHAR(50),
    dietary_restrictions TEXT[],
    allergies TEXT[],
    medical_conditions TEXT[],
    fitness_goals TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Client profiles (detailed health information)
CREATE TABLE client_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    bmr DECIMAL(8,2),
    tdee DECIMAL(8,2),
    target_weight_kg DECIMAL(5,2),
    target_calories_per_day INTEGER,
    target_protein_g INTEGER,
    target_carbs_g INTEGER,
    target_fat_g INTEGER,
    preferred_cuisine TEXT[],
    cooking_skill_level VARCHAR(50),
    meal_prep_preference BOOLEAN DEFAULT false,
    budget_range VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Diet plans
CREATE TABLE diet_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'active',
    total_calories INTEGER,
    total_protein_g INTEGER,
    total_carbs_g INTEGER,
    total_fat_g INTEGER,
    created_by_agent VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Daily meal plans
CREATE TABLE daily_meals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    diet_plan_id UUID REFERENCES diet_plans(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    meal_type VARCHAR(50) NOT NULL, -- breakfast, lunch, dinner, snack
    meal_name VARCHAR(255) NOT NULL,
    calories INTEGER,
    protein_g INTEGER,
    carbs_g INTEGER,
    fat_g INTEGER,
    ingredients TEXT[],
    instructions TEXT,
    prep_time_minutes INTEGER,
    cooking_time_minutes INTEGER,
    difficulty_level VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Workout plans
CREATE TABLE workout_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'active',
    fitness_level VARCHAR(50),
    workout_days_per_week INTEGER,
    session_duration_minutes INTEGER,
    created_by_agent VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Daily workouts
CREATE TABLE daily_workouts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workout_plan_id UUID REFERENCES workout_plans(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    workout_name VARCHAR(255) NOT NULL,
    workout_type VARCHAR(50), -- strength, cardio, flexibility, etc.
    duration_minutes INTEGER,
    exercises JSONB,
    calories_burned INTEGER,
    difficulty_level VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User tracking (meals consumed)
CREATE TABLE meal_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    meal_type VARCHAR(50) NOT NULL,
    meal_name VARCHAR(255),
    calories_consumed INTEGER,
    protein_g INTEGER,
    carbs_g INTEGER,
    fat_g INTEGER,
    photo_url TEXT,
    notes TEXT,
    compliance_score DECIMAL(3,2), -- 0.00 to 1.00
    tracked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User tracking (workouts completed)
CREATE TABLE workout_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    workout_name VARCHAR(255),
    workout_type VARCHAR(50),
    duration_minutes INTEGER,
    calories_burned INTEGER,
    photo_url TEXT,
    notes TEXT,
    compliance_score DECIMAL(3,2), -- 0.00 to 1.00
    tracked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Follow-up interactions
CREATE TABLE follow_ups (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    agent_type VARCHAR(100) NOT NULL, -- follow_up_agent, recommender_agent, etc.
    interaction_type VARCHAR(100), -- meal_reminder, workout_reminder, progress_check
    message TEXT NOT NULL,
    user_response TEXT,
    status VARCHAR(50) DEFAULT 'pending', -- pending, responded, completed
    scheduled_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    responded_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent recommendations
CREATE TABLE agent_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    agent_type VARCHAR(100) NOT NULL,
    recommendation_type VARCHAR(100), -- diet_adjustment, workout_modification, etc.
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(50) DEFAULT 'medium', -- low, medium, high, urgent
    status VARCHAR(50) DEFAULT 'pending', -- pending, accepted, rejected, implemented
    data_analysis JSONB, -- stores analysis results
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    implemented_at TIMESTAMP WITH TIME ZONE
);

-- Grocery lists
CREATE TABLE grocery_lists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    diet_plan_id UUID REFERENCES diet_plans(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    total_estimated_cost DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'draft', -- draft, active, completed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Grocery items
CREATE TABLE grocery_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    grocery_list_id UUID REFERENCES grocery_lists(id) ON DELETE CASCADE,
    item_name VARCHAR(255) NOT NULL,
    quantity DECIMAL(8,2) NOT NULL,
    unit VARCHAR(50),
    estimated_cost DECIMAL(8,2),
    category VARCHAR(100),
    priority VARCHAR(50) DEFAULT 'medium',
    is_purchased BOOLEAN DEFAULT false,
    purchased_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Recipes
CREATE TABLE recipes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    ingredients JSONB NOT NULL,
    instructions TEXT[] NOT NULL,
    prep_time_minutes INTEGER,
    cooking_time_minutes INTEGER,
    servings INTEGER,
    calories_per_serving INTEGER,
    protein_g_per_serving INTEGER,
    carbs_g_per_serving INTEGER,
    fat_g_per_serving INTEGER,
    difficulty_level VARCHAR(50),
    cuisine_type VARCHAR(100),
    tags TEXT[],
    photo_url TEXT,
    is_ai_generated BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent interactions log
CREATE TABLE agent_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    agent_type VARCHAR(100) NOT NULL,
    interaction_data JSONB NOT NULL,
    input_data JSONB,
    output_data JSONB,
    processing_time_ms INTEGER,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Weekly progress reports
CREATE TABLE weekly_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    week_start_date DATE NOT NULL,
    week_end_date DATE NOT NULL,
    total_calories_consumed INTEGER,
    total_calories_burned INTEGER,
    net_calories INTEGER,
    weight_change_kg DECIMAL(5,2),
    compliance_score DECIMAL(3,2),
    diet_adherence_percentage DECIMAL(5,2),
    workout_adherence_percentage DECIMAL(5,2),
    recommendations JSONB,
    generated_by_agent VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_diet_plans_user_id ON diet_plans(user_id);
CREATE INDEX idx_workout_plans_user_id ON workout_plans(user_id);
CREATE INDEX idx_meal_tracking_user_date ON meal_tracking(user_id, date);
CREATE INDEX idx_workout_tracking_user_date ON workout_tracking(user_id, date);
CREATE INDEX idx_follow_ups_user_id ON follow_ups(user_id);
CREATE INDEX idx_agent_recommendations_user_id ON agent_recommendations(user_id);
CREATE INDEX idx_grocery_lists_user_id ON grocery_lists(user_id);
CREATE INDEX idx_recipes_user_id ON recipes(user_id);
CREATE INDEX idx_agent_interactions_user_id ON agent_interactions(user_id);
CREATE INDEX idx_weekly_reports_user_id ON weekly_reports(user_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables with updated_at columns
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_client_profiles_updated_at BEFORE UPDATE ON client_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_diet_plans_updated_at BEFORE UPDATE ON diet_plans FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workout_plans_updated_at BEFORE UPDATE ON workout_plans FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_grocery_lists_updated_at BEFORE UPDATE ON grocery_lists FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_recipes_updated_at BEFORE UPDATE ON recipes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

