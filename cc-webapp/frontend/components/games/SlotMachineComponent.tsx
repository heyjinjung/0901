'use client';
import React from 'react';
import useFeedback from '../../hooks/useFeedback';

export function SlotMachineComponent() {
  useFeedback();
  return null; // 디자인 영향 없음
}

export default SlotMachineComponent;
