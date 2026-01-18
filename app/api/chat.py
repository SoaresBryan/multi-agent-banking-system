from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents import AgentOrchestrator

router = APIRouter(prefix="/chat", tags=["chat"])

sessions: dict[str, AgentOrchestrator] = {}


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    estado: dict


class SessionResponse(BaseModel):
    session_id: str
    message: str


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Envia uma mensagem para o sistema de agentes.

    - Se `session_id` nao for fornecido, cria uma nova sessao
    - Retorna a resposta do agente e o estado atual da conversa
    - As mensagens sao persistidas no MongoDB
    """
    if request.session_id and request.session_id in sessions:
        orchestrator = sessions[request.session_id]
        session_id = request.session_id
    else:
        session_id = str(uuid4())
        orchestrator = AgentOrchestrator(conversation_id=session_id)
        orchestrator.registrar_todos_agentes()
        sessions[session_id] = orchestrator

    try:
        resposta = await orchestrator.processar_mensagem(request.message)
        return ChatResponse(
            response=resposta,
            session_id=session_id,
            estado=orchestrator.get_estado(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/new", response_model=SessionResponse)
async def new_session():
    """
    Cria uma nova sessao de chat.
    """
    session_id = str(uuid4())
    orchestrator = AgentOrchestrator(conversation_id=session_id)
    orchestrator.registrar_todos_agentes()
    sessions[session_id] = orchestrator

    return SessionResponse(
        session_id=session_id,
        message="Nova sessao criada. Envie uma mensagem para iniciar o atendimento.",
    )


@router.delete("/{session_id}")
async def end_session(session_id: str):
    """
    Encerra uma sessao de chat.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessao nao encontrada")

    del sessions[session_id]
    return {"message": "Sessao encerrada com sucesso"}


@router.get("/{session_id}/estado")
async def get_session_state(session_id: str):
    """
    Retorna o estado atual de uma sessao.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessao nao encontrada")

    orchestrator = sessions[session_id]
    return orchestrator.get_estado()


@router.get("/{session_id}/historico")
async def get_session_history(session_id: str):
    """
    Retorna o historico de mensagens de uma sessao.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessao nao encontrada")

    orchestrator = sessions[session_id]
    return {"historico": orchestrator.contexto.historico}
