import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from spacelift import Spacelift
from dotenv import load_dotenv
import gql

# Load environment variables
load_dotenv()

app = FastAPI(title="Spacelift API", description="FastAPI wrapper for Spacelift operations")

# Initialize Spacelift client
def get_spacelift_client():
    try:
        return Spacelift(
            base_url=os.getenv("SPACELIFT_BASE_URL"),
            key_id=os.getenv("SPACELIFT_KEY_ID"),
            key_secret=os.getenv("SPACELIFT_KEY_SECRET")
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

# Pydantic models for request/response
class StackCommit(BaseModel):
    authorLogin: Optional[str] = None
    authorName: Optional[str] = None
    hash: Optional[str] = None
    message: Optional[str] = None
    timestamp: Optional[int] = None
    url: Optional[str] = None

class StackRun(BaseModel):
    id: Optional[str] = None
    branch: Optional[str] = None
    commit: Optional[StackCommit] = None
    createdAt: Optional[int] = None
    state: Optional[str] = None
    title: Optional[str] = None

class Stack(BaseModel):
    id: str
    name: Optional[str] = None
    administrative: Optional[bool] = None
    branch: Optional[str] = None
    description: Optional[str] = None
    labels: Optional[List[str]] = None
    lockedAt: Optional[int] = None
    lockedBy: Optional[str] = None
    blocked: Optional[bool] = None
    blocker: Optional[StackRun] = None
    namespace: Optional[str] = None
    projectRoot: Optional[str] = None
    repository: Optional[str] = None
    space: Optional[str] = None
    state: Optional[str] = None
    workerPool: Optional[Dict[str, Any]] = None
    createdAt: Optional[int] = None
    isDisabled: Optional[bool] = None
    isDrifted: Optional[bool] = None
    runs: Optional[List[StackRun]] = None

class WorkerPool(BaseModel):
    id: str
    name: Optional[str] = None
    description: Optional[str] = None

class Space(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    labels: Optional[List[str]] = None
    parentSpace: Optional[str] = None
    inheritEntities: Optional[bool] = None
    createdAt: Optional[str] = None
    deletedAt: Optional[str] = None

class ConfigItem(BaseModel):
    id: str
    value: Optional[str] = None
    writeOnly: Optional[bool] = None

class Context(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    labels: Optional[List[str]] = None
    config: Optional[List[ConfigItem]] = None
    space: Optional[str] = None
    createdAt: Optional[str] = None
    deletedAt: Optional[str] = None

class BlueprintInput(BaseModel):
    id: str
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    defaultValue: Optional[str] = None
    required: Optional[bool] = None

class Blueprint(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    inputs: Optional[List[BlueprintInput]] = None
    space: Optional[str] = None
    createdAt: Optional[str] = None
    deletedAt: Optional[str] = None

class CreateSpaceRequest(BaseModel):
    name: str
    parent_space_id: str
    description: str
    labels: Optional[List[str]] = None
    inherit_entities: Optional[bool] = True

class CreateContextRequest(BaseModel):
    name: str
    space_id: str
    description: Optional[str] = ""
    labels: Optional[List[str]] = None
    envvars: Optional[List[Dict[str, Any]]] = None

class CreateStackFromBlueprintRequest(BaseModel):
    blueprint_id: str
    inputs: List[Dict[str, Any]]

# Stack endpoints
@app.get("/stacks", response_model=List[Stack], tags=["stacks"])
async def list_stacks(label: Optional[str] = None, state: Optional[str] = None):
    """
    List all stacks with optional filtering by label and/or state.
    
    - **label**: Optional filter by stack label
    - **state**: Optional filter by stack state (e.g., FINISHED, UNCONFIRMED, STOPPED, FAILED)
    """
    client = get_spacelift_client()
    try:
        stacks = client.get_stacks(query_fields=[
            "id",
            "name",
            "administrative",
            "branch",
            "description",
            "labels",
            "lockedAt",
            "lockedBy",
            "blocked",
            "blocker { id branch commit { authorLogin authorName hash message timestamp url } createdAt state title }",
            "namespace",
            "projectRoot",
            "repository",
            "space",
            "state",
            "workerPool { id name description }",
            "createdAt",
            "isDisabled",
            "isDrifted",
            "runs { id branch commit { authorLogin authorName hash message timestamp url } state createdAt }"
        ])
        
        # Filter by label if provided
        if label:
            stacks = [stack for stack in stacks if "labels" in stack and label in stack["labels"]]
            
        # Filter by state if provided
        if state:
            stacks = [stack for stack in stacks if "state" in stack and stack["state"] == state.upper()]
            
        return stacks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stacks/{stack_id}", response_model=Stack, tags=["stacks"])
async def get_stack(stack_id: str):
    """Get details of a specific stack"""
    client = get_spacelift_client()
    try:
        stack = client.get_stack_by_id(
            stack_id=stack_id,
            query_fields=[
                "id",
                "name",
                "administrative",
                "branch",
                "description",
                "labels",
                "lockedAt",
                "lockedBy",
                "blocked",
                "blocker { id branch commit { authorLogin authorName hash message timestamp url } createdAt state title }",
                "namespace",
                "projectRoot",
                "repository",
                "space",
                "state",
                "workerPool { id name description }",
                "createdAt",
                "isDisabled",
                "isDrifted",
                "runs { id branch commit { authorLogin authorName hash message timestamp url } state createdAt }"
            ]
        )
        if not stack:
            raise HTTPException(status_code=404, detail="Stack not found")
        return stack
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stacks/{stack_id}/run", response_model=StackRun, tags=["stacks"])
async def trigger_stack_run(stack_id: str):
    """Trigger a run for a specific stack"""
    client = get_spacelift_client()
    try:
        result = client.trigger_run(stack_id=stack_id, query_fields=["id"])
        return {"stack_id": stack_id, "run_id": result.get("id")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/stacks/{stack_id}", tags=["stacks"])
async def delete_stack(stack_id: str):
    """Delete a specific stack"""
    client = get_spacelift_client()
    try:
        result = client.delete_stack(stack_id=stack_id)
        return {"message": "Stack deleted successfully", "id": stack_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stacks/blueprint", response_model=Dict[str, Any], tags=["stacks"])
async def create_stack_from_blueprint(request: CreateStackFromBlueprintRequest):
    """Create a new stack from a blueprint"""
    client = get_spacelift_client()
    try:
        result = client.create_stack_from_blueprint(
            blueprint_id=request.blueprint_id,
            inputs=request.inputs
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stacks/raw", tags=["stacks"])
async def list_stacks_raw():
    """
    List all stacks with all available fields for schema exploration.
    This endpoint returns the raw GraphQL response without Pydantic filtering.
    """
    client = get_spacelift_client()
    try:
        # Request a wide range of fields to explore the schema
        stacks = client.get_stacks(query_fields=[
            "id",
            "name",
            "administrative",
            "branch",
            "description",
            "labels",
            "lockedAt",
            "lockedBy",
            "blocked",
            "blocker { id branch commit { authorLogin authorName hash message timestamp url } createdAt state title }",
            "namespace",
            "projectRoot",
            "repository",
            "space",
            "state",
            "workerPool { id name description }",
            "createdAt",
            "isDisabled",
            "isDrifted",
            "runs { id branch commit { authorLogin authorName hash message timestamp url } state createdAt }"
        ])
        return {"stacks": stacks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Space endpoints
@app.get("/spaces", response_model=List[Space], tags=["spaces"])
async def list_spaces():
    """List all spaces"""
    client = get_spacelift_client()
    try:
        return client.get_spaces(query_fields=[
            "id",
            "name",
            "description",
            "labels",
            "parentSpace",
            "inheritEntities",
            "createdAt",
            "deletedAt"
        ])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/spaces/{space_id}", response_model=Space, tags=["spaces"])
async def get_space(space_id: str):
    """Get details of a specific space"""
    client = get_spacelift_client()
    try:
        space = client.get_space_by_id(
            space_id=space_id,
            query_fields=[
                "id",
                "name",
                "description",
                "labels",
                "parentSpace",
                "inheritEntities",
                "createdAt",
                "deletedAt"
            ]
        )
        if not space:
            raise HTTPException(status_code=404, detail="Space not found")
        return space
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/spaces", response_model=Dict[str, Any], tags=["spaces"])
async def create_space(request: CreateSpaceRequest):
    """Create a new space"""
    client = get_spacelift_client()
    try:
        result = client.create_space(
            space_name=request.name,
            parent_space_id=request.parent_space_id,
            description=request.description,
            labels=request.labels,
            inherit_entities=request.inherit_entities
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/spaces/{space_id}", tags=["spaces"])
async def delete_space(space_id: str):
    """Delete a specific space"""
    client = get_spacelift_client()
    try:
        result = client.delete_space(space_id=space_id)
        return {"message": "Space deleted successfully", "id": space_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Context endpoints
@app.get("/contexts", response_model=List[Context], tags=["contexts"])
async def list_contexts():
    """List all contexts"""
    client = get_spacelift_client()
    try:
        return client.get_contexts(query_fields=[
            "id",
            "name",
            "description",
            "labels",
            "config { id value writeOnly }",
            "space",
            "createdAt",
            "deletedAt"
        ])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/contexts/{context_id}", response_model=Context, tags=["contexts"])
async def get_context(context_id: str):
    """Get details of a specific context"""
    client = get_spacelift_client()
    try:
        context = client.get_context_by_id(
            context_id=context_id,
            query_fields=[
                "id",
                "name",
                "description",
                "labels",
                "config { id value writeOnly }",
                "space",
                "createdAt",
                "deletedAt"
            ]
        )
        if not context:
            raise HTTPException(status_code=404, detail="Context not found")
        return context
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/contexts", response_model=Dict[str, Any], tags=["contexts"])
async def create_context(request: CreateContextRequest):
    """Create a new context"""
    client = get_spacelift_client()
    try:
        result = client.create_context(
            context_name=request.name,
            space_id=request.space_id,
            description=request.description,
            labels=request.labels,
            envvars=request.envvars
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/contexts/{context_id}", tags=["contexts"])
async def delete_context(context_id: str):
    """Delete a specific context"""
    client = get_spacelift_client()
    try:
        result = client.delete_context(context_id=context_id)
        return {"message": "Context deleted successfully", "id": context_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Blueprint endpoints
@app.get("/blueprints", response_model=List[Blueprint], tags=["blueprints"])
async def list_blueprints():
    """List all blueprints"""
    client = get_spacelift_client()
    try:
        return client.get_blueprints(query_fields=[
            "id",
            "name",
            "description",
            "inputs { id name type description defaultValue required }",
            "space",
            "createdAt",
            "deletedAt"
        ])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/blueprints/{blueprint_id}", response_model=Blueprint, tags=["blueprints"])
async def get_blueprint(blueprint_id: str):
    """Get details of a specific blueprint"""
    client = get_spacelift_client()
    try:
        blueprint = client.get_blueprint_by_id(
            blueprint_id=blueprint_id,
            query_fields=[
                "id",
                "name",
                "description",
                "inputs { id name type description defaultValue required }",
                "space",
                "createdAt",
                "deletedAt"
            ]
        )
        if not blueprint:
            raise HTTPException(status_code=404, detail="Blueprint not found")
        return blueprint
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Schema endpoints
@app.get("/schema", tags=["schema"])
async def get_schema():
    """
    Get the full GraphQL schema through introspection.
    This shows all available types, queries, and mutations.
    """
    client = get_spacelift_client()
    try:
        # GraphQL introspection query
        query = """
        query IntrospectionQuery {
            __schema {
                types {
                    name
                    description
                    fields {
                        name
                        description
                        type {
                            name
                            kind
                            ofType {
                                name
                                kind
                            }
                        }
                        args {
                            name
                            description
                            type {
                                name
                                kind
                                ofType {
                                    name
                                    kind
                                }
                            }
                        }
                    }
                }
                queryType {
                    name
                    fields {
                        name
                        description
                    }
                }
                mutationType {
                    name
                    fields {
                        name
                        description
                    }
                }
            }
        }
        """
        result = client._execute(gql(query))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
