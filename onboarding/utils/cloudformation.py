import itertools
import sys
import time
from decimal import Decimal

from botocore.exceptions import ClientError

from onboarding import logger

spinner_chars = ['\\', '|', '/', '-']


def get_stack_status(create_or_update_stack):
    """
    Decorator to create stack and return stack status.

    Always it checks if stack is already exiting. If the stack is
    already available then it check if stack 'status' is 'COMPLETE'
    or 'FAILED'.

    If status is COMPLETE then it skips the stack creation otherwise if
    status is FAILED then it first deletes the stack and tries to
    recreate.

    If the status is neither COMPLETE nor FAILED then it assumes that
    stack does not exist and tries to create.

    Somehow if the stack creation fails then it intimates sfn that stack
    not created and sfn execution stops with 'red' state.
    """
    def wrapper(*args, **kwargs):
        """
        Wrapper method for create/update stack.
        Args:
            *args: Args parameters.
            **kwargs: Kwargs Parameters.

        Returns:
            Returns wrapper status.
        """
        try:
            arguments = create_or_update_stack(*args, **kwargs)
            client = arguments.pop('client')
            alter_cfn = arguments.pop('alter_cfn')
            status = __stack_status(client, arguments['StackName'])
            if status == 'COMPLETE':
                logger.info('Stack [{}] already exists.'.format(
                    arguments['StackName']))
                if alter_cfn:
                    template_changed, change_set_name, change_set =\
                        stack_has_changed(client, **arguments)
                    if template_changed:
                        execute_change_set(client, change_set_name,
                                           arguments['StackName'])
                        waiter = client.get_waiter('stack_update_complete')
                        waiter.wait(StackName=arguments['StackName'])
                        logger.info('Stack [{}] updated'.format(
                            arguments['StackName']))
                return True
            elif status == 'FAILED':
                logger.info('Deleting Stack: {}'.format(
                    arguments['StackName']))
                client.delete_stack(StackName=arguments['StackName'])
                waiter = client.get_waiter('stack_delete_complete')
                waiter.wait(StackName=arguments['StackName'])
                logger.info('Stack: {} deleted.'.format(
                    arguments['StackName']))
            if status != 'PROGRESS':
                logger.info('Creating Stack: {}'.format(
                    arguments['StackName']))
                client.create_stack(**arguments)
            waiter = client.get_waiter('stack_create_complete')
            waiter.wait(StackName=arguments['StackName'])
            logger.info('Stack [{}] created'.format(arguments['StackName']))
        except Exception as e:
            logger.exception(str(e))
            raise Exception
        return True
    return wrapper


def __stack_status(client, stack_name):
    """
    Checks the status of cloudformation stack.

    Args:
        session/client (boto3 object): boto3 cloudformation object.

        stack_name (string): Name of the stack to be checked.

    Returns:
        Returns cloudformation stack current status.

    """
    try:
        data = client.describe_stacks(StackName=stack_name)
    except ClientError as e:
        logger.exception(e)
        return None
    else:
        status_dict = {
            'CREATE_COMPLETE': 'COMPLETE',
            'ROLLBACK_COMPLETE': 'FAILED',
            'CREATE_FAILED': 'FAILED',
            'DELETE_FAILED': 'FAILED',
            'CREATE_IN_PROGRESS': 'PROGRESS',
            'UPDATE_COMPLETE': 'COMPLETE',
            'UPDATE_ROLLBACK_COMPLETE': 'COMPLETE'
        }
        status = status_dict.get(data['Stacks'][0]['StackStatus'])
        logger.info('Stack: {}, status: {}'.format(stack_name,
                                                   status))
        return status


def stack_has_changed(client, **kwargs):
    """
    Method to check if cloudformation stack is changed.
    Args:
        client: boto3 cloudformation client.
        **kwargs: keyword arguments to create/update stack

    Returns:
        Returns cloudformation change set status.

    """
    change_set_name = "{}Update".format(kwargs['StackName'])
    client.create_change_set(
        UsePreviousTemplate=False,
        ChangeSetName=change_set_name,
        **kwargs
    )
    change_set = client.describe_change_set(
        ChangeSetName=change_set_name,
        StackName=kwargs['StackName']
    )

    wait_for_change_set_state(
        client,
        kwargs['StackName'],
        change_set_name,
        'Waiting for change set creation to complete...',
        lambda change_set: (
            change_set['Status'] == 'CREATE_IN_PROGRESS' or
            change_set['Status'] == 'CREATE_PENDING'
        )
    )

    no_change_status_reason = \
        "The submitted information didn't contain changes"

    if change_set['Status'] == 'FAILED' and \
            no_change_status_reason in change_set['StatusReason']:
        logger.info(
            "Template and parameters haven't changed. "
            "Cleaning up change set."
        )
        delete_change_set(client, change_set_name, kwargs['StackName'])
        logger.info("Stack hasn't changed")
        return False, change_set_name, change_set
    logger.info("Stack has changed")
    return True, change_set_name, change_set


def delete_change_set(client, change_set_name, stack_name):
    """
    Deletes the cloudformation change set.
    Args:
        client: Boto3 client.
        change_set_name: Name of the change set.
        stack_name: Name of the stack.
    """
    client.delete_change_set(
        ChangeSetName=change_set_name,
        StackName=stack_name
    )


def execute_change_set(client, change_set_name, stack_name):
    """
    Deletes the cloudformation change set.
    Args:
        client: Boto3 client.
        change_set_name: Name of the change set.
        stack_name: Name of the stack.
    """
    client.execute_change_set(
        ChangeSetName=change_set_name,
        StackName=stack_name
    )


def wait_for_change_set_state(
        cf_client,
        name_of_stack,
        change_set_name,
        wait_message,
        is_unfinished):
    '''
    Waits for an indefinite amount of time for the state check
    function to return false
    '''
    spinner = itertools.cycle(spinner_chars)

    sys.stdout.write(wait_message)
    sys.stdout.flush()

    try:
        unfinished = is_unfinished(
            cf_client.describe_change_set(
                StackName=name_of_stack,
                ChangeSetName=change_set_name
            )
        )

        check_state_every = Decimal('10.0')
        spin_every = Decimal('0.2')
        elapsed = Decimal('0')
        # check the state every 10 seconds, but spin the
        # spinner every 1/2 second
        while unfinished:
            if (elapsed % check_state_every) == 0:
                change_set = cf_client.describe_change_set(
                    StackName=name_of_stack,
                    ChangeSetName=change_set_name
                )
                unfinished = is_unfinished(change_set)

            sys.stdout.write(
                ('\b' if elapsed > 0 else '')+spinner.next())
            sys.stdout.flush()
            elapsed += spin_every
            time.sleep(spin_every)
        logger.info("Done")
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)
