import uuid

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0004_coursestudent_completed_lectures'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignmentSubmission',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('file', models.FileField(blank=True, null=True, upload_to='assignments/submissions/')),
                ('note', models.TextField(blank=True, default='')),
                ('grade', models.CharField(blank=True, default='', max_length=10)),
                ('feedback', models.TextField(blank=True, default='')),
                ('status', models.CharField(
                    choices=[('SUBMITTED', 'Submitted'), ('GRADED', 'Graded')],
                    default='SUBMITTED',
                    max_length=16,
                )),
                ('lesson', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='assignment_submissions',
                    to='course.lessons',
                )),
                ('student', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='assignment_submissions',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'db_table': 'assignment_submission',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='assignmentsubmission',
            constraint=models.UniqueConstraint(
                fields=('lesson', 'student'),
                name='uniq_assignment_submission_per_lesson_student',
            ),
        ),
    ]
