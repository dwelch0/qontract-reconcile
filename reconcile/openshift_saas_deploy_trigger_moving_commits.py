import sys

import reconcile.openshift_saas_deploy_trigger_base as osdt_base

from reconcile.status import ExitCodes
from reconcile.utils.saasherder import TriggerTypes
from reconcile.utils.semver_helper import make_semver


QONTRACT_INTEGRATION = "openshift-saas-deploy-trigger-moving-commits"
QONTRACT_INTEGRATION_VERSION = make_semver(0, 2, 0)


def run(dry_run, thread_pool_size=10, internal=None, use_jump_host=True):
    error = osdt_base.run(
        dry_run=dry_run,
        trigger_type=TriggerTypes.MOVING_COMMITS,
        integration=QONTRACT_INTEGRATION,
        integration_version=QONTRACT_INTEGRATION_VERSION,
        thread_pool_size=thread_pool_size,
        internal=internal,
        use_jump_host=use_jump_host,
    )

    if error:
        sys.exit(ExitCodes.ERROR)
