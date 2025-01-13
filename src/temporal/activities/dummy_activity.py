from temporalio import activity


@activity.defn
async def dummy_activity() -> list:
    """
    Temporal activity to simulate a dummy activity.

    Returns:
        str: A dummy string.
    """
    return ["Dummy activity executed"]
