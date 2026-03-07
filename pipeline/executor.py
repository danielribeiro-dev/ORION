"""
Executor Module.

Responsabilidade:
    - Executar o plano de ações gerado pelo Planner.
    - Invocar plugins e ferramentas.
    - Coletar resultados brutos.
    - Atuar como PEP (Policy Enforcement Point).

v0.4.0:
    - Removido AuthService hardcoded como admin (BUG-01).
    - Usa container.current_user — usuário real carregado do profile.json.
    - AuthService agora é singleton no Container, não instanciado aqui.

Proibições:
    - OBRIGATÓRIO retornar sempre PluginResult.
"""

from typing import Any, List
from core.interfaces import BaseExecutor
from core.contracts import PluginResult, ActionLevel
from core.logger import logger


class Executor(BaseExecutor):
    """
    Motor de execução que processa o plano de ações.
    """

    def execute(self, plan: List[Any]) -> PluginResult:
        """
        Executa sequencialmente os passos do plano com validação de governança.
        format: [(plugin_name, params), ...]
        """
        from core.container import Container
        container = Container.get_instance()

        # v0.4.0: Usa o usuário da sessão persistente — sem hardcode de "admin"
        user = container.current_user

        last_result = None

        for step in plan:
            plugin_name, params = step

            # 0. Intercept SYSTEM intent estruturalmente (sem LLM)
            if plugin_name == "system":
                logger.info("[Executor] Interceptando intent SYSTEM estruturalmente.")
                system_info = (
                    f"**Identidade do Sistema ORION**\n"
                    f"Nome: {container.settings.system_name}\n"
                    f"Versão: {container.settings.version}\n"
                    f"Ambiente: {container.settings.env.value}\n\n"
                    f"**Sessão Atual**\n"
                    f"Usuário: {user.username if user else 'Desconhecido'}\n"
                    f"Role: {user.role if user else 'Desconhecido'}\n"
                    f"Dev Mode: {'Ativo' if container.profile.is_dev_mode() else 'Inativo'}\n"
                )
                if user:
                    if user.role == "admin":
                        system_info += "Permissões: Acesso Total (Nível 0, 1, 2)\n"
                    elif user.role == "power_user":
                        system_info += "Permissões: Nível 0, 1, 2 (com supervisão)\n"
                    elif user.role == "user":
                        system_info += "Permissões: Nível 0, 1, 2 (requer aprovação)\n"
                    else:
                        system_info += "Permissões: Nível 0, 1 (Somente Leitura)\n"
                else:
                    system_info += "Permissões: Nenhuma (Autenticação Necessária)\n"

                last_result = PluginResult(
                    data=[{"text": system_info}],
                    sources=[],
                    confidence=1.0,
                    degraded=False,
                    plugin="system",
                    metadata={"provider": "structural"}
                )
                continue

            plugin = container.plugins.get(plugin_name)

            if plugin:
                try:
                    # 1. Determinar ActionLevel baseado no plugin e ação
                    risk_map = {
                        "chat": ActionLevel.LEVEL_0,
                        "web": ActionLevel.LEVEL_1,
                        "memory": ActionLevel.LEVEL_1,
                        "fs": ActionLevel.LEVEL_1
                    }

                    # Ações de memória que alteram configurações são LEVEL_2
                    if plugin_name == "memory" and params.get("action") in [
                        "set_system_name", "set_user_name", "set_system_language"
                    ]:
                        risk_map["memory"] = ActionLevel.LEVEL_2

                    level = risk_map.get(plugin_name, ActionLevel.LEVEL_2)

                    # 2. Consultar Governança (GovernanceEngine)
                    intent_name = params.get("intent", plugin_name.upper())
                    governance = container.capability_guard
                    allowed = governance.validate(intent_name, user, level)

                    if not allowed:
                        logger.warning(f"[Executor] Ação '{intent_name}' bloqueada pela Governança.")
                        last_result = self._create_error_result(plugin_name, "Ação bloqueada pela política de segurança.")
                        continue

                    # 3. Confirmação PEP para ações de alto risco (LEVEL_2)
                    if level == ActionLevel.LEVEL_2:
                        from core.ui import ConsoleUI
                        confirmed = ConsoleUI.confirm_action(f"Executar Ação de Alto Risco: {plugin_name} {params}?")

                        from core.audit import AuditLogger
                        AuditLogger.log_action(user, intent_name, level, confirmed, "Confirmação do Usuário")

                        if not confirmed:
                            logger.info(f"[Executor] Ação '{intent_name}' cancelada pelo usuário.")
                            last_result = self._create_error_result(plugin_name, "Ação cancelada pelo usuário.")
                            continue

                    logger.info(f"[Executor] Executando plugin: {plugin_name} (Nível: {level.name})")
                    res = plugin.execute(params)

                    if isinstance(res, PluginResult):
                        last_result = res
                    else:
                        logger.error(f"[Executor] Plugin {plugin_name} não retornou PluginResult!")
                        last_result = self._wrap_legacy(plugin_name, res)

                except Exception as e:
                    logger.error(f"[Executor] Erro ao executar {plugin_name}: {e}")
                    last_result = self._create_error_result(plugin_name, str(e))
            else:
                logger.error(f"[Executor] Plugin '{plugin_name}' não encontrado.")
                last_result = self._create_error_result(plugin_name, "Plugin não encontrado")

        if not last_result:
            return self._create_error_result("executor", "Plano vazio ou sem resultados")

        return last_result

    def _wrap_legacy(self, plugin: str, legacy_res: Any) -> PluginResult:
        return PluginResult(
            data=[{"legacy_output": str(legacy_res)}],
            sources=[],
            confidence=0.5,
            degraded=True,
            plugin=plugin,
            metadata={"warning": "legacy_output_wrap"}
        )

    def _create_error_result(self, plugin: str, error_msg: str) -> PluginResult:
        return PluginResult(
            data=[{"error": error_msg}],
            sources=[],
            confidence=0.0,
            degraded=True,
            plugin=plugin
        )
