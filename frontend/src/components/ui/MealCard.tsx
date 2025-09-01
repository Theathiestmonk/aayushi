import React from 'react';
import { CheckCircle, Circle } from 'lucide-react';

interface MealCardProps {
  meal: {
    id: string;
    name: string;
    type: 'breakfast' | 'lunch' | 'snack' | 'dinner';
    calories: number;
    carbs_g: number;
    protein_g: number;
    fat_g: number;
    completed: boolean;
  };
  onToggleComplete: (id: string) => void;
  className?: string;
}

const MealCard: React.FC<MealCardProps> = ({ meal, onToggleComplete, className = '' }) => {
  const getMealTypeIcon = (type: string) => {
    switch (type) {
      case 'breakfast': return '🌅';
      case 'lunch': return '☀️';
      case 'snack': return '🍎';
      case 'dinner': return '🌙';
      default: return '🍽️';
    }
  };

  const getMealTypeName = (type: string) => {
    return type.charAt(0).toUpperCase() + type.slice(1);
  };

  const getMealTypeColor = (type: string) => {
    switch (type) {
      case 'breakfast': return 'from-yellow-100 to-orange-100';
      case 'lunch': return 'from-green-100 to-blue-100';
      case 'snack': return 'from-purple-100 to-pink-100';
      case 'dinner': return 'from-blue-100 to-indigo-100';
      default: return 'from-gray-100 to-gray-200';
    }
  };

  return (
    <div className={`bg-gray-50 rounded-lg p-4 ${className}`}>
      <div className="flex items-start space-x-3">
        <button
          onClick={() => onToggleComplete(meal.id)}
          className="mt-1 hover:scale-110 transition-transform"
        >
          {meal.completed ? (
            <CheckCircle className="w-5 h-5 text-green-500" />
          ) : (
            <Circle className="w-5 h-5 text-gray-400 hover:text-gray-600 transition-colors" />
          )}
        </button>
        
        <div className="flex-1">
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-semibold text-gray-900">{getMealTypeName(meal.type)}</h4>
            <span className="text-sm font-medium text-gray-600">{meal.calories} kcal</span>
          </div>
          
          <div className="flex items-center space-x-3 mb-3">
            <div className={`w-12 h-12 bg-gradient-to-br ${getMealTypeColor(meal.type)} rounded-lg flex items-center justify-center`}>
              <span className="text-lg">{getMealTypeIcon(meal.type)}</span>
            </div>
            <div className="flex-1">
              <p className="text-sm text-gray-700 leading-tight">{meal.name}</p>
            </div>
          </div>
          
          <div className="flex space-x-4 text-xs text-gray-600">
            <span className="flex items-center space-x-1">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              <span>C {meal.carbs_g}g</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
              <span>P {meal.protein_g}g</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="w-2 h-2 bg-yellow-500 rounded-full"></span>
              <span>F {meal.fat_g}g</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MealCard;


