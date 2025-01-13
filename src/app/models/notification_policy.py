from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
)

from pydantic import BaseModel, Field


class Space(BaseModel):
    id: str
    labels: List[str]
    name: str

class WorkerPool(BaseModel):
    public: bool
    id: str
    name: str
    labels: List[str] = Field(default_factory=list)

class Module(BaseModel):
    id: str
    administrative: bool
    branch: str
    labels: List[str] = Field(default_factory=list)
    namespace: Optional[str] = None
    name: str
    project_root: Optional[str] = None
    repository: str
    terraform_provider: str
    space: Space
    worker_pool: WorkerPool

class Commit(BaseModel):
    author: str
    branch: str
    created_at: int
    hash: str
    message: str
    url: str

class TestRun(BaseModel):
    created_at: int
    id: str
    state: str
    title: str
    updated_at: int

class ModuleVersion(BaseModel):
    commit: Commit
    created_at: int
    id: str
    latest: bool
    number: str
    state: str
    test_runs: List[TestRun] = Field(default_factory=list)

class CreatorSession(BaseModel):
    admin: bool
    creator_ip: str
    login: str
    name: str
    teams: List[str] = Field(default_factory=list)
    machine: bool

class Entity(BaseModel):
    address: str
    data: Optional[Dict[str, Any]] = None
    name: str
    type: str
    entity_vendor: str
    entity_type: str

class Change(BaseModel):
    action: str
    entity: Entity
    phase: str
    moved: bool = False

class RuntimeConfig(BaseModel):
    after_apply: List[str] = Field(default_factory=list)
    after_destroy: List[str] = Field(default_factory=list)
    after_init: List[str] = Field(default_factory=list)
    after_perform: List[str] = Field(default_factory=list)
    after_plan: List[str] = Field(default_factory=list)
    after_run: List[str] = Field(default_factory=list)
    before_apply: List[str] = Field(default_factory=list)
    before_destroy: List[str] = Field(default_factory=list)
    before_init: List[str] = Field(default_factory=list)
    before_perform: List[str] = Field(default_factory=list)
    before_plan: List[str] = Field(default_factory=list)
    environment: Dict[str, str] = Field(default_factory=dict)
    project_root: str = ""
    runner_image: str
    terraform_version: str

class PolicyReceipt(BaseModel):
    flags: List[str] = Field(default_factory=list)
    name: str
    outcome: str
    type: str

class Run(BaseModel):
    based_on_local_workspace: bool = False
    branch: str
    changes: List[Change] = Field(default_factory=list)
    command: str = ""
    commit: Commit
    created_at: int
    creator_session: CreatorSession
    drift_detection: bool = False
    flags: List[str] = Field(default_factory=list)
    id: str
    runtime_config: RuntimeConfig
    state: str
    triggered_by: Optional[str] = None
    type: str
    updated_at: int
    user_provided_metadata: List[str] = Field(default_factory=list)
    policy_receipts: Optional[List[PolicyReceipt]] = None
    states_history: Optional[List[Dict[str, str]]] = None

class Stack(BaseModel):
    administrative: bool = False
    autodeploy: bool = False
    autoretry: Optional[bool] = None
    branch: str
    id: str
    labels: List[str] = Field(default_factory=list)
    locked_by: Optional[str] = None
    name: str
    namespace: Optional[str] = None
    project_root: Optional[str] = None
    repository: str
    space: Space
    state: str
    terraform_version: Optional[str] = None
    tracked_commit: Commit
    worker_pool: Optional[WorkerPool] = None
    additional_project_globs: Optional[List[str]] = None

class Timing(BaseModel):
    duration: int
    state: str

class Urls(BaseModel):
    run: str

class RunUpdated(BaseModel):
    state: str = ""
    username: str = ""
    note: str
    run: Run
    stack: Stack
    timing: List[Timing] = Field(default_factory=list)
    urls: Urls
    plan_policy_decision: Optional[str] = None
    policy_receipts: Optional[List[PolicyReceipt]] = None

class WebhookEndpoint(BaseModel):
    id: str
    labels: List[str] = Field(default_factory=list)

class InternalError(BaseModel):
    error: str
    message: str
    severity: str

class NotificationPolicy(BaseModel):
    account: Dict[str, str]
    run_updated: RunUpdated
    webhook_endpoints: List[WebhookEndpoint] = Field(default_factory=list)
    internal_error: Optional[InternalError] = None
    module_version: Optional[Dict[str, Union[Module, ModuleVersion]]] = None

    class Config:
        extra = "allow"  # Allow extra fields in the JSON that aren't in our model
