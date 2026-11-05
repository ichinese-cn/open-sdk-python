# Generated from docs/api/open-api.yaml by sdks/tools (pnpm sdk:gen) — do not edit.
"""Every operation of the open API as a method; the client (client.py) supplies tokens, retries and paging."""
from __future__ import annotations

from typing import Any, Dict, Iterator, Mapping, Optional, Tuple


class Operations:
    """One method per operation: path parameters by position, then ``query`` and ``body`` (as the operation
    takes them), then keyword options choosing the token (``tenant_key``, ``user_access_token``,
    ``access_token``) and extra ``headers``."""

    def _call(self, op_id: str, method: str, path: str, path_params: Dict[str, str], query: Optional[Dict[str, Any]], body: Any, token_types: Tuple[str, ...], **options: Any) -> Any:  # pragma: no cover
        raise NotImplementedError

    def _iterate(self, op_id: str, method: str, path: str, path_params: Dict[str, str], query: Optional[Dict[str, Any]], token_types: Tuple[str, ...], **options: Any) -> Iterator[Dict[str, Any]]:  # pragma: no cover
        raise NotImplementedError

    def get_user_info(self, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """The current user (user token)

        ``GET /user/info; user token; scopes: openid``
        """
        return self._call("getUserInfo", "GET", "/user/info", {}, None, None, ("user",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def get_tenant(self, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """The institution that installed the app (tenant token)

        ``GET /tenant; tenant token``
        """
        return self._call("getTenant", "GET", "/tenant", {}, None, None, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def list_tenant_members(self, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """The institution's members (directory); members in all regions are listed together, without revealing regions

        ``GET /tenant/members; tenant token; scopes: org:member:readonly, org:member``
        """
        return self._call("listTenantMembers", "GET", "/tenant/members", {}, query, None, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def iter_list_tenant_members(self, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Iterator[Dict[str, Any]]:
        """Every item of ``list_tenant_members``, page after page (``page_size`` defaults to 100)."""
        return self._iterate("listTenantMembers", "GET", "/tenant/members", {}, query, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def invite_tenant_member(self, body: Dict[str, Any], *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Invite a member (they join only after accepting, the same as inviting in the institution admin)

        ``POST /tenant/invitations; tenant token; scopes: org:member``
        """
        return self._call("inviteTenantMember", "POST", "/tenant/invitations", {}, None, body, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def list_classes(self, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Classes: with a tenant token, all of the institution's classes; with a user token, the classes this user teaches

        ``GET /classes; tenant / user token; scopes: class:readonly, class:member``
        """
        return self._call("listClasses", "GET", "/classes", {}, query, None, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def iter_list_classes(self, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Iterator[Dict[str, Any]]:
        """Every item of ``list_classes``, page after page (``page_size`` defaults to 100)."""
        return self._iterate("listClasses", "GET", "/classes", {}, query, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def get_class(self, class_id: str, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """A class

        ``GET /classes/{class_id}; tenant / user token; scopes: class:readonly, class:member``
        """
        return self._call("getClass", "GET", "/classes/{class_id}", {"class_id": class_id}, None, None, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def list_class_members(self, class_id: str, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Roster (teachers and learners)

        ``GET /classes/{class_id}/members; tenant / user token; scopes: class:readonly, class:member``
        """
        return self._call("listClassMembers", "GET", "/classes/{class_id}/members", {"class_id": class_id}, query, None, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def iter_list_class_members(self, class_id: str, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Iterator[Dict[str, Any]]:
        """Every item of ``list_class_members``, page after page (``page_size`` defaults to 100)."""
        return self._iterate("listClassMembers", "GET", "/classes/{class_id}/members", {"class_id": class_id}, query, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def add_class_member(self, class_id: str, body: Dict[str, Any], *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Add one of the institution's members to a class (as a learner)

        ``POST /classes/{class_id}/members; tenant / user token; scopes: class:member``
        """
        return self._call("addClassMember", "POST", "/classes/{class_id}/members", {"class_id": class_id}, None, body, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def remove_class_member(self, class_id: str, open_id: str, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Remove a learner from a class

        ``DELETE /classes/{class_id}/members/{open_id}; tenant / user token; scopes: class:member``
        """
        return self._call("removeClassMember", "DELETE", "/classes/{class_id}/members/{open_id}", {"class_id": class_id, "open_id": open_id}, None, None, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def list_class_sessions(self, class_id: str, query: Dict[str, Any], *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """A class's sessions (within a time range of at most 100 days)

        ``GET /classes/{class_id}/sessions; tenant / user token; scopes: schedule:readonly, schedule``
        """
        return self._call("listClassSessions", "GET", "/classes/{class_id}/sessions", {"class_id": class_id}, query, None, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def iter_list_class_sessions(self, class_id: str, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Iterator[Dict[str, Any]]:
        """Every item of ``list_class_sessions``, page after page (``page_size`` defaults to 100)."""
        return self._iterate("listClassSessions", "GET", "/classes/{class_id}/sessions", {"class_id": class_id}, query, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def cancel_class_session(self, class_id: str, session_id: str, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Cancel a class session (members are notified, the same as cancelling in the timetable)

        ``POST /classes/{class_id}/sessions/{session_id}/cancel; tenant / user token; scopes: schedule``
        """
        return self._call("cancelClassSession", "POST", "/classes/{class_id}/sessions/{session_id}/cancel", {"class_id": class_id, "session_id": session_id}, None, None, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def reschedule_class_session(self, class_id: str, session_id: str, body: Dict[str, Any], *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Reschedule a class session

        ``POST /classes/{class_id}/sessions/{session_id}/reschedule; tenant / user token; scopes: schedule``
        """
        return self._call("rescheduleClassSession", "POST", "/classes/{class_id}/sessions/{session_id}/reschedule", {"class_id": class_id, "session_id": session_id}, None, body, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def get_session_attendance(self, class_id: str, session_id: str, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Attendance of a class session (who came, and how long they stayed in the classroom)

        ``GET /classes/{class_id}/sessions/{session_id}/attendance; tenant / user token; scopes: attendance:readonly``
        """
        return self._call("getSessionAttendance", "GET", "/classes/{class_id}/sessions/{session_id}/attendance", {"class_id": class_id, "session_id": session_id}, None, None, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def list_assignments(self, class_id: str, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """A class's assignments and exams

        ``GET /classes/{class_id}/assignments; tenant / user token; scopes: coursework, grade:readonly``
        """
        return self._call("listAssignments", "GET", "/classes/{class_id}/assignments", {"class_id": class_id}, query, None, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def iter_list_assignments(self, class_id: str, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Iterator[Dict[str, Any]]:
        """Every item of ``list_assignments``, page after page (``page_size`` defaults to 100)."""
        return self._iterate("listAssignments", "GET", "/classes/{class_id}/assignments", {"class_id": class_id}, query, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def create_assignment(self, class_id: str, body: Dict[str, Any], *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Create an assignment (text instructions + due time; questions are edited in the platform). With a user token, the user must be a teacher of this class

        ``POST /classes/{class_id}/assignments; tenant / user token; scopes: coursework``
        """
        return self._call("createAssignment", "POST", "/classes/{class_id}/assignments", {"class_id": class_id}, None, body, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def list_submissions(self, class_id: str, assignment_id: str, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """An assignment's submissions and scores

        ``GET /classes/{class_id}/assignments/{assignment_id}/submissions; tenant / user token; scopes: grade:readonly``
        """
        return self._call("listSubmissions", "GET", "/classes/{class_id}/assignments/{assignment_id}/submissions", {"class_id": class_id, "assignment_id": assignment_id}, query, None, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def iter_list_submissions(self, class_id: str, assignment_id: str, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Iterator[Dict[str, Any]]:
        """Every item of ``list_submissions``, page after page (``page_size`` defaults to 100)."""
        return self._iterate("listSubmissions", "GET", "/classes/{class_id}/assignments/{assignment_id}/submissions", {"class_id": class_id, "assignment_id": assignment_id}, query, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def set_submission_score(self, class_id: str, assignment_id: str, open_id: str, body: Dict[str, Any], *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Write back a score (the result of external grading); the learner is notified that grades are published

        ``PUT /classes/{class_id}/assignments/{assignment_id}/submissions/{open_id}/score; tenant / user token; scopes: coursework``
        """
        return self._call("setSubmissionScore", "PUT", "/classes/{class_id}/assignments/{assignment_id}/submissions/{open_id}/score", {"class_id": class_id, "assignment_id": assignment_id, "open_id": open_id}, None, body, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def export_class_grades(self, class_id: str, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Export grades (one row per learner per assignment)

        ``GET /classes/{class_id}/grades; tenant / user token; scopes: grade:readonly``
        """
        return self._call("exportClassGrades", "GET", "/classes/{class_id}/grades", {"class_id": class_id}, query, None, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def iter_export_class_grades(self, class_id: str, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Iterator[Dict[str, Any]]:
        """Every item of ``export_class_grades``, page after page (``page_size`` defaults to 100)."""
        return self._iterate("exportClassGrades", "GET", "/classes/{class_id}/grades", {"class_id": class_id}, query, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def list_courses(self, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """The institution's recorded courses (tenant token) or the courses this user authored (user token)

        ``GET /courses; tenant / user token; scopes: course, learning:progress:readonly``
        """
        return self._call("listCourses", "GET", "/courses", {}, query, None, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def iter_list_courses(self, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Iterator[Dict[str, Any]]:
        """Every item of ``list_courses``, page after page (``page_size`` defaults to 100)."""
        return self._iterate("listCourses", "GET", "/courses", {}, query, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def get_course_outline(self, course_id: str, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Course outline (titles and order of chapters and lessons)

        ``GET /courses/{course_id}; tenant / user token; scopes: course``
        """
        return self._call("getCourseOutline", "GET", "/courses/{course_id}", {"course_id": course_id}, None, None, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def update_course_outline(self, course_id: str, body: Dict[str, Any], *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Change a course's title and introduction; a published course that is changed goes through review again as usual

        ``PATCH /courses/{course_id}; tenant / user token; scopes: course``
        """
        return self._call("updateCourseOutline", "PATCH", "/courses/{course_id}", {"course_id": course_id}, None, body, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def list_course_progress(self, course_id: str, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Learners' learning progress (number of lessons completed). A user token can only see its own

        ``GET /courses/{course_id}/progress; tenant / user token; scopes: learning:progress:readonly``
        """
        return self._call("listCourseProgress", "GET", "/courses/{course_id}/progress", {"course_id": course_id}, query, None, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def iter_list_course_progress(self, course_id: str, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Iterator[Dict[str, Any]]:
        """Every item of ``list_course_progress``, page after page (``page_size`` defaults to 100)."""
        return self._iterate("listCourseProgress", "GET", "/courses/{course_id}/progress", {"course_id": course_id}, query, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def send_bot_message(self, body: Dict[str, Any], *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Send a bot message (text or card) to a group chat the bot is in, or privately to a user who installed the app

        ``POST /im/messages; tenant / app token; scopes: im:message:send_as_bot``
        """
        return self._call("sendBotMessage", "POST", "/im/messages", {}, None, body, ("tenant", "app"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def list_bot_chats(self, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Group chats the bot is in

        ``GET /im/chats; tenant / app token; scopes: im:chat:readonly``
        """
        return self._call("listBotChats", "GET", "/im/chats", {}, query, None, ("tenant", "app"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def iter_list_bot_chats(self, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Iterator[Dict[str, Any]]:
        """Every item of ``list_bot_chats``, page after page (``page_size`` defaults to 100)."""
        return self._iterate("listBotChats", "GET", "/im/chats", {}, query, ("tenant", "app"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def send_notification(self, body: Dict[str, Any], *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Send a notification to members of this institution (it goes to "System notifications" and is pushed according to each recipient's notification settings and quiet hours)

        ``POST /notifications; tenant token; scopes: notify:send``
        """
        return self._call("sendNotification", "POST", "/notifications", {}, None, body, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def list_class_recordings(self, class_id: str, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Replays and post-class summaries of a class's live sessions (no playback URL; `watch_url` opens the replay page in the platform)

        ``GET /classes/{class_id}/recordings; tenant / user token; scopes: live:recording:readonly``
        """
        return self._call("listClassRecordings", "GET", "/classes/{class_id}/recordings", {"class_id": class_id}, query, None, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def iter_list_class_recordings(self, class_id: str, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Iterator[Dict[str, Any]]:
        """Every item of ``list_class_recordings``, page after page (``page_size`` defaults to 100)."""
        return self._iterate("listClassRecordings", "GET", "/classes/{class_id}/recordings", {"class_id": class_id}, query, ("tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def list_tenant_events(self, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """The institution's events (including drafts and those pending review)

        ``GET /events; tenant token; scopes: event, event:registration:readonly``
        """
        return self._call("listTenantEvents", "GET", "/events", {}, query, None, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def iter_list_tenant_events(self, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Iterator[Dict[str, Any]]:
        """Every item of ``list_tenant_events``, page after page (``page_size`` defaults to 100)."""
        return self._iterate("listTenantEvents", "GET", "/events", {}, query, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def create_tenant_event(self, body: Dict[str, Any], *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Create an event (a draft; the institution publishes it in its console, moderated as usual)

        ``POST /events; tenant token; scopes: event``
        """
        return self._call("createTenantEvent", "POST", "/events", {}, None, body, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def update_tenant_event(self, event_id: str, body: Dict[str, Any], *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Change an event (the same fields as event editing in the platform's institution console)

        ``PATCH /events/{event_id}; tenant token; scopes: event``
        """
        return self._call("updateTenantEvent", "PATCH", "/events/{event_id}", {"event_id": event_id}, None, body, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def list_event_registrations(self, event_id: str, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """An event's registrations and check-ins

        ``GET /events/{event_id}/registrations; tenant token; scopes: event:registration:readonly``
        """
        return self._call("listEventRegistrations", "GET", "/events/{event_id}/registrations", {"event_id": event_id}, query, None, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def iter_list_event_registrations(self, event_id: str, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Iterator[Dict[str, Any]]:
        """Every item of ``list_event_registrations``, page after page (``page_size`` defaults to 100)."""
        return self._iterate("listEventRegistrations", "GET", "/events/{event_id}/registrations", {"event_id": event_id}, query, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def list_tenant_jobs(self, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """The institution's job postings (including drafts and those pending review)

        ``GET /jobs; tenant token; scopes: job, job:candidate:readonly``
        """
        return self._call("listTenantJobs", "GET", "/jobs", {}, query, None, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def iter_list_tenant_jobs(self, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Iterator[Dict[str, Any]]:
        """Every item of ``list_tenant_jobs``, page after page (``page_size`` defaults to 100)."""
        return self._iterate("listTenantJobs", "GET", "/jobs", {}, query, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def create_tenant_job(self, body: Dict[str, Any], *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Sync in a job posting (as a draft; submitting and publishing still go through the institution's review and NetEase Yidun automatic review)

        ``POST /jobs; tenant token; scopes: job``
        """
        return self._call("createTenantJob", "POST", "/jobs", {}, None, body, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def list_job_candidates(self, job_id: str, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """A job's candidates (the fields they agreed to give the institution when applying)

        ``GET /jobs/{job_id}/candidates; tenant token; scopes: job:candidate:readonly``
        """
        return self._call("listJobCandidates", "GET", "/jobs/{job_id}/candidates", {"job_id": job_id}, query, None, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def iter_list_job_candidates(self, job_id: str, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Iterator[Dict[str, Any]]:
        """Every item of ``list_job_candidates``, page after page (``page_size`` defaults to 100)."""
        return self._iterate("listJobCandidates", "GET", "/jobs/{job_id}/candidates", {"job_id": job_id}, query, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def list_trial_venues(self, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """The institution's teaching sites (use their venue_id to schedule trial slots)

        ``GET /trial/venues; tenant token; scopes: trial``
        """
        return self._call("listTrialVenues", "GET", "/trial/venues", {}, query, None, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def iter_list_trial_venues(self, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Iterator[Dict[str, Any]]:
        """Every item of ``list_trial_venues``, page after page (``page_size`` defaults to 100)."""
        return self._iterate("listTrialVenues", "GET", "/trial/venues", {}, query, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def list_trial_slots(self, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Trial lesson slots (by default only those not over yet, by time)

        ``GET /trial/slots; tenant token; scopes: trial``
        """
        return self._call("listTrialSlots", "GET", "/trial/slots", {}, query, None, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def iter_list_trial_slots(self, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Iterator[Dict[str, Any]]:
        """Every item of ``list_trial_slots``, page after page (``page_size`` defaults to 100)."""
        return self._iterate("listTrialSlots", "GET", "/trial/slots", {}, query, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def create_trial_slots(self, body: Dict[str, Any], *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Schedule trial lesson slots (they can repeat weekly); the teaching site must be published

        ``POST /trial/slots; tenant token; scopes: trial``
        """
        return self._call("createTrialSlots", "POST", "/trial/slots", {}, None, body, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def cancel_trial_slot(self, slot_id: str, body: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Cancel a trial lesson slot (whoever booked it is notified as usual; the booking is cancelled with it)

        ``POST /trial/slots/{slot_id}/cancel; tenant token; scopes: trial``
        """
        return self._call("cancelTrialSlot", "POST", "/trial/slots/{slot_id}/cancel", {"slot_id": slot_id}, None, body, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def list_trial_bookings(self, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Trial lesson bookings at the institution's teaching sites

        ``GET /trial/bookings; tenant token; scopes: trial``
        """
        return self._call("listTrialBookings", "GET", "/trial/bookings", {}, query, None, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def iter_list_trial_bookings(self, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Iterator[Dict[str, Any]]:
        """Every item of ``list_trial_bookings``, page after page (``page_size`` defaults to 100)."""
        return self._iterate("listTrialBookings", "GET", "/trial/bookings", {}, query, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def confirm_trial_booking(self, booking_id: str, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Confirm a trial lesson booking

        ``POST /trial/bookings/{booking_id}/confirm; tenant token; scopes: trial``
        """
        return self._call("confirmTrialBooking", "POST", "/trial/bookings/{booking_id}/confirm", {"booking_id": booking_id}, None, None, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def list_trade_orders(self, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """The institution's orders (read-only, for reconciliation). Write operations involving money are not open

        ``GET /trade/orders; tenant token; scopes: trade:order:readonly``
        """
        return self._call("listTradeOrders", "GET", "/trade/orders", {}, query, None, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def iter_list_trade_orders(self, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Iterator[Dict[str, Any]]:
        """Every item of ``list_trade_orders``, page after page (``page_size`` defaults to 100)."""
        return self._iterate("listTradeOrders", "GET", "/trade/orders", {}, query, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def list_tenant_reviews(self, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Reviews of this institution (and its courses and teaching sites)

        ``GET /reviews; tenant token; scopes: review``
        """
        return self._call("listTenantReviews", "GET", "/reviews", {}, query, None, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def iter_list_tenant_reviews(self, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Iterator[Dict[str, Any]]:
        """Every item of ``list_tenant_reviews``, page after page (``page_size`` defaults to 100)."""
        return self._iterate("listTenantReviews", "GET", "/reviews", {}, query, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def reply_review(self, review_id: str, body: Dict[str, Any], *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Reply to a review on behalf of the institution (one reply per review; the content is moderated as usual)

        ``POST /reviews/{review_id}/reply; tenant token; scopes: review``
        """
        return self._call("replyReview", "POST", "/reviews/{review_id}/reply", {"review_id": review_id}, None, body, ("tenant",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def list_public_content(self, kind: str, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Public courses, events and jobs shown in this region

        ``GET /public/{kind}; app / tenant / user token``
        """
        return self._call("listPublicContent", "GET", "/public/{kind}", {"kind": kind}, query, None, ("app", "tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def iter_list_public_content(self, kind: str, query: Optional[Dict[str, Any]] = None, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Iterator[Dict[str, Any]]:
        """Every item of ``list_public_content``, page after page (``page_size`` defaults to 100)."""
        return self._iterate("listPublicContent", "GET", "/public/{kind}", {"kind": kind}, query, ("app", "tenant", "user"), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def get_user_interests(self, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """The user's interest profile (weighted tags of topics and content types; raw browsing and interaction records are not given)

        ``GET /user/profile/interests; user token; scopes: profile:interest:readonly``
        """
        return self._call("getUserInterests", "GET", "/user/profile/interests", {}, None, None, ("user",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def add_interest_signal(self, body: Dict[str, Any], *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Add an interest signal with its source

        ``POST /user/profile/interest_signals; user token; scopes: profile:interest``
        """
        return self._call("addInterestSignal", "POST", "/user/profile/interest_signals", {}, None, body, ("user",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def get_user_learning_profile(self, *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """The user's learning profile (level, goals, languages being learned)

        ``GET /user/profile/learning; user token; scopes: profile:learning:readonly``
        """
        return self._call("getUserLearningProfile", "GET", "/user/profile/learning", {}, None, None, ("user",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)

    def report_on_behalf(self, body: Dict[str, Any], *, tenant_key: Optional[str] = None, user_access_token: Optional[str] = None, access_token: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> Any:
        """Report a piece of public content on behalf of a user (it enters the platform's moderation queue; the user can see it in their own report history)

        ``POST /reports; user token; scopes: report:create``
        """
        return self._call("reportOnBehalf", "POST", "/reports", {}, None, body, ("user",), tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers)
