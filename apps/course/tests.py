"""Smoke tests for the v2 lesson taxonomy.

Run with:
    python manage.py test apps.course

These exercise the nested course create path through all lesson kinds plus
the new student-facing endpoints (solution reveal, assignment submission).
They use the standard Django test client + in-memory SQLite test DB so they
do NOT need Postgres or Redis.
"""

import json
from io import BytesIO
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from apps.course.models.assignment_submission import AssignmentSubmission
from apps.course.models.category import Category
from apps.notifications.models import Notification, NotificationType
from apps.course.models.course import Course
from apps.course.models.lessons import Lessons
from apps.course.models.student import CourseStudent
from apps.course.models.units import CourseUnit
from apps.order.models import OrderStatus
from apps.quiz.models.quiz import Quiz


User = get_user_model()


def _png_bytes():
    # A real, Pillow-encoded PNG so ImageField's image validator accepts it.
    from PIL import Image

    buf = BytesIO()
    Image.new('RGB', (16, 16), (79, 70, 229)).save(buf, format='PNG')
    return buf.getvalue()


@override_settings(
    DEFAULT_FILE_STORAGE='django.core.files.storage.InMemoryStorage',
)
class LessonTaxonomyV2Tests(TestCase):

    def setUp(self):
        self.teacher = User.objects.create_user(
            email='teacher@example.com', username='teacher', password='pw', role='TEACHER'
        )
        self.student = User.objects.create_user(
            email='student@example.com', username='student', password='pw'
        )
        self.category = Category.objects.create(title='Web Development')

        self.client = APIClient()
        self.client.force_authenticate(user=self.teacher)

    def _make_cover(self):
        png = BytesIO(_png_bytes())
        png.name = 'cover.png'
        return png

    def _full_units_payload(self):
        return [
            {
                'title': 'Intro',
                'desc': 'Onboarding',
                'lessons': [
                    {
                        'kind': 'VIDEO',
                        'title': 'Welcome video',
                        'desc': 'A short intro',
                        'duration_min': 3,
                        'content_md': '',
                        'additional_task': '',
                        'external_url': '',
                        'assignment_instructions': '',
                        'assignment_due_at': None,
                        'exercise': None,
                        'attached_quiz': None,
                        'video': None,
                        'presentation': None,
                    },
                    {
                        'kind': 'ARTICLE',
                        'title': 'Reading lesson',
                        'desc': '',
                        'duration_min': 5,
                        'content_md': '# Hello\nBody text',
                        'additional_task': '',
                        'external_url': '',
                        'assignment_instructions': '',
                        'assignment_due_at': None,
                        'exercise': None,
                        'attached_quiz': None,
                        'video': None,
                        'presentation': None,
                    },
                    {
                        'kind': 'EXERCISE',
                        'title': 'Practice',
                        'desc': '',
                        'duration_min': 10,
                        'content_md': 'Write a function',
                        'additional_task': '',
                        'external_url': '',
                        'assignment_instructions': '',
                        'assignment_due_at': None,
                        'exercise': {
                            'language': 'python',
                            'starter_code': 'def f():\n    pass',
                            'solution': 'def f():\n    return 42',
                            'hints': [
                                # Mix legacy string + new dict to exercise both branches.
                                'Think about the return type',
                                {'text': 'Use a literal', 'penalty_percent': 15},
                            ],
                        },
                        'attached_quiz': None,
                        'video': None,
                        'presentation': None,
                    },
                    {
                        'kind': 'QUIZ',
                        'title': 'Knowledge check',
                        'desc': '',
                        'duration_min': 5,
                        'content_md': '',
                        'additional_task': '',
                        'external_url': '',
                        'assignment_instructions': '',
                        'assignment_due_at': None,
                        'exercise': None,
                        'attached_quiz': {
                            'title': 'Knowledge check',
                            'description': 'Two questions',
                            'time_limit_min': 5,
                            'show_timer': False,
                            'questions': [
                                {
                                    'question_text': 'Is the sky blue?',
                                    'points': 1,
                                    'variants': [
                                        {'text': 'Yes', 'is_correct': True},
                                        {'text': 'No', 'is_correct': False},
                                    ],
                                },
                            ],
                        },
                        'video': None,
                        'presentation': None,
                    },
                    {
                        'kind': 'ASSIGNMENT',
                        'title': 'Build a thing',
                        'desc': '',
                        'duration_min': 60,
                        'content_md': '',
                        'additional_task': '',
                        'external_url': '',
                        'assignment_instructions': 'Submit your thing.',
                        'assignment_due_at': None,
                        'exercise': None,
                        'attached_quiz': None,
                        'video': None,
                        'presentation': None,
                    },
                    {
                        'kind': 'RESOURCE',
                        'title': 'Further reading',
                        'desc': '',
                        'duration_min': 0,
                        'content_md': 'Optional MDN page',
                        'additional_task': '',
                        'external_url': 'https://developer.mozilla.org',
                        'assignment_instructions': '',
                        'assignment_due_at': None,
                        'exercise': None,
                        'attached_quiz': None,
                        'video': None,
                        'presentation': None,
                    },
                    {
                        'kind': 'DISCUSSION',
                        'title': 'Reflect',
                        'desc': '',
                        'duration_min': 5,
                        'content_md': 'What surprised you?',
                        'additional_task': '',
                        'external_url': '',
                        'assignment_instructions': '',
                        'assignment_due_at': None,
                        'exercise': None,
                        'attached_quiz': None,
                        'video': None,
                        'presentation': None,
                    },
                ],
            },
        ]

    def _create_course(self):
        payload = {
            'title': 'Demo Course',
            'desc': 'Demo course',
            'base_price': 0,
            'discount_price': 0,
            'category': str(self.category.id),
            'cover_img': self._make_cover(),
            'units': json.dumps(self._full_units_payload()),
        }
        response = self.client.post('/api/teachers/courses/', payload, format='multipart')
        self.assertIn(response.status_code, (200, 201), msg=response.content)
        course = Course.objects.filter(created_by=self.teacher).order_by('-created_at').first()
        self.assertIsNotNone(course, msg='Course should have been created')
        return course

    def test_nested_course_create_persists_every_lesson_kind(self):
        course = self._create_course()

        kinds = list(
            Lessons.objects.filter(course_unit__course=course).values_list('kind', flat=True)
        )
        self.assertEqual(
            sorted(kinds),
            sorted(['VIDEO', 'ARTICLE', 'EXERCISE', 'QUIZ', 'ASSIGNMENT', 'RESOURCE', 'DISCUSSION']),
        )

        quiz_lesson = Lessons.objects.get(course_unit__course=course, kind='QUIZ')
        self.assertEqual(Quiz.objects.filter(lesson=quiz_lesson).count(), 1)
        quiz = Quiz.objects.get(lesson=quiz_lesson)
        self.assertEqual(quiz.time_limit_min, 5)
        self.assertFalse(quiz.show_timer)
        self.assertEqual(quiz.questions.count(), 1)

    def test_exercise_hints_normalize_string_and_dict_shapes(self):
        course = self._create_course()
        ex = Lessons.objects.get(course_unit__course=course, kind='EXERCISE').exercise
        self.assertIsInstance(ex, dict)
        self.assertEqual(len(ex['hints']), 2)
        for hint in ex['hints']:
            self.assertIn('text', hint)
            self.assertIn('penalty_percent', hint)
            self.assertGreaterEqual(hint['penalty_percent'], 0)
        # Explicit penalty preserved on the dict-shaped hint.
        self.assertEqual(ex['hints'][1]['penalty_percent'], 15)

    def test_student_lesson_payload_strips_solution(self):
        course = self._create_course()
        # Enroll the student.
        CourseStudent.objects.create(user=self.student, course=course)
        from apps.order.models import Order
        Order.objects.create(course=course, user=self.student, status=OrderStatus.PAID, total_amount=0)

        enrollment = CourseStudent.objects.get(user=self.student, course=course)

        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/users/my-courses/{enrollment.id}/')
        self.assertEqual(response.status_code, 200, msg=response.content)
        data = response.json()
        body = data.get('data', data)
        exercise_lesson = next(
            lesson
            for unit in body['course']['units']
            for lesson in unit['lessons']
            if lesson['kind'] == 'EXERCISE'
        )
        # Solution must NOT leak — frontend must call the reveal endpoint.
        self.assertEqual(exercise_lesson['exercise']['solution'], '')
        self.assertTrue(exercise_lesson['exercise'].get('has_solution'))

    def test_exercise_solution_reveal_endpoint(self):
        course = self._create_course()
        CourseStudent.objects.create(user=self.student, course=course)
        from apps.order.models import Order
        Order.objects.create(course=course, user=self.student, status=OrderStatus.PAID, total_amount=0)

        lesson = Lessons.objects.get(course_unit__course=course, kind='EXERCISE')

        self.client.force_authenticate(user=self.student)
        response = self.client.post(f'/api/users/exercise/{lesson.id}/solution/', {}, format='json')
        self.assertEqual(response.status_code, 200, msg=response.content)
        payload = response.json()
        self.assertIn('return 42', payload.get('data', payload).get('solution', ''))

    def test_assignment_submission_round_trip(self):
        course = self._create_course()
        CourseStudent.objects.create(user=self.student, course=course)
        from apps.order.models import Order
        Order.objects.create(course=course, user=self.student, status=OrderStatus.PAID, total_amount=0)

        lesson = Lessons.objects.get(course_unit__course=course, kind='ASSIGNMENT')

        self.client.force_authenticate(user=self.student)
        file_data = BytesIO(b'submission contents')
        file_data.name = 'work.txt'
        response = self.client.post(
            f'/api/users/assignment/{lesson.id}/submit/',
            {'file': file_data, 'note': 'My work'},
            format='multipart',
        )
        self.assertEqual(response.status_code, 201, msg=response.content)
        self.assertEqual(AssignmentSubmission.objects.filter(lesson=lesson, student=self.student).count(), 1)

        # Resubmit — each attempt is kept as history (no unique constraint).
        again = BytesIO(b'second pass')
        again.name = 'work2.txt'
        response = self.client.post(
            f'/api/users/assignment/{lesson.id}/submit/',
            {'file': again, 'note': 'better'},
            format='multipart',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(AssignmentSubmission.objects.filter(lesson=lesson, student=self.student).count(), 2)

        # Student history endpoint returns both attempts, newest first.
        response = self.client.get(f'/api/users/assignment/{lesson.id}/submission/')
        self.assertEqual(response.status_code, 200, msg=response.content)
        history = response.json().get('data', [])
        self.assertEqual(len(history), 2)

        # Submitting notifies the tutor (one per submit / resubmit).
        self.assertEqual(
            Notification.objects.filter(
                recipient=self.teacher, type=NotificationType.ASSIGNMENT_SUBMITTED
            ).count(),
            2,
        )

        # Tutor lists every attempt (per-lesson view).
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f'/api/teachers/assignment/{lesson.id}/submissions/')
        self.assertEqual(response.status_code, 200, msg=response.content)
        body = response.json()
        rows = body.get('data', body)
        self.assertEqual(len(rows), 2)

        # Tutor inbox aggregates across courses too.
        response = self.client.get('/api/teachers/assignment/submissions/')
        self.assertEqual(response.status_code, 200, msg=response.content)
        inbox = response.json().get('data', [])
        self.assertEqual(len(inbox), 2)
        self.assertEqual(inbox[0].get('lesson_title'), lesson.title)

        # Tutor grades the latest attempt -> the student gets a notification.
        submission_id = rows[0]['id']
        response = self.client.patch(
            f'/api/teachers/assignment/submission/{submission_id}/grade/',
            {'grade': 'A', 'feedback': 'Great work'},
            format='json',
        )
        self.assertEqual(response.status_code, 200, msg=response.content)
        self.assertEqual(
            Notification.objects.filter(
                recipient=self.student, type=NotificationType.ASSIGNMENT_GRADED
            ).count(),
            1,
        )

    def test_multiple_file_submission_when_allowed(self):
        course = self._create_course()
        CourseStudent.objects.create(user=self.student, course=course)
        from apps.order.models import Order
        Order.objects.create(course=course, user=self.student, status=OrderStatus.PAID, total_amount=0)

        lesson = Lessons.objects.get(course_unit__course=course, kind='ASSIGNMENT')
        lesson.allow_multiple_files = True
        lesson.save(update_fields=['allow_multiple_files'])

        self.client.force_authenticate(user=self.student)
        f1 = BytesIO(b'one'); f1.name = 'a.txt'
        f2 = BytesIO(b'two'); f2.name = 'b.txt'
        response = self.client.post(
            f'/api/users/assignment/{lesson.id}/submit/',
            {'files': [f1, f2], 'note': 'multi'},
            format='multipart',
        )
        self.assertEqual(response.status_code, 201, msg=response.content)
        data = response.json().get('data', {})
        self.assertEqual(len(data.get('files', [])), 2)

        sub = AssignmentSubmission.objects.filter(lesson=lesson, student=self.student).first()
        self.assertEqual(sub.files.count(), 1)  # 1 primary on `file` + 1 extra row

    def test_discussion_posts_are_public(self):
        course = self._create_course()
        CourseStudent.objects.create(user=self.student, course=course)
        from apps.order.models import Order
        Order.objects.create(course=course, user=self.student, status=OrderStatus.PAID, total_amount=0)
        lesson = Lessons.objects.get(course_unit__course=course, kind='DISCUSSION')

        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            f'/api/users/discussion/{lesson.id}/posts/', {'text': 'my answer'}, format='json'
        )
        self.assertEqual(response.status_code, 201, msg=response.content)

        # The course tutor (and any enrolled user) sees the post publicly.
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f'/api/users/discussion/{lesson.id}/posts/')
        self.assertEqual(response.status_code, 200, msg=response.content)
        posts = response.json().get('data', [])
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]['text'], 'my answer')
        self.assertTrue(posts[0]['author_name'])

    def test_exercise_submission_upserts(self):
        from apps.course.models.student_activity import ExerciseSubmission

        course = self._create_course()
        CourseStudent.objects.create(user=self.student, course=course)
        from apps.order.models import Order
        Order.objects.create(course=course, user=self.student, status=OrderStatus.PAID, total_amount=0)
        lesson = Lessons.objects.get(course_unit__course=course, kind='EXERCISE')

        self.client.force_authenticate(user=self.student)
        r1 = self.client.post(f'/api/users/exercise/{lesson.id}/submit/', {'code': 'print(1)'}, format='json')
        self.assertEqual(r1.status_code, 201, msg=r1.content)
        r2 = self.client.post(f'/api/users/exercise/{lesson.id}/submit/', {'code': 'print(2)'}, format='json')
        self.assertEqual(r2.status_code, 201, msg=r2.content)

        self.assertEqual(
            ExerciseSubmission.objects.filter(lesson=lesson, student=self.student).count(), 1
        )
        got = self.client.get(f'/api/users/exercise/{lesson.id}/submission/')
        self.assertEqual(got.json().get('data', {}).get('code'), 'print(2)')

    def test_update_unit_edits_title_and_desc(self):
        course = self._create_course()
        unit = CourseUnit.objects.filter(course=course).order_by('order', 'created_at').first()
        response = self.client.patch(
            f'/api/teachers/courses/{course.id}/units/{unit.id}/',
            {'title': 'Renamed unit', 'desc': 'Updated description'},
            format='json',
        )
        self.assertEqual(response.status_code, 200, msg=response.content)
        unit.refresh_from_db()
        self.assertEqual(unit.title, 'Renamed unit')
        self.assertEqual(unit.desc, 'Updated description')

        # Empty title is rejected.
        response = self.client.patch(
            f'/api/teachers/courses/{course.id}/units/{unit.id}/',
            {'title': '   '},
            format='json',
        )
        self.assertEqual(response.status_code, 400, msg=response.content)

    def test_reorder_persists_lesson_order_and_cross_unit_move(self):
        course = self._create_course()
        units = list(CourseUnit.objects.filter(course=course).order_by('order', 'created_at'))
        self.assertGreaterEqual(len(units), 1)

        first = units[0]
        lessons = list(Lessons.objects.filter(course_unit=first).order_by('order', 'created_at'))
        self.assertGreaterEqual(len(lessons), 2)

        # Reverse the lesson order in the first unit.
        reversed_ids = [str(item.id) for item in reversed(lessons)]
        payload = {
            'units': [
                {
                    'id': str(unit.id),
                    'lessons': reversed_ids if unit.id == first.id else [
                        str(item.id)
                        for item in Lessons.objects.filter(course_unit=unit).order_by('order', 'created_at')
                    ],
                }
                for unit in units
            ]
        }

        response = self.client.post(
            f'/api/teachers/courses/{course.id}/reorder/', payload, format='json'
        )
        self.assertEqual(response.status_code, 200, msg=response.content)

        new_order = [
            str(pk)
            for pk in Lessons.objects.filter(course_unit=first).order_by('order').values_list('id', flat=True)
        ]
        self.assertEqual(new_order, reversed_ids)

        # If there's a second unit, move the first lesson into it.
        if len(units) >= 2:
            second = units[1]
            moved_id = reversed_ids[0]
            payload['units'][0]['lessons'] = reversed_ids[1:]
            payload['units'][1]['lessons'] = [moved_id] + [
                str(item.id)
                for item in Lessons.objects.filter(course_unit=second).order_by('order', 'created_at')
            ]
            response = self.client.post(
                f'/api/teachers/courses/{course.id}/reorder/', payload, format='json'
            )
            self.assertEqual(response.status_code, 200, msg=response.content)
            moved = Lessons.objects.get(pk=moved_id)
            self.assertEqual(str(moved.course_unit_id), str(second.id))

    def test_course_student_progress_persists_completed_lectures(self):
        course = self._create_course()
        from apps.order.models import Order
        CourseStudent.objects.create(user=self.student, course=course)
        Order.objects.create(course=course, user=self.student, status=OrderStatus.PAID, total_amount=0)

        enrollment = CourseStudent.objects.get(user=self.student, course=course)
        first_two = list(Lessons.objects.filter(course_unit__course=course).values_list('id', flat=True))[:2]

        self.client.force_authenticate(user=self.student)
        response = self.client.patch(
            f'/api/users/my-courses/{enrollment.id}/',
            {'completed_lectures': [str(pk) for pk in first_two]},
            format='json',
        )
        self.assertEqual(response.status_code, 200, msg=response.content)
        enrollment.refresh_from_db()
        self.assertEqual(sorted(enrollment.completed_lectures), sorted(str(pk) for pk in first_two))
        # 2 of 7 lessons ≈ 29%
        self.assertGreater(enrollment.progress, 20)
        self.assertLess(enrollment.progress, 40)
