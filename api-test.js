// 백엔드 API 통신 테스트
fetch('http://localhost:8000/health')
  .then(response => response.json())
  .then(data => console.log('Backend API Response:', data))
  .catch(error => console.error('Error connecting to backend:', error));

// 결과는 브라우저 콘솔에서 확인할 수 있습니다.
console.log('API 통신 테스트 스크립트가 실행되었습니다. 브라우저 콘솔에서 결과를 확인하세요.');
