import logging
import os
from logging import getLogger
from typing import Optional

from gql import Client, gql
from gql.transport.requests import (
    RequestsHTTPTransport,
)
from graphql import DocumentNode

log = getLogger(__name__)


class Spacelift:
    def __init__(
        self,
        base_url: Optional[str] = None,
        key_id: Optional[str] = None,
        key_secret: Optional[str] = None,
    ):
        params = self._validate_params(base_url, key_id, key_secret)
        self.base_url = params["base_url"]
        self.key_id = params["key_id"]
        self.key_secret = params["key_secret"]
        self._jwt = None
        self.headers = {}
        self.transport = RequestsHTTPTransport(url=self.base_url, headers=self.headers)
        self.client = Client(transport=self.transport)

    @staticmethod
    def _validate_params(
        base_url: Optional[str] = None,
        key_id: Optional[str] = None,
        key_secret: Optional[str] = None,
    ) -> dict:
        """
        Ensures each parameter is provided by either the constructor or environment variables.
        TODO: add support for spacelift's CLI config file, etc.
        """
        base_url = base_url or os.environ.get("SPACELIFT_BASE_URL")
        key_id = key_id or os.environ.get("SPACELIFT_KEY_ID")
        key_secret = key_secret or os.environ.get("SPACELIFT_KEY_SECRET")
        result = {
            "base_url": base_url,
            "key_id": key_id,
            "key_secret": key_secret,
        }
        null_params = [k for k, v in result.items() if not v]
        if null_params:
            raise ValueError(f"Missing spacelift params: {null_params}")
        return result

    def _execute(
        self, query: DocumentNode, variable_values: Optional[dict] = None
    ) -> dict:
        self.transport.headers["Authorization"] = f"Bearer {self.jwt}"
        return self.client.execute(query, variable_values=variable_values)

    def _get_jwt(self):
        query_text = """
        mutation GetSpaceliftToken($keyId: ID!, $keySecret: String!) {
            apiKeyUser(id: $keyId, secret: $keySecret) {
                id
                jwt
            }
        }
        """
        variable_values = {
            "keyId": self.key_id,
            "keySecret": self.key_secret,
        }
        query = gql(query_text)
        result = self.client.execute(
            query, variable_values=variable_values
        )  # cannot use self._execute() here because it would cause infinite recursion
        log.debug(f"get_jwt result: {result}")
        if result.get("apiKeyUser") is None:
            raise ValueError(f"Invalid spacelift keyId: {self.key_id}")
        return result["apiKeyUser"]["jwt"]

    @property
    def jwt(self):
        if not self._jwt:
            self._jwt = self._get_jwt()
        return self._jwt

    def get_stacks(self, query_fields: Optional[list[str]] = None) -> list[dict]:
        if query_fields is None:
            query_fields = ["id", "space"]
        query_text = f'query Stacks {{ stacks {{ {" ".join(query_fields)}  }} }}'
        query = gql(query_text)
        return self._execute(query)["stacks"]

    def get_stack_by_id(
        self, stack_id: str, query_fields: Optional[list[str]] = None
    ) -> dict:
        if query_fields is None:
            query_fields = ["id", "space"]
        query_text = f'query Stack($id: ID!) {{ stack(id: $id) {{ {" ".join(query_fields)}  }} }}'
        variable_values = {
            "id": stack_id,
        }
        query = gql(query_text)
        return self._execute(query, variable_values=variable_values)["stack"]

    def get_spaces(self, query_fields: Optional[list[str]] = None) -> list[dict]:
        if query_fields is None:
            query_fields = ["id", "name"]
        query_text = f'query Spaces {{ spaces {{ {" ".join(query_fields)}  }} }}'
        query = gql(query_text)
        return self._execute(query)["spaces"]

    def get_space_by_id(
        self, space_id: str, query_fields: Optional[list[str]] = None
    ) -> dict:
        if query_fields is None:
            query_fields = ["id", "name"]
        query_text = f'query Space($id: ID!) {{ space(id: $id) {{ {" ".join(query_fields)}  }} }}'
        variable_values = {
            "id": space_id,
        }
        query = gql(query_text)
        return self._execute(query, variable_values=variable_values)["space"]

    def get_contexts(self, query_fields: Optional[list[str]] = None) -> list[dict]:
        if query_fields is None:
            query_fields = ["id", "name"]
        query_text = f'query Contexts {{ contexts {{ {" ".join(query_fields)}  }} }}'
        query = gql(query_text)
        return self._execute(query)["contexts"]

    def get_context_by_id(
        self, context_id: str, query_fields: Optional[list[str]] = None
    ) -> dict:
        if query_fields is None:
            query_fields = [
                "id",
                "name",
            ]
        query_text = f'query Context($id: ID!) {{ context(id: $id) {{ {" ".join(query_fields)}  }} }}'
        variable_values = {
            "id": context_id,
        }
        query = gql(query_text)
        return self._execute(query, variable_values=variable_values)["context"]

    def create_context(
        self,
        context_name: str,
        space_id: str,
        description: str = "",
        labels: list[str] = None,
        envvars: list[dict] = None,
    ):
        if labels is None:
            labels = []
        if envvars is None:
            envvars = []

        query_text = """
        mutation ContextCreateV2($name: String!, $envvars: [ConfigInput!], $space: ID, $description: String, $labels: [String!]) {
            contextCreateV2(input: {name: $name, configAttachments: $envvars, space: $space, description: $description, labels: $labels }) {
                id
                name
                config {
                    id
                    value
                }
            }
        }
        """

        variable_values = {
            "name": context_name,
            "description": description,
            "labels": labels,
            "space": space_id,
            "envvars": envvars,
        }

        query = gql(query_text)
        result = self._execute(query, variable_values=variable_values)
        log.debug(f"create_context result: {result}")
        return result

    def delete_context(self, context_id: str):
        query_text = """
        mutation ContextDelete($id: ID!) {
            contextDelete(id: $id) {
                id
            }
        }
        """
        variable_values = {
            "id": context_id,
        }
        query = gql(query_text)
        result = self._execute(query, variable_values=variable_values)
        log.debug(f"delete_context result: {result}")
        return result

    def create_space(
        self,
        space_name: str,
        parent_space_id: str,
        description: str,
        labels: list[str] = None,
        inherit_entities: bool = True,
    ):
        if labels is None:
            labels = []

        query_text = """
        mutation SpaceCreate($name: String!, $parent: ID!, $description: String!, $labels: [String!], $inheritEntities: Boolean!) {
            spaceCreate(input: {name: $name, parentSpace: $parent, description: $description, labels: $labels, inheritEntities: $inheritEntities}) {
                id
                name
                description
                labels
            }
        }
        """
        variable_values = {
            "name": space_name,
            "parent": parent_space_id,
            "description": description,
            "labels": labels,
            "inheritEntities": inherit_entities,
        }
        query = gql(query_text)
        result = self._execute(query, variable_values=variable_values)
        log.debug(f"create_space result: {result}")
        return result

    def delete_space(self, space_id: str):
        query_text = """
        mutation SpaceDelete($id: ID!) {
            spaceDelete(space: $id) {
                id
            }
        }
        """
        variable_values = {
            "id": space_id,
        }
        query = gql(query_text)
        result = self._execute(query, variable_values=variable_values)
        log.debug(f"delete_space result: {result}")
        return result

    def delete_stack(self, stack_id: str):
        query_text = """
        mutation DeleteStack($id: ID!) {
            stackDelete(id: $id) {
                id
            }
        }
        """
        variable_values = {
            "id": stack_id,
        }
        query = gql(query_text)
        result = self._execute(query, variable_values=variable_values)
        log.debug(f"delete_stack result: {result}")
        return result

    def trigger_run(self, stack_id: str, query_fields: Optional[list[str]] = None):
        if query_fields is None:
            query_fields = ["id", "branch"]

        query_text = f"""
        mutation RunTrigger($stack: ID!) {{
            runTrigger(stack: $stack, runType: TRACKED) {{
                {" ".join(query_fields)}
            }}
        }}
        """
        variable_values = {
            "stack": stack_id,
        }
        query = gql(query_text)
        result = self._execute(query, variable_values=variable_values)["runTrigger"]
        log.debug(f"trigger_run result: {result}")
        return result

    def get_blueprints(self, query_fields: Optional[list[str]] = None) -> list[dict]:
        if query_fields is None:
            query_fields = ["id", "name"]
        newline = "\n"
        query_text = f"""
        query SearchBlueprints($input: SearchInput!) {{
         searchBlueprints(input: $input) {{
          edges {{
           node {{
            {newline.join(query_fields)}
           }}
          }}
         }}
        }}
        """
        variable_values = {
            "input": {
                "fullTextSearch": "",
                "predicates": [],
            }
        }
        query = gql(query_text)
        nodes = self._execute(query, variable_values=variable_values)[
            "searchBlueprints"
        ]["edges"]
        return [node["node"] for node in nodes]

    def get_blueprint_by_id(
        self, blueprint_id: str, query_fields: Optional[list[str]] = None
    ) -> dict:
        if query_fields is None:
            query_fields = ["id", "name"]
        newline = "\n"
        query_text = f"""
        query blueprint($id: ID!) {{
         blueprint(id: $id) {{
          {newline.join(query_fields)}
         }}
        }}
        """
        variable_values = {
            "id": blueprint_id,
        }
        query = gql(query_text)
        return self._execute(query, variable_values=variable_values)["blueprint"]

    def create_stack_from_blueprint(
        self, blueprint_id: str, inputs: list[dict]
    ) -> dict:
        query_text = """
        mutation BlueprintCreateStack($id: ID!, $input: BlueprintStackCreateInput!) {
            blueprintCreateStack(id: $id, input: $input) {
                stackID
                runID
            }
        }
        """
        variable_values = {
            "id": blueprint_id,
            "input": {"templateInputs": inputs},
        }
        query = gql(query_text)
        raw_result = self._execute(query, variable_values=variable_values)
        result = raw_result["blueprintCreateStack"]
        log.debug(f"create_stack_from_blueprint result: {result}")
        return result


def space_context_test():
    sl = Spacelift(os.environ.get("SPACELIFT_BASE_URL"))
    # result = sl.get_stacks()
    # log.info(f"get_stacks result: {result}")
    # result = sl.get_stack_by_id(stack_id="mcr-tf", query_fields=["id", "name"])
    # log.info(f"get_stack_by_id result: {result}")
    #
    # result = sl.get_stacks(["id", "name", "branch", "namespace", "repository", "state"])
    # log.info(f"get_stacks result: {result}")

    # result = sl.get_context_by_id(context_id="customer-a", query_fields=["id", "name", "config { id value writeOnly }"])
    LIBRARY_TEST_NAME = "library-test-customer-a"

    result = sl.get_contexts(
        query_fields=["id", "name", "config { id value writeOnly }"]
    )
    log.info(f"First context: {result[0]}")

    try:
        log.info('Attempting to delete context_id="abc"')
        result = sl.delete_context(context_id="abc")
        log.info(f"delete_context(context_id='abc') result: {result}")
    except Exception as e:
        log.error(f"Exception: {type(e)}:{e}")

    try:
        result = sl.create_context(
            context_name=LIBRARY_TEST_NAME,
            space_id="root",
            envvars=[
                {
                    "id": "FOO",
                    "value": "bar",
                    "type": "ENVIRONMENT_VARIABLE",
                    "writeOnly": False,
                },
                {
                    "id": "BAZ",
                    "value": "qux",
                    "type": "ENVIRONMENT_VARIABLE",
                    "writeOnly": True,
                },
            ],
        )
        log.info(f"create_context result: {result}")

    except Exception as e:
        log.error(f"create_context exception: {type(e)}:{e}")
        result = sl.delete_context(context_id=LIBRARY_TEST_NAME)
        log.info(f"delete_context result: {result}")

    spaces = sl.get_spaces(query_fields=["id", "name", "description", "parentSpace"])
    log.info(f"Spaces: {spaces}")

    delete_spaces = [space for space in spaces if space["name"] == LIBRARY_TEST_NAME]
    log.info(f"Spaces to delete: {delete_spaces}")

    for space in delete_spaces:
        log.info(f"Deleting space: {space['id']}")
        result = sl.delete_space(space_id=space["id"])
        log.info(f"delete_space result: {result}")

    if not delete_spaces:
        result = sl.create_space(
            space_name=LIBRARY_TEST_NAME,
            parent_space_id="root",
            description=f"{LIBRARY_TEST_NAME} space",
            labels=["customer", "a"],
        )

        log.info(f"create_space result: {result}")


def blueprint_test():
    sl = Spacelift(os.environ.get("SPACELIFT_BASE_URL"))
    # result = sl.get_blueprints(query_fields=["id", "name"])
    bp_id = "fcr-aw4-1-az2-1"
    result = sl.get_blueprint_by_id(
        blueprint_id=bp_id, query_fields=["id", "name", "inputs { id name type }"]
    )
    log.info(f"Blueprint details: {result}")

    inputs = [
        {
            "id": "environment",
            "value": "dev",
        },
        {
            "id": "customer_name",
            "value": "abc",
        },
        {
            "id": "description",
            "value": "abc dev environment",
        },
        {"id": "context_id", "value": "svc_abcd-context"},
        {"id": "space_id", "value": "svc_abcd-space-01HJP3651BQT2GY2EQSG6KVWDB"},
    ]
    result = sl.create_stack_from_blueprint(blueprint_id=bp_id, inputs=inputs)
    log.info(f"Create stack result: {result}")


def main():
    # Configure basic logging
    logging.basicConfig(level=logging.INFO)

    # space_context_test()
    blueprint_test()


if __name__ == "__main__":
    main()
