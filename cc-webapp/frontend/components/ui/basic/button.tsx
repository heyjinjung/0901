import React from 'react';

interface ButtonProps {
	children?: React.ReactNode;
	className?: string;
	variant?: 'default' | 'outline';
	onClick?: () => void;
}

export function Button({ children, className = '', variant = 'default', ...rest }: ButtonProps) {
	const base = 'px-4 py-2 rounded-md transition';
	const variantClass =
		variant === 'outline' ? 'bg-transparent border border-primary/20' : 'bg-primary text-white';
	return (
		<button className={`${base} ${variantClass} ${className}`} {...rest}>
			{children}
		</button>
	);
}

export default Button;
