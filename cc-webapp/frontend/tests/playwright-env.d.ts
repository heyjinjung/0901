// 최소 타입 셈블리: 에디터용 간이 선언(컨테이너 실행에는 영향 없음)
declare module '@playwright/test' {
	export const test: any;
	export const expect: any;
	export type Page = any;
	export const request: any;
	export type APIRequestContext = any;
}
declare var process: any;
