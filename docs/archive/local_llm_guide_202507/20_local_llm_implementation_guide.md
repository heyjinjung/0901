# 로컬 LLM 구현 가이드

## 개요
백엔드에서 로컬 LLM 대화모델을 설정하고 구현하는 방법을 안내합니다.

## 현재 상태 분석

### 이미 구현된 부분
1. **환경 변수 설정**: `.env.example`에 LLM 관련 설정 준비됨
2. **SentimentAnalyzer 클래스**: 로컬 모델 로드 인터페이스 준비됨
3. **LLM 폴백 시스템**: 구조적 준비 완료 (스텁 상태)
4. **테스트 프레임워크**: LLM 폴백 테스트 코드 작성됨

### 구현 필요한 부분
1. **실제 로컬 모델 로딩 로직**
2. **LLM 추론 엔진 통합**
3. **대화 컨텍스트 관리**
4. **모델 파일 관리**

## 구현 방안

### 1. 로컬 LLM 라이브러리 선택

#### Option A: Transformers + PyTorch
```python
# requirements.txt에 추가
transformers>=4.21.0
torch>=1.12.0
accelerate>=0.12.0
```

#### Option B: llama.cpp Python binding
```python
# requirements.txt에 추가
llama-cpp-python>=0.1.78
```

#### Option C: Ollama API 연동
```python
# requirements.txt에 추가
requests>=2.28.0
```

### 2. load_local_model() 함수 구현

#### Transformers 기반 구현 예시
```python
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from pathlib import Path

def load_local_model():
    """실제 로컬 LLM 모델 로드"""
    model_path = os.getenv('LOCAL_LLM_MODEL_PATH', '/app/models/llm/')
    model_name = os.getenv('LOCAL_LLM_MODEL_NAME', 'microsoft/DialoGPT-medium')
    
    try:
        # 로컬 경로가 존재하는지 확인
        if Path(model_path).exists():
            logger.info(f"Loading local model from {model_path}")
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForCausalLM.from_pretrained(model_path)
        else:
            logger.info(f"Downloading model {model_name}")
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # 로컬에 저장
            Path(model_path).mkdir(parents=True, exist_ok=True)
            tokenizer.save_pretrained(model_path)
            model.save_pretrained(model_path)
        
        # GPU 사용 가능한 경우 GPU로 이동
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model = model.to(device)
        
        return LocalLLMWrapper(model, tokenizer, device)
        
    except Exception as e:
        logger.error(f"Failed to load local LLM model: {e}")
        return None

class LocalLLMWrapper:
    """로컬 LLM 모델 래퍼 클래스"""
    
    def __init__(self, model, tokenizer, device):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        
        # 특별한 토큰 설정
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
    
    def generate_response(self, user_input: str, max_length: int = 100) -> str:
        """사용자 입력에 대한 응답 생성"""
        try:
            # 입력 토큰화
            inputs = self.tokenizer.encode(user_input + self.tokenizer.eos_token, 
                                         return_tensors='pt').to(self.device)
            
            # 응답 생성
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=max_length,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # 디코딩
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # 원본 입력 제거하고 응답만 반환
            response = response[len(user_input):].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return "죄송합니다. 응답을 생성하는 중 오류가 발생했습니다."
    
    def predict(self, text: str) -> dict:
        """감정 분석을 위한 예측 (기존 인터페이스 호환)"""
        response = self.generate_response(f"다음 텍스트의 감정을 분석해주세요: {text}")
        
        # 감정 키워드 매칭으로 기본 감정 추출
        emotions = {
            'happy': ['기쁘', '좋', '즐거', '행복'],
            'sad': ['슬프', '우울', '속상'],
            'angry': ['화나', '짜증', '분노'],
            'neutral': ['보통', '일반', '중립']
        }
        
        detected_emotion = 'neutral'
        for emotion, keywords in emotions.items():
            if any(keyword in response for keyword in keywords):
                detected_emotion = emotion
                break
        
        return {
            'emotion': detected_emotion,
            'confidence': 0.8,
            'llm_response': response
        }
```

### 3. call_llm_fallback() 함수 구현

```python
def call_llm_fallback(text: str) -> EmotionResult:
    """LLM 폴백 시스템 실제 구현"""
    try:
        # 환경 변수에서 API 키 확인
        openai_key = os.getenv('OPENAI_API_KEY')
        claude_key = os.getenv('CLAUDE_API_KEY')
        
        if openai_key:
            return call_openai_api(text, openai_key)
        elif claude_key:
            return call_claude_api(text, claude_key)
        else:
            raise ValueError("No LLM API keys configured")
            
    except Exception as e:
        logger.error(f"LLM fallback failed: {e}")
        raise NotImplementedError("LLM fallback failed")

def call_openai_api(text: str, api_key: str) -> EmotionResult:
    """OpenAI API 호출"""
    import openai
    
    openai.api_key = api_key
    
    prompt = f"""
    다음 텍스트의 감정을 분석하고 결과를 JSON 형식으로 반환해주세요:
    텍스트: "{text}"
    
    응답 형식:
    {{"emotion": "excited|joy|anger|sadness|neutral", "confidence": 0.0-1.0}}
    """
    
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100,
        temperature=0.3
    )
    
    result = json.loads(response.choices[0].text.strip())
    
    return EmotionResult(
        emotion=result['emotion'],
        score=result['confidence'],
        confidence=result['confidence'],
        language=detect_language(text),
        fallback_attempted=True
    )
```

### 4. 대화 서비스 통합

```python
# app/services/conversation_service.py (새로 생성)

class ConversationService:
    """로컬 LLM 기반 대화 서비스"""
    
    def __init__(self):
        self.llm_model = None
        self.load_model()
    
    def load_model(self):
        """LLM 모델 로드"""
        try:
            self.llm_model = load_local_model()
            if self.llm_model:
                logger.info("Local LLM model loaded successfully")
            else:
                logger.warning("Failed to load local LLM model")
        except Exception as e:
            logger.error(f"Error loading LLM model: {e}")
    
    async def generate_response(self, user_input: str, context: ChatContext) -> str:
        """대화 응답 생성"""
        if not self.llm_model:
            return "죄송합니다. 현재 대화 서비스가 이용 불가능합니다."
        
        # 컨텍스트 고려한 입력 구성
        context_text = self._build_context_text(context)
        full_input = f"{context_text}\n사용자: {user_input}\nAI:"
        
        return self.llm_model.generate_response(full_input)
    
    def _build_context_text(self, context: ChatContext) -> str:
        """대화 컨텍스트를 텍스트로 구성"""
        if not context.messages:
            return "안녕하세요! 무엇을 도와드릴까요?"
        
        context_lines = []
        for msg in context.messages[-5:]:  # 최근 5개 메시지만 사용
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            context_lines.append(f"{role}: {content}")
        
        return "\n".join(context_lines)
```

### 5. 환경 변수 확장

```bash
# .env에 추가할 LLM 관련 설정

# 로컬 LLM 설정
LOCAL_LLM_ENABLED=true
LOCAL_LLM_MODEL_PATH="/app/models/llm/"
LOCAL_LLM_MODEL_NAME="microsoft/DialoGPT-medium"
LOCAL_LLM_MAX_LENGTH=100
LOCAL_LLM_TEMPERATURE=0.7

# GPU 설정
USE_GPU=true
GPU_MEMORY_LIMIT=4096  # MB

# 대화 설정
CONVERSATION_CONTEXT_SIZE=5
CONVERSATION_MAX_TOKENS=150

# 폴백 설정
LLM_FALLBACK_ENABLED=true
LLM_FALLBACK_TIMEOUT=10  # seconds
```

### 6. API 엔드포인트 추가

```python
# app/routers/conversation.py (새로 생성)

from fastapi import APIRouter, Depends, HTTPException
from app.services.conversation_service import ConversationService
from app.services.cj_ai_service import ChatContext

router = APIRouter(prefix="/conversation", tags=["conversation"])

@router.post("/chat")
async def chat_with_llm(
    user_input: str,
    user_id: int,
    conversation_service: ConversationService = Depends()
):
    """로컬 LLM과 대화"""
    try:
        # 기존 컨텍스트 로드 (실제로는 데이터베이스에서)
        context = ChatContext(user_id=user_id)
        
        # LLM 응답 생성
        response = await conversation_service.generate_response(user_input, context)
        
        # 컨텍스트에 대화 추가
        context.add_message({"role": "user", "content": user_input})
        context.add_message({"role": "assistant", "content": response})
        
        return {
            "response": response,
            "user_id": user_id,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="대화 생성 중 오류가 발생했습니다.")
```

## 구현 우선순위

### Phase 1: 기본 구현
1. Transformers 라이브러리로 기본 모델 로드
2. 간단한 대화 응답 생성
3. 기존 SentimentAnalyzer와 통합

### Phase 2: 고도화
1. 대화 컨텍스트 관리
2. GPU 가속 지원
3. 모델 최적화 (양자화, 캐싱)

### Phase 3: 프로덕션 준비
1. 로드 밸런싱
2. 모델 hot-swapping
3. 성능 모니터링

## 테스트 방법

```python
# 간단한 테스트 스크립트
async def test_local_llm():
    """로컬 LLM 테스트"""
    service = ConversationService()
    
    if service.llm_model:
        response = await service.generate_response(
            "안녕하세요, 기분이 좋습니다!",
            ChatContext(user_id=1)
        )
        print(f"LLM Response: {response}")
    else:
        print("LLM model not loaded")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_local_llm())
```

## 주의사항

1. **메모리 사용량**: LLM 모델은 많은 메모리를 사용합니다 (2-8GB)
2. **응답 시간**: GPU 없이는 응답 생성이 느릴 수 있습니다
3. **모델 크기**: 모델 파일이 큰 경우 다운로드/저장 공간 고려 필요
4. **API 호환성**: 기존 코드와의 호환성 유지 필요

이 가이드를 참고하여 단계적으로 로컬 LLM을 구현하시면 됩니다.
