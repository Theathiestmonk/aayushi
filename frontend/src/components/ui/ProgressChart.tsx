import React from 'react';

interface ProgressChartProps {
  type: 'circle' | 'semi-circle';
  value: number;
  maxValue: number;
  size?: number;
  strokeWidth?: number;
  color?: string;
  gradient?: {
    from: string;
    to: string;
  };
  label?: string;
  subtitle?: string;
  className?: string;
}

const ProgressChart: React.FC<ProgressChartProps> = ({
  type,
  value,
  maxValue,
  size = 120,
  strokeWidth = 8,
  color = '#3b82f6',
  gradient,
  label,
  subtitle,
  className = ''
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = type === 'circle' ? 2 * Math.PI * radius : Math.PI * radius;
  const progress = Math.min(100, (value / maxValue) * 100);
  const strokeDasharray = (circumference * progress) / 100;

  const centerX = size / 2;
  const centerY = type === 'circle' ? size / 2 : size;

  return (
    <div className={`text-center ${className}`}>
      <div className="relative mx-auto" style={{ width: size, height: size }}>
        <svg 
          className="w-full h-full transform -rotate-90" 
          viewBox={`0 0 ${size} ${size}`}
        >
          {/* Background circle/arc */}
          <path
            d={type === 'circle' 
              ? `M ${centerX} ${centerY - radius} A ${radius} ${radius} 0 1 1 ${centerX} ${centerY + radius} A ${radius} ${radius} 0 1 1 ${centerX} ${centerY - radius}`
              : `M ${centerX - radius} ${centerY} A ${radius} ${radius} 0 0 1 ${centerX + radius} ${centerY}`
            }
            fill="none"
            stroke="#e5e7eb"
            strokeWidth={strokeWidth}
          />
          
          {/* Progress circle/arc */}
          <path
            d={type === 'circle' 
              ? `M ${centerX} ${centerY - radius} A ${radius} ${radius} 0 1 1 ${centerX} ${centerY + radius} A ${radius} ${radius} 0 1 1 ${centerX} ${centerY - radius}`
              : `M ${centerX - radius} ${centerY} A ${radius} ${radius} 0 0 1 ${centerX + radius} ${centerY}`
            }
            fill="none"
            stroke={gradient ? `url(#${gradient.from.replace('#', '')}${gradient.to.replace('#', '')})` : color}
            strokeWidth={strokeWidth}
            strokeDasharray={`${strokeDasharray} ${circumference}`}
            strokeLinecap="round"
          />
          
          {gradient && (
            <defs>
              <linearGradient 
                id={`${gradient.from.replace('#', '')}${gradient.to.replace('#', '')}`} 
                x1="0%" 
                y1="0%" 
                x2="100%" 
                y2="0%"
              >
                <stop offset="0%" stopColor={gradient.from} />
                <stop offset="100%" stopColor={gradient.to} />
              </linearGradient>
            </defs>
          )}
        </svg>
        
        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          {label && <p className="text-2xl font-bold text-gray-900">{label}</p>}
          {subtitle && <p className="text-sm text-gray-600">{subtitle}</p>}
        </div>
      </div>
    </div>
  );
};

export default ProgressChart;


