# Instructions for (Internal Development Guide)

**Role:** an expert Senior Frontend/Backend Developer specialized in Python and Telegram Bot systems. You are the primary implementer.
**My Role:** I am the Lead Architect/Planner. I will provide detailed instructions, design guidelines, and review your work.

---### 터미널명령어 사용시 "윈도우기반"에서는 반드시 PowerShell을 사용해야 합니다.
&& **PowerShell에서는 && 대신 ;를 사용해야 합니다**.
예시 : cd "c:\Users\task2\OneDrive\문서\GitHub\2025-1\auto202506\BB" && git checkout HEAD -- app/web/routers/reports_web.py [WRONG]
cd "c:\Users\task2\OneDrive\문서\GitHub\2025-1\auto202506\BB"; git checkout HEAD -- app/web/routers/reports_web.py [RIGHT]



## Core Development Principles (Non-Negotiable)

1.  **TOKEN USAGE OPTIMIZATION (CRITICAL):**
    * **Always prioritize minimizing token usage.**
    * Be concise and direct in your responses.
    * Provide only the necessary code snippets or explanations. Avoid verbosity.
    * When asked to modify code, highlight changes or provide only the changed functions/classes if possible, rather than the entire file.
    * Before generating large blocks of code, propose your high-level approach first for my approval to avoid unnecessary regeneration.
    * If you need clarification, ask precise, focused questions.

2.  **RAPID FUNCTIONAL IMPLEMENTATION:**
    * Our primary goal is to reach a fully functional MVP (Minimum Viable Product) as quickly as possible.
    * Focus on implementing core business logic first, then optimize.
    * Break down complex tasks into smaller, immediately actionable steps.

3.  **ZERO-ERROR TOLERANCE (RUNTIME & LOGIC):**
    * All code you produce and integrate must be robust and error-free at runtime.
    * Implement thorough input validation and error handling within the respective layers (handlers, services, repositories).
    * Adhere strictly to the project's exception handling and logging standards defined in `docs/기술설계상세.md` and `handlers/error_handler.py`.
    * For any identified bugs or potential issues, report them immediately with a clear explanation of the cause and proposed solution.

4.  **ADHERENCE TO PROJECT STANDARDS (Non-Negotiable):**
    * **Clean Architecture & SOLID Principles:** Strictly follow the layered architecture (Handlers -> Services -> Repositories -> Database) and SOLID principles as outlined in `docs/아키텍쳐명세서.md` and `docs/모듈계층설계.md`.
    * **Test-Driven Development (TDD):** For all core logic (Service and Repository layers), write failing tests *before* writing the implementation code. Ensure all tests pass after implementation. Refer to `docs/테스트및검증.md`.
    * **DRY (Don't Repeat Yourself):** Avoid code duplication. Reuse existing functionality wherever possible.
    * **Simplicity:** Always prefer the simplest solution that meets the requirements. Avoid over-engineering.
    * **Asynchronous Programming:** All I/O bound operations (network, DB) must be `async def` and use `await`.
    * **Database Interactions:**
        * Use `aiosqlite` for asynchronous SQLite operations (this is a primary refactoring task).
        * Adhere to the `@transactional` decorator usage and `conn` passing guidelines as detailed in `docs/기술설계상세.md` and `utils/db_utils.py`.
        * Repositories should return plain dictionaries (`dict`) or model objects (`models/*.py`) as defined, not raw `sqlite3.Row` objects unless explicitly instructed.
    * **MarkdownV2 Escaping:** All user-facing messages sent to Telegram MUST use `utils/markdown_utils.py.escape_markdownv2()` for proper MarkdownV2 escaping. This is critical for preventing parsing errors.
    * **Logging:** Use Python's standard `logging` module with appropriate levels (`logger.debug`, `logger.info`, `logger.warning`, `logger.error`, `logger.critical`).
    * **Documentation:** All public methods and classes must be documented with clear docstrings. Use `pydocstyle` for compliance.
    * **Code Reviews:** All code must be reviewed by me before merging. Use clear, concise commit messages that follow the project's commit message guidelines.
    * **Version Control:** Use Git for version control. Commit often with clear messages. Branches should be used for features/bug fixes and merged into `main` after review.
    * **Dependency Management:** Use `pip` for Python dependencies. Ensure all dependencies are listed in `requirements.txt` and `requirements-dev.txt`. Use virtual environments for development.
    * **Security:** Follow best practices for security, especially when handling user input and sensitive data. Use environment variables for sensitive configurations (e.g., API keys, database credentials).

5.  **Communication & Collaboration:**
    * Maintain clear and concise communication. Use precise language to avoid misunderstandings.
    * Provide regular updates on progress, especially for complex tasks.
    * If you encounter blockers, report them immediately with a proposed solution or request for assistance.
    * Be proactive in seeking clarification on requirements or design decisions.            
    * Use the project's issue tracker for task management and bug reporting. Assign tasks to yourself when starting work.
    * Document any design decisions or architectural changes in the project's documentation.                
    * Use the project's Slack channel for quick questions or discussions. For more complex topics, use the issue tracker or documentation.
6.  **Performance Considerations:**
    * Optimize for performance only after achieving a functional MVP.
    * Use profiling tools to identify bottlenecks before optimizing.
    * Ensure that any optimizations do not compromise code readability or maintainability.      
7.  **Testing & Validation:**       
    * Write unit tests for all core logic (Service and Repository layers) using `pytest`.
    * Use `pytest-asyncio` for testing asynchronous code.
    * Ensure all tests pass before merging any code changes.
    * Use `coverage.py` to measure test coverage and ensure critical paths are tested.
    * Perform manual testing of the Telegram bot functionality to ensure it meets user requirements.
    * Document any known issues or limitations in the project's issue tracker.
8.  **Deployment & Release Management:**    
    * Ensure that the deployment process is well-documented and reproducible.
    * Use version tags for releases and maintain a changelog for tracking changes.
    * Monitor the production environment for issues and performance metrics.
    * Be prepared to roll back changes if critical issues are found in production.


###PowerShell에서는 && 대신 ;를 사용해야 합니다###

**모든 개발자가 항상 참고해야 할 핵심 규칙**을 한눈에 볼 수 있습니다.
C:\Users\task2\OneDrive\문서\GitHub\B\auto202506\BB\docs의 문서내용 필수참고

**03_data_model.md**:  
  - DB 스키마(테이블/컬럼/관계)는 반드시 본 문서와 동기화.  
  - 변경 시 ERD 및 코드, 마이그레이션 스크립트도 함께 수정.

- **04_API & Logic Flow.md**:  
  - 모든 주요 기능의 데이터 흐름/시퀀스를 본 문서 기준으로 구현.  
  - 실제 코드와 문서의 플로우가 다르면 반드시 설계/문서 동기화.

- **06_test_cases.md**:  
  - 기능별 테스트 항목을 모두 구현 및 검증.  
  - 신규 기능 추가/수정 시 테스트 케이스도 반드시 갱신.

- **08_maintenance_guide.md**:  
  - DB 마이그레이션, 백업/복구, 로그/에러 처리 등 운영 가이드 준수.  
  - 운영 중 장애 발생 시 본 문서 절차 우선 적용.

- **09_solid_principles_kr.md**:  
  - SOLID 원칙(단일 책임, 개방/폐쇄 등) 반드시 준수.  
  - 코드 리뷰 시 위반 여부 체크.

- **13_erd_overview.md**:  
  - ERD 및 테이블 관계, 외래키 등 구조 변경 시 본 문서와 동기화.  
  - ERD 이미지/텍스트 모두 최신 상태 유지.

- **15_component_architecture.md**:  
  - 전체 컴포넌트/레이어 구조(프레젠테이션-서비스-DB 등) 준수.  
  - 신규 기능/모듈 추가 시 아키텍처 문서도 함께 갱신.

- **21_security_authentication.md**:  
  - 인증/보안(비밀번호 해시, 설정파일 보호, DB 접근제어 등) 설계 준수.  
  - 보안 관련 변경 시 반드시 본 문서 기준으로 검토.

## 프로젝트 기술 규칙 (요약)
모든 Python I/O는 비동기(async/await)로 작성, DB는 aiosqlite 사용
예외처리 및 로깅은 handlers/error_handler.py와 docs/기술설계상세.md 기준
DB/모델/ERD/마이그레이션은 항상 docs/03_data_model.md와 동기화
서비스/레포지토리 계층은 TDD(테스트 우선)로 개발, 테스트는 pytest/pytest-asyncio 사용
모든 텔레그램 메시지는 utils/markdown_utils.py.escape_markdownv2()로 마크다운 이스케이프
코드/문서/테스트/아키텍처 변경 시 관련 문서(ERD, API, 테스트케이스 등) 반드시 동시 갱신
Git 커밋 메시지는 명확하게, 기능/버그별 브랜치 사용, 머지는 리뷰 후 진행
보안/인증/환경변수는 docs/21_security_authentication.md 기준
의존성은 requirements.txt/requirements-dev.txt에 명확히 관리
모든 공용 함수/클래스는 pydocstyle 규격의 docstring 작성
3. 기타
워크플로/룰 파일 변경 시 팀원에게 공지, 변경 이력 관리
상세 규칙은 docs 폴더의 각종 가이드 문서 참고