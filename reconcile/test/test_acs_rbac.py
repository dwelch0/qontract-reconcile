import copy
from unittest.mock import Mock

import pytest

from reconcile.acs_rbac import (
    AcsAccessScope,
    AcsRbacIntegration,
    AcsRole,
    AssignmentPair,
)
from reconcile.gql_definitions.acs.acs_rbac import (
    AcsRbacQueryData,
    ClusterV1,
    NamespaceV1,
    NamespaceV1_ClusterV1,
    OidcPermissionAcsV1,
    RoleV1,
    UserV1,
)
from reconcile.utils import acs_api

AUTH_PROVIDER_ID = "6a41743c-792b-11ee-b962-0242ac120002"


@pytest.fixture
def query_data_desired_state() -> AcsRbacQueryData:
    return AcsRbacQueryData(
        acs_rbacs=[
            UserV1(
                acs_user="foo@redhat.com",
                roles=[
                    RoleV1(
                        name="app-sre-admin",
                        oidc_permissions=[
                            OidcPermissionAcsV1(
                                name="app-sre-acs-admin",
                                description="admin access to acs instance",
                                service="acs",
                                permission_set="admin",
                                clusters=[],
                                namespaces=[],
                            )
                        ],
                    )
                ],
            ),
            UserV1(
                acs_user="bar@redhat.com",
                roles=[
                    RoleV1(
                        name="app-sre-admin",
                        oidc_permissions=[
                            OidcPermissionAcsV1(
                                name="app-sre-acs-admin",
                                description="admin access to acs instance",
                                service="acs",
                                permission_set="admin",
                                clusters=[],
                                namespaces=[],
                            )
                        ],
                    )
                ],
            ),
            UserV1(
                acs_user="foofoo@redhat.com",
                roles=[
                    RoleV1(
                        name="tenant-role-a",
                        oidc_permissions=[
                            OidcPermissionAcsV1(
                                name="cluster-analyst",
                                description="analyst access to clusters in acs instance",
                                service="acs",
                                permission_set="analyst",
                                clusters=[
                                    ClusterV1(name="clusterA"),
                                    ClusterV1(name="clusterB"),
                                ],
                                namespaces=[],
                            )
                        ],
                    )
                ],
            ),
            UserV1(
                acs_user="barbar@redhat.com",
                roles=[
                    RoleV1(
                        name="tenant-role-a",
                        oidc_permissions=[
                            OidcPermissionAcsV1(
                                name="cluster-analyst",
                                description="analyst access to clusters in acs instance",
                                service="acs",
                                permission_set="analyst",
                                clusters=[
                                    ClusterV1(name="clusterA"),
                                    ClusterV1(name="clusterB"),
                                ],
                                namespaces=[],
                            )
                        ],
                    )
                ],
            ),
            UserV1(
                acs_user="foobar@redhat.com",
                roles=[
                    RoleV1(
                        name="tenant-role-b",
                        oidc_permissions=[
                            OidcPermissionAcsV1(
                                name="service-vuln-admin",
                                description="vuln-admin access to service namespaces in acs instance",
                                service="acs",
                                permission_set="vuln-admin",
                                clusters=[],
                                namespaces=[
                                    NamespaceV1(
                                        name="serviceA-stage",
                                        cluster=NamespaceV1_ClusterV1(
                                            name="stage-cluster"
                                        ),
                                    ),
                                    NamespaceV1(
                                        name="serviceA-prod",
                                        cluster=NamespaceV1_ClusterV1(
                                            name="prod-cluster"
                                        ),
                                    ),
                                ],
                            )
                        ],
                    )
                ],
            ),
        ]
    )


@pytest.fixture
def modeled_acs_roles() -> list[AcsRole]:
    return [
        AcsRole(
            name="app-sre-acs-admin",
            description="admin access to acs instance",
            assignments=[
                AssignmentPair(key="email", value="foo@redhat.com"),
                AssignmentPair(key="email", value="bar@redhat.com"),
            ],
            permission_set_name="Admin",
            access_scope=AcsAccessScope(
                name="Unrestricted",
                description="Access to all clusters and namespaces",
                clusters=[],
                namespaces=[],
            ),
            system_default=False,
        ),
        AcsRole(
            name="cluster-analyst",
            description="analyst access to clusters in acs instance",
            assignments=[
                AssignmentPair(key="email", value="foofoo@redhat.com"),
                AssignmentPair(key="email", value="barbar@redhat.com"),
            ],
            permission_set_name="Analyst",
            access_scope=AcsAccessScope(
                name="cluster-analyst",
                description="analyst access to clusters in acs instance",
                clusters=["clusterA", "clusterB"],
                namespaces=[],
            ),
            system_default=False,
        ),
        AcsRole(
            name="service-vuln-admin",
            description="vuln-admin access to service namespaces in acs instance",
            assignments=[AssignmentPair(key="email", value="foobar@redhat.com")],
            permission_set_name="Vulnerability Management Admin",
            access_scope=AcsAccessScope(
                name="service-vuln-admin",
                description="vuln-admin access to service namespaces in acs instance",
                clusters=[],
                namespaces=[
                    {"clusterName": "stage-cluster", "namespaceName": "serviceA-stage"},
                    {"clusterName": "prod-cluster", "namespaceName": "serviceA-prod"},
                ],
            ),
            system_default=False,
        ),
    ]


@pytest.fixture
def api_response_roles() -> list[acs_api.Role]:
    return [
        acs_api.Role(
            api_data={
                "name": "app-sre-acs-admin",
                "permissionSetId": "1",
                "accessScopeId": "1",
                "description": "admin access to acs instance",
                "system_default": False,
            }
        ),
        acs_api.Role(
            api_data={
                "name": "cluster-analyst",
                "permissionSetId": "2",
                "accessScopeId": "2",
                "description": "analyst access to clusters in acs instance",
                "system_default": False,
            }
        ),
        acs_api.Role(
            api_data={
                "name": "service-vuln-admin",
                "permissionSetId": "3",
                "accessScopeId": "3",
                "description": "vuln-admin access to service namespaces in acs instance",
                "system_default": False,
            }
        ),
    ]


@pytest.fixture
def api_response_groups() -> list[acs_api.Group]:
    return [
        acs_api.Group(
            api_data={
                "roleName": "app-sre-acs-admin",
                "props": {
                    "id": "1",
                    "authProviderId": AUTH_PROVIDER_ID,
                    "key": "email",
                    "value": "foo@redhat.com",
                },
            }
        ),
        acs_api.Group(
            api_data={
                "roleName": "app-sre-acs-admin",
                "props": {
                    "id": "2",
                    "authProviderId": AUTH_PROVIDER_ID,
                    "key": "email",
                    "value": "bar@redhat.com",
                },
            }
        ),
        acs_api.Group(
            api_data={
                "roleName": "cluster-analyst",
                "props": {
                    "id": "3",
                    "authProviderId": AUTH_PROVIDER_ID,
                    "key": "email",
                    "value": "foofoo@redhat.com",
                },
            }
        ),
        acs_api.Group(
            api_data={
                "roleName": "cluster-analyst",
                "props": {
                    "id": "4",
                    "authProviderId": AUTH_PROVIDER_ID,
                    "key": "email",
                    "value": "barbar@redhat.com",
                },
            }
        ),
        acs_api.Group(
            api_data={
                "roleName": "service-vuln-admin",
                "props": {
                    "id": "5",
                    "authProviderId": AUTH_PROVIDER_ID,
                    "key": "email",
                    "value": "foobar@redhat.com",
                },
            }
        ),
    ]


@pytest.fixture
def api_response_access_scopes() -> list[acs_api.AccessScope]:
    return [
        acs_api.AccessScope(
            api_data={
                "id": "1",
                "name": "Unrestricted",
                "description": "Access to all clusters and namespaces",
                "rules": None,
            }
        ),
        acs_api.AccessScope(
            api_data={
                "id": "2",
                "name": "cluster-analyst",
                "description": "analyst access to clusters in acs instance",
                "rules": {
                    "includedClusters": ["clusterA", "clusterB"],
                    "includedNamespaces": [],
                },
            }
        ),
        acs_api.AccessScope(
            api_data={
                "id": "3",
                "name": "service-vuln-admin",
                "description": "vuln-admin access to service namespaces in acs instance",
                "rules": {
                    "includedClusters": [],
                    "includedNamespaces": [
                        {
                            "clusterName": "stage-cluster",
                            "namespaceName": "serviceA-stage",
                        },
                        {
                            "clusterName": "prod-cluster",
                            "namespaceName": "serviceA-prod",
                        },
                    ],
                },
            }
        ),
    ]


@pytest.fixture
def api_response_permission_sets() -> list[acs_api.PermissionSet]:
    return [
        acs_api.PermissionSet(
            api_data={
                "id": "1",
                "name": "Admin",
            }
        ),
        acs_api.PermissionSet(
            api_data={
                "id": "2",
                "name": "Analyst",
            }
        ),
        acs_api.PermissionSet(
            api_data={
                "id": "3",
                "name": "Vulnerability Management Admin",
            }
        ),
    ]


def test_get_desired_state(mocker, query_data_desired_state, modeled_acs_roles):
    query_func = mocker.patch("reconcile.acs_rbac.acs_rbac_query", autospec=True)
    query_func.return_value = query_data_desired_state

    integration = AcsRbacIntegration()
    result = integration.get_desired_state(query_func)

    assert result == modeled_acs_roles


def test_get_current_state(
    modeled_acs_roles,
    api_response_roles,
    api_response_groups,
    api_response_access_scopes,
    api_response_permission_sets,
):
    acs_mock = Mock()

    acs_mock.get_roles.return_value = api_response_roles
    acs_mock.get_groups.return_value = api_response_groups
    acs_mock.get_access_scope_by_id.side_effect = api_response_access_scopes
    acs_mock.get_permission_set_by_id.side_effect = api_response_permission_sets

    integration = AcsRbacIntegration()
    result = integration.get_current_state(acs_mock, AUTH_PROVIDER_ID)

    assert result == modeled_acs_roles


def test_add_rbac_dry_run(
    mocker,
    modeled_acs_roles,
    api_response_access_scopes,
    api_response_permission_sets,
):
    dry_run = True
    desired = modeled_acs_roles

    current = modeled_acs_roles[:-1]
    current_access_scopes = api_response_access_scopes[:-1]

    acs_mock = Mock()

    acs_mock.get_access_scopes.return_value = current_access_scopes
    acs_mock.get_permission_sets.return_value = api_response_permission_sets
    mocker.patch.object(
        acs_mock, "create_access_scope", side_effect=[api_response_access_scopes[2].id]
    )
    mocker.patch.object(acs_mock, "create_role")
    mocker.patch.object(acs_mock, "create_group_batch")

    integration = AcsRbacIntegration()
    integration.reconcile(desired, current, acs_mock, AUTH_PROVIDER_ID, dry_run)

    acs_mock.get_access_scopes.assert_called_once()
    acs_mock.get_permission_sets.assert_called_once()

    acs_mock.create_access_scope.assert_not_called()
    acs_mock.create_role.assert_not_called()
    acs_mock.create_group_batch.assert_not_called()


def test_add_rbac(
    mocker,
    modeled_acs_roles,
    api_response_access_scopes,
    api_response_permission_sets,
):
    dry_run = False
    desired = modeled_acs_roles

    current = modeled_acs_roles[:-1]
    current_access_scopes = api_response_access_scopes[:-1]

    acs_mock = Mock()

    acs_mock.get_access_scopes.return_value = current_access_scopes
    acs_mock.get_permission_sets.return_value = api_response_permission_sets
    mocker.patch.object(
        acs_mock, "create_access_scope", side_effect=[api_response_access_scopes[2].id]
    )
    mocker.patch.object(acs_mock, "create_role")
    mocker.patch.object(acs_mock, "create_group_batch")

    integration = AcsRbacIntegration()
    integration.reconcile(desired, current, acs_mock, AUTH_PROVIDER_ID, dry_run)

    acs_mock.get_access_scopes.assert_called_once()
    acs_mock.get_permission_sets.assert_called_once()
    acs_mock.create_access_scope.assert_has_calls(
        [
            mocker.call(
                desired[2].access_scope.name,
                desired[2].access_scope.description,
                desired[2].access_scope.clusters,
                desired[2].access_scope.namespaces,
            ),
        ]
    )
    acs_mock.create_role.assert_has_calls(
        [
            mocker.call(
                desired[2].name,
                desired[2].description,
                api_response_permission_sets[2].id,
                api_response_access_scopes[2].id,
            ),
        ]
    )
    acs_mock.create_group_batch.assert_has_calls(
        [
            mocker.call(
                [
                    acs_api.AcsApi.GroupAdd(
                        role_name=desired[2].name,
                        key=a.key,
                        value=a.value,
                        auth_provider_id=AUTH_PROVIDER_ID,
                    )
                    for a in desired[2].assignments
                ]
            )
        ]
    )


def test_delete_rbac_dry_run(
    mocker, modeled_acs_roles, api_response_access_scopes, api_response_groups
):
    dry_run = True
    current = modeled_acs_roles

    desired = modeled_acs_roles[:-1]  # remove 'cluster-analyst' role

    acs_mock = Mock()

    acs_mock.get_access_scopes.return_value = api_response_access_scopes
    acs_mock.get_groups.return_value = api_response_groups
    mocker.patch.object(acs_mock, "delete_role")
    mocker.patch.object(acs_mock, "delete_group_batch")
    mocker.patch.object(acs_mock, "delete_access_scope")

    integration = AcsRbacIntegration()
    integration.reconcile(desired, current, acs_mock, AUTH_PROVIDER_ID, dry_run)

    acs_mock.get_access_scopes.assert_called_once()
    acs_mock.get_groups.assert_called_once()

    acs_mock.delete_role.assert_not_called()
    acs_mock.delete_group_batch.assert_not_called()
    acs_mock.delete_access_scope.assert_not_called()


def test_delete_rbac(
    mocker, modeled_acs_roles, api_response_access_scopes, api_response_groups
):
    dry_run = False
    current = modeled_acs_roles

    desired = (
        modeled_acs_roles[:1] + modeled_acs_roles[2:]
    )  # remove 'cluster-analyst' role

    acs_mock = Mock()

    acs_mock.get_access_scopes.return_value = api_response_access_scopes
    acs_mock.get_groups.return_value = api_response_groups
    mocker.patch.object(acs_mock, "delete_role")
    mocker.patch.object(acs_mock, "delete_group_batch")
    mocker.patch.object(acs_mock, "delete_access_scope")

    integration = AcsRbacIntegration()
    integration.reconcile(desired, current, acs_mock, AUTH_PROVIDER_ID, dry_run)

    acs_mock.get_access_scopes.assert_called_once()
    acs_mock.get_groups.assert_called_once()
    acs_mock.delete_role.assert_has_calls([mocker.call(current[1].name)])
    acs_mock.delete_group_batch.assert_has_calls(
        [mocker.call([api_response_groups[2], api_response_groups[3]])]
    )
    acs_mock.delete_access_scope.assert_has_calls(
        [mocker.call(api_response_access_scopes[1].id)]
    )


def test_update_rbac_groups_only(
    mocker,
    modeled_acs_roles,
    api_response_access_scopes,
    api_response_permission_sets,
    api_response_groups,
):
    dry_run = False
    desired = modeled_acs_roles

    current = copy.deepcopy(modeled_acs_roles)
    # change a user assignment in 'app-sre-acs-admin' role
    current[0].assignments[0].value = "lasagna"
    current_groups = copy.deepcopy(api_response_groups)
    current_groups[0].value = "lasagna"

    acs_mock = Mock()

    acs_mock.get_access_scopes.return_value = api_response_access_scopes
    acs_mock.get_permission_sets.return_value = api_response_permission_sets
    acs_mock.get_groups.return_value = current_groups
    mocker.patch.object(acs_mock, "update_group_batch")
    mocker.patch.object(acs_mock, "update_access_scope")
    mocker.patch.object(acs_mock, "update_role")

    integration = AcsRbacIntegration()
    integration.reconcile(desired, current, acs_mock, AUTH_PROVIDER_ID, dry_run)

    acs_mock.get_access_scopes.assert_called_once()
    acs_mock.get_permission_sets.assert_called_once()
    acs_mock.get_groups.assert_called_once()

    acs_mock.update_group_batch.assert_has_calls(
        [
            mocker.call(
                [current_groups[0]],
                [
                    acs_api.AcsApi.GroupAdd(
                        role_name=desired[0].name,
                        key=desired[0].assignments[0].key,
                        value=desired[0].assignments[0].value,
                        auth_provider_id=AUTH_PROVIDER_ID,
                    )
                ],
            )
        ]
    )

    acs_mock.update_access_scope.assert_not_called()
    acs_mock.update_role.assert_not_called()


def test_full_reconcile(
    mocker,
    modeled_acs_roles,
    api_response_access_scopes,
    api_response_permission_sets,
    api_response_groups,
):
    dry_run = False

    desired = modeled_acs_roles[:-1] + [
        AcsRole(
            name="new-role",
            description="add me",
            assignments=[
                AssignmentPair(key="email", value="elsa@redhat.com"),
                AssignmentPair(key="email", value="anna@redhat.com"),
            ],
            permission_set_name="Admin",
            access_scope=AcsAccessScope(
                name="Unrestricted",
                description="Access to all clusters and namespaces",
                clusters=[],
                namespaces=[],
            ),
            system_default=False,
        )
    ]

    current = copy.deepcopy(modeled_acs_roles)
    # change permission set to trigger update to existing 'cluster-analyst' role
    current[1].permission_set_name = "Vulnerability Management Admin"
    # remove a cluster from scope to trigger update to access scope of 'cluster-analyst'
    current[1].access_scope.clusters.pop()
    current_access_scopes = copy.deepcopy(api_response_access_scopes)
    current_access_scopes[1].clusters.pop()

    acs_mock = Mock()

    acs_mock.get_access_scopes.return_value = current_access_scopes
    acs_mock.get_permission_sets.return_value = api_response_permission_sets
    acs_mock.get_groups.return_value = api_response_groups
    mocker.patch.object(acs_mock, "create_access_scope")
    mocker.patch.object(acs_mock, "create_role")
    mocker.patch.object(acs_mock, "create_group_batch")
    mocker.patch.object(acs_mock, "delete_role")
    mocker.patch.object(acs_mock, "delete_group_batch")
    mocker.patch.object(acs_mock, "delete_access_scope")
    mocker.patch.object(acs_mock, "update_group_batch")
    mocker.patch.object(acs_mock, "update_access_scope")
    mocker.patch.object(acs_mock, "update_role")

    integration = AcsRbacIntegration()
    integration.reconcile(desired, current, acs_mock, AUTH_PROVIDER_ID, dry_run)

    acs_mock.create_role.assert_has_calls(
        [
            mocker.call(
                desired[2].name,
                desired[2].description,
                api_response_permission_sets[0].id,
                api_response_access_scopes[0].id,
            ),
        ]
    )
    acs_mock.create_group_batch.assert_has_calls(
        [
            mocker.call(
                [
                    acs_api.AcsApi.GroupAdd(
                        role_name=desired[2].name,
                        key=a.key,
                        value=a.value,
                        auth_provider_id=AUTH_PROVIDER_ID,
                    )
                    for a in desired[2].assignments
                ]
            )
        ]
    )

    acs_mock.delete_role.assert_has_calls([mocker.call(current[2].name)])
    acs_mock.delete_group_batch.assert_has_calls(
        [mocker.call([api_response_groups[4]])]
    )
    acs_mock.delete_access_scope.assert_has_calls(
        [mocker.call(api_response_access_scopes[2].id)]
    )

    acs_mock.update_role.assert_has_calls(
        [
            mocker.call(
                desired[1].name,
                desired[1].description,
                # use originals
                api_response_permission_sets[1].id,
                api_response_access_scopes[1].id,
            )
        ]
    )
    acs_mock.update_access_scope.assert_has_calls(
        [
            mocker.call(
                api_response_access_scopes[1].id,
                desired[1].access_scope.name,
                desired[1].access_scope.description,
                desired[1].access_scope.clusters,
                desired[1].access_scope.namespaces,
            )
        ]
    )

    assert acs_mock.get_access_scopes.call_count == 3
    assert acs_mock.get_permission_sets.call_count == 2
    assert acs_mock.get_groups.call_count == 2
    # new desired role is admin scope. Should use existing 'Unrestricted' system default
    acs_mock.create_access_scope.assert_not_called()
    acs_mock.update_group_batch.assert_not_called()
