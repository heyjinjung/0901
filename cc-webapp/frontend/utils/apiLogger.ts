// Casino-Club F2P API 호출 로그 유틸
export function apiLogTry(title: string) {
  console.log(`[타이틀시도] ${title}`);
}
export function apiLogSuccess(title: string) {
  console.log(`[타이틀성공] ${title}`);
}
export function apiLogFail(title: string, error?: any) {
  console.log(`[타이틀실패] ${title}`, error);
}
