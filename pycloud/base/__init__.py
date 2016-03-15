from ..core.modules import BaseModule

class CoreModule(BaseModule):
    name = 'The Basics'

    policy_types = [
        'pycloud.base.policies.Dir',
    ]
    task_types = [
        'pycloud.base.tasks.BashTask',
    ]
    operation_types = [
        'pycloud.base.operations.SimpleOperation',
    ]
