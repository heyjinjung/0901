// React 타입 선언 파일
declare module 'react';
declare module 'react/jsx-runtime';

// key prop을 모든 컴포넌트에서 사용할 수 있도록 확장
declare namespace React {
  interface Attributes {
    key?: React.Key | null;
  }
}
