# Generated from docs/api/open-api.yaml by sdks/tools (pnpm sdk:gen) — do not edit.
"""The SDK's version, its default address and the contract's constants."""
from typing import Dict, List, Tuple

#: The SDK's version (it follows the open API's).
VERSION = "1.0.0-rc.5"
__version__ = VERSION
#: The open API's address from the release configuration (sdks/release.json); ``base_url`` overrides it.
DEFAULT_BASE_URL = "https://open.ichinese.cn"
API_PREFIX = "/open-apis/v1"

#: Every scope (permission code) of the open API.
SCOPES: List[str] = [
    "openid",
    "profile",
    "phone",
    "email",
    "org:member:readonly",
    "org:member",
    "class:readonly",
    "class:member",
    "schedule:readonly",
    "schedule",
    "attendance:readonly",
    "coursework",
    "grade:readonly",
    "course",
    "learning:progress:readonly",
    "im:message:send_as_bot",
    "im:chat:readonly",
    "notify:send",
    "live:recording:readonly",
    "event",
    "event:registration:readonly",
    "job",
    "job:candidate:readonly",
    "trial",
    "trade:order:readonly",
    "trade:booking:readonly",
    "venue:readonly",
    "venue",
    "opening:readonly",
    "review",
    "profile:interest:readonly",
    "profile:interest",
    "profile:learning:readonly",
    "report:create",
    "community:post",
    "me:schedule:readonly",
    "me:learning:readonly",
    "me:words:readonly",
    "me:words",
    "insights:readonly",
]

#: The events an app can subscribe to.
EVENT_TYPES: List[str] = [
    "app.installed",
    "app.uninstalled",
    "app.scopes_changed",
    "coursework.submitted",
    "grade.published",
    "schedule.session_changed",
    "event.registered",
    "job.candidate_applied",
    "trade.order_paid",
    "review.created",
    "trial.booked",
    "im.message_received",
    "class.member_changed",
    "course.completed",
    "exam.results_released",
    "event.checked_in",
    "live.recording_ready",
    "trade.order_refunded",
    "trial.confirmed",
    "trial.cancelled",
    "community.post_reviewed",
    "community.video_ready",
    "booking.changed",
]

#: ``error.details.reason`` values.
ERROR_REASONS: List[str] = [
    "invalid_credentials",
    "invalid_token",
    "token_expired",
    "token_type",
    "app_disabled",
    "not_installed",
    "not_available",
    "scope_denied",
    "scope_pending",
    "scope_not_declared",
    "gold_only",
    "rate_limited",
    "daily_quota_exceeded",
    "code_expired",
    "code_used",
    "code_invalid",
    "redirect_uri_mismatch",
    "origin_not_trusted",
    "ip_not_allowed",
    "org_not_installed",
    "minor_not_allowed",
    "birth_year_required",
    "feature_disabled",
    "app_post_stopped",
    "consent_required",
    "video_not_ready",
    "video_failed",
    "post_rate_limited",
    "app_user_daily_limit",
    "post_in_progress",
    "no_org_account",
    "teacher_busy",
    "online_only",
    "venue_unavailable",
    "venue_not_found",
    "slot_overlap",
    "slot_taken",
    "not_draft",
    "not_editable",
    "org_not_verified",
    "opening_ended",
    "opening_incomplete",
]

#: Token types each operation accepts (the client picks the token by them).
OPERATION_TOKENS: Dict[str, Tuple[str, ...]] = {
    "get_user_info": ("user",),
    "get_tenant": ("tenant",),
    "list_tenant_members": ("tenant",),
    "invite_tenant_member": ("tenant",),
    "list_classes": ("tenant", "user"),
    "get_class": ("tenant", "user"),
    "list_class_members": ("tenant", "user"),
    "add_class_member": ("tenant", "user"),
    "remove_class_member": ("tenant", "user"),
    "list_class_sessions": ("tenant", "user"),
    "create_class_sessions": ("tenant", "user"),
    "set_class_session_place": ("tenant", "user"),
    "cancel_class_session": ("tenant", "user"),
    "reschedule_class_session": ("tenant", "user"),
    "get_session_attendance": ("tenant", "user"),
    "list_assignments": ("tenant", "user"),
    "create_assignment": ("tenant", "user"),
    "list_submissions": ("tenant", "user"),
    "set_submission_score": ("tenant", "user"),
    "export_class_grades": ("tenant", "user"),
    "list_courses": ("tenant", "user"),
    "get_course_outline": ("tenant", "user"),
    "update_course_outline": ("tenant", "user"),
    "list_course_progress": ("tenant", "user"),
    "send_bot_message": ("tenant", "app"),
    "list_bot_chats": ("tenant", "app"),
    "send_notification": ("tenant",),
    "list_class_recordings": ("tenant", "user"),
    "list_tenant_events": ("tenant",),
    "create_tenant_event": ("tenant",),
    "update_tenant_event": ("tenant",),
    "list_event_registrations": ("tenant",),
    "list_tenant_jobs": ("tenant",),
    "create_tenant_job": ("tenant",),
    "list_job_candidates": ("tenant",),
    "list_trial_venues": ("tenant",),
    "list_trial_slots": ("tenant",),
    "create_trial_slots": ("tenant",),
    "cancel_trial_slot": ("tenant",),
    "set_trial_teacher": ("tenant",),
    "list_trial_bookings": ("tenant",),
    "confirm_trial_booking": ("tenant",),
    "list_venues": ("tenant",),
    "create_venue": ("tenant",),
    "get_venue": ("tenant",),
    "list_openings": ("tenant", "user"),
    "get_opening": ("tenant", "user"),
    "get_insights": ("tenant",),
    "list_trade_orders": ("tenant",),
    "list_bookings": ("tenant",),
    "get_booking": ("tenant",),
    "list_tenant_reviews": ("tenant",),
    "reply_review": ("tenant",),
    "list_public_content": ("app", "tenant", "user"),
    "get_user_interests": ("user",),
    "add_interest_signal": ("user",),
    "get_user_learning_profile": ("user",),
    "report_on_behalf": ("user",),
    "create_community_image_upload": ("user", "tenant"),
    "create_community_video_upload": ("user", "tenant"),
    "complete_community_video_upload": ("user", "tenant"),
    "get_community_video": ("user", "tenant"),
    "list_community_posts": ("user", "tenant"),
    "create_community_post": ("user", "tenant"),
    "get_community_post": ("user", "tenant"),
    "delete_community_post": ("user", "tenant"),
    "list_community_categories": ("user", "tenant"),
    "get_my_schedule": ("user",),
    "list_my_courses": ("user",),
    "list_my_words": ("user",),
    "add_my_word": ("user",),
    "list_class_exams": ("tenant",),
    "list_class_exam_results": ("tenant",),
}

SCOPE_OPENID = "openid"
SCOPE_PROFILE = "profile"
SCOPE_PHONE = "phone"
SCOPE_EMAIL = "email"
SCOPE_ORG_MEMBER_READONLY = "org:member:readonly"
SCOPE_ORG_MEMBER = "org:member"
SCOPE_CLASS_READONLY = "class:readonly"
SCOPE_CLASS_MEMBER = "class:member"
SCOPE_SCHEDULE_READONLY = "schedule:readonly"
SCOPE_SCHEDULE = "schedule"
SCOPE_ATTENDANCE_READONLY = "attendance:readonly"
SCOPE_COURSEWORK = "coursework"
SCOPE_GRADE_READONLY = "grade:readonly"
SCOPE_COURSE = "course"
SCOPE_LEARNING_PROGRESS_READONLY = "learning:progress:readonly"
SCOPE_IM_MESSAGE_SEND_AS_BOT = "im:message:send_as_bot"
SCOPE_IM_CHAT_READONLY = "im:chat:readonly"
SCOPE_NOTIFY_SEND = "notify:send"
SCOPE_LIVE_RECORDING_READONLY = "live:recording:readonly"
SCOPE_EVENT = "event"
SCOPE_EVENT_REGISTRATION_READONLY = "event:registration:readonly"
SCOPE_JOB = "job"
SCOPE_JOB_CANDIDATE_READONLY = "job:candidate:readonly"
SCOPE_TRIAL = "trial"
SCOPE_TRADE_ORDER_READONLY = "trade:order:readonly"
SCOPE_TRADE_BOOKING_READONLY = "trade:booking:readonly"
SCOPE_VENUE_READONLY = "venue:readonly"
SCOPE_VENUE = "venue"
SCOPE_OPENING_READONLY = "opening:readonly"
SCOPE_REVIEW = "review"
SCOPE_PROFILE_INTEREST_READONLY = "profile:interest:readonly"
SCOPE_PROFILE_INTEREST = "profile:interest"
SCOPE_PROFILE_LEARNING_READONLY = "profile:learning:readonly"
SCOPE_REPORT_CREATE = "report:create"
SCOPE_COMMUNITY_POST = "community:post"
SCOPE_ME_SCHEDULE_READONLY = "me:schedule:readonly"
SCOPE_ME_LEARNING_READONLY = "me:learning:readonly"
SCOPE_ME_WORDS_READONLY = "me:words:readonly"
SCOPE_ME_WORDS = "me:words"
SCOPE_INSIGHTS_READONLY = "insights:readonly"
