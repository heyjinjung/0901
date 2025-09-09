'use client';

import { useEffect } from 'react';
import App from '../App';

export default function LoginPage() {
	useEffect(() => {
		// 로그인 페이지 접근 시 로컬 스토리지에 강제 화면 설정
		if (typeof window !== 'undefined') {
			window.localStorage.setItem('E2E_FORCE_SCREEN', 'login');
		}
	}, []);

	return <App />;
}
