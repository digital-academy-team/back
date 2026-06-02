from rest_framework import serializers

from apps.course.models.assignment_submission import AssignmentSubmission


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source='student.username', read_only=True)
    student_email = serializers.CharField(source='student.email', read_only=True)
    student_full_name = serializers.SerializerMethodField()
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    course_id = serializers.CharField(source='lesson.course_unit.course.id', read_only=True)
    course_title = serializers.CharField(source='lesson.course_unit.course.title', read_only=True)
    files = serializers.SerializerMethodField()

    class Meta:
        model = AssignmentSubmission
        fields = [
            'id',
            'lesson',
            'lesson_title',
            'course_id',
            'course_title',
            'student',
            'student_username',
            'student_email',
            'student_full_name',
            'file',
            'files',
            'note',
            'grade',
            'feedback',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'lesson',
            'lesson_title',
            'course_id',
            'course_title',
            'student',
            'student_username',
            'student_email',
            'student_full_name',
            'status',
            'created_at',
            'updated_at',
        ]

    def get_student_full_name(self, obj) -> str:
        name = (obj.student.get_full_name() or '').strip()
        return name or obj.student.username or obj.student.email or ''

    def get_files(self, obj):
        """All files in this submission: the primary ``file`` first, then any
        extra ``AssignmentSubmissionFile`` rows. Absolute URLs when possible."""
        request = self.context.get('request')

        def abs_url(field):
            url = field.url
            return request.build_absolute_uri(url) if request else url

        out = []
        if obj.file:
            out.append({'id': f'{obj.id}-primary', 'url': abs_url(obj.file), 'name': obj.file.name})
        for row in obj.files.all():
            if row.file:
                out.append({'id': str(row.id), 'url': abs_url(row.file), 'name': row.file.name})
        return out


class AssignmentSubmissionWriteSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=False, allow_null=True)
    note = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = AssignmentSubmission
        fields = ['file', 'note']


class AssignmentSubmissionGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = ['grade', 'feedback']
