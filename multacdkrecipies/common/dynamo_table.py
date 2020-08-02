from aws_cdk import aws_dynamodb as dynamo


DYNAMO_DB_STREAM_OPTIONS = ["NEW_IMAGE", "OLD_IMAGE", "NEW_AND_OLD_IMAGES", "KEYS_ONLY"]


def base_dynamodb_table(construct, **kwargs):
    """
    Function that generates a DynamoDB Table.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param kwargs: Consist of required 'queue_name' and optionals 'queue_delivery_delay' and 'queue_visibility_timeout'.
    :return: DynamoDB Table Construct.
    """
    dynamodb_table_name = construct.prefix + "_" + kwargs["table_name"] + "_table_" + construct.environment_
    dynamodb_table_partition_key = dynamo.Attribute(name=kwargs["partition_key"], type=dynamo.AttributeType.STRING)
    sort_key = kwargs.get("sort_key")
    if sort_key is None:
        dynamodb_table_sort_key = None
    else:
        if sort_key.get("type") == "string":
            sort_key_type = dynamo.AttributeType.STRING
        elif sort_key.get("type") == "integer":
            sort_key_type = dynamo.AttributeType.NUMBER
        elif sort_key.get("type") == "binary":
            sort_key_type = dynamo.AttributeType.BINARY
        else:
            sort_key_type = dynamo.AttributeType.STRING
        dynamodb_table_sort_key = dynamo.Attribute(name=sort_key.get("name"), type=sort_key_type)

    stream_info = kwargs.get("stream")
    if stream_info is None:
        dynamodb_table_streams = None
    else:
        full_element_info = dynamo.StreamViewType.NEW_AND_OLD_IMAGES
        dynamodb_table_streams = full_element_info if stream_info.get("enabled") is True else None

    dynamodb_table_ttl_attribute = kwargs.get("ttl_attribute")

    billing_mode = kwargs.get("billing_mode")
    if billing_mode == "provisioned":
        dynamodb_billing_mode = dynamo.BillingMode.PROVISIONED
        dynamodb_read_capacity = kwargs.get("read_capacity", 5)
        dynamodb_write_capacity = kwargs.get("write_capacity", 5)
    else:
        dynamodb_billing_mode = dynamo.BillingMode.PAY_PER_REQUEST
        dynamodb_read_capacity = None
        dynamodb_write_capacity = None

    dynamodb_table = dynamo.Table(
        construct,
        id=dynamodb_table_name,
        table_name=dynamodb_table_name,
        partition_key=dynamodb_table_partition_key,
        sort_key=dynamodb_table_sort_key,
        billing_mode=dynamodb_billing_mode,
        read_capacity=dynamodb_read_capacity,
        write_capacity=dynamodb_write_capacity,
        stream=dynamodb_table_streams,
        time_to_live_attribute=dynamodb_table_ttl_attribute,
    )

    for global_index in kwargs.get("global_secondary_indexes", list()):
        global_index["partition_key"] = dynamo.Attribute(name=global_index["partition_key"], type=dynamo.AttributeType.STRING)
        if global_index.get("sort_key") is None:
            global_index["sort_key"] = None
        else:
            if sort_key.get("type") == "string":
                sort_key_type = dynamo.AttributeType.STRING
            elif sort_key.get("type") == "integer":
                sort_key_type = dynamo.AttributeType.NUMBER
            elif sort_key.get("type") == "binary":
                sort_key_type = dynamo.AttributeType.BINARY
            else:
                sort_key_type = dynamo.AttributeType.STRING
            global_index["sort_key"] = dynamo.Attribute(name=sort_key.get("name"), type=sort_key_type)
        dynamodb_table.add_global_secondary_index(**global_index)

    for local_index in kwargs.get("local_secondary_indexes", list()):
        sort_key = local_index.get("sort_key")
        if sort_key.get("type") == "string":
            sort_key_type = dynamo.AttributeType.STRING
        elif sort_key.get("type") == "integer":
            sort_key_type = dynamo.AttributeType.NUMBER
        elif sort_key.get("type") == "binary":
            sort_key_type = dynamo.AttributeType.BINARY
        else:
            sort_key_type = dynamo.AttributeType.STRING
        local_index["sort_key"] = dynamo.Attribute(name=sort_key.get("name"), type=sort_key_type)
        dynamodb_table.add_global_secondary_index(**local_index)

    return dynamodb_table, bool(dynamodb_table_streams)
