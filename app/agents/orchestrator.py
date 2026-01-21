import logging
import re
import time
from pathlib import Path

from crewai import Agent, Crew, Process, Task

from app.agents.base import (
    TipoAgente,
    criar_agente_cambio,
    criar_agente_credito,
    criar_agente_entrevista,
    criar_agente_triagem,
)
from app.agents.tools.context import (
    ContextoConversa,
    reset_contexto,
    set_contexto,
)
from app.memory import ChatMemory, get_memory

logger = logging.getLogger(__name__)


def carregar_prompt(tipo_agente: TipoAgente) -> str:
    """Carrega o prompt do arquivo correspondente ao tipo de agente."""
    prompts_dir = Path(__file__).parent / "prompts"
    arquivo_map = {
        TipoAgente.TRIAGEM: "triagem_prompt.txt",
        TipoAgente.CREDITO: "credito_prompt.txt",
        TipoAgente.ENTREVISTA: "entrevista_prompt.txt",
        TipoAgente.CAMBIO: "cambio_prompt.txt",
    }

    arquivo = prompts_dir / arquivo_map[tipo_agente]
    return arquivo.read_text(encoding="utf-8")


class AgentOrchestrator:
    """Orquestra as transicoes entre agentes CrewAI."""

    REDIRECT_PATTERNS = {
        r"\[REDIRECIONA_CREDITO\]": TipoAgente.CREDITO,
        r"\[REDIRECIONA_ENTREVISTA\]": TipoAgente.ENTREVISTA,
        r"\[REDIRECIONA_CAMBIO\]": TipoAgente.CAMBIO,
        r"\[REDIRECIONA_TRIAGEM\]": TipoAgente.TRIAGEM,
    }

    def __init__(self, conversation_id: str | None = None):
        self.contexto = ContextoConversa()
        set_contexto(self.contexto)

        self.agente_atual_tipo: TipoAgente = TipoAgente.TRIAGEM
        self.agentes: dict[TipoAgente, Agent] = {}
        self.atendimento_encerrado = False
        self.conversation_id = conversation_id
        self.memory: ChatMemory | None = None

        if conversation_id:
            self._init_memory()

    def _init_memory(self) -> None:
        if self.conversation_id:
            agent_id = self.agente_atual_tipo.value
            self.memory = get_memory(agent_id, self.conversation_id)
            logger.debug(f"Memory initialized for conversation {self.conversation_id}")

    def registrar_todos_agentes(self) -> None:
        self.agentes[TipoAgente.TRIAGEM] = criar_agente_triagem()
        self.agentes[TipoAgente.CREDITO] = criar_agente_credito()
        self.agentes[TipoAgente.ENTREVISTA] = criar_agente_entrevista()
        self.agentes[TipoAgente.CAMBIO] = criar_agente_cambio()

    def _get_agente_atual(self) -> Agent:
        return self.agentes[self.agente_atual_tipo]

    def _build_task_description(self, mensagem: str) -> str:
        from app.services.credito_service import CreditoService

        credito_service = CreditoService()

        historico = "\n".join(
            [f"- {m['role']}: {m['content']}" for m in self.contexto.historico[-20:]]
        )
        if not historico:
            historico = "(inicio da conversa)"

        ctx = f"""Cliente autenticado: {'Sim' if self.contexto.cliente_autenticado else 'Nao'}
Nome: {self.contexto.nome_cliente or 'Nao identificado'}
Tentativas de auth: {self.contexto.tentativas_auth}/3"""

        nome = self.contexto.nome_cliente or "Cliente"
        score = self.contexto.score or 0
        limite_atual = self.contexto.limite_atual or 0
        limite_maximo = credito_service.obter_limite_maximo_por_score(score) if score else 0

        prompt = carregar_prompt(self.agente_atual_tipo)

        return prompt.format(
            contexto=ctx,
            historico=historico,
            mensagem=mensagem,
            nome=nome,
            score=score,
            limite_atual=limite_atual,
            limite_maximo=limite_maximo,
        )

    def _detectar_redirecionamento(self, resposta: str) -> TipoAgente | None:
        for pattern, tipo in self.REDIRECT_PATTERNS.items():
            if re.search(pattern, resposta):
                return tipo
        return None

    def _limpar_tags_resposta(self, resposta: str) -> str:
        resultado = resposta
        for pattern in self.REDIRECT_PATTERNS.keys():
            resultado = re.sub(pattern, "", resultado)
        resultado = re.sub(r"\[ENCERRA_ATENDIMENTO\]", "", resultado)
        return resultado.strip()

    def _detectar_encerramento(self, resposta: str) -> bool:
        return "[ENCERRA_ATENDIMENTO]" in resposta

    def _salvar_memoria(self, mensagem_user: str, resposta_ai: str) -> None:
        if self.memory:
            try:
                self.memory.add_user_message(mensagem_user)
                self.memory.add_ai_message(resposta_ai)
                logger.debug(f"Messages saved for conversation {self.conversation_id}")
            except Exception as e:
                logger.error(f"Error saving to memory: {e}")

    async def processar_mensagem(self, mensagem: str) -> str:
        if self.atendimento_encerrado:
            return "O atendimento foi encerrado. Para iniciar um novo atendimento, por favor reinicie a conversa."

        set_contexto(self.contexto)

        self.contexto.adicionar_mensagem("user", mensagem)

        agente = self._get_agente_atual()

        logger.info(f"=" * 60)
        logger.info(f"[ORQUESTRADOR] Agente atual: {self.agente_atual_tipo.value}")
        logger.info(f"[ORQUESTRADOR] Mensagem recebida: {mensagem[:100]}...")
        logger.info(f"[ORQUESTRADOR] Cliente: {self.contexto.nome_cliente} | Score: {self.contexto.score}")
        logger.info(f"[ORQUESTRADOR] Dados extras: {self.contexto.dados_extras}")

        task_description = self._build_task_description(mensagem)

        logger.debug(f"[ORQUESTRADOR] Task description:\n{task_description[:500]}...")

        task = Task(
            description=task_description,
            expected_output="Resposta para o cliente de forma natural e profissional",
            agent=agente,
        )

        crew = Crew(
            agents=[agente],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
        )

        try:
            logger.info(f"[ORQUESTRADOR] Iniciando execucao do Crew...")
            inicio = time.time()
            result = crew.kickoff()
            fim = time.time()
            resposta = str(result)
            logger.info(f"[ORQUESTRADOR] Crew executado em {fim - inicio:.2f}s")
            logger.info(f"[ORQUESTRADOR] Resposta bruta: {resposta[:200]}...")
        except Exception as e:
            logger.error(f"[ORQUESTRADOR] Erro ao executar crew: {e}")
            resposta = "Desculpe, ocorreu um erro no processamento. Por favor, tente novamente."

        if self._detectar_encerramento(resposta):
            logger.info(f"[ORQUESTRADOR] Encerramento detectado")
            self.atendimento_encerrado = True
            resposta = self._limpar_tags_resposta(resposta)
            self.contexto.adicionar_mensagem("assistant", resposta)
            self._salvar_memoria(mensagem, resposta)
            return resposta

        novo_agente = self._detectar_redirecionamento(resposta)
        if novo_agente:
            logger.info(f"[ORQUESTRADOR] Redirecionamento detectado: {self.agente_atual_tipo.value} -> {novo_agente.value}")
            resposta_limpa = self._limpar_tags_resposta(resposta)
            agente_anterior = self.agente_atual_tipo
            self.agente_atual_tipo = novo_agente
            if self.conversation_id:
                self.memory = get_memory(novo_agente.value, self.conversation_id)

            if agente_anterior == TipoAgente.ENTREVISTA and len(resposta_limpa.strip()) > 20:
                self.contexto.adicionar_mensagem("assistant", resposta_limpa)
                self._salvar_memoria(mensagem, resposta_limpa)

            logger.info(f"[ORQUESTRADOR] Reprocessando automaticamente com novo agente...")
            return await self._processar_com_novo_agente(mensagem)
        else:
            logger.info(f"[ORQUESTRADOR] Nenhum redirecionamento detectado")

        logger.info(f"[ORQUESTRADOR] Resposta final: {resposta[:150]}...")
        logger.info(f"=" * 60)

        self.contexto.adicionar_mensagem("assistant", resposta)
        self._salvar_memoria(mensagem, resposta)
        return resposta

    async def _processar_com_novo_agente(self, mensagem: str) -> str:
        set_contexto(self.contexto)

        logger.info(f"[NOVO_AGENTE] Processando com agente: {self.agente_atual_tipo.value}")
        logger.info(f"[NOVO_AGENTE] Dados extras: {self.contexto.dados_extras}")

        agente = self._get_agente_atual()
        task_description = self._build_task_description(mensagem)

        logger.debug(f"[NOVO_AGENTE] Task description:\n{task_description[:500]}...")

        task = Task(
            description=task_description,
            expected_output="Resposta para o cliente de forma natural e profissional",
            agent=agente,
        )

        crew = Crew(
            agents=[agente],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
        )

        try:
            logger.info(f"[NOVO_AGENTE] Iniciando execucao do Crew...")
            inicio = time.time()
            result = crew.kickoff()
            fim = time.time()
            resposta = str(result)
            logger.info(f"[NOVO_AGENTE] Crew executado em {fim - inicio:.2f}s")
            logger.info(f"[NOVO_AGENTE] Resposta bruta: {resposta[:200]}...")
        except Exception as e:
            logger.error(f"[NOVO_AGENTE] Erro ao executar crew: {e}")
            resposta = "Desculpe, ocorreu um erro no processamento. Por favor, tente novamente."

        resposta = self._limpar_tags_resposta(resposta)

        logger.info(f"[NOVO_AGENTE] Resposta final: {resposta[:150]}...")

        self.contexto.adicionar_mensagem("assistant", resposta)
        self._salvar_memoria(mensagem, resposta)
        return resposta

    def resetar(self) -> None:
        self.contexto = ContextoConversa()
        set_contexto(self.contexto)
        reset_contexto()
        self.agente_atual_tipo = TipoAgente.TRIAGEM
        self.atendimento_encerrado = False
        self.memory = None
        self.conversation_id = None

    def get_estado(self) -> dict:
        return {
            "agente_atual": self.agente_atual_tipo.value,
            "cliente_autenticado": self.contexto.cliente_autenticado,
            "nome_cliente": self.contexto.nome_cliente,
            "atendimento_encerrado": self.atendimento_encerrado,
            "mensagens": len(self.contexto.historico),
            "conversation_id": self.conversation_id,
        }
