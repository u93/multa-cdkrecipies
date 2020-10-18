from aws_cdk import aws_sns as sns


def base_topic(construct, **kwargs):
    """
    Function that generates an SNS Topic.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param kwargs: Consist of required 'topic_name'.
    :return: SNS Topic Construct.
    """
    sns_name = construct.prefix + "_" + kwargs["topic_name"] + "_" + "topic" + "_" + construct.environment_
    sns_topic = sns.Topic(construct, id=sns_name, topic_name=sns_name, display_name=sns_name)

    return sns_topic
