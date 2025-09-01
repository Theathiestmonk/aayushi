-- Diet Plan Database Schema for AI Dietitian System
-- This schema stores comprehensive diet plans, daily meals, and progress tracking

-- 1. Diet Plan Table (weekly plan)
CREATE TABLE IF NOT EXISTS diet_plans (
    plan_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    calorie_target INTEGER NOT NULL CHECK (calorie_target > 0),
    protein_target DECIMAL(5,2) NOT NULL CHECK (protein_target > 0),
    carb_target DECIMAL(5,2) NOT NULL CHECK (carb_target > 0),
    fat_target DECIMAL(5,2) NOT NULL CHECK (fat_target > 0),
    plan_name TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure end_date is after start_date
    CONSTRAINT valid_date_range CHECK (end_date >= start_date),
    -- Ensure calorie targets are reasonable
    CONSTRAINT reasonable_calorie_target CHECK (calorie_target >= 800 AND calorie_target <= 5000),
    CONSTRAINT reasonable_protein_target CHECK (protein_target >= 20 AND protein_target <= 300),
    CONSTRAINT reasonable_carb_target CHECK (carb_target >= 50 AND carb_target <= 600),
    CONSTRAINT reasonable_fat_target CHECK (fat_target >= 20 AND fat_target <= 200)
);

-- 2. Daily Plan Table
CREATE TABLE IF NOT EXISTS daily_plans (
    daily_plan_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID NOT NULL REFERENCES diet_plans(plan_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_calories INTEGER NOT NULL CHECK (total_calories > 0),
    total_protein DECIMAL(5,2) NOT NULL CHECK (total_protein > 0),
    total_carbs DECIMAL(5,2) NOT NULL CHECK (total_carbs > 0),
    total_fat DECIMAL(5,2) NOT NULL CHECK (total_fat > 0),
    water_intake_target DECIMAL(4,2) NOT NULL CHECK (water_intake_target > 0), -- in liters
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Note: Date validation will be handled at the application level
    -- to avoid PostgreSQL check constraint limitations with subqueries
    
    -- Unique constraint for plan_id and date combination
    UNIQUE(plan_id, date),
    -- Ensure daily totals are reasonable
    CONSTRAINT reasonable_daily_calories CHECK (total_calories >= 800 AND total_calories <= 5000),
    CONSTRAINT reasonable_daily_protein CHECK (total_protein >= 20 AND total_protein <= 300),
    CONSTRAINT reasonable_daily_carbs CHECK (total_carbs >= 50 AND total_carbs <= 600),
    CONSTRAINT reasonable_daily_fat CHECK (total_fat >= 20 AND total_fat <= 200),
    CONSTRAINT reasonable_water_intake CHECK (water_intake_target >= 0.5 AND water_intake_target <= 10.0)
);

-- 3. Meal Table
CREATE TABLE IF NOT EXISTS meals (
    meal_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    daily_plan_id UUID NOT NULL REFERENCES daily_plans(daily_plan_id) ON DELETE CASCADE,
    meal_type TEXT NOT NULL CHECK (meal_type IN ('Breakfast', 'Snack', 'Lunch', 'Evening Snack', 'Dinner')),
    meal_time TIME NOT NULL,
    meal_name TEXT NOT NULL,
    calories INTEGER NOT NULL CHECK (calories >= 0),
    protein DECIMAL(5,2) NOT NULL CHECK (protein >= 0),
    carbs DECIMAL(5,2) NOT NULL CHECK (carbs >= 0),
    fat DECIMAL(5,2) NOT NULL CHECK (fat >= 0),
    fiber DECIMAL(5,2) DEFAULT 0 CHECK (fiber >= 0),
    instructions TEXT,
    difficulty_level TEXT CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    prep_time_minutes INTEGER CHECK (prep_time_minutes > 0),
    cooking_time_minutes INTEGER CHECK (cooking_time_minutes >= 0),
    cost_category TEXT CHECK (cost_category IN ('budget', 'moderate', 'premium')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Food Items Table (detailed breakdown)
CREATE TABLE IF NOT EXISTS food_items (
    food_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meal_id UUID NOT NULL REFERENCES meals(meal_id) ON DELETE CASCADE,
    food_name TEXT NOT NULL,
    quantity DECIMAL(8,2) NOT NULL CHECK (quantity > 0),
    unit TEXT NOT NULL CHECK (unit IN ('g', 'ml', 'pieces', 'cups', 'tbsp', 'tsp', 'medium', 'large', 'small')),
    calories INTEGER NOT NULL CHECK (calories >= 0),
    protein DECIMAL(5,2) NOT NULL CHECK (protein >= 0),
    carbs DECIMAL(5,2) NOT NULL CHECK (carbs >= 0),
    fat DECIMAL(5,2) NOT NULL CHECK (fat >= 0),
    fiber DECIMAL(5,2) DEFAULT 0 CHECK (fiber >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Tracking / Progress Table
CREATE TABLE IF NOT EXISTS progress_tracking (
    progress_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    weight_kg DECIMAL(5,2) CHECK (weight_kg > 0),
    waist_cm DECIMAL(5,2) CHECK (waist_cm > 0),
    energy_level INTEGER CHECK (energy_level >= 1 AND energy_level <= 10),
    compliance_percentage DECIMAL(5,2) CHECK (compliance_percentage >= 0 AND compliance_percentage <= 100),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint for user_id and date combination
    UNIQUE(user_id, date)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_diet_plans_user_id ON diet_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_diet_plans_status ON diet_plans(status);
CREATE INDEX IF NOT EXISTS idx_diet_plans_date_range ON diet_plans(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_diet_plans_created_at ON diet_plans(created_at);
CREATE INDEX IF NOT EXISTS idx_daily_plans_plan_id ON daily_plans(plan_id);
CREATE INDEX IF NOT EXISTS idx_daily_plans_date ON daily_plans(date);
CREATE INDEX IF NOT EXISTS idx_daily_plans_plan_date ON daily_plans(plan_id, date);
CREATE INDEX IF NOT EXISTS idx_meals_daily_plan_id ON meals(daily_plan_id);
CREATE INDEX IF NOT EXISTS idx_meals_meal_type ON meals(meal_type);
CREATE INDEX IF NOT EXISTS idx_meals_meal_time ON meals(meal_time);
CREATE INDEX IF NOT EXISTS idx_food_items_meal_id ON food_items(meal_id);
CREATE INDEX IF NOT EXISTS idx_progress_tracking_user_id ON progress_tracking(user_id);
CREATE INDEX IF NOT EXISTS idx_progress_tracking_date ON progress_tracking(date);
CREATE INDEX IF NOT EXISTS idx_progress_tracking_user_date ON progress_tracking(user_id, date);

-- Create functions to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_diet_plans_updated_at BEFORE UPDATE ON diet_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_daily_plans_updated_at BEFORE UPDATE ON daily_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_meals_updated_at BEFORE UPDATE ON meals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_food_items_updated_at BEFORE UPDATE ON food_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_progress_tracking_updated_at BEFORE UPDATE ON progress_tracking
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to validate daily plan dates
CREATE OR REPLACE FUNCTION validate_daily_plan_date()
RETURNS TRIGGER AS $$
DECLARE
    plan_start_date DATE;
    plan_end_date DATE;
BEGIN
    -- Get the plan's start and end dates
    SELECT start_date, end_date INTO plan_start_date, plan_end_date
    FROM diet_plans
    WHERE plan_id = NEW.plan_id;
    
    -- Check if the daily plan date is within the plan's range
    IF NEW.date < plan_start_date OR NEW.date > plan_end_date THEN
        RAISE EXCEPTION 'Daily plan date % is outside the diet plan range (% to %)', 
            NEW.date, plan_start_date, plan_end_date;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to validate daily plan dates before insert/update
CREATE TRIGGER validate_daily_plan_date_trigger
    BEFORE INSERT OR UPDATE ON daily_plans
    FOR EACH ROW EXECUTE FUNCTION validate_daily_plan_date();

-- Enable Row Level Security (RLS)
ALTER TABLE diet_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE meals ENABLE ROW LEVEL SECURITY;
ALTER TABLE food_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE progress_tracking ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can only access their own diet plans
CREATE POLICY "Users can view own diet plans" ON diet_plans
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own diet plans" ON diet_plans
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own diet plans" ON diet_plans
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own diet plans" ON diet_plans
    FOR DELETE USING (auth.uid() = user_id);

-- Daily plans inherit permissions from diet plans
CREATE POLICY "Users can view own daily plans" ON daily_plans
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM diet_plans 
            WHERE diet_plans.plan_id = daily_plans.plan_id 
            AND diet_plans.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own daily plans" ON daily_plans
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM diet_plans 
            WHERE diet_plans.plan_id = daily_plans.plan_id 
            AND diet_plans.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update own daily plans" ON daily_plans
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM diet_plans 
            WHERE diet_plans.plan_id = daily_plans.plan_id 
            AND diet_plans.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete own daily plans" ON daily_plans
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM diet_plans 
            WHERE diet_plans.plan_id = daily_plans.plan_id 
            AND diet_plans.user_id = auth.uid()
        )
    );

-- Meals inherit permissions from daily plans
CREATE POLICY "Users can view own meals" ON meals
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM daily_plans dp
            JOIN diet_plans dp2 ON dp.plan_id = dp2.plan_id
            WHERE dp.daily_plan_id = meals.daily_plan_id 
            AND dp2.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own meals" ON meals
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM daily_plans dp
            JOIN diet_plans dp2 ON dp.plan_id = dp2.plan_id
            WHERE dp.daily_plan_id = meals.daily_plan_id 
            AND dp2.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update own meals" ON meals
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM daily_plans dp
            JOIN diet_plans dp2 ON dp.plan_id = dp2.plan_id
            WHERE dp.daily_plan_id = meals.daily_plan_id 
            AND dp2.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete own meals" ON meals
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM daily_plans dp
            JOIN diet_plans dp2 ON dp.plan_id = dp2.plan_id
            WHERE dp.daily_plan_id = meals.daily_plan_id 
            AND dp2.user_id = auth.uid()
        )
    );

-- Food items inherit permissions from meals
CREATE POLICY "Users can view own food items" ON food_items
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM meals m
            JOIN daily_plans dp ON m.daily_plan_id = dp.daily_plan_id
            JOIN diet_plans dp2 ON dp.plan_id = dp2.plan_id
            WHERE m.meal_id = food_items.meal_id 
            AND dp2.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own food items" ON food_items
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM meals m
            JOIN daily_plans dp ON m.daily_plan_id = dp.daily_plan_id
            JOIN diet_plans dp2 ON dp.plan_id = dp2.plan_id
            WHERE m.meal_id = food_items.meal_id 
            AND dp2.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update own food items" ON food_items
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM meals m
            JOIN daily_plans dp ON m.daily_plan_id = dp.daily_plan_id
            JOIN diet_plans dp2 ON dp.plan_id = dp2.plan_id
            WHERE m.meal_id = food_items.meal_id 
            AND dp2.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete own food items" ON food_items
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM meals m
            JOIN daily_plans dp ON m.daily_plan_id = dp.daily_plan_id
            JOIN diet_plans dp2 ON dp.plan_id = dp2.plan_id
            WHERE m.meal_id = food_items.meal_id 
            AND dp2.user_id = auth.uid()
        )
    );

-- Progress tracking policies
CREATE POLICY "Users can view own progress" ON progress_tracking
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own progress" ON progress_tracking
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own progress" ON progress_tracking
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own progress" ON progress_tracking
    FOR DELETE USING (auth.uid() = user_id);

-- Create views for easier data access
CREATE OR REPLACE VIEW diet_plan_summary AS
SELECT 
    dp.plan_id,
    dp.user_id,
    dp.start_date,
    dp.end_date,
    dp.calorie_target,
    dp.protein_target,
    dp.carb_target,
    dp.fat_target,
    dp.plan_name,
    dp.status,
    dp.created_at,
    COUNT(daily.daily_plan_id) as total_days,
    COUNT(meals.meal_id) as total_meals
FROM diet_plans dp
LEFT JOIN daily_plans daily ON dp.plan_id = daily.plan_id
LEFT JOIN meals ON daily.daily_plan_id = meals.daily_plan_id
GROUP BY dp.plan_id, dp.user_id, dp.start_date, dp.end_date, dp.calorie_target, 
         dp.protein_target, dp.carb_target, dp.fat_target, dp.plan_name, dp.status, dp.created_at;

-- Create view for daily nutrition summary
CREATE OR REPLACE VIEW daily_nutrition_summary AS
SELECT 
    dp.daily_plan_id,
    dp.plan_id,
    dp.date,
    dp.total_calories,
    dp.total_protein,
    dp.total_carbs,
    dp.total_fat,
    dp.water_intake_target,
    dp.notes,
    COUNT(m.meal_id) as meal_count,
    STRING_AGG(m.meal_type, ', ' ORDER BY m.meal_time) as meal_types
FROM daily_plans dp
LEFT JOIN meals m ON dp.daily_plan_id = m.daily_plan_id
GROUP BY dp.daily_plan_id, dp.plan_id, dp.date, dp.total_calories, 
         dp.total_protein, dp.total_carbs, dp.total_fat, dp.water_intake_target, dp.notes;

-- Insert sample data for testing (optional)
-- INSERT INTO diet_plans (user_id, start_date, end_date, calorie_target, protein_target, carb_target, fat_target, plan_name)
-- VALUES ('sample-user-id', '2024-01-01', '2024-01-31', 2000, 150, 200, 67, 'Sample Weight Loss Plan');

COMMENT ON TABLE diet_plans IS 'Stores monthly diet plans with daily calorie and macronutrient targets';
COMMENT ON TABLE daily_plans IS 'Stores daily nutrition targets and water intake goals';
COMMENT ON TABLE meals IS 'Stores individual meals with timing, nutrition, and instructions';
COMMENT ON TABLE food_items IS 'Stores detailed food breakdown for each meal';
COMMENT ON TABLE progress_tracking IS 'Stores user progress tracking data including weight and compliance';
