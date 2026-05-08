def handler(event, context):
    name = event.get("name", "World")
    message = f"Hello, {name}! Deployed with Terraform."
    print(f"Received event: {event}")
    return {"statusCode": 200, "body": message}
