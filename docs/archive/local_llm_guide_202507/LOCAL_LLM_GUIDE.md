# LLM/AI 연동 가이드 요약

이 문서는 로컬 LLM 연동, AI 서비스 구조, 예시 코드를 통합 요약합니다.

## LLM 연동
- Transformers, llama.cpp, Ollama API 등 지원
- requirements.txt 예시, 환경설정 안내

## AI 서비스 구조
- SentimentAnalyzer, LLM 폴백 시스템, 대화 컨텍스트 관리

## 예시 코드
```python
from transformers import pipeline
sentiment = pipeline('sentiment-analysis')
result = sentiment('Casino-Club F2P is awesome!')
```
