from dataclasses import dataclass, asdict, is_dataclass
from typing import List, Optional, Dict, Union, Any
import json

def convert_to_dict(obj: Any) -> Any:
    """Helper function to convert objects to dictionaries recursively"""
    if is_dataclass(obj):
        return {k: convert_to_dict(v) for k, v in asdict(obj).items()}
    elif isinstance(obj, dict):
        return {k: convert_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_dict(item) for item in obj]
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    return str(obj)

@dataclass
class Space:
    id: str
    labels: List[str]
    name: str

@dataclass
class WorkerPool:
    public: bool
    id: str
    name: str
    labels: List[str]

@dataclass
class Module:
    id: str
    administrative: bool
    branch: str
    labels: List[str]
    namespace: Optional[str]
    name: str
    project_root: Optional[str]
    repository: str
    terraform_provider: str
    space: Space
    worker_pool: WorkerPool

@dataclass
class Commit:
    author: str
    branch: str
    created_at: int
    hash: str
    message: str
    url: str

@dataclass
class TestRun:
    created_at: int
    id: str
    state: str
    title: str
    updated_at: int

@dataclass
class ModuleVersion:
    commit: Commit
    created_at: int
    id: str
    latest: bool
    number: str
    state: str
    test_runs: List[TestRun]

@dataclass
class CreatorSession:
    admin: bool
    creator_ip: str
    login: str
    name: str
    teams: List[str]
    machine: bool

@dataclass
class Entity:
    address: str
    data: Optional[Dict[str, Any]]
    name: str
    type: str
    entity_vendor: str
    entity_type: str

@dataclass
class Change:
    action: str
    entity: Entity
    phase: str
    moved: bool = False

@dataclass
class RuntimeConfig:
    after_apply: List[str]
    after_destroy: List[str]
    after_init: List[str]
    after_perform: List[str]
    after_plan: List[str]
    after_run: List[str]
    before_apply: List[str]
    before_destroy: List[str]
    before_init: List[str]
    before_perform: List[str]
    before_plan: List[str]
    environment: Dict[str, str]
    project_root: str
    runner_image: str
    terraform_version: str

@dataclass
class PolicyReceipt:
    flags: List[str]
    name: str
    outcome: str
    type: str

@dataclass
class Run:
    based_on_local_workspace: bool
    branch: str
    changes: List[Change]
    command: str
    commit: Commit
    created_at: int
    creator_session: CreatorSession
    drift_detection: bool
    flags: List[str]
    id: str
    runtime_config: RuntimeConfig
    state: str
    triggered_by: Optional[str]
    type: str
    updated_at: int
    user_provided_metadata: List[str]
    policy_receipts: Optional[List[PolicyReceipt]] = None

@dataclass
class Stack:
    administrative: bool
    autodeploy: bool
    autoretry: bool
    branch: str
    id: str
    labels: List[str]
    locked_by: Optional[str]
    name: str
    namespace: Optional[str]
    project_root: Optional[str]
    repository: str
    space: Space
    state: str
    terraform_version: Optional[str]
    tracked_commit: Commit
    worker_pool: WorkerPool

@dataclass
class Timing:
    duration: int
    state: str

@dataclass
class Urls:
    run: str

@dataclass
class RunUpdated:
    state: str
    username: str
    note: str
    run: Run
    stack: Stack
    timing: List[Timing]
    urls: Urls
    plan_policy_decision: Optional[str] = None
    policy_receipts: Optional[List[PolicyReceipt]] = None

@dataclass
class WebhookEndpoint:
    id: str
    labels: List[str]

@dataclass
class InternalError:
    error: str
    message: str
    severity: str

@dataclass
class NotificationPolicy:
    account: Dict[str, str]
    run_updated: RunUpdated
    webhook_endpoints: List[WebhookEndpoint]
    internal_error: Optional[InternalError] = None
    module_version: Optional[Dict[str, Union[Module, ModuleVersion]]] = None

    def to_dict(self) -> dict:
        """Convert the notification policy to a dictionary"""
        return convert_to_dict(self)

    def to_json(self) -> str:
        """Convert the notification policy to a JSON string"""
        return json.dumps(self.to_dict())
