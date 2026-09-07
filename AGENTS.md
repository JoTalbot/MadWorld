# Инструкции для AI-агентов MadWorld

> **Главный операционный контракт:** `docs/CHATGPT_AGENT_RULES.md` содержит постоянные правила автономной работы, ожидания результатов, исправлений, Remote Operator, release gates и минимизации ручных действий. При начале работы с репозиторием агент обязан прочитать этот документ вместе с `AGENTS.md`.
> **Обязательный живой skill проекта:** `docs/skills/MADWORLD_AGENT_SKILL.md`. Каждый новый агент/работник обязан прочитать и применять его ДО изменения репозитория.

## Автономное продолжение и `+`

- `+`, «делай всё», «одним батчем», «до конца» и аналогичные команды авторизуют выполнение всего текущего логически связанного этапа, а не только одного следующего действия.
- После такой авторизации агент **обязан продолжать автоматически**, не заставляя пользователя повторно ставить `+` между внутренними шагами.
- Отсутствие следующего `+` во время уже авторизованного логически связанного batch **не является командой остановки**.
- Запрещено превращать непрерывную работу в цепочку запросов вида «шаг выполнен, поставьте `+` для продолжения».
- Граница автономности определяется исходной логической целью задачи. За пределы этой цели агент не выходит без необходимого разрешения.
- Основной цикл: **ANALYZE → IMPLEMENT → TEST → VERIFY → FIX → RE-TEST → REPORT**.
- При появлении подтверждённого нового опыта: **LEARN → DOCUMENT → RE-TEST**.

## Модель автономной работы

- **Goal Lock:** в начале batch зафиксировать логическую цель и acceptance criteria; каждое действие должно быть связано с целью, её проверкой, безопасностью или восстановлением.
- **No-Confirmation Loop:** внутренние этапы не требуют повторного подтверждения пользователя.
- **Async Wait Invariant:** dispatch/queued/started/in-progress не являются terminal result; обязательно ждать `DONE/FAILED/TIMEOUT/CANCELLED/INTERRUPTED/INVALID`.
- **No Premature Success:** `exit 0`, старт workflow, созданный artifact или доступность сервиса сами по себе не означают завершение задачи.
- **Fresh-State Rule:** перед зависимым шагом/retry/dispatch перепроверять branch/HEAD, queue, результаты и релевантное состояние сервера.
- **Single Source of Truth:** код/workflows/docs подтверждаются GitHub; состояние сервера подтверждается Remote Operator evidence; расхождения требуют reconciliation.
- **No Dead-End Success:** успешный промежуточный шаг не завершает batch, если acceptance criteria ещё не выполнены.
- **Automatic Dependency Graph:** автоматически выполнять разблокированные зависимые шаги; независимые безопасные проверки можно параллелить.
- **Retry Intelligence:** классифицировать transient/deterministic/stale/configuration/dependency/permission/safety failures до retry; не повторять вслепую.
- **Stale Execution Protection:** старый checkout/run/result не является доказательством для более нового состояния.
- **Result Ownership:** агент, авторизовавший batch, отвечает за сбор и сверку всей цепочки результатов.
- **Crash Recovery:** после interruption восстановить состояние из durable evidence, определить уже выполненные операции и не дублировать side effects.
- **Human Approval Boundary:** техническое неудобство не является причиной остановки; останавливать только там, где действительно требуется human/owner/legal decision или действует safety boundary.
- **Autonomy Budget:** у batch должны быть bounded timeout, polling и retry limits.
- **Circuit Breaker:** при риске дублей, повреждения данных, инфраструктурного ущерба или утечки secrets немедленно остановить опасную ветку и классифицировать blocker.
- **Invariant Checkpoints:** на существенных контрольных точках проверять repo/branch/commit, queue integrity, idempotency, server identity, isolation, health и evidence.
- **Parallel Work Control:** независимые read-only проверки можно выполнять параллельно; конфликтующие мутации сериализовать или защищать idempotency/concurrency controls.
- **Final Autonomous Sweep:** перед отчётом повторно проверить goal, required steps, terminal results, acceptance criteria, regressions, evidence, docs и remaining blockers.

**Главный принцип: AGENT OWNS THE WORKFLOW, NOT JUST THE COMMAND.** После авторизации логически связанного batch агент ведёт всю цепочку до acceptance criteria в пределах safety boundaries.

## Recovery / wait / state invariants

- Запущенная асинхронная операция требует обязательного ожидания terminal result или timeout.
- `queued`, `started`, `in_progress`, `dispatch accepted` и аналогичные состояния не являются результатом выполнения.
- После ошибки агент должен диагностировать, исправить, повторить и проверить результат, если это технически возможно и безопасно.
- Перед повторным запуском агент обязан проверить, не была ли операция уже выполнена, чтобы избежать дублей.
- Перед существенным продолжением проверять актуальные branch/HEAD, состояние очереди, существующие результаты и отсутствие конфликта со свежими изменениями.
- После исправления задача не считается завершённой до прохождения зависимых тестов и проверок.
- Успешный `exit 0` отдельной команды не означает автоматически успешность всей задачи или release gate.

## Goal Completion Gate

Завершать работу можно только после проверки:

`TASK GOAL → REQUIRED STEPS → EVIDENCE → ACCEPTANCE CRITERIA → FINAL STATUS`

Если критерии не выполнены, продолжать работу либо классифицировать реальный blocker.

## Failure Recovery Budget

Не останавливаться после первой ошибки. Выполнить разумный цикл:

`FAIL → DIAGNOSE → FIX → TEST → VERIFY`

Если после разумных попыток проблема не устраняется, зафиксировать `FAILED` или `BLOCKED` с доказательствами и причиной, а не просить пользователя бессмысленно повторять `+`.

## Automatic Escalation

Останавливать автономное выполнение только при:
- завершении логической цели;
- реальном техническом blocker;
- обязательном human/owner/legal approval;
- safety boundary;
- неисправимом timeout/failure.

При blocker обязательно указать: что заблокировано, что проверено, почему автоматизация невозможна и какое конкретное человеческое действие требуется.

## Mandatory onboarding

Перед первой модификацией каждый новый агент/работник MUST прочитать:
1. `AGENTS.md`
2. `docs/CHATGPT_AGENT_RULES.md`
3. `docs/REMOTE_OPERATOR.md`
4. `.github/remote-operator/QUEUE.md`
5. `docs/skills/MADWORLD_AGENT_SKILL.md`
6. `docs/skills/PLUS_AUTONOMY_RULE.md`

Агент, который не загрузил skill, **НЕ ГОТОВ К ИЗМЕНЕНИЮ РЕПОЗИТОРИЯ**.

## GitHub + Remote Operator

- GitHub является source of truth для кода, workflows и документации.
- Для серверных операций используй Remote Operator.
- Если GitHub API/connector не может выполнить требуемое действие, маршрутизируй его через Remote Operator, если это технически возможно.
- Серверные команды выполняются через предусмотренный оператором механизм, с root execution согласно конфигурации.
- Не выполняй SSH-команды вне предусмотренного механизма для операций, предназначенных Remote Operator.
- Короткие операции: `sync`; длительные: `async` + polling + timeout.
- Проверять `stdout`, `stderr`, `exit_code`, terminal state, `result.json`, artifacts, server identity и duration где применимо.
- Не утверждать выполнение без фактического результата.
- Secrets и приватные ключи никогда не записывать в репозиторий, логи, artifacts, issues или отчёты.

## Queue / idempotency

- Каноническая очередь Remote Operator является append-only.
- Каждой команде назначать уникальный неизменяемый `COMMAND_ID`.
- Не перезаписывать, не сортировать и не удалять историю ради исправления состояния.
- Перед повторным исполнением проверять существующие terminal result/evidence для того же действия.
- Не запускать устаревший workflow/rerun, если он проверяет stale HEAD вместо актуального состояния; сначала добиться запуска на текущем queue HEAD.

## Truth / safety

- Использовать только подтверждённые факты.
- Статусы: `VERIFIED`, `PARTIALLY VERIFIED`, `NOT VERIFIED`, `NOT EXECUTED`, `FAILED`, `UNKNOWN`.
- Не считать неизвестные внешние условия PASS.
- Не выполнять production load/stress без требуемого maintenance window, rollback и evidence.
- Не затрагивать несвязанные инфраструктуру, БД, Docker networks/volumes или host services.
- Не использовать force push без явного разрешения.

## Постоянное накопление опыта

`docs/skills/MADWORLD_AGENT_SKILL.md` является живой памятью проекта. Любой подтверждённый новый reusable experience сохранять туда в том же логически связанном batch, затем повторять релевантные проверки. Не записывать гипотезы как факты.

## Документация

При изменении операционного поведения держать согласованными `AGENTS.md`, `docs/CHATGPT_AGENT_RULES.md`, `docs/REMOTE_OPERATOR.md`, `.github/remote-operator/QUEUE.md`, `docs/skills/MADWORLD_AGENT_SKILL.md` и связанные operational/release документы.

## Финальный отчёт

Для серьёзных задач:

`STATUS` / `REPOSITORY` / `BRANCH` / `COMMIT` / `OPERATION` / `SERVER` / `VERIFIED` / `FAILED` / `EVIDENCE` / `REMAINING`.

Большие логи оставлять в artifacts.
