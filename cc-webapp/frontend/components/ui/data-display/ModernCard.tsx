import React from 'react';

interface ModernCardProps {
	children?: React.ReactNode;
	className?: string;
}

export default function ModernCard({ children, className = '' }: ModernCardProps) {
	return <div className={`rounded-xl p-4 shadow-md bg-card/70 ${className}`}>{children}</div>;
}
