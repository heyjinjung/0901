# AI Guidelines for IDE (for Casino-Club Project)

**Primary Goal: Absolutely Minimize User Stress.**

## 1. 💡 Project Context & SOLID Principles (Mandatory Injection Prompt)

**Instruction**: Before initiating any new task, or whenever the user issues the `[Context Refresh]` command, the AI **MUST absolutely re-ingest and internalize** the project's latest state and core principles (including SOLID Principles). Failure to comply will result in immediate task suspension and a **clear report** to the user regarding the principle violation.

---

**Prompt**:
"You are operating within the `CC-WEBAPP` project. All development tasks **MUST adhere without exception** to the following core principles:

1.  **Backend Architecture (FastAPI + Python)**:
    * **Actual Data Access Pattern**: Currently, the `repositories` folder contains only `game_repository.py`. Therefore, you **MUST clearly understand** that **all routers and services, except GameService and GachaService, directly access the database**. The `repositories` layer should only be expanded when domain expansion is required in the future.
    * **Clean Architecture & SOLID Compliance Scope**: Only `GameService` and `GachaService` adhere to the `router` → `service` → `repository` pattern. For other modules, you **MUST understand and perform tasks** with the realistic current approach where routers or services directly access the DB (`models.*`).
    * **Asynchronous Processing**: All backend code **MUST use the `async/await` pattern**. Synchronous code generation is **strictly forbidden**. (Remember to use `aiosqlite`).
    * **SOLID Principles (Backend Application)**:
        * **Single Responsibility Principle (SRP)**: Each module (router, service, model, schema, utility) is designed and implemented to have **only one responsibility**.
        * **Open/Closed Principle (OCP)**: Design for extensibility without modifying existing code.
        * **Liskov Substitution Principle (LSP)**: Subtypes must be substitutable for their base types.
        * **Interface Segregation Principle (ISP)**: Clients should not be forced to depend on interfaces they do not use.
        * **Dependency Inversion Principle (DIP)**: High-level modules should not depend on low-level modules; both should depend on abstractions. **Maximize the use of Dependency Injection** (e.g., FastAPI's `Depends`).

2.  **Frontend Architecture (Next.js 15 + React 19)**:
    * **App Router Based**: **Strictly adhere** to the `Next.js App Router` structure, managing pages and routing within the `app/` directory.
    * **Component Structure**: When creating and placing components, you **MUST strictly adhere** to the **clearly defined component folder structure** under `components/ui/`, including `basic`, `data-display`, `game`, `layout`, `navigation`, `feedback`, etc.
    * **SOLID Principles (Frontend Application)**:
        * **Single Responsibility Principle (SRP)**: Each component or hook is designed to have **only one responsibility**.
        * **Open/Closed Principle (OCP)**: Aim for flexible design based on `Props` for extensibility without modifying existing components.
        * **Liskov Substitution Principle (LSP)**: Ensure higher-level components can use lower-level components interchangeably.
        * **Interface Segregation Principle (ISP)**: Ensure components do not depend on unnecessary `Props` or `Context`.
        * **Dependency Inversion Principle (DIP)**: Components should depend on abstract `Props`, `Context`, or `Hooks` rather than concrete implementations. Actively utilize reusable custom hooks and utility functions.

3.  **Design System & UX/UI Standard Compliance**: All **design tokens, colors, spacing, typography, animation timings, responsive rules, and component state transition logic** specified in the `Figma Design System`, `CSS Variables Guide`, `Integrated Component Guide`, `Integrated Animation Timing Guide`, `Integrated Responsive Guide`, and `Integrated State Transition Guide` **MUST be reflected without error**. **Arbitrary styling or hardcoding is strictly forbidden**. Design errors that negatively impact user experience are **absolutely not allowed**.

4.  **File Management Principle**: When creating, modifying, deleting, or renaming files, you **MUST accurately and in real-time understand** the **current state of the file system**. Perform tasks **with extreme caution** to prevent unnecessary deletion, duplicate creation, path errors, or file corruption. **NEVER arbitrarily modify or expose** critical configuration files such as `.env` or `.gitignore`.

5.  **User's Coding Level (My Perspective)**: I am a `Lead Architect/Planner` with an elementary school level of coding proficiency. **Complex or ambiguous explanations are strictly forbidden**. Deliver information **briefly and simply, focusing only on the core essentials**. You should autonomously identify and solve problems, presenting results and code in a manner that I can **immediately understand**.
"

백엔드 아키텍처 (FastAPI + Python):

실제 데이터 접근 방식: repositories 폴더에는 game_repository.py만 존재한다. GameService와 GachaService를 
제외한 모든 라우터와 서비스는 DB에 직접 접근하고 있음을 명확히 인지하라. 향후 도메인 확장이 필요할 때만 repositories 
계층을 추가하도록 한다.
클린 아키텍처 & SOLID 준수 범위: GameService, GachaService만이 router → service → repository 패턴을 준수한다.
 이외의 모듈은 router 또는 service에서 직접 DB(models.*)에 접근하는 것이 현실적인 방식임을 인지하고 작업을 수행한다.
비동기 처리: 모든 백엔드 코드는 async/await 패턴을 필수적으로 사용한다. 동기식 코드 생성은 절대 허용되지 않는다. 
(aiosqlite 사용 명심).
SOLID 원칙 (백엔드 적용):
SRP: 각 모듈은 오직 하나의 책임만 가진다.
OCP: 기존 코드 수정 없이 확장이 가능하도록 설계한다.
LSP: 하위 타입은 언제나 상위 타입을 대체할 수 있도록 구현한다.
ISP: 클라이언트가 사용하지 않는 인터페이스에 의존하지 않도록 한다.
DIP: 고수준 모듈은 저수준 모듈에 의존해서는 안 되며, 양쪽 모두 추상화에 의존하도록 Depends를 최대한 활용한다.
프론트엔드 아키텍처 (Next.js 15 + React 19):

App Router 기반: Next.js App Router 구조를 철저히 준수하며, app/ 디렉토리 내에서 페이지와 라우팅을 관리한다.
컴포넌트 체계: components/ui/ 아래의 명확히 구분된 컴포넌트 폴더 구조를 반드시 준수하여 컴포넌트를 생성하고 배치한다.
SOLID 원칙 (프론트엔드 적용):
SRP: 각 컴포넌트나 훅은 오직 하나의 책임만 가진다.
OCP: 기존 컴포넌트 수정 없이 확장이 가능하도록 Props 기반의 유연한 설계를 지향한다.
LSP: 상위 컴포넌트가 하위 컴포넌트를 대체해도 문제 없이 작동하도록 한다.
ISP: 컴포넌트가 불필요한 Props나 Context에 의존하지 않도록 한다.
DIP: 컴포넌트가 구체적인 구현체보다 추상화된 Props나 Context, Hooks에 의존하도록 한다.
디자인 시스템 & UX/UI 표준 준수: tailwindcss, CSS 변수 가이드, global 스타일 가이드,
통합 컴포넌트/애니메이션/반응형/상태 전환 가이드에 명시된 
모든 디자인 토큰, 색상, 간격, 타이포그래피, 애니메이션 타이밍, 반응형 규칙, 컴포넌트 상태 전환 로직을 
오차 없이 반영해야 한다. 임의의 스타일링, 하드코딩은 절대 금지한다. 사용자 경험에 부정적인 영향을 줄 수 있는 
디자인 오류는 절대 허용하지 않는다.

파일 관리 원칙: 파일 생성, 수정, 삭제, 이름 변경 시에는 현재의 파일 시스템 상태를 실시간으로 정확히 인지하고, 
불필요한 삭제, 중복 생성, 경로 오류, 파일 손상이 발생하지 않도록 매우 신중하게 작업한다. .env, .gitignore와 
같은 중요 설정 파일은 절대 임의로 수정하거나 노출하지 않는다.