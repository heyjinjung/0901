FROM node:20-alpine AS base
# 기본 Next.js 빌드 환경 설정
WORKDIR /app

# 의존성 설치 단계
FROM base AS deps
COPY package.json package-lock.json* ./
# 빌드 단계에서는 devDependencies도 필요(Tailwind/PostCSS 등)
# lock 불일치 시 install로 폴백
RUN npm ci || npm install

# 빌드 단계
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# .env.production 파일이 있으면 사용
RUN if [ -f .env.production ]; then cp .env.production .env; fi

# 프로덕션 빌드
RUN npm run build

# 프로덕션 이미지
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# 필요한 파일만 복사하여 이미지 크기 최소화
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json

# Standalone 모드 지원
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
## 일부 런타임 경로가 .next/*.json 매니페스트를 직접 참조하는 케이스 방지
## (standalone 모드에서는 일반적으로 필요 없으나 ENOENT 회피용으로 동봉)
RUN mkdir -p .next
COPY --from=builder /app/.next/BUILD_ID ./.next/BUILD_ID
COPY --from=builder /app/.next/routes-manifest.json ./.next/routes-manifest.json
COPY --from=builder /app/.next/prerender-manifest.json ./.next/prerender-manifest.json
COPY --from=builder /app/.next/server/app-paths-manifest.json ./.next/server/app-paths-manifest.json
COPY --from=builder /app/.next/server/middleware-manifest.json ./.next/server/middleware-manifest.json

# Next.js 런타임이 참조하는 주요 매니페스트/메타 파일 복사
# (일부 버전에서 standalone 서버가 .next/* 파일을 직접 요구함)
COPY --from=builder /app/.next/BUILD_ID ./.next/BUILD_ID
COPY --from=builder /app/.next/routes-manifest.json ./.next/routes-manifest.json
COPY --from=builder /app/.next/app-build-manifest.json ./.next/app-build-manifest.json
COPY --from=builder /app/.next/build-manifest.json ./.next/build-manifest.json
# 일부 매니페스트는 버전에 따라 생성되지 않음 → 필수 아님. 누락되어도 standalone 런타임 동작 가능.
# middleware/font/server-reference/app-paths 매니페스트는 존재할 때만 COPY (단순화: 생략)

# 포트 노출
EXPOSE 3000

ENV PORT 3000

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost:3000/ > /dev/null 2>&1 || exit 1

# 서버 시작
CMD ["node", "server.js"]
