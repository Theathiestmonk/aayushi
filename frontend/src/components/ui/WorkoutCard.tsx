import React from 'react';

interface WorkoutCardProps {
  workout: {
    id: string;
    name: string;
    progress: number;
    goal: number;
    category: 'cardio' | 'strength' | 'flexibility';
    icon: string;
  };
  className?: string;
}

const WorkoutCard: React.FC<WorkoutCardProps> = ({ workout, className = '' }) => {
  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'cardio': return 'bg-green-100 text-green-800 border-green-200';
      case 'strength': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'flexibility': return 'bg-purple-100 text-purple-800 border-purple-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getCategoryName = (category: string) => {
    switch (category) {
      case 'cardio': return 'Cardio';
      case 'strength': return 'Strength';
      case 'flexibility': return 'Flexibility';
      default: return 'Other';
    }
  };

  const progressPercentage = (workout.progress / workout.goal) * 100;

  return (
    <div className={`p-4 rounded-lg border ${getCategoryColor(workout.category)} ${className}`}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-2xl">{workout.icon}</span>
        <span className={`text-xs px-2 py-1 rounded-full ${getCategoryColor(workout.category)}`}>
          {getCategoryName(workout.category)}
        </span>
      </div>
      
      <h4 className="font-semibold text-gray-900 mb-2">{workout.name}</h4>
      
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-600">
          {Math.round(progressPercentage)}% ({workout.progress}/{workout.goal})
        </span>
      </div>
      
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className="bg-current h-2 rounded-full transition-all duration-300"
          style={{ width: `${progressPercentage}%` }}
        ></div>
      </div>
    </div>
  );
};

export default WorkoutCard;


