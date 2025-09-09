import React from 'react';

interface RewardResultModalProps {
	open?: boolean;
	isOpen?: boolean; // alias used by some components
	onClose?: () => void;
	children?: React.ReactNode;
	type?: 'success' | 'error' | 'info';
	title?: string;
	message?: string;
	reward?: any;
}

export default function RewardResultModal({ open = false, isOpen, onClose, children, type, title, message, reward }: RewardResultModalProps) {
	const visible = typeof isOpen === 'boolean' ? isOpen : open;
	if (!visible) return null;
	return (
		<div className="fixed inset-0 flex items-center justify-center z-50">
			<div className="bg-black/50 absolute inset-0" onClick={onClose} />
			<div className="relative z-10 p-6 bg-card rounded-lg">
				{title && <h3 className="font-bold mb-2">{title}</h3>}
				{message && <p className="mb-4 text-sm text-muted-foreground">{message}</p>}
				{children}
			</div>
		</div>
	);
}
