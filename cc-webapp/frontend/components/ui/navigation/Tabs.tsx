import React from 'react';

interface TabItem {
	key: string;
	label: string;
	icon?: React.ReactNode;
}

interface TabsProps {
	children?: React.ReactNode;
	className?: string;
	items?: TabItem[];
	activeTab?: string;
	onTabChange?: (key: string) => void;
	variant?: string;
	size?: string;
}

export default function Tabs({ children, className = '', items, activeTab, onTabChange }: TabsProps) {
	return (
		<div className={`flex space-x-2 ${className}`}>
			{items ? (
				items.map(item => (
					<button key={item.key} onClick={() => onTabChange?.(item.key)} className={`px-3 py-1`}>
						{item.icon}
						<span className="ml-2">{item.label}</span>
					</button>
				))
			) : (
				children
			)}
		</div>
	);
}
