from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0005_assignmentsubmission'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessons',
            name='captions',
            field=models.FileField(blank=True, null=True, upload_to='lessons/captions'),
        ),
    ]
