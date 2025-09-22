-- Daily Health Metrics Table for AI Dietitian System
-- This table stores daily tracking data for steps, sleep, water intake, etc.

CREATE TABLE IF NOT EXISTS daily_health_metrics (
    -- Core identification
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    
    -- Denormalized user name (synced via triggers)
    user_full_name TEXT DEFAULT '' NOT NULL,
    
    -- Date tracking
    date DATE NOT NULL,
    
    -- Physical activity metrics
    steps_today INTEGER DEFAULT 0 CHECK (steps_today >= 0),
    steps_goal INTEGER DEFAULT 0 CHECK (steps_goal >= 0),
    calories_burned INTEGER DEFAULT 0 CHECK (calories_burned >= 0),
    
    -- Sleep metrics
    sleep_hours DECIMAL(3,1) DEFAULT 0 CHECK (sleep_hours >= 0 AND sleep_hours <= 24),
    sleep_goal DECIMAL(3,1) DEFAULT 0 CHECK (sleep_goal >= 0 AND sleep_goal <= 24),
    sleep_quality INTEGER DEFAULT 0 CHECK (sleep_quality >= 0 AND sleep_quality <= 5), -- 0-5 scale
    
    -- Hydration metrics
    water_intake_l DECIMAL(4,2) DEFAULT 0 CHECK (water_intake_l >= 0),
    water_goal_l DECIMAL(4,2) DEFAULT 0 CHECK (water_goal_l >= 0),
    
    -- Nutrition metrics
    calories_eaten INTEGER DEFAULT 0 CHECK (calories_eaten >= 0),
    calories_goal INTEGER DEFAULT 0 CHECK (calories_goal >= 0),
    
    -- Macronutrients
    carbs_g DECIMAL(6,2) DEFAULT 0 CHECK (carbs_g >= 0),
    carbs_goal DECIMAL(6,2) DEFAULT 0 CHECK (carbs_goal >= 0),
    protein_g DECIMAL(6,2) DEFAULT 0 CHECK (protein_g >= 0),
    protein_goal DECIMAL(6,2) DEFAULT 0 CHECK (protein_goal >= 0),
    fat_g DECIMAL(6,2) DEFAULT 0 CHECK (fat_g >= 0),
    fat_goal DECIMAL(6,2) DEFAULT 0 CHECK (fat_goal >= 0),
    
    -- Weight tracking
    weight_kg DECIMAL(5,2) DEFAULT 0 CHECK (weight_kg >= 0 AND weight_kg < 500),
    target_weight_kg DECIMAL(5,2) DEFAULT 0 CHECK (target_weight_kg >= 0 AND target_weight_kg < 500),
    
    -- System fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure one record per user per date
    UNIQUE(user_id, date)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_daily_health_metrics_user_id ON daily_health_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_daily_health_metrics_date ON daily_health_metrics(date);
CREATE INDEX IF NOT EXISTS idx_daily_health_metrics_user_date ON daily_health_metrics(user_id, date);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_daily_health_metrics_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_daily_health_metrics_updated_at 
    BEFORE UPDATE ON daily_health_metrics 
    FOR EACH ROW 
    EXECUTE FUNCTION update_daily_health_metrics_updated_at();

-- Maintain user_full_name by syncing from user_profiles
CREATE OR REPLACE FUNCTION set_daily_metrics_user_full_name()
RETURNS TRIGGER AS $$
BEGIN
    SELECT COALESCE(up.full_name, '') INTO NEW.user_full_name
    FROM user_profiles up
    WHERE up.id = NEW.user_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger on insert and update of daily_health_metrics to set user_full_name
DROP TRIGGER IF EXISTS trg_set_daily_metrics_user_full_name_ins ON daily_health_metrics;
CREATE TRIGGER trg_set_daily_metrics_user_full_name_ins
    BEFORE INSERT ON daily_health_metrics
    FOR EACH ROW
    EXECUTE FUNCTION set_daily_metrics_user_full_name();

DROP TRIGGER IF EXISTS trg_set_daily_metrics_user_full_name_upd ON daily_health_metrics;
CREATE TRIGGER trg_set_daily_metrics_user_full_name_upd
    BEFORE UPDATE OF user_id ON daily_health_metrics
    FOR EACH ROW
    EXECUTE FUNCTION set_daily_metrics_user_full_name();

-- Also propagate profile name changes into daily_health_metrics
CREATE OR REPLACE FUNCTION propagate_profile_name_to_daily_metrics()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE daily_health_metrics
    SET user_full_name = COALESCE(NEW.full_name, '')
    WHERE user_id = NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_propagate_profile_name ON user_profiles;
CREATE TRIGGER trg_propagate_profile_name
    AFTER UPDATE OF full_name ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION propagate_profile_name_to_daily_metrics();

-- Row Level Security (RLS)
ALTER TABLE daily_health_metrics ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own health metrics
CREATE POLICY "Users can view own health metrics" ON daily_health_metrics
    FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can only update their own health metrics
CREATE POLICY "Users can update own health metrics" ON daily_health_metrics
    FOR UPDATE USING (auth.uid() = user_id);

-- Policy: Users can only insert their own health metrics
CREATE POLICY "Users can insert own health metrics" ON daily_health_metrics
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policy: Users can only delete their own health metrics
CREATE POLICY "Users can delete own health metrics" ON daily_health_metrics
    FOR DELETE USING (auth.uid() = user_id);

-- Grant permissions
GRANT ALL ON daily_health_metrics TO authenticated;

-- Create a view for health metrics summary
CREATE OR REPLACE VIEW health_metrics_summary AS
SELECT 
    user_id,
    user_full_name,
    date,
    steps_today,
    steps_goal,
    ROUND((steps_today::DECIMAL / NULLIF(steps_goal, 0) * 100), 2) as steps_percentage,
    sleep_hours,
    sleep_goal,
    ROUND((sleep_hours / NULLIF(sleep_goal, 0) * 100), 2) as sleep_percentage,
    water_intake_l,
    water_goal_l,
    ROUND((water_intake_l / NULLIF(water_goal_l, 0) * 100), 2) as water_percentage,
    calories_eaten,
    calories_goal,
    ROUND((calories_eaten::DECIMAL / NULLIF(calories_goal, 0) * 100), 2) as calories_percentage,
    weight_kg,
    target_weight_kg,
    created_at,
    updated_at
FROM daily_health_metrics;

-- Grant permissions on the view
GRANT SELECT ON health_metrics_summary TO authenticated;

