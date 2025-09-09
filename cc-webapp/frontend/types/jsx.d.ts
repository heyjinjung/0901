/**
 * React JSX 네임스페이스 선언
 * JSX.IntrinsicElements가 없다는 오류 해결
 */

import React from 'react';

declare global {
  namespace JSX {
    interface IntrinsicElements {
      [elemName: string]: any;
    }
  }
}
