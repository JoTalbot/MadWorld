"""Authoritative contract lifecycle built on the existing transactional job boundary."""

from __future__ import annotations

from datetime import timedelta
from uuid import UUID

from app.application.errors import IdempotencyConflict, NotFound
from app.application.services import InventoryService, JobService, WalletService
from app.application.ports import UnitOfWork
from app.domain.contracts import ContractTemplate, TEMPLATES_BY_CODE
from app.domain.primitives import JobState, utc_now

CONTRACT_JOB_TYPE = "contract"


class ContractService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    @staticmethod
    def templates() -> list[ContractTemplate]:
        from app.domain.contracts import CONTRACT_TEMPLATES
        return list(CONTRACT_TEMPLATES)

    def accept(self, owner_id: UUID, template_code: str, inventory_id: UUID, wallet_id: UUID, idempotency_key: str):
        template = TEMPLATES_BY_CODE.get(template_code)
        if template is None:
            raise NotFound("contract template not found")
        existing = self.uow.jobs.get_by_idempotency_key(idempotency_key)
        if existing is not None:
            if existing.job_type != CONTRACT_JOB_TYPE or existing.owner_id != owner_id or existing.metadata.get("template_code") != template_code:
                raise IdempotencyConflict("idempotency key already belongs to another contract")
            return existing
        now = utc_now()
        metadata = {
            "template_code": template.code,
            "contract_type": template.contract_type.value,
            "title": template.title,
            "description": template.description,
            "item_definition_id": str(template.item_definition_id),
            "required_quantity": template.required_quantity,
            "reward": template.reward,
            "penalty": template.penalty,
            "inventory_id": str(inventory_id),
            "wallet_id": str(wallet_id),
        }
        job = JobService(self.uow).create(owner_id, CONTRACT_JOB_TYPE, now, now + timedelta(seconds=template.duration_seconds), idempotency_key, metadata)
        JobService(self.uow).start(job.id)
        return self.uow.jobs.get(job.id) or job

    def get(self, contract_id: UUID, owner_id: UUID):
        job = self.uow.jobs.get(contract_id)
        if job is None or job.job_type != CONTRACT_JOB_TYPE or job.owner_id != owner_id:
            raise NotFound("contract not found")
        return job

    def complete(self, contract_id: UUID, owner_id: UUID, now=None):
        job = self.get(contract_id, owner_id)
        if job.state is JobState.COMPLETED:
            return job
        current = now or utc_now()
        if current >= job.completes_at:
            job.cancel()
            self.uow.jobs.save(job)
            return job
        item_id = UUID(job.metadata["item_definition_id"])
        inventory_id = UUID(job.metadata["inventory_id"])
        wallet_id = UUID(job.metadata["wallet_id"])
        required = int(job.metadata["required_quantity"])
        stack = self.uow.inventories.get_stack(inventory_id, item_id)
        if stack is None or stack.quantity < required:
            raise ValueError("contract delivery requirements are not satisfied")
        InventoryService(self.uow).remove(inventory_id, item_id, required)
        WalletService(self.uow).post_entry(wallet_id, int(job.metadata["reward"]), f"contract:{job.metadata['template_code']}", f"contract-reward:{job.id}", owner_id)
        completed = JobService(self.uow).complete(contract_id, current)
        event = __import__("app.domain.events", fromlist=["DEFAULT_EVENT_REGISTRY"]).DEFAULT_EVENT_REGISTRY.create("contract.completed", "contract", contract_id, {"template_code": job.metadata["template_code"], "reward": int(job.metadata["reward"]), "owner_id": str(owner_id)})
        self.uow.audit.append(event.event_type, event.aggregate_type, contract_id, event.to_dict())
        self.uow.outbox.enqueue(event.event_type, event.aggregate_type, contract_id, event.to_dict())
        return completed

    def cancel(self, contract_id: UUID, owner_id: UUID):
        job = self.get(contract_id, owner_id)
        if job.state is JobState.COMPLETED:
            raise ValueError("completed contract cannot be cancelled")
        cancelled = JobService(self.uow).cancel(contract_id)
        event = __import__("app.domain.events", fromlist=["DEFAULT_EVENT_REGISTRY"]).DEFAULT_EVENT_REGISTRY.create("contract.cancelled", "contract", contract_id, {"template_code": job.metadata["template_code"], "owner_id": str(owner_id)})
        self.uow.audit.append(event.event_type, event.aggregate_type, contract_id, event.to_dict())
        self.uow.outbox.enqueue(event.event_type, event.aggregate_type, contract_id, event.to_dict())
        return cancelled
