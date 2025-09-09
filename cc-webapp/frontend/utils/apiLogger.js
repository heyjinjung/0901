/**
 * API 로깅 유틸리티
 * 모든 API 호출을 콘솔에 일관되게 표시
 */

const API_LOG_STYLE = {
  request: 'color: #4CAF50; font-weight: bold;',
  success: 'color: #2196F3; font-weight: bold;',
  error: 'color: #F44336; font-weight: bold;',
  data: 'color: #666;'
};

/**
 * API 요청 로그
 */
export const apiLogTry = (endpoint) => {
  console.log(`%c[API 요청] ${endpoint}`, API_LOG_STYLE.request);
  console.log(`%c⏱️ ${new Date().toLocaleTimeString()}`, API_LOG_STYLE.data);
};

/**
 * API 성공 응답 로그
 */
export const apiLogSuccess = (endpoint, data = null) => {
  console.log(`%c[API 성공] ${endpoint}`, API_LOG_STYLE.success);
  if (data) {
    console.log('%c📦 응답 데이터:', API_LOG_STYLE.data, data);
  }
};

/**
 * API 실패 로그
 */
export const apiLogFail = (endpoint, error) => {
  console.error(`%c[API 실패] ${endpoint}`, API_LOG_STYLE.error);
  console.error('%c❌ 에러 내용:', API_LOG_STYLE.error, error);
};

/**
 * API 로거 래퍼 - fetch나 axios를 래핑
 */
export const withApiLogging = async (endpoint, apiCall) => {
  apiLogTry(endpoint);
  try {
    const response = await apiCall();
    apiLogSuccess(endpoint, response);
    return response;
  } catch (error) {
    apiLogFail(endpoint, error);
    throw error;
  }
};