from aws_cdk import aws_iotanalytics as iotanl_


def base_iot_analytics_dataset(construct, resource_dependencies: list, **kwargs):
    """
    Function that generates an IoT Analytics Dataset.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param resource_dependencies: Resources that have to be created for the IoT Analytics Dataset can exist.
    :param kwargs: Consist of required 'dataset_name', 'sql_action', 'trigger_action'. Optional 'retention_period'
    :return: IoT Analytics Dataset Construct.
    """
    dataset_name = kwargs["dataset_name"].replace("-", "_")

    received_retention_days = kwargs.get("retention_period")
    unlimited_storage = False if received_retention_days is not None else True
    retention_days = 90 if received_retention_days is None else received_retention_days
    retention_period_property = iotanl_.CfnDataset.RetentionPeriodProperty(
        number_of_days=retention_days, unlimited=unlimited_storage
    )

    actions = list()
    sql_action_definition = kwargs["sql_action"]

    received_time_expression = sql_action_definition.get("delta_time", {}).get("timestamp_field")
    received_offset_seconds = sql_action_definition.get("delta_time", {}).get("offset_seconds")
    if received_time_expression is None or received_offset_seconds is None:
        delta_time = None
    else:
        time_expression = f"from_unixtime({sql_action_definition.get('delta_time', {}).get('timestamp_field')})"
        delta_time = [
            iotanl_.CfnDataset.FilterProperty(
                delta_time=iotanl_.CfnDataset.DeltaTimeProperty(
                    offset_seconds=received_offset_seconds,
                    time_expression=time_expression,
                )
            )
        ]

    sql_action = iotanl_.CfnDataset.ActionProperty(
        action_name=dataset_name,
        query_action=iotanl_.CfnDataset.QueryActionProperty(
            sql_query=sql_action_definition["sql_query"],
            filters=delta_time,
        ),
    )
    actions.append(sql_action)

    time_trigger_definition = kwargs.get("trigger_action", {})
    received_schedule_expression = time_trigger_definition.get("schedule")
    if received_schedule_expression is None:
        triggers = None
    else:
        triggers = list()
        schedule_expression = f"cron({received_schedule_expression})"
        time_trigger = iotanl_.CfnDataset.TriggerProperty(
            schedule=iotanl_.CfnDataset.ScheduleProperty(schedule_expression=schedule_expression)
        )
        triggers.append(time_trigger)

    dataset = iotanl_.CfnDataset(
        construct,
        id=dataset_name,
        dataset_name=dataset_name,
        retention_period=retention_period_property,
        actions=actions,
        triggers=triggers,
    )

    for dependency in resource_dependencies:
        dataset.add_depends_on(target=dependency)

    return dataset
