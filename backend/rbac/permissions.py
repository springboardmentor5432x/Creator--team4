from rbac.roles import Role
permissions = {
    Role.CREATOR: [
        "view_profile",
        "edit_profile",
        "view_dashboard",
        "view_analytics"
    ],

    Role.AGENCY: [
        "view_profile",
        "edit_profile",
        "view_dashboard",
        "manage_creators",
        "view_analytics"
    ],

    Role.MARKETING_TEAM: [
        "view_profile",
        "view_dashboard",
        "view_reports",
        "view_trends"
    ],

    Role.ADMINISTRATOR: [
        "*"
    ]
}