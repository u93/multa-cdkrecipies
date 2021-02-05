from aws_cdk import aws_iot as iot


def base_iot_rule(construct, action_property, **kwargs):
    """
    Function that generates an IoT Rule.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param action_property: Action property for the resources that the Rule will interact.
    :param kwargs: Consist of required 'rule_name', 'rule_disabled', 'sql', 'aws_iot_sql_version' and optional 'description'.
    :return: IoT Rule Construct.
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
    rule_name = rule_name.replace("-", "_")
    iot_rule = iot.CfnTopicRule(construct, id=rule_name, rule_name=rule_name, topic_rule_payload=rule_payload)

    return iot_rule
