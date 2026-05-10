import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('railwayapp', '0002_remove_billablerate_assignment_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContractorFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_name', models.CharField(max_length=255)),
                ('object_key', models.CharField(max_length=500, unique=True)),
                ('content_type', models.CharField(max_length=100)),
                ('file_size', models.PositiveIntegerField()),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('staff_member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='railwayapp.staffmember')),
            ],
            options={
                'db_table': 'ContractorFile',
                'ordering': ['-uploaded_at'],
            },
        ),
    ]
