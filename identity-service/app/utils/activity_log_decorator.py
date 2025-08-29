def log_activity(user, activity_type, **kwargs):
    description_template = ACTIVITY_DESCRIPTIONS.get(activity_type, "{activity_type}")
    description = description_template.format(
        username=user.username,
        activity_type=activity_type,
        **kwargs
    )

    log = ActivityLog(
        user_id=user.id,
        activity_type=activity_type,
        description=description,
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent")
    )
    db.session.add(log)
    db.session.commit()
