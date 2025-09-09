# 테스트 실패 자동 수정 워크플로

<!-- 테스트 환경 초기화 -->
1. PowerShell 환경 설정
```powershell
cd c:/Users/task2/OneDrive/문서/GitHub/2025-2/auto202506-a/cc-webapp/backend; 
Remove-Item -Recurse -Force __pycache__,.pytest_cache
```

<!-- 의존성 설치 -->
2. 패키지 설치 및 가상환경 구성
```powershell
python -m venv c:/Users/task2/OneDrive/문서/GitHub/2025-2/auto202506-a/.venv; 
c:/Users/task2/OneDrive/문서/GitHub/2025-2/auto202506-a/.venv/Scripts/activate; 
pip install -r requirements-dev.txt
```

<!-- DB 마이그레이션 -->
3. 테스트 DB 설정
```powershell
alembic upgrade head; 
python migration_script.py test
```

<!-- 테스트 실행 -->
4. pytest 실행 및 결과 리포트 생성
```powershell
pytest tests/ -v --cov=app --cov-report=html; 
Get-Content .\test_results\.last-run.json
```

<!-- 정리 단계 -->
5. 테스트 아티팩트 삭제
```powershell
Remove-Item -Recurse -Force test*.db; 
deactivate
