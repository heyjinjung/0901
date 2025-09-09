# Celery tasks
from app.core.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

@celery_app.task
def sample_task():
    """샘플 Celery 태스크"""
    logger.info("Sample task executed")
    return "Task completed successfully"

@celery_app.task
def process_user_action(user_id: int, action: str):
    """사용자 액션 처리 태스크"""
    logger.info(f"Processing action {action} for user {user_id}")
    # 여기에 실제 액션 처리 로직 추가
    return f"Action {action} processed for user {user_id}"
