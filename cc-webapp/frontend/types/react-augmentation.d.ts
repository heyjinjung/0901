import 'react';

// React 컴포넌트 Props에 key 속성이 자동으로 포함되도록 React 타입 확장
declare module 'react' {
  interface Attributes {
    key?: React.Key;
  }
}
