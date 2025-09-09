import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    // globals.css 파일 읽기
    const cssPath = path.join(process.cwd(), 'styles', 'globals.css');
    const cssContent = fs.readFileSync(cssPath, 'utf-8');
    
    // Tailwind 지시문 확인
    const hasTailwindDirectives = 
      cssContent.includes('@tailwind base') &&
      cssContent.includes('@tailwind components') &&
      cssContent.includes('@tailwind utilities');
    
    // CSS 변수 확인
    const cssVariables = cssContent.match(/--[\w-]+:/g) || [];
    
    return NextResponse.json({
      hasTailwindDirectives,
      cssVariablesCount: cssVariables.length,
      cssFileSize: cssContent.length,
      firstLines: cssContent.split('\n').slice(0, 20).join('\n')
    });
  } catch (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}