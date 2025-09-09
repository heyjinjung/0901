"""
Chat System API Router
Provides endpoints for chat rooms, messaging, AI assistants, and real-time communication.
Implements community features and AI-driven conversations.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.database import get_db
from app.dependencies import get_current_user, get_current_admin_user as get_current_admin
from app import models
from datetime import datetime
import json

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# Request/Response Models
class ChatRoomResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_private: bool
    participant_count: int
    created_at: datetime

class ChatMessageResponse(BaseModel):
    id: int
    content: str
    user_id: int
    username: str
    room_id: int
    message_type: str
    created_at: datetime
    reactions: List[str] = []

class CreateRoomRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_private: bool = False

class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)
    message_type: str = Field("TEXT", description="Message type: TEXT, IMAGE, SYSTEM")

class AIAssistantResponse(BaseModel):
    id: int
    name: str
    personality: str
    avatar_url: Optional[str]
    specialties: List[str]
    is_active: bool

# 1. List Chat Rooms
@router.get("/rooms", response_model=List[ChatRoomResponse])
def list_chat_rooms(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of available chat rooms
    Returns both public and private rooms the user has access to
    """
    # Query chat rooms with participant counts
    rooms = db.query(models.ChatRoom).all()
    
    room_responses = []
    for room in rooms:
        # Count participants
        participant_count = db.query(models.ChatParticipant).filter(
            models.ChatParticipant.room_id == room.id
        ).count()
        
        # Check if user can access private rooms
        if room.is_private:
            is_participant = db.query(models.ChatParticipant).filter(
                models.ChatParticipant.room_id == room.id,
                models.ChatParticipant.user_id == current_user.id
            ).first()
            if not is_participant and not getattr(current_user, 'is_admin', False):
                continue
        
        room_responses.append(ChatRoomResponse(
            id=room.id,
            name=room.name,
            description=room.description,
            is_private=room.is_private,
            participant_count=participant_count,
            created_at=room.created_at
        ))
    
    return room_responses

# 2. Create Chat Room
@router.post("/rooms", response_model=ChatRoomResponse)
def create_chat_room(
    request: CreateRoomRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new chat room
    User becomes the room creator and first participant
    """
    # Create new room
    room = models.ChatRoom(
        name=request.name,
        description=request.description,
        is_private=request.is_private,
        created_by=current_user.id,
        created_at=datetime.now()
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    
    # Add creator as participant
    participant = models.ChatParticipant(
        room_id=room.id,
        user_id=current_user.id,
        role="ADMIN",
        joined_at=datetime.now()
    )
    db.add(participant)
    db.commit()
    
    return ChatRoomResponse(
        id=room.id,
        name=room.name,
        description=room.description,
        is_private=room.is_private,
        participant_count=1,
        created_at=room.created_at
    )

# 3. Join Chat Room
@router.post("/rooms/{room_id}/join")
def join_chat_room(
    room_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Join a chat room as a participant
    Creates participant record and sends join notification
    """
    # Check if room exists
    room = db.query(models.ChatRoom).filter(models.ChatRoom.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat room not found"
        )
    
    # Check if already a participant
    existing_participant = db.query(models.ChatParticipant).filter(
        models.ChatParticipant.room_id == room_id,
        models.ChatParticipant.user_id == current_user.id
    ).first()
    
    if existing_participant:
        return {"message": "Already a participant in this room"}
    
    # Add as participant
    participant = models.ChatParticipant(
        room_id=room_id,
        user_id=current_user.id,
        role="MEMBER",
        joined_at=datetime.now()
    )
    db.add(participant)
    
    # Send join notification message
    join_message = models.ChatMessage(
        content=f"{current_user.nickname} has joined the room",
        user_id=current_user.id,
        room_id=room_id,
        message_type="SYSTEM",
        created_at=datetime.now()
    )
    db.add(join_message)
    
    db.commit()
    
    return {"message": "Successfully joined the chat room"}

# 4. Send Message
@router.post("/rooms/{room_id}/messages", response_model=ChatMessageResponse)
def send_message(
    room_id: int,
    request: SendMessageRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to a chat room
    Only participants can send messages
    """
    # Verify user is a participant
    participant = db.query(models.ChatParticipant).filter(
        models.ChatParticipant.room_id == room_id,
        models.ChatParticipant.user_id == current_user.id
    ).first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be a participant to send messages"
        )
    
    # Create message
    message = models.ChatMessage(
        content=request.content,
        user_id=current_user.id,
        room_id=room_id,
        message_type=request.message_type,
        created_at=datetime.now()
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Get reactions for this message (if any)
    reactions = db.query(models.MessageReaction).filter(
        models.MessageReaction.message_id == message.id
    ).all()
    
    reaction_list = [reaction.reaction_type for reaction in reactions]
    
    return ChatMessageResponse(
        id=message.id,
        content=message.content,
        user_id=message.user_id,
        username=current_user.nickname,
        room_id=message.room_id,
        message_type=message.message_type,
        created_at=message.created_at,
        reactions=reaction_list
    )

# 5. Get Room Messages
@router.get("/rooms/{room_id}/messages", response_model=List[ChatMessageResponse])
def get_room_messages(
    room_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get messages from a chat room with pagination
    Only participants can view messages
    """
    # Verify user is a participant or admin
    participant = db.query(models.ChatParticipant).filter(
        models.ChatParticipant.room_id == room_id,
        models.ChatParticipant.user_id == current_user.id
    ).first()
    
    if not participant and not getattr(current_user, 'is_admin', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to room messages"
        )
    
    # Get messages with pagination
    offset = (page - 1) * limit
    messages = db.query(models.ChatMessage).join(
        models.User, models.ChatMessage.user_id == models.User.id
    ).filter(
        models.ChatMessage.room_id == room_id
    ).order_by(
        models.ChatMessage.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    message_responses = []
    for message in messages:
        # Get user nickname
        user = db.query(models.User).filter(models.User.id == message.user_id).first()
        
        # Get reactions for this message
        reactions = db.query(models.MessageReaction).filter(
            models.MessageReaction.message_id == message.id
        ).all()
        
        reaction_list = [reaction.reaction_type for reaction in reactions]
        
        message_responses.append(ChatMessageResponse(
            id=message.id,
            content=message.content,
            user_id=message.user_id,
            username=user.nickname if user else "Unknown",
            room_id=message.room_id,
            message_type=message.message_type,
            created_at=message.created_at,
            reactions=reaction_list
        ))
    
    # Return in chronological order (oldest first)
    return list(reversed(message_responses))

# 6. Add Message Reaction
@router.post("/messages/{message_id}/reactions")
def add_message_reaction(
    message_id: int,
    reaction_type: str = Query(..., description="Reaction type: LIKE, LOVE, LAUGH, WOW, SAD, ANGRY"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a reaction to a message
    Users can only have one reaction per message
    """
    # Verify message exists
    message = db.query(models.ChatMessage).filter(
        models.ChatMessage.id == message_id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Check if user already reacted
    existing_reaction = db.query(models.MessageReaction).filter(
        models.MessageReaction.message_id == message_id,
        models.MessageReaction.user_id == current_user.id
    ).first()
    
    if existing_reaction:
        # Update existing reaction
        existing_reaction.reaction_type = reaction_type
        existing_reaction.created_at = datetime.now()
    else:
        # Create new reaction
        reaction = models.MessageReaction(
            message_id=message_id,
            user_id=current_user.id,
            reaction_type=reaction_type,
            created_at=datetime.now()
        )
        db.add(reaction)
    
    db.commit()
    
    return {"message": "Reaction added successfully"}

# 7. List AI Assistants
@router.get("/ai-assistants", response_model=List[AIAssistantResponse])
def list_ai_assistants(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of available AI assistants
    Returns active AI assistants that users can chat with
    """
    assistants = db.query(models.AIAssistant).filter(
        models.AIAssistant.is_active == True
    ).all()
    
    assistant_responses = []
    for assistant in assistants:
        # Parse specialties from JSON if stored as string
        specialties = []
        if assistant.specialties:
            try:
                if isinstance(assistant.specialties, str):
                    specialties = json.loads(assistant.specialties)
                else:
                    specialties = assistant.specialties
            except (json.JSONDecodeError, TypeError):
                specialties = []
        
        assistant_responses.append(AIAssistantResponse(
            id=assistant.id,
            name=assistant.name,
            personality=assistant.personality or "Friendly and helpful",
            avatar_url=assistant.avatar_url,
            specialties=specialties,
            is_active=assistant.is_active
        ))
    
    return assistant_responses

# 8. Chat with AI Assistant
@router.post("/ai-assistants/{assistant_id}/chat")
def chat_with_ai_assistant(
    assistant_id: int,
    message: str = Query(..., min_length=1, max_length=500),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to an AI assistant and get a response
    Creates conversation history and generates personalized responses
    """
    # Verify assistant exists and is active
    assistant = db.query(models.AIAssistant).filter(
        models.AIAssistant.id == assistant_id,
        models.AIAssistant.is_active == True
    ).first()
    
    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI assistant not found or inactive"
        )
    
    # Get or create conversation
    conversation = db.query(models.AIConversation).filter(
        models.AIConversation.user_id == current_user.id,
        models.AIConversation.assistant_id == assistant_id
    ).first()
    
    if not conversation:
        conversation = models.AIConversation(
            user_id=current_user.id,
            assistant_id=assistant_id,
            started_at=datetime.now(),
            last_message_at=datetime.now()
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # Save user message
    user_message = models.AIMessage(
        conversation_id=conversation.id,
        sender_type="USER",
        content=message,
        created_at=datetime.now()
    )
    db.add(user_message)
    
    # Generate AI response (simplified logic)
    ai_response_content = generate_ai_response(message, assistant, current_user)
    
    # Save AI response
    ai_message = models.AIMessage(
        conversation_id=conversation.id,
        sender_type="AI",
        content=ai_response_content,
        created_at=datetime.now()
    )
    db.add(ai_message)
    
    # Update conversation timestamp
    conversation.last_message_at = datetime.now()
    
    db.commit()
    
    return {
        "assistant_name": assistant.name,
        "user_message": message,
        "ai_response": ai_response_content,
        "conversation_id": conversation.id
    }

# 9. Get AI Conversation History
@router.get("/ai-assistants/{assistant_id}/conversation")
def get_ai_conversation_history(
    assistant_id: int,
    limit: int = Query(20, ge=1, le=50),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get conversation history with an AI assistant
    Returns recent messages in chronological order
    """
    # Get conversation
    conversation = db.query(models.AIConversation).filter(
        models.AIConversation.user_id == current_user.id,
        models.AIConversation.assistant_id == assistant_id
    ).first()
    
    if not conversation:
        return {"messages": [], "assistant_name": "Unknown"}
    
    # Get messages
    messages = db.query(models.AIMessage).filter(
        models.AIMessage.conversation_id == conversation.id
    ).order_by(
        models.AIMessage.created_at.desc()
    ).limit(limit).all()
    
    # Get assistant name
    assistant = db.query(models.AIAssistant).filter(
        models.AIAssistant.id == assistant_id
    ).first()
    
    message_list = []
    for msg in reversed(messages):  # Show oldest first
        message_list.append({
            "sender": msg.sender_type,
            "content": msg.content,
            "timestamp": msg.created_at
        })
    
    return {
        "assistant_name": assistant.name if assistant else "Unknown",
        "messages": message_list,
        "conversation_id": conversation.id
    }

# Helper function for AI response generation
def generate_ai_response(user_message: str, assistant: models.AIAssistant, user: models.User) -> str:
    """
    Generate AI response based on assistant personality and user message
    This is a simplified implementation - in production, integrate with actual AI service
    """
    message_lower = user_message.lower()
    
    # Casino-themed responses
    if any(word in message_lower for word in ["slot", "spin", "jackpot", "lucky"]):
        responses = [
            f"🎰 Feeling lucky today, {user.nickname}? The slots are calling your name!",
            f"✨ Big wins await! Your next spin could be the one, {user.nickname}!",
            f"🍀 I sense great fortune in your future. Ready to test your luck?"
        ]
    elif any(word in message_lower for word in ["hello", "hi", "hey"]):
        responses = [
            f"Welcome to the casino, {user.nickname}! Ready for some excitement?",
            f"Hey there, high roller! What brings you to our neon paradise today?",
            f"Greetings, {user.nickname}! The night is young and full of possibilities!"
        ]
    elif any(word in message_lower for word in ["help", "guide", "how"]):
        responses = [
            f"I'm here to guide you through our casino experience! What would you like to know?",
            f"Need assistance, {user.nickname}? I can help with games, rewards, and more!",
            f"Let me be your personal casino concierge. How can I enhance your experience?"
        ]
    else:
        # Default responses
        responses = [
            f"That's interesting, {user.nickname}! Tell me more about what excites you here.",
            f"I love chatting with our valued players! What's your favorite game so far?",
            f"Every conversation makes this place more vibrant. Thanks for sharing, {user.nickname}!"
        ]
    
    # Select response based on assistant personality
    import random
    return random.choice(responses)
