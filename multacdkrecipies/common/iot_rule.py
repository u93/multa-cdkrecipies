import traceback

from aws_cdk import aws_iot as iot


def base_iot_rule(construct, action_property, **kwargs):
    """

    :param construct:
    :param action_property:
    :param kwargs:
    :return:
    """
    rule_payload = iot.CfnTopicRule.TopicRulePayloadProperty(
        actions=[action_property],
        rule_disabled=kwargs["rule_disabled"],
        sql=kwargs["sql"],
        aws_iot_sql_version=kwargs["aws_iot_sql_version"],
        description=kwargs.get("description"),
    )

    # Defining AWS IoT Rule
    rule_name = construct.prefix + "_" + kwargs["rule_name"] + "_" + construct.environment_
    iot_rule = iot.CfnTopicRule(construct, id=rule_name, rule_name=rule_name, topic_rule_payload=rule_payload)

    return iot_rule
