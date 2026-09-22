from temporalio import activity


@activity.defn
async def send_scheduled_message(
    scheduled_message_id: str,
):
    print(
        f"Sending scheduled message: "
        f"{scheduled_message_id}"
    )