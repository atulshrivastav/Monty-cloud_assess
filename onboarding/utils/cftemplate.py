def tags(stack_name):
    """
    Returns a dictionary list of the usual tags and a 'Name' tag you
        specify the value for. The usual tags are:
    """
    return [
        dict(
            Key='Name',
            Value=stack_name
        ),
        dict(
            Key='tr:environment-type',
            Value='Production'
        ),
        dict(
            Key='tr:resource-owner',
            Value='Atul Shrivastav'
        )
    ]
