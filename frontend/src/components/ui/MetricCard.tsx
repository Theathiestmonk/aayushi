import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  iconColor: string;
  iconBgColor: string;
  subtitle?: string;
  progress?: {
    current: number;
    goal: number;
    unit?: string;
    leftText?: string;
  };
  className?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  icon: Icon,
  iconColor,
  iconBgColor,
  subtitle,
  progress,
  className = ''
}) => {
  const progressPercentage = progress ? Math.min(100, (progress.current / progress.goal) * 100) : 0;
  const leftValue = progress ? progress.goal - progress.current : 0;

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`w-10 h-10 ${iconBgColor} rounded-lg flex items-center justify-center`}>
            <Icon className={`w-5 h-5 ${iconColor}`} />
          </div>
          <span className="font-semibold text-gray-900">{title}</span>
        </div>
      </div>
      
      <div className="mb-4">
        <p className="text-3xl font-bold text-gray-900">{value}</p>
        {subtitle && <p className="text-sm text-gray-600 mt-1">{subtitle}</p>}
        
        {progress && (
          <div className="mt-2">
            <div className="flex justify-between text-sm text-gray-600 mb-1">
              <span>{Math.round(progressPercentage)}%</span>
              <span>
                {leftValue > 0 ? `${leftValue} ${progress.unit || ''} left` : 'Goal reached!'}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-300 ${iconColor.replace('text-', 'bg-')}`}
                style={{ width: `${progressPercentage}%` }}
              ></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MetricCard;


