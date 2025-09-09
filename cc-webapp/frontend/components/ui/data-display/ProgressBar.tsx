import React from 'react';

interface ProgressBarProps {
	value?: number;
	max?: number;
	className?: string;
	variant?: string;
	size?: string;
	showLabel?: boolean;
}

function ProgressBar({ value = 0, max = 100, className = '', showLabel = false }: ProgressBarProps) {
	const pct = Math.max(0, Math.min(100, (value / max) * 100));
	return (
		<div className={`w-full bg-muted/20 rounded-full h-3 overflow-hidden ${className}`}>
			<div
				className="h-full bg-gradient-to-r from-primary to-gold"
				style={{ width: `${pct}%` }}
			/>
			{showLabel && <div className="text-xs text-muted-foreground mt-1">{Math.round(pct)}%</div>}
		</div>
	);
}

export default ProgressBar;
