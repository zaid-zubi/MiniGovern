def dataset_submitted_template(dataset_name: str) -> tuple[str, str]:
    subject = f"[MiniGovern] Dataset '{dataset_name}' submitted"

    body = (
        f"Dataset '{dataset_name}' has been submitted for approval.\n"
    )

    return subject, body


def dataset_approved_template(dataset_name: str) -> tuple[str, str]:
    subject = f"[MiniGovern] Dataset '{dataset_name}' approved"

    body = (
        f"Good news!\n\n"
        f"Your dataset '{dataset_name}' has been approved."
    )

    return subject, body


def dataset_rejected_template(
        dataset_name: str,
        comment: str | None = None,
) -> tuple[str, str]:
    subject = f"[MiniGovern] Dataset '{dataset_name}' rejected"

    body = f"Your dataset '{dataset_name}' has been rejected."

    if comment:
        body += f"\n\nReason: {comment}"

    return subject, body
