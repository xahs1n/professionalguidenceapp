import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'p2p.settings')
django.setup()

from django.contrib.auth import get_user_model
from home.models import Session, DirectMessage
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

def setup_test_data():
    # 1. Ensure admin exists and has skills
    admin, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@test.com'})
    if created:
        admin.set_password('shary123')
    
    admin.user_type = 'mentee'
    admin.current_skill_level = 'Beginner'
    admin.save()
    admin.skills.add('Python', 'Django')

    # 2. Ensure a Mentor exists with the same skills
    expert_mentor, created = User.objects.get_or_create(username='expert_mentor', defaults={'email': 'mentor@test.com', 'is_available_for_mentoring': True})
    expert_mentor.set_password('shary123')
    expert_mentor.user_type = 'mentor'
    expert_mentor.full_name = 'Expert Mentor'
    expert_mentor.mentor_expertise = 'Expert in Python and Django'
    expert_mentor.save()
    expert_mentor.skills.add('Python', 'Django')

    # 3. Create a Session by the Mentor (so admin mentee sees it as recommended)
    s1, created = Session.objects.get_or_create(subject_detail="Advanced Django", initiator=expert_mentor)
    s1.session_type = 'post'
    s1.description = "Learn advanced django."
    s1.scheduled_at = timezone.now() + timedelta(days=2)
    s1.status = 'open'
    s1.save()
    s1.tags.add('Python', 'Django', 'Beginner')  # added 'Beginner' map directly to skill level!

    # 4. Create some Chat Messages between admin and expert_mentor
    msg, created = DirectMessage.objects.get_or_create(
        sender=expert_mentor,
        recipient=admin,
        content="Hello admin! I can help you with Python."
    )

    print("Successfully setup: Admin Mentee, Expert Mentor, overlapping tags, test session & chat message.")

if __name__ == '__main__':
    setup_test_data()
